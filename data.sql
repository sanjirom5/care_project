-- Insert mock users (20 users)
INSERT INTO app_user (email, given_name, surname, city, phone_number, profile_description, password) VALUES
('arman@example.com', 'Arman', 'Armanov', 'Astana', '+77012345678', 'Friendly and responsible.', '123'),
('amina@example.com', 'Amina', 'Aminova', 'Almaty', '+77019876543', 'Calm and patient.', '123'),
('gulnar@example.com', 'Gulnar', 'Sadykova', 'Astana', '+77021234567', 'Good with kids.', '123'),
('serik@example.com', 'Serik', 'Ibragimov', 'Karagandy', '+77034567812', 'Energetic helper.', '123'),
('dinara@example.com', 'Dinara', 'Bek', 'Almaty', '+77051230987', 'Loves children.', '123'),
('azamat@example.com', 'Azamat', 'Kairat', 'Shymkent', '+77067778899', 'Very caring.', '123'),
('saltanat@example.com', 'Saltanat', 'Nur', 'Astana', '+77077665544', 'Experienced nanny.', '123'),
('bekzat@example.com', 'Bekzat', 'Zholdas', 'Almaty', '+77081234512', 'Patient caregiver.', '123'),
('aliya@example.com', 'Aliya', 'Tursyn', 'Astana', '+77092345678', 'Loves helping others.', '123'),
('marat@example.com', 'Marat', 'Oralbay', 'Atyrau', '+77013456278', 'Responsible adult.', '123'),
('nurgul@example.com', 'Nurgul', 'Aman', 'Astana', '+77099887766', 'Attentive helper.', '123'),
('zhanar@example.com', 'Zhanar', 'Yessen', 'Almaty', '+77045678921', 'Experienced family assistant.', '123'),
('samat@example.com', 'Samat', 'Nurzhan', 'Karagandy', '+77014523678', 'Calm and reliable.', '123'),
('lays@example.com', 'Laysan', 'Abay', 'Shymkent', '+77015673456', 'Loves elder care.', '123'),
('bek@mail.com', 'Bek', 'Sultanov', 'Astana', '+77017894561', 'Happy to help.', '123'),
('gul@mail.com', 'Gul', 'Amanova', 'Almaty', '+77023456788', 'Kind-hearted assistant.', '123'),
('dina@mail.com', 'Dina', 'Sarsen', 'Almaty', '+77035672345', 'Positive energy.', '123'),
('timur@mail.com', 'Timur', 'Atabay', 'Astana', '+77047893456', 'Enjoys helping families.', '123'),
('aila@mail.com', 'Aila', 'Kassym', 'Atyrau', '+77056789432', 'Fun and caring.', '123'),
('nazar@mail.com', 'Nazar', 'Orinbay', 'Shymkent', '+77067894523', 'Friendly helper.', '123');


-- Insert caregivers
-- user 1  → babysitter
-- user 3  → babysitter
-- user 4  → elderly
-- user 6  → playmate
-- user 7  → babysitter
-- user 9  → elderly
-- user 11 → babysitter
-- user 12 → playmate
-- user 13 → elderly
-- user 15 → playmate
INSERT INTO caregiver (caregiver_user_id, gender, caregiving_type, hourly_rate) VALUES
(1,  'male',   'babysitter', 3500),
(3,  'female', 'babysitter', 3000),
(4,  'male',   'elderly',    4000),
(6,  'male',   'playmate',   3000),
(7,  'female', 'babysitter', 3800),
(9,  'female', 'elderly',    4200),
(11, 'female', 'babysitter', 2500),
(12, 'female', 'playmate',   2800),
(13, 'male',   'elderly',    4500),
(15, 'male',   'playmate',   2700);


-- Insert members
INSERT INTO member (member_user_id, house_rules, dependent_description) VALUES
(2,  'Quiet after 9 PM, hygiene important.',  'Elderly grandmother, needs daily check-ins.'),
(5,  'No smoking, clean kitchen.',            '5-year-old daughter who likes painting.'),
(8,  'No loud music.',                        'Child with ADHD, needs patient supervision.'),
(10, 'No pets allowed.',                      'Infant (4 months), needs feeding schedule.'),
(14, 'Respect privacy.',                      'Grandfather recovering from surgery.'),
(16, 'Kitchen closed after 10 PM.',           '7-year-old boy, energetic.'),
(17, 'No shoes inside.',                      'Toddler learning to walk.'),
(18, 'Keep rooms clean.',                     'Elderly father needs mobility support.'),
(19, 'Very sensitive to noise.',              'Son with special education needs.'),
(20, 'Avoid strong perfumes.',                'Baby girl who naps often.');


-- Insert addresses
INSERT INTO address (member_user_id, house_number, street, town) VALUES
(2,  '10', 'Kabanbay Batyr', 'Almaty'),   -- deleted by 4.2
(5,  '21', 'Turan',          'Astana'),
(8,  '33', 'Abay',           'Almaty'),
(10, '9',  'Seifullin',      'Atyrau'),
(14, '5',  'Satpayev',       'Shymkent'),
(16, '12', 'Turan',          'Astana'),
(17, '3',  'Kenesary',       'Almaty'),
(18, '48', 'Abay',           'Almaty'),
(19, '77', 'Kabanbay Batyr', 'Astana'),   -- deleted by 4.2
(20, '18', 'Mangilik El',    'Astana');


-- Insert jobs
-- job type matches what the member actually needs,
-- and avoids jobs for members 2 and 19 who will be deleted in step 4.2
INSERT INTO job (job_id, member_user_id, required_caregiving_type, other_requirements, date_posted) VALUES
(1,  5,  'babysitter', 'Night shifts, feeding experience.',                  '2025-11-01'),
(2,  8,  'playmate',   'Creative person preferred, soft-spoken preferred.',  '2025-11-02'),
(3,  10, 'babysitter', 'Need infant care experience.',                       '2025-11-03'),
(4,  14, 'elderly',    'Medical knowledge preferred.',                       '2025-11-04'),
(5,  16, 'playmate',   'Energetic and fun.',                                 '2025-11-05'),
(6,  17, 'babysitter', 'Strict with house rules.',                           '2025-11-06'),
(7,  18, 'elderly',    'Mobility support required.',                         '2025-11-07'),
(8,  20, 'babysitter', 'Flexible hours.',                                    '2025-11-08');


-- Job applications: caregiver type must match job's required type
-- babysitter jobs (1, 3, 6, 8) → caregivers 1, 3, 7, 11  (all babysitters)
-- playmate jobs  (2, 5)        → caregivers 6, 12, 15     (all playmates)
-- elderly jobs   (4, 7)        → caregivers 4, 9, 13      (all elderly)
INSERT INTO job_application (caregiver_user_id, job_id, date_applied) VALUES
(1,  1, '2025-11-02'),   -- babysitter → babysitter job
(3,  3, '2025-11-04'),   -- babysitter → babysitter job
(7,  1, '2025-11-02'),   -- babysitter → babysitter job (2nd applicant)
(11, 6, '2025-11-07'),   -- babysitter → babysitter job
(6,  2, '2025-11-03'),   -- playmate   → playmate job
(12, 5, '2025-11-06'),   -- playmate   → playmate job
(15, 2, '2025-11-03'),   -- playmate   → playmate job (2nd applicant)
(4,  4, '2025-11-05'),   -- elderly    → elderly job
(9,  7, '2025-11-08'),   -- elderly    → elderly job
(13, 4, '2025-11-05');   -- elderly    → elderly job (2nd applicant)


-- Appointments: caregiver type still matches member's need
INSERT INTO appointment (appointment_id, caregiver_user_id, member_user_id, appointment_date, appointment_time, work_hours, status) VALUES
(1,  1,  5,  '2025-11-14', '09:00', 4, 'accepted'),   -- babysitter → member 5
(2,  3,  10, '2025-11-15', '10:30', 6, 'accepted'),   -- babysitter → member 10
(3,  4,  14, '2025-11-16', '08:00', 5, 'accepted'),   -- elderly    → member 14
(4,  6,  8,  '2025-11-17', '11:00', 3, 'accepted'),   -- playmate   → member 8
(5,  7,  17, '2025-11-18', '09:30', 4, 'accepted'),   -- babysitter → member 17
(6,  9,  18, '2025-11-19', '07:45', 5, 'accepted'),   -- elderly    → member 18
(7,  11, 20, '2025-11-20', '13:15', 6, 'accepted'),   -- babysitter → member 20
(8,  12, 16, '2025-11-21', '15:00', 4, 'accepted'),   -- playmate   → member 16
(9,  13, 14, '2025-11-22', '17:00', 5, 'accepted'),   -- elderly    → member 14
(10, 15, 8,  '2025-11-23', '16:00', 3, 'accepted');   -- playmate   → member 8