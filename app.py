from flask import Flask, render_template, request, redirect
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import DB_URL
from models import Base, AppUser

app = Flask(__name__, template_folder="templates")

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine, expire_on_commit=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/users")
def users():
    session = Session()
    rows = session.execute(text("""
        SELECT u.user_id, u.email, u.given_name, u.surname, u.city,
               CASE
                 WHEN c.caregiver_user_id IS NOT NULL AND m.member_user_id IS NOT NULL THEN 'Caregiver, Member'
                 WHEN c.caregiver_user_id IS NOT NULL THEN 'Caregiver'
                 WHEN m.member_user_id IS NOT NULL THEN 'Member'
                 ELSE 'Unknown'
               END AS role
        FROM app_user u
        LEFT JOIN caregiver c ON c.caregiver_user_id = u.user_id
        LEFT JOIN member m ON m.member_user_id = u.user_id
        ORDER BY u.user_id
    """)).mappings().all()

    return render_template("users.html", users=rows)

@app.route("/users/create", methods=["GET", "POST"])
def create_user():
    session = Session()
    if request.method == "POST":
        # 1) Insert app_user
        res = session.execute(text("""
            INSERT INTO app_user (email, given_name, surname, city, phone_number, profile_description, password)
            VALUES (:email, :given_name, :surname, :city, :phone_number, :profile_description, :password)
            RETURNING user_id
        """), {
            "email": request.form.get("email"),
            "given_name": request.form.get("given_name"),
            "surname": request.form.get("surname"),
            "city": request.form.get("city"),
            "phone_number": request.form.get("phone_number"),
            "profile_description": request.form.get("profile_description"),
            "password": request.form.get("password")
        })
        new_user_id = res.fetchone()[0]

        # 2) If is_member checked -> create member + address
        if request.form.get("is_member"):
            session.execute(text("""
                INSERT INTO member (member_user_id, house_rules, dependent_description)
                VALUES (:uid, :house_rules, :dependent_description)
            """), {
                "uid": new_user_id,
                "house_rules": request.form.get("house_rules"),
                "dependent_description": request.form.get("dependent_description")
            })

            # if address fields provided -> insert address
            house_number = request.form.get("house_number")
            street = request.form.get("street")
            town = request.form.get("town")
            if house_number or street or town:
                session.execute(text("""
                    INSERT INTO address (member_user_id, house_number, street, town)
                    VALUES (:uid, :house_number, :street, :town)
                """), {
                    "uid": new_user_id,
                    "house_number": house_number,
                    "street": street,
                    "town": town
                })

        session.commit()
        return redirect("/users")

    # GET
    return render_template("user_form.html", user=None, member=None, address=None, edit=False)

@app.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    session = Session()

    def norm_rate(v):
        if not v:
            return None
        try:
            f = float(v)
        except:
            return None
        return int(round(f / 100) * 100)

    if request.method == "POST":
        # Update base user row
        session.execute(text("""
            UPDATE app_user
            SET email=:email,
                given_name=:gn,
                surname=:sn,
                city=:city,
                phone_number=:ph,
                profile_description=:pd,
                password=:pw
            WHERE user_id=:uid
        """), {
            "email": request.form.get("email"),
            "gn": request.form.get("given_name"),
            "sn": request.form.get("surname"),
            "city": request.form.get("city"),
            "ph": request.form.get("phone_number"),
            "pd": request.form.get("profile_description"),
            "pw": request.form.get("password"),
            "uid": user_id
        })

        # Determine roles
        want_member = bool(request.form.get("is_member"))
        want_caregiver = bool(request.form.get("is_caregiver"))

        # ----- MEMBER -----
        mem_exists = session.execute(text(
            "SELECT 1 FROM member WHERE member_user_id=:uid"
        ), {"uid": user_id}).fetchone()

        if want_member:
            # Create/update member
            if mem_exists:
                session.execute(text("""
                    UPDATE member
                    SET house_rules=:hr,
                        dependent_description=:dd
                    WHERE member_user_id=:uid
                """), {
                    "hr": request.form.get("house_rules"),
                    "dd": request.form.get("dependent_description"),
                    "uid": user_id
                })
            else:
                session.execute(text("""
                    INSERT INTO member (member_user_id, house_rules, dependent_description)
                    VALUES (:uid, :hr, :dd)
                """), {
                    "uid": user_id,
                    "hr": request.form.get("house_rules"),
                    "dd": request.form.get("dependent_description")
                })

            # Address create/update
            addr = session.execute(text(
                "SELECT 1 FROM address WHERE member_user_id=:uid"
            ), {"uid": user_id}).fetchone()

            hn = request.form.get("house_number")
            st = request.form.get("street")
            tn = request.form.get("town")

            if addr:
                session.execute(text("""
                    UPDATE address
                    SET house_number=:hn, street=:st, town=:tn
                    WHERE member_user_id=:uid
                """), {"hn": hn, "st": st, "tn": tn, "uid": user_id})
            else:
                if hn or st or tn:
                    session.execute(text("""
                        INSERT INTO address (member_user_id, house_number, street, town)
                        VALUES (:uid, :hn, :st, :tn)
                    """), {"uid": user_id, "hn": hn, "st": st, "tn": tn})

        else:
            # Deleting member role (clean up tables)
            session.execute(text("DELETE FROM address WHERE member_user_id=:uid"), {"uid": user_id})
            session.execute(text("DELETE FROM job_application WHERE job_id IN (SELECT job_id FROM job WHERE member_user_id=:uid)"), {"uid": user_id})
            session.execute(text("DELETE FROM job WHERE member_user_id=:uid"), {"uid": user_id})
            session.execute(text("DELETE FROM member WHERE member_user_id=:uid"), {"uid": user_id})

        # ----- CAREGIVER -----
        care_exists = session.execute(text(
            "SELECT 1 FROM caregiver WHERE caregiver_user_id=:uid"
        ), {"uid": user_id}).fetchone()

        if want_caregiver:
            gender = request.form.get("gender")
            caregiving_type = request.form.get("caregiving_type")
            hourly_rate = norm_rate(request.form.get("hourly_rate"))

            if care_exists:
                session.execute(text("""
                    UPDATE caregiver
                    SET gender=:g,
                        caregiving_type=:ct,
                        hourly_rate=:hr
                    WHERE caregiver_user_id=:uid
                """), {"g": gender, "ct": caregiving_type, "hr": hourly_rate, "uid": user_id})
            else:
                session.execute(text("""
                    INSERT INTO caregiver (caregiver_user_id, gender, caregiving_type, hourly_rate)
                    VALUES (:uid, :g, :ct, :hr)
                """), {"uid": user_id, "g": gender, "ct": caregiving_type, "hr": hourly_rate})

        else:
            fk = session.execute(text(
                "SELECT 1 FROM appointment WHERE caregiver_user_id=:uid LIMIT 1"
            ), {"uid": user_id}).fetchone()

            if not fk:
                session.execute(text("DELETE FROM caregiver WHERE caregiver_user_id=:uid"), {"uid": user_id})

        session.commit()
        return redirect("/users")

    # ===== GET =====
    user_row = session.execute(text("SELECT * FROM app_user WHERE user_id=:uid"), {"uid": user_id}).fetchone()
    member_row = session.execute(text("SELECT * FROM member WHERE member_user_id=:uid"), {"uid": user_id}).fetchone()
    address_row = session.execute(text("SELECT * FROM address WHERE member_user_id=:uid"), {"uid": user_id}).fetchone()
    caregiver_row = session.execute(text("SELECT * FROM caregiver WHERE caregiver_user_id=:uid"), {"uid": user_id}).fetchone()

    class Obj: pass

    def conv(row):
        if not row:
            return None
        o = Obj()
        for k, v in row._mapping.items():
            setattr(o, k, v)
        return o

    return render_template(
        "user_form.html",
        user=conv(user_row),
        member=conv(member_row),
        address=conv(address_row),
        caregiver=conv(caregiver_row),
        role=("Caregiver" if caregiver_row else "Member" if member_row else "Unknown"),
        edit=True
    )

@app.route("/users/delete/<int:user_id>")
def delete_user(user_id):
    session = Session()

    # 1. Delete appointments where user is a member
    session.execute(text("""
        DELETE FROM appointment
        WHERE member_user_id = :uid
    """), {"uid": user_id})

    # 2. Delete appointments where user is a caregiver
    session.execute(text("""
        DELETE FROM appointment
        WHERE caregiver_user_id = :uid
    """), {"uid": user_id})

    # 3. Delete job applications sent by this user (as caregiver)
    session.execute(text("""
        DELETE FROM job_application
        WHERE caregiver_user_id = :uid
    """), {"uid": user_id})

    # 4. Delete job applications to jobs owned by this user (as member)
    session.execute(text("""
        DELETE FROM job_application
        WHERE job_id IN (
            SELECT job_id FROM job WHERE member_user_id = :uid
        )
    """), {"uid": user_id})

    # 5. Delete jobs posted by this user (as member)
    session.execute(text("""
        DELETE FROM job
        WHERE member_user_id = :uid
    """), {"uid": user_id})

    # 6. Delete address (if user is a member)
    session.execute(text("""
        DELETE FROM address
        WHERE member_user_id = :uid
    """), {"uid": user_id})

    # 7. Delete caregiver profile (if exists)
    session.execute(text("""
        DELETE FROM caregiver
        WHERE caregiver_user_id = :uid
    """), {"uid": user_id})

    # 8. Delete member profile (if exists)
    session.execute(text("""
        DELETE FROM member
        WHERE member_user_id = :uid
    """), {"uid": user_id})

    # 9. Finally delete user
    session.execute(text("""
        DELETE FROM app_user
        WHERE user_id = :uid
    """), {"uid": user_id})

    session.commit()
    return redirect("/users")
from sqlalchemy.exc import IntegrityError

# --- Signup choice (first step) ---
@app.route("/signup", methods=["GET", "POST"])
def signup_choice():
    if request.method == "GET":
        return render_template("signup_choice.html")
    role = request.form.get("role")
    if role == "caregiver":
        return redirect("/signup/caregiver")
    return redirect("/signup/member")

@app.route("/signup/caregiver", methods=["GET", "POST"])
def signup_caregiver():
    session = Session()
    error = None

    if request.method == "POST":
        # basic form values
        email = (request.form.get("email") or "").strip().lower()
        given_name = request.form.get("given_name") or ""
        surname = request.form.get("surname") or ""
        city = request.form.get("city") or ""
        phone_number = request.form.get("phone_number") or ""
        profile_description = request.form.get("profile_description") or None
        password = request.form.get("password") or ""

        uploaded_photo = request.files.get("photo")
        photo_filename = uploaded_photo.filename if uploaded_photo and uploaded_photo.filename else None
        
        # validate email
        if not email:
            error = "Email is required."
            return render_template("signup_caregiver.html", error=error, form=request.form)

        # check existing email
        exists = session.execute(
            text("SELECT 1 FROM app_user WHERE email = :email LIMIT 1"),
            {"email": email}
        ).fetchone()
        if exists:
            error = "This email is already registered. Use another email or sign in."
            return render_template("signup_caregiver.html", error=error, form=request.form)

        # try to create app_user, handle race conditions with IntegrityError
        try:
            res = session.execute(text("""
                INSERT INTO app_user (email, given_name, surname, city, phone_number, profile_description, password)
                VALUES (:email, :given_name, :surname, :city, :phone_number, :profile_description, :password)
                RETURNING user_id
            """), {
                "email": email,
                "given_name": given_name,
                "surname": surname,
                "city": city,
                "phone_number": phone_number,
                "profile_description": profile_description,
                "password": password
            })
            new_user_id = res.fetchone()[0]
        except IntegrityError:
            session.rollback()
            error = "Email already exists (concurrent request). Try a different email or sign in."
            return render_template("signup_caregiver.html", error=error, form=request.form)

        # normalize hourly rate: convert to float, round to nearest 100 and store integer KZT
        def norm_rate_to_kzt(raw):
            if not raw:
                return None
            try:
                f = float(raw)
            except Exception:
                return None
            return int(round(f / 100.0) * 100)

        hourly_rate_raw = request.form.get("hourly_rate") or ""
        hourly_rate_kzt = norm_rate_to_kzt(hourly_rate_raw)

        # Insert caregiver row.
        try:
            session.execute(text("""
                INSERT INTO caregiver (caregiver_user_id, gender, caregiving_type, hourly_rate)
                VALUES (:uid, :gender, :caregiving_type, :hourly_rate)
            """), {
                "uid": new_user_id,
                "gender": request.form.get("gender"),
                "caregiving_type": request.form.get("caregiving_type"),
                "hourly_rate": hourly_rate_kzt
            })
            session.commit()
        except IntegrityError:
            session.rollback()
            error = "Failed to create caregiver profile due to database constraint. Check schema."
            return render_template("signup_caregiver.html", error=error, form=request.form)

        return redirect("/users")

    return render_template("signup_caregiver.html")


@app.route("/signup/member", methods=["GET", "POST"])
def signup_member():
    session = Session()
    error = None

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        given_name = request.form.get("given_name") or ""
        surname = request.form.get("surname") or ""
        city = request.form.get("city") or ""
        phone_number = request.form.get("phone_number") or ""
        password = request.form.get("password") or ""

        # validate email
        if not email:
            error = "Email is required."
            return render_template("signup_member.html", error=error, form=request.form)

        exists = session.execute(
            text("SELECT 1 FROM app_user WHERE email = :email LIMIT 1"),
            {"email": email}
        ).fetchone()
        if exists:
            error = "This email is already registered. Use another email or sign in."
            return render_template("signup_member.html", error=error, form=request.form)

        # create app_user - protect with try/except
        try:
            res = session.execute(text("""
                INSERT INTO app_user (email, given_name, surname, city, phone_number, profile_description, password)
                VALUES (:email, :given_name, :surname, :city, :phone_number, :profile_description, :password)
                RETURNING user_id
            """), {
                "email": email,
                "given_name": given_name,
                "surname": surname,
                "city": city,
                "phone_number": phone_number,
                # we keep profile_description NULL by default for members
                "profile_description": None,
                "password": password
            })
            new_user_id = res.fetchone()[0]
        except IntegrityError:
            session.rollback()
            error = "Email already exists (concurrent request). Try a different email or sign in."
            return render_template("signup_member.html", error=error, form=request.form)

        # insert member record
        try:
            session.execute(text("""
                INSERT INTO member (member_user_id, house_rules, dependent_description)
                VALUES (:uid, :house_rules, :dependent_description)
            """), {
                "uid": new_user_id,
                "house_rules": request.form.get("house_rules"),
                "dependent_description": request.form.get("dependent_description")
            })

            # optional address
            house_number = request.form.get("house_number")
            street = request.form.get("street")
            town = request.form.get("town")
            if house_number or street or town:
                session.execute(text("""
                    INSERT INTO address (member_user_id, house_number, street, town)
                    VALUES (:uid, :house_number, :street, :town)
                """), {
                    "uid": new_user_id,
                    "house_number": house_number,
                    "street": street,
                    "town": town
                })

            session.commit()
        except IntegrityError:
            session.rollback()
            error = "Failed to create member profile due to database constraint. Check schema."
            return render_template("signup_member.html", error=error, form=request.form)

        return redirect("/users")

    # GET
    return render_template("signup_member.html")

#  CAREGIVER CRUD 
@app.route("/caregivers")
def caregivers():
    session = Session()
    rows = session.execute(text("SELECT * FROM caregiver ORDER BY caregiver_user_id")).mappings().all()
    return render_template("caregivers.html", caregivers=rows)

@app.route("/caregivers/create", methods=["GET","POST"])
def create_caregiver():
    session = Session()
    if request.method == "POST":
        session.execute(text("""
            INSERT INTO caregiver (caregiver_user_id, photo, gender, caregiving_type, hourly_rate)
            VALUES (:uid, :photo, :gender, :ct, :hr)
        """), {
            "uid": request.form.get("caregiver_user_id"),
            "photo": request.form.get("photo"),
            "gender": request.form.get("gender"),
            "ct": request.form.get("caregiving_type"),
            "hr": request.form.get("hourly_rate") or None
        })
        session.commit()
        return redirect("/caregivers")
    return render_template("caregiver_form.html", caregiver=None, create=True)

@app.route("/caregivers/edit/<int:uid>", methods=["GET","POST"])
def edit_caregiver(uid):
    session = Session()
    if request.method == "POST":
        session.execute(text("""
            UPDATE caregiver SET photo=:photo, gender=:gender, caregiving_type=:ct, hourly_rate=:hr
            WHERE caregiver_user_id = :uid
        """), {"photo": request.form.get("photo"),
               "gender": request.form.get("gender"),
               "ct": request.form.get("caregiving_type"),
               "hr": request.form.get("hourly_rate") or None,
               "uid": uid})
        session.commit()
        return redirect("/caregivers")
    row = session.execute(text("SELECT * FROM caregiver WHERE caregiver_user_id=:uid"), {"uid": uid}).fetchone()
    caregiver = dict(row._mapping) if row else None
    return render_template("caregiver_form.html", caregiver=caregiver, create=False)

@app.route("/caregivers/delete/<int:uid>")
def delete_caregiver(uid):
    session = Session()
    session.execute(text("DELETE FROM caregiver WHERE caregiver_user_id=:uid"), {"uid": uid})
    session.commit()
    return redirect("/caregivers")


#  MEMBER CRUD 
@app.route("/members")
def members():
    session = Session()
    rows = session.execute(text("""
        SELECT
            m.member_user_id,
            m.dependent_description,
            m.house_rules,
            a.house_number,
            a.street,
            a.town,
            u.given_name,
            u.surname,
            u.email,
            u.city
        FROM member m
        LEFT JOIN address a ON a.member_user_id = m.member_user_id
        LEFT JOIN app_user u ON u.user_id = m.member_user_id
        ORDER BY m.member_user_id
    """)).fetchall()

    class Obj: pass

    members = []
    for r in rows:
        o = Obj()
        try:
            keys = r.keys()
            o.id = r['member_user_id']
            parts = [r['house_number'], r['street'], r['town']]
            o.address = ", ".join([str(p) for p in parts if p])
            o.dependent = r['dependent_description'] or ""
            o.house_rules = r['house_rules'] or ""
            given = r.get('given_name') or ""
            surname = r.get('surname') or ""
            o.name = (given + " " + surname).strip()
            o.email = r.get('email') or ""
            o.city = r.get('city') or ""
        except Exception:
            o.id = r[0]
            o.dependent = r[1] or ""
            o.house_rules = r[2] or ""
            parts = [r[3], r[4], r[5]]
            o.address = ", ".join([str(p) for p in parts if p])
            o.name = (r[6] or "") + " " + (r[7] or "")
            o.email = r[8] or ""
            o.city = r[9] or ""

        members.append(o)

    return render_template("members.html", members=members)

@app.route("/members/create", methods=["GET","POST"])
def create_member():
    session = Session()
    if request.method == "POST":
        session.execute(text("""
            INSERT INTO member (member_user_id, house_rules, dependent_description)
            VALUES (:uid, :hr, :dd)
        """), {"uid": request.form.get("member_user_id"),
               "hr": request.form.get("house_rules"),
               "dd": request.form.get("dependent_description")})
        
        hn = request.form.get("house_number"); st = request.form.get("street"); tn = request.form.get("town")
        if hn or st or tn:
            session.execute(text("""
                INSERT INTO address (member_user_id, house_number, street, town)
                VALUES (:uid, :hn, :st, :tn)
            """), {"uid": request.form.get("member_user_id"), "hn": hn, "st": st, "tn": tn})
        session.commit()
        return redirect("/members")
    return render_template("member_form.html", member=None, address=None, create=True)

@app.route("/members/edit/<int:uid>", methods=["GET","POST"])
def edit_member(uid):
    session = Session()
    if request.method == "POST":
        session.execute(text("""
            UPDATE member SET house_rules=:hr, dependent_description=:dd WHERE member_user_id=:uid
        """), {"hr": request.form.get("house_rules"), "dd": request.form.get("dependent_description"), "uid": uid})
        # address update/insert
        addr = session.execute(text("SELECT address_id FROM address WHERE member_user_id=:uid"), {"uid": uid}).fetchone()
        hn = request.form.get("house_number"); st = request.form.get("street"); tn = request.form.get("town")
        if addr:
            session.execute(text("""
                UPDATE address SET house_number=:hn, street=:st, town=:tn WHERE member_user_id=:uid
            """), {"hn": hn, "st": st, "tn": tn, "uid": uid})
        else:
            if hn or st or tn:
                session.execute(text("""
                    INSERT INTO address (member_user_id, house_number, street, town)
                    VALUES (:uid, :hn, :st, :tn)
                """), {"uid": uid, "hn": hn, "st": st, "tn": tn})
        session.commit()
        return redirect("/members")
    mr = session.execute(text("SELECT * FROM member WHERE member_user_id=:uid"), {"uid": uid}).fetchone()
    ar = session.execute(text("SELECT * FROM address WHERE member_user_id=:uid"), {"uid": uid}).fetchone()
    member = dict(mr._mapping) if mr else None
    address = dict(ar._mapping) if ar else None
    return render_template("member_form.html", member=member, address=address, create=False)

@app.route("/members/delete/<int:uid>")
def delete_member(uid):
    session = Session()
    # remove dependent rows carefully (appointments, jobs, app applications)
    session.execute(text("DELETE FROM appointment WHERE member_user_id = :uid"), {"uid": uid})
    session.execute(text("DELETE FROM job_application WHERE job_id IN (SELECT job_id FROM job WHERE member_user_id = :uid)"), {"uid": uid})
    session.execute(text("DELETE FROM job WHERE member_user_id = :uid"), {"uid": uid})
    session.execute(text("DELETE FROM address WHERE member_user_id = :uid"), {"uid": uid})
    session.execute(text("DELETE FROM member WHERE member_user_id = :uid"), {"uid": uid})
    session.commit()
    return redirect("/members")


#  ADDRESS CRUD
@app.route("/addresses")
def addresses():
    session = Session()
    rows = session.execute(text("SELECT * FROM address ORDER BY address_id")).mappings().all()
    return render_template("addresses.html", addresses=rows)

@app.route("/addresses/edit/<int:aid>", methods=["GET","POST"])
def edit_address(aid):
    session = Session()
    if request.method == "POST":
        session.execute(text("""
            UPDATE address SET house_number=:hn, street=:st, town=:tn WHERE address_id=:aid
        """), {"hn": request.form.get("house_number"), "st": request.form.get("street"), "tn": request.form.get("town"), "aid": aid})
        session.commit()
        return redirect("/addresses")
    row = session.execute(text("SELECT * FROM address WHERE address_id=:aid"), {"aid": aid}).fetchone()
    addr = dict(row._mapping) if row else None
    return render_template("address_form.html", address=addr)

@app.route("/addresses/delete/<int:aid>")
def delete_address(aid):
    session = Session()
    session.execute(text("DELETE FROM address WHERE address_id=:aid"), {"aid": aid})
    session.commit()
    return redirect("/addresses")


#  JOB CRUD 
@app.route("/jobs")
def jobs():
    session = Session()
    rows = session.execute(text("""
        SELECT j.*, u.given_name || ' ' || u.surname AS member_name
        FROM job j LEFT JOIN app_user u ON u.user_id = j.member_user_id
        ORDER BY j.job_id
    """)).mappings().all()
    return render_template("jobs.html", jobs=rows)

@app.route("/jobs/create", methods=["GET","POST"])
def create_job():
    session = Session()
    if request.method == "POST":
        session.execute(text("""
            INSERT INTO job (member_user_id, required_caregiving_type, other_requirements, date_posted)
            VALUES (:mid, :rct, :req, CURRENT_DATE)
        """), {"mid": request.form.get("member_user_id"),
               "rct": request.form.get("required_caregiving_type"),
               "req": request.form.get("other_requirements")})
        session.commit()
        return redirect("/jobs")
    # provide member list for select
    members = session.execute(text("SELECT user_id, given_name, surname FROM app_user ORDER BY user_id")).mappings().all()
    return render_template("job_form.html", job=None, members=members, create=True)

@app.route("/jobs/edit/<int:jid>", methods=["GET","POST"])
def edit_job(jid):
    session = Session()
    if request.method == "POST":
        session.execute(text("""
            UPDATE job SET required_caregiving_type=:rct, other_requirements=:req WHERE job_id=:jid
        """), {"rct": request.form.get("required_caregiving_type"), "req": request.form.get("other_requirements"), "jid": jid})
        session.commit()
        return redirect("/jobs")
    row = session.execute(text("SELECT * FROM job WHERE job_id=:jid"), {"jid": jid}).fetchone()
    job = dict(row._mapping) if row else None
    members = session.execute(text("SELECT user_id, given_name, surname FROM app_user ORDER BY user_id")).mappings().all()
    return render_template("job_form.html", job=job, members=members, create=False)

@app.route("/jobs/delete/<int:jid>")
def delete_job(jid):
    session = Session()
    session.execute(text("DELETE FROM job_application WHERE job_id=:jid"), {"jid": jid})
    session.execute(text("DELETE FROM job WHERE job_id=:jid"), {"jid": jid})
    session.commit()
    return redirect("/jobs")


#  JOB APPLICATION CRUD 
@app.route("/applications")
def applications():
    session = Session()
    rows = session.execute(text("""
        SELECT ja.*, u.given_name || ' ' || u.surname AS caregiver_name, j.required_caregiving_type, j.member_user_id
        FROM job_application ja
        LEFT JOIN app_user u ON u.user_id = ja.caregiver_user_id
        LEFT JOIN job j ON j.job_id = ja.job_id
        ORDER BY ja.job_id
    """)).mappings().all()
    return render_template("applications.html", applications=rows)

@app.route("/applications/create", methods=["GET","POST"])
def create_application():
    session = Session()
    if request.method == "POST":
        session.execute(text("""
            INSERT INTO job_application (caregiver_user_id, job_id, date_applied)
            VALUES (:cid, :jid, CURRENT_DATE)
        """), {"cid": request.form.get("caregiver_user_id"), "jid": request.form.get("job_id")})
        session.commit()
        return redirect("/applications")
    caregivers = session.execute(text("SELECT user_id, (given_name || ' ' || surname) as name FROM app_user ORDER BY user_id")).mappings().all()
    jobs_list = session.execute(text("SELECT job_id, other_requirements FROM job ORDER BY job_id")).mappings().all()
    return render_template("application_form.html", caregivers=caregivers, jobs=jobs_list, create=True)

@app.route("/applications/delete/<int:cid>/<int:jid>")
def delete_application(cid, jid):
    session = Session()
    session.execute(text("DELETE FROM job_application WHERE caregiver_user_id=:cid AND job_id=:jid"), {"cid": cid, "jid": jid})
    session.commit()
    return redirect("/applications")


#  APPOINTMENT CRUD 
@app.route("/appointments")
def appointments():
    session = Session()
    rows = session.execute(text("""
        SELECT a.*, cu.given_name || ' ' || cu.surname as caregiver_name, mu.given_name || ' ' || mu.surname as member_name
        FROM appointment a
        LEFT JOIN app_user cu ON cu.user_id = a.caregiver_user_id
        LEFT JOIN app_user mu ON mu.user_id = a.member_user_id
        ORDER BY a.appointment_id
    """)).mappings().all()
    return render_template("appointments.html", appointments=rows)

@app.route("/appointments/create", methods=["GET","POST"])
def create_appointment():
    session = Session()
    if request.method == "POST":
        session.execute(text("""
            INSERT INTO appointment (caregiver_user_id, member_user_id, appointment_date, appointment_time, work_hours, status)
            VALUES (:cid, :mid, :adate, :atime, :work_hours, :status)
        """), {
            "cid": request.form.get("caregiver_user_id"),
            "mid": request.form.get("member_user_id"),
            "adate": request.form.get("appointment_date"),
            "atime": request.form.get("appointment_time"),
            "work_hours": request.form.get("work_hours"),
            "status": request.form.get("status")
        })
        session.commit()
        return redirect("/appointments")
    caregivers = session.execute(text("SELECT user_id, given_name||' '||surname AS name FROM app_user WHERE user_id IN (SELECT caregiver_user_id FROM caregiver)")).mappings().all()
    members = session.execute(text("SELECT user_id, given_name||' '||surname AS name FROM app_user WHERE user_id IN (SELECT member_user_id FROM member)")).mappings().all()
    return render_template("appointment_form.html", caregivers=caregivers, members=members, create=True)

@app.route("/appointments/delete/<int:aid>")
def delete_appointment(aid):
    session = Session()
    session.execute(text("DELETE FROM appointment WHERE appointment_id=:aid"), {"aid": aid})
    session.commit()
    return redirect("/appointments")

if __name__ == "__main__":
    app.run(debug=True)
