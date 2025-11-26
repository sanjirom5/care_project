-- USERS
CREATE TABLE app_user (
  user_id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  given_name VARCHAR(100) NOT NULL,
  surname VARCHAR(100) NOT NULL,
  city VARCHAR(100),
  phone_number VARCHAR(30),
  profile_description TEXT,
  password VARCHAR(255) NOT NULL
);

-- CAREGIVERS
CREATE TABLE caregiver (
  caregiver_user_id INT PRIMARY KEY REFERENCES app_user(user_id) ON DELETE CASCADE,
  gender VARCHAR(10) CHECK (gender IN ('male','female','other')),
  caregiving_type VARCHAR(20) CHECK (caregiving_type IN ('babysitter','elderly','playmate')),
  hourly_rate NUMERIC(6,2),
  photo_url TEXT,
  photo_thumb_url TEXT,
  photo_filename TEXT,
  photo_content_type TEXT,
  photo_size_bytes INT,
  photo_uploaded_at TIMESTAMP
);

-- MEMBERS
CREATE TABLE member (
  member_user_id INT PRIMARY KEY REFERENCES app_user(user_id) ON DELETE CASCADE,
  house_rules TEXT,
  dependent_description TEXT
);

-- ADDRESS
CREATE TABLE address (
  address_id SERIAL PRIMARY KEY,
  member_user_id INT REFERENCES member(member_user_id) ON DELETE CASCADE,
  house_number VARCHAR(30),
  street VARCHAR(200),
  town VARCHAR(100)
);

-- JOBS
CREATE TABLE job (
  job_id SERIAL PRIMARY KEY,
  member_user_id INT REFERENCES member(member_user_id) ON DELETE CASCADE,
  required_caregiving_type VARCHAR(20),
  other_requirements TEXT,
  date_posted DATE DEFAULT CURRENT_DATE
);

-- JOB APPLICATIONS
CREATE TABLE job_application (
  caregiver_user_id INT REFERENCES caregiver(caregiver_user_id) ON DELETE CASCADE,
  job_id INT REFERENCES job(job_id) ON DELETE CASCADE,
  date_applied DATE,
  PRIMARY KEY (caregiver_user_id, job_id)
);

-- APPOINTMENTS
CREATE TABLE appointment (
  appointment_id SERIAL PRIMARY KEY,
  caregiver_user_id INT REFERENCES caregiver(caregiver_user_id),
  member_user_id INT REFERENCES member(member_user_id),
  appointment_date DATE,
  appointment_time TIME,
  work_hours NUMERIC(5,2),
  status VARCHAR(20) CHECK (status IN ('pending','accepted','declined'))
);

