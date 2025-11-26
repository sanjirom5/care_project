#!/usr/bin/env python3
"""
main.py - Part 2 runner for Caregivers platform (SQLAlchemy + textual SQL)
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL") or "postgresql+psycopg2://care_user:your_strong_password@localhost/care_platform"

engine = create_engine(DB_URL, echo=False, future=True)

def run(sql, params=None, fetch=False):
    """Helper to run SQL and optionally fetch results."""
    try:
        with engine.begin() as conn:
            if fetch:
                return conn.execute(text(sql), params or {}).fetchall()
            else:
                conn.execute(text(sql), params or {})
    except SQLAlchemyError as e:
        print("SQL ERROR:", e)
        raise

def print_rows(rows, limit=20):
    if not rows:
        print("(0 rows)")
        return
    for r in rows[:limit]:
        print(r)
    if len(rows) > limit:
        print(f"... {len(rows)} rows total (showing {limit})")

def main():
    print("== Part 2 script started ==")

    # ----------------------------------------------------
    # 3. UPDATE OPERATIONS
    # ----------------------------------------------------

    print("\n-- 3.1 Update Arman's phone number --")
    run("""
        UPDATE app_user
        SET phone_number = '+77773414141'
        WHERE given_name='Arman' AND surname='Armanov';
    """)
    rows = run("SELECT user_id, given_name, surname, phone_number FROM app_user WHERE given_name='Arman';", fetch=True)
    print_rows(rows)

    print("\n-- 3.2 Add commission fee to caregivers --")
    run("""
        UPDATE caregiver
        SET hourly_rate = CASE
            WHEN hourly_rate < 10 THEN hourly_rate + 0.30
            ELSE hourly_rate * 1.10
        END;
    """)
    rows = run("SELECT caregiver_user_id, hourly_rate FROM caregiver ORDER BY caregiver_user_id;", fetch=True)
    print_rows(rows)

    # ----------------------------------------------------
    # 4. DELETE OPERATIONS
    # ----------------------------------------------------

    print("\n-- 4.1 Delete jobs posted by Amina Aminova --")
    run("""
        DELETE FROM job
        WHERE member_user_id IN (
            SELECT m.member_user_id
            FROM member m
            JOIN app_user u ON m.member_user_id = u.user_id
            WHERE u.given_name='Amina' AND u.surname='Aminova'
        );
    """)
    rows = run("SELECT job_id, member_user_id, other_requirements FROM job ORDER BY job_id;", fetch=True)
    print_rows(rows)

    print("\n-- 4.2 Delete members who live on Kabanbay Batyr (with cascade fix) --")

    # STEP 1 — delete appointments first (foreign key safety)
    run("""
        DELETE FROM appointment
        WHERE member_user_id IN (
            SELECT member_user_id
            FROM address
            WHERE street ILIKE 'Kabanbay Batyr'
        );
    """)

    # STEP 2 — now delete members
    run("""
        DELETE FROM member
        WHERE member_user_id IN (
            SELECT member_user_id
            FROM address
            WHERE street ILIKE 'Kabanbay Batyr'
        );
    """)

    rows = run("SELECT member_user_id, house_rules FROM member ORDER BY member_user_id;", fetch=True)
    print_rows(rows)

    # ----------------------------------------------------
    # 5. SIMPLE QUERIES
    # ----------------------------------------------------

    print("\n-- 5.1 Caregiver + Member names for accepted appointments --")
    rows = run("""
        SELECT a.appointment_id,
               uc.given_name AS caregiver_name,
               um.given_name AS member_name,
               a.appointment_date, a.appointment_time, a.work_hours
        FROM appointment a
        JOIN caregiver c ON a.caregiver_user_id = c.caregiver_user_id
        JOIN app_user uc ON c.caregiver_user_id = uc.user_id
        JOIN member m ON a.member_user_id = m.member_user_id
        JOIN app_user um ON m.member_user_id = um.user_id
        WHERE a.status = 'accepted'
        ORDER BY a.appointment_date;
    """, fetch=True)
    print_rows(rows)

    print("\n-- 5.2 Jobs containing 'soft-spoken' --")
    rows = run("SELECT job_id, other_requirements FROM job WHERE other_requirements ILIKE '%soft-spoken%';", fetch=True)
    print_rows(rows)

    print("\n-- 5.3 Work hours of all babysitter appointments --")
    rows = run("""
        SELECT a.appointment_id, a.work_hours, uc.given_name
        FROM appointment a
        JOIN caregiver c ON a.caregiver_user_id = c.caregiver_user_id
        JOIN app_user uc ON c.caregiver_user_id = uc.user_id
        WHERE c.caregiving_type='babysitter';
    """, fetch=True)
    print_rows(rows)

    print("\n-- 5.4 Members looking for elderly care in Astana with 'No pets.' --")
    rows = run("""
        SELECT DISTINCT um.user_id, um.given_name, um.surname, ad.town, m.house_rules
        FROM job
        JOIN member m ON job.member_user_id = m.member_user_id
        JOIN app_user um ON m.member_user_id = um.user_id
        LEFT JOIN address ad ON m.member_user_id = ad.member_user_id
        WHERE job.required_caregiving_type='elderly'
          AND (ad.town ILIKE 'Astana' OR um.city ILIKE 'Astana')
          AND m.house_rules ILIKE '%No pets.%';
    """, fetch=True)
    print_rows(rows)

    # ----------------------------------------------------
    # 6. COMPLEX QUERIES
    # ----------------------------------------------------

    print("\n-- 6.1 Count applicants per job --")
    rows = run("""
        SELECT j.job_id, j.member_user_id,
               COUNT(ja.caregiver_user_id) AS applicant_count
        FROM job j
        LEFT JOIN job_application ja ON j.job_id = ja.job_id
        GROUP BY j.job_id, j.member_user_id
        ORDER BY j.job_id;
    """, fetch=True)
    print_rows(rows)

    print("\n-- 6.2 Total hours worked by caregivers (accepted only) --")
    rows = run("""
        SELECT c.caregiver_user_id, au.given_name,
               SUM(a.work_hours) AS total_hours
        FROM appointment a
        JOIN caregiver c ON a.caregiver_user_id = c.caregiver_user_id
        JOIN app_user au ON c.caregiver_user_id = au.user_id
        WHERE a.status='accepted'
        GROUP BY c.caregiver_user_id, au.given_name
        ORDER BY total_hours DESC;
    """, fetch=True)
    print_rows(rows)

    print("\n-- 6.3 Average caregiver pay (accepted appointments) --")
    rows = run("""
        SELECT AVG(c.hourly_rate) AS avg_hourly_rate
        FROM caregiver c
        JOIN appointment a ON a.caregiver_user_id = c.caregiver_user_id
        WHERE a.status='accepted';
    """, fetch=True)
    print_rows(rows)

    print("\n-- 6.4 Caregivers earning above average --")
    rows = run("""
        WITH avg_rate AS (
          SELECT AVG(c.hourly_rate) AS avg_hourly
          FROM caregiver c
          JOIN appointment a ON a.caregiver_user_id = c.caregiver_user_id
          WHERE a.status='accepted'
        )
        SELECT DISTINCT c.caregiver_user_id, au.given_name, c.hourly_rate
        FROM caregiver c
        JOIN app_user au ON c.caregiver_user_id = au.user_id
        CROSS JOIN avg_rate
        WHERE c.hourly_rate > avg_rate.avg_hourly;
    """, fetch=True)
    print_rows(rows)

    # ----------------------------------------------------
    # 7. DERIVED ATTRIBUTE
    # ----------------------------------------------------

    print("\n-- 7. Total cost for each caregiver (accepted appointments) --")
    rows = run("""
        SELECT c.caregiver_user_id, au.given_name,
               SUM(c.hourly_rate * a.work_hours) AS total_payment
        FROM caregiver c
        JOIN appointment a ON a.caregiver_user_id = c.caregiver_user_id
        JOIN app_user au ON c.caregiver_user_id = au.user_id
        WHERE a.status='accepted'
        GROUP BY c.caregiver_user_id, au.given_name
        ORDER BY total_payment DESC;
    """, fetch=True)
    print_rows(rows)

    # ----------------------------------------------------
    # 8. VIEW OPERATION
    # ----------------------------------------------------

    print("\n-- 8. Create VIEW view_job_applications_applicants --")
    run("DROP VIEW IF EXISTS view_job_applications_applicants;")
    run("""
        CREATE VIEW view_job_applications_applicants AS
        SELECT j.job_id, j.member_user_id,
               au.given_name AS member_name,
               j.required_caregiving_type, j.other_requirements,
               ja.caregiver_user_id, ac.given_name AS caregiver_name,
               ja.date_applied
        FROM job j
        LEFT JOIN job_application ja ON j.job_id = ja.job_id
        LEFT JOIN member m ON j.member_user_id = m.member_user_id
        LEFT JOIN app_user au ON m.member_user_id = au.user_id
        LEFT JOIN app_user ac ON ja.caregiver_user_id = ac.user_id;
    """)

    rows = run("SELECT * FROM view_job_applications_applicants ORDER BY job_id LIMIT 50;", fetch=True)
    print_rows(rows)

    print("\n== Part 2 COMPLETE ==")


if __name__ == "__main__":
    main()
