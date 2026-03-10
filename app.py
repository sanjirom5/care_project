from flask import Flask, render_template, request, redirect, session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from functools import wraps
from config import DB_URL

app = Flask(__name__, template_folder="templates")
app.secret_key = "change-this-in-production"

engine = create_engine(DB_URL)
DB = sessionmaker(bind=engine, expire_on_commit=False)


# ---------------------------------------------------------------------------
# Auth decorators
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated


def member_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        if session.get("role") not in ("member", "both"):
            return render_template("forbidden.html"), 403
        return f(*args, **kwargs)
    return decorated


def caregiver_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        if session.get("role") not in ("caregiver", "both"):
            return render_template("forbidden.html"), 403
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def normalize_hourly_rate(raw):
    if not raw:
        return None
    try:
        return int(round(float(raw) / 100) * 100)
    except (ValueError, TypeError):
        return None


def upsert_member(db, user_id, form):
    exists = db.execute(
        text("SELECT 1 FROM member WHERE member_user_id = :uid"), {"uid": user_id}
    ).fetchone()
    if exists:
        db.execute(text("""
            UPDATE member SET house_rules = :hr, dependent_description = :dd
            WHERE member_user_id = :uid
        """), {"hr": form.get("house_rules"), "dd": form.get("dependent_description"), "uid": user_id})
    else:
        db.execute(text("""
            INSERT INTO member (member_user_id, house_rules, dependent_description)
            VALUES (:uid, :hr, :dd)
        """), {"uid": user_id, "hr": form.get("house_rules"), "dd": form.get("dependent_description")})
    _upsert_address(db, user_id, form)


def _upsert_address(db, user_id, form):
    hn, st, tn = form.get("house_number"), form.get("street"), form.get("town")
    addr = db.execute(
        text("SELECT 1 FROM address WHERE member_user_id = :uid"), {"uid": user_id}
    ).fetchone()
    if addr:
        db.execute(text("""
            UPDATE address SET house_number = :hn, street = :st, town = :tn
            WHERE member_user_id = :uid
        """), {"hn": hn, "st": st, "tn": tn, "uid": user_id})
    elif hn or st or tn:
        db.execute(text("""
            INSERT INTO address (member_user_id, house_number, street, town)
            VALUES (:uid, :hn, :st, :tn)
        """), {"uid": user_id, "hn": hn, "st": st, "tn": tn})


def upsert_caregiver(db, user_id, form):
    gender = form.get("gender")
    caregiving_type = form.get("caregiving_type")
    hourly_rate = normalize_hourly_rate(form.get("hourly_rate"))
    exists = db.execute(
        text("SELECT 1 FROM caregiver WHERE caregiver_user_id = :uid"), {"uid": user_id}
    ).fetchone()
    if exists:
        db.execute(text("""
            UPDATE caregiver SET gender = :g, caregiving_type = :ct, hourly_rate = :hr
            WHERE caregiver_user_id = :uid
        """), {"g": gender, "ct": caregiving_type, "hr": hourly_rate, "uid": user_id})
    else:
        db.execute(text("""
            INSERT INTO caregiver (caregiver_user_id, gender, caregiving_type, hourly_rate)
            VALUES (:uid, :g, :ct, :hr)
        """), {"uid": user_id, "g": gender, "ct": caregiving_type, "hr": hourly_rate})


def delete_member_cascade(db, user_id):
    db.execute(text("DELETE FROM appointment WHERE member_user_id = :uid"), {"uid": user_id})
    db.execute(text("""
        DELETE FROM job_application
        WHERE job_id IN (SELECT job_id FROM job WHERE member_user_id = :uid)
    """), {"uid": user_id})
    db.execute(text("DELETE FROM job WHERE member_user_id = :uid"), {"uid": user_id})
    db.execute(text("DELETE FROM address WHERE member_user_id = :uid"), {"uid": user_id})
    db.execute(text("DELETE FROM member WHERE member_user_id = :uid"), {"uid": user_id})


def delete_caregiver_cascade(db, user_id):
    has_appt = db.execute(
        text("SELECT 1 FROM appointment WHERE caregiver_user_id = :uid LIMIT 1"), {"uid": user_id}
    ).fetchone()
    if not has_appt:
        db.execute(text("DELETE FROM caregiver WHERE caregiver_user_id = :uid"), {"uid": user_id})


def get_user_role(db, uid):
    is_c = db.execute(text("SELECT 1 FROM caregiver WHERE caregiver_user_id = :uid"), {"uid": uid}).fetchone()
    is_m = db.execute(text("SELECT 1 FROM member WHERE member_user_id = :uid"), {"uid": uid}).fetchone()
    if is_c and is_m:
        return "both"
    if is_c:
        return "caregiver"
    if is_m:
        return "member"
    return "unknown"


def row_to_obj(row):
    if row is None:
        return None
    class _Obj: pass
    o = _Obj()
    for k, v in row._mapping.items():
        setattr(o, k, v)
    return o


# ---------------------------------------------------------------------------
# Login / Logout / Dashboard
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect("/dashboard")
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        with DB() as db:
            row = db.execute(
                text("SELECT * FROM app_user WHERE email = :e LIMIT 1"), {"e": email}
            ).fetchone()
        if not row or row._mapping["password"] != password:
            return render_template("login.html", error="Invalid email or password.")
        uid = row._mapping["user_id"]
        with DB() as db:
            role = get_user_role(db, uid)
        session["user_id"] = uid
        session["name"] = row._mapping["given_name"]
        session["role"] = role
        return redirect("/dashboard")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# ---------------------------------------------------------------------------
# Sign up
# ---------------------------------------------------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup_choice():
    if request.method == "POST":
        role = request.form.get("role")
        return redirect("/signup/caregiver" if role == "caregiver" else "/signup/member")
    return render_template("signup_choice.html")


@app.route("/signup/caregiver", methods=["GET", "POST"])
def signup_caregiver():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        if not email:
            return render_template("signup_caregiver.html", error="Email is required.", form=request.form)
        with DB() as db:
            if db.execute(text("SELECT 1 FROM app_user WHERE email = :e LIMIT 1"), {"e": email}).fetchone():
                return render_template("signup_caregiver.html", error="Email already registered.", form=request.form)
            try:
                res = db.execute(text("""
                    INSERT INTO app_user
                        (email, given_name, surname, city, phone_number, profile_description, password)
                    VALUES (:email, :gn, :sn, :city, :ph, :pd, :pw)
                    RETURNING user_id
                """), {
                    "email": email,
                    "gn": request.form.get("given_name") or "",
                    "sn": request.form.get("surname") or "",
                    "city": request.form.get("city") or "",
                    "ph": request.form.get("phone_number") or "",
                    "pd": request.form.get("profile_description") or None,
                    "pw": request.form.get("password") or "",
                })
                new_id = res.fetchone()[0]
                db.execute(text("""
                    INSERT INTO caregiver (caregiver_user_id, gender, caregiving_type, hourly_rate)
                    VALUES (:uid, :g, :ct, :hr)
                """), {
                    "uid": new_id,
                    "g": request.form.get("gender"),
                    "ct": request.form.get("caregiving_type"),
                    "hr": normalize_hourly_rate(request.form.get("hourly_rate")),
                })
                db.commit()
                session["user_id"] = new_id
                session["name"] = request.form.get("given_name") or ""
                session["role"] = "caregiver"
            except IntegrityError:
                db.rollback()
                return render_template("signup_caregiver.html",
                                       error="Registration failed, please try again.", form=request.form)
        return redirect("/dashboard")
    return render_template("signup_caregiver.html")


@app.route("/signup/member", methods=["GET", "POST"])
def signup_member():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        if not email:
            return render_template("signup_member.html", error="Email is required.", form=request.form)
        with DB() as db:
            if db.execute(text("SELECT 1 FROM app_user WHERE email = :e LIMIT 1"), {"e": email}).fetchone():
                return render_template("signup_member.html", error="Email already registered.", form=request.form)
            try:
                res = db.execute(text("""
                    INSERT INTO app_user
                        (email, given_name, surname, city, phone_number, profile_description, password)
                    VALUES (:email, :gn, :sn, :city, :ph, NULL, :pw)
                    RETURNING user_id
                """), {
                    "email": email,
                    "gn": request.form.get("given_name") or "",
                    "sn": request.form.get("surname") or "",
                    "city": request.form.get("city") or "",
                    "ph": request.form.get("phone_number") or "",
                    "pw": request.form.get("password") or "",
                })
                new_id = res.fetchone()[0]
                upsert_member(db, new_id, request.form)
                db.commit()
                session["user_id"] = new_id
                session["name"] = request.form.get("given_name") or ""
                session["role"] = "member"
            except IntegrityError:
                db.rollback()
                return render_template("signup_member.html",
                                       error="Registration failed, please try again.", form=request.form)
        return redirect("/dashboard")
    return render_template("signup_member.html")


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

@app.route("/jobs")
@login_required
def jobs():
    with DB() as db:
        rows = db.execute(text("""
            SELECT j.*, u.given_name || ' ' || u.surname AS member_name
            FROM job j
            LEFT JOIN app_user u ON u.user_id = j.member_user_id
            ORDER BY j.job_id
        """)).mappings().all()
    return render_template("jobs.html", jobs=rows)


@app.route("/jobs/create", methods=["GET", "POST"])
@member_required
def create_job():
    if request.method == "POST":
        with DB() as db:
            db.execute(text("""
                INSERT INTO job (member_user_id, required_caregiving_type, other_requirements, date_posted)
                VALUES (:mid, :rct, :req, CURRENT_DATE)
            """), {
                "mid": session["user_id"],
                "rct": request.form.get("required_caregiving_type"),
                "req": request.form.get("other_requirements"),
            })
            db.commit()
        return redirect("/jobs")
    return render_template("job_form.html", job=None, create=True)


@app.route("/jobs/edit/<int:jid>", methods=["GET", "POST"])
@member_required
def edit_job(jid):
    with DB() as db:
        row = db.execute(text("SELECT * FROM job WHERE job_id = :jid"), {"jid": jid}).fetchone()
    if not row or row._mapping["member_user_id"] != session["user_id"]:
        return render_template("forbidden.html"), 403
    if request.method == "POST":
        with DB() as db:
            db.execute(text("""
                UPDATE job SET required_caregiving_type = :rct, other_requirements = :req
                WHERE job_id = :jid
            """), {
                "rct": request.form.get("required_caregiving_type"),
                "req": request.form.get("other_requirements"),
                "jid": jid,
            })
            db.commit()
        return redirect("/jobs")
    return render_template("job_form.html", job=dict(row._mapping), create=False)


@app.route("/jobs/delete/<int:jid>")
@member_required
def delete_job(jid):
    with DB() as db:
        row = db.execute(text("SELECT member_user_id FROM job WHERE job_id = :jid"), {"jid": jid}).fetchone()
        if not row or row._mapping["member_user_id"] != session["user_id"]:
            return render_template("forbidden.html"), 403
        db.execute(text("DELETE FROM job_application WHERE job_id = :jid"), {"jid": jid})
        db.execute(text("DELETE FROM job WHERE job_id = :jid"), {"jid": jid})
        db.commit()
    return redirect("/jobs")


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

@app.route("/applications")
@login_required
def applications():
    uid = session["user_id"]
    role = session.get("role")
    with DB() as db:
        if role in ("caregiver", "both"):
            rows = db.execute(text("""
                SELECT ja.*, u.given_name || ' ' || u.surname AS caregiver_name,
                       j.required_caregiving_type, j.member_user_id
                FROM job_application ja
                LEFT JOIN app_user u ON u.user_id = ja.caregiver_user_id
                LEFT JOIN job j ON j.job_id = ja.job_id
                WHERE ja.caregiver_user_id = :uid
                ORDER BY ja.job_id
            """), {"uid": uid}).mappings().all()
        else:
            rows = db.execute(text("""
                SELECT ja.*, u.given_name || ' ' || u.surname AS caregiver_name,
                       j.required_caregiving_type, j.member_user_id
                FROM job_application ja
                LEFT JOIN app_user u ON u.user_id = ja.caregiver_user_id
                LEFT JOIN job j ON j.job_id = ja.job_id
                WHERE j.member_user_id = :uid
                ORDER BY ja.job_id
            """), {"uid": uid}).mappings().all()
    return render_template("applications.html", applications=rows)


@app.route("/applications/create", methods=["GET", "POST"])
@caregiver_required
def create_application():
    if request.method == "POST":
        with DB() as db:
            db.execute(text("""
                INSERT INTO job_application (caregiver_user_id, job_id, date_applied)
                VALUES (:cid, :jid, CURRENT_DATE)
            """), {"cid": session["user_id"], "jid": request.form.get("job_id")})
            db.commit()
        return redirect("/applications")
    with DB() as db:
        jobs_list = db.execute(
            text("SELECT job_id, other_requirements FROM job ORDER BY job_id")
        ).mappings().all()
    return render_template("application_form.html", jobs=jobs_list)


@app.route("/applications/delete/<int:cid>/<int:jid>")
@caregiver_required
def delete_application(cid, jid):
    if session["user_id"] != cid:
        return render_template("forbidden.html"), 403
    with DB() as db:
        db.execute(text("""
            DELETE FROM job_application WHERE caregiver_user_id = :cid AND job_id = :jid
        """), {"cid": cid, "jid": jid})
        db.commit()
    return redirect("/applications")


# ---------------------------------------------------------------------------
# Appointments
# ---------------------------------------------------------------------------

@app.route("/appointments")
@login_required
def appointments():
    uid = session["user_id"]
    with DB() as db:
        rows = db.execute(text("""
            SELECT a.*,
                   cu.given_name || ' ' || cu.surname AS caregiver_name,
                   mu.given_name || ' ' || mu.surname AS member_name
            FROM appointment a
            LEFT JOIN app_user cu ON cu.user_id = a.caregiver_user_id
            LEFT JOIN app_user mu ON mu.user_id = a.member_user_id
            WHERE a.caregiver_user_id = :uid OR a.member_user_id = :uid
            ORDER BY a.appointment_date DESC
        """), {"uid": uid}).mappings().all()
    return render_template("appointments.html", appointments=rows)


@app.route("/appointments/create", methods=["GET", "POST"])
@member_required
def create_appointment():
    if request.method == "POST":
        with DB() as db:
            db.execute(text("""
                INSERT INTO appointment
                    (caregiver_user_id, member_user_id, appointment_date, appointment_time, work_hours, status)
                VALUES (:cid, :mid, :adate, :atime, :wh, 'pending')
            """), {
                "cid": request.form.get("caregiver_user_id"),
                "mid": session["user_id"],
                "adate": request.form.get("appointment_date"),
                "atime": request.form.get("appointment_time"),
                "wh": request.form.get("work_hours"),
            })
            db.commit()
        return redirect("/appointments")
    with DB() as db:
        caregivers = db.execute(text("""
            SELECT user_id, given_name || ' ' || surname AS name
            FROM app_user WHERE user_id IN (SELECT caregiver_user_id FROM caregiver)
            ORDER BY user_id
        """)).mappings().all()
    return render_template("appointment_form.html", caregivers=caregivers)


@app.route("/appointments/delete/<int:aid>")
@login_required
def delete_appointment(aid):
    with DB() as db:
        row = db.execute(
            text("SELECT caregiver_user_id, member_user_id FROM appointment WHERE appointment_id = :aid"),
            {"aid": aid}
        ).fetchone()
        if not row:
            return redirect("/appointments")
        m = row._mapping
        if session["user_id"] not in (m["caregiver_user_id"], m["member_user_id"]):
            return render_template("forbidden.html"), 403
        db.execute(text("DELETE FROM appointment WHERE appointment_id = :aid"), {"aid": aid})
        db.commit()
    return redirect("/appointments")


if __name__ == "__main__":
    app.run(debug=True)