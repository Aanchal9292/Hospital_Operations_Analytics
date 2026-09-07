-- =============================================================
-- Hospital Operations Analytics - Data Import
-- Loads cleaned CSVs from the /data folder into MySQL.
--
-- NOTE: adjust the file paths to your local machine, and make sure
-- your MySQL server has 'secure_file_priv' pointing at (or empty,
-- allowing) the folder containing these CSVs. On many installs you
-- must copy the CSVs into the server's configured secure directory.
-- Run: SHOW VARIABLES LIKE 'secure_file_priv'; to check.
-- =============================================================

USE hospital_analytics;

SET FOREIGN_KEY_CHECKS = 0;

LOAD DATA LOCAL INFILE 'data/departments.csv'
INTO TABLE departments
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'data/patients.csv'
INTO TABLE patients
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'data/doctors.csv'
INTO TABLE doctors
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'data/admissions.csv'
INTO TABLE admissions
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Admission_ID, Patient_ID, Department_ID, Doctor_ID, Admission_Date,
 @Discharge_Date, Diagnosis, Admission_Type)
SET Discharge_Date = NULLIF(@Discharge_Date, '');

LOAD DATA LOCAL INFILE 'data/appointments.csv'
INTO TABLE appointments
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'data/beds.csv'
INTO TABLE beds
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Bed_ID, Department_ID, Bed_Type, Availability_Status, @Admission_ID)
SET Admission_ID = NULLIF(@Admission_ID, '');

LOAD DATA LOCAL INFILE 'data/billing.csv'
INTO TABLE billing
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'data/lab_tests.csv'
INTO TABLE lab_tests
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'data/medications.csv'
INTO TABLE medications
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

SET FOREIGN_KEY_CHECKS = 1;

-- Sanity checks
SELECT 'patients' AS tbl, COUNT(*) AS rows_loaded FROM patients
UNION ALL SELECT 'doctors', COUNT(*) FROM doctors
UNION ALL SELECT 'departments', COUNT(*) FROM departments
UNION ALL SELECT 'admissions', COUNT(*) FROM admissions
UNION ALL SELECT 'appointments', COUNT(*) FROM appointments
UNION ALL SELECT 'beds', COUNT(*) FROM beds
UNION ALL SELECT 'billing', COUNT(*) FROM billing
UNION ALL SELECT 'lab_tests', COUNT(*) FROM lab_tests
UNION ALL SELECT 'medications', COUNT(*) FROM medications;
