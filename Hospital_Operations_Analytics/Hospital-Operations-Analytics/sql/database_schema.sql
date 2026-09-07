-- =============================================================
-- Hospital Operations Analytics - Database Schema
-- =============================================================

CREATE DATABASE IF NOT EXISTS hospital_analytics;
USE hospital_analytics;

DROP TABLE IF EXISTS medications;
DROP TABLE IF EXISTS lab_tests;
DROP TABLE IF EXISTS billing;
DROP TABLE IF EXISTS beds;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS admissions;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS departments;

-- -------------------------------------------------------------
CREATE TABLE departments (
    Department_ID   INT PRIMARY KEY,
    Department_Name VARCHAR(50) NOT NULL,
    Location        VARCHAR(50),
    Capacity        INT
);

-- -------------------------------------------------------------
CREATE TABLE patients (
    Patient_ID         INT PRIMARY KEY,
    Name                VARCHAR(100) NOT NULL,
    Age                 INT,
    Gender              VARCHAR(10),
    City                VARCHAR(50),
    Registration_Date   DATE
);

-- -------------------------------------------------------------
CREATE TABLE doctors (
    Doctor_ID       INT PRIMARY KEY,
    Doctor_Name     VARCHAR(100) NOT NULL,
    Department_ID   INT,
    Specialization  VARCHAR(100),
    Experience      INT,
    FOREIGN KEY (Department_ID) REFERENCES departments(Department_ID)
);

-- -------------------------------------------------------------
CREATE TABLE admissions (
    Admission_ID    INT PRIMARY KEY,
    Patient_ID      INT,
    Department_ID   INT,
    Doctor_ID       INT,
    Admission_Date  DATE,
    Discharge_Date  DATE NULL,
    Diagnosis       VARCHAR(150),
    Admission_Type  VARCHAR(20),
    FOREIGN KEY (Patient_ID) REFERENCES patients(Patient_ID),
    FOREIGN KEY (Department_ID) REFERENCES departments(Department_ID),
    FOREIGN KEY (Doctor_ID) REFERENCES doctors(Doctor_ID)
);

-- -------------------------------------------------------------
CREATE TABLE appointments (
    Appointment_ID     INT PRIMARY KEY,
    Patient_ID          INT,
    Doctor_ID            INT,
    Department_ID       INT,
    Appointment_Date    DATE,
    Appointment_Time    VARCHAR(10),
    Waiting_Time         INT,
    Status               VARCHAR(20),
    FOREIGN KEY (Patient_ID) REFERENCES patients(Patient_ID),
    FOREIGN KEY (Doctor_ID) REFERENCES doctors(Doctor_ID),
    FOREIGN KEY (Department_ID) REFERENCES departments(Department_ID)
);

-- -------------------------------------------------------------
CREATE TABLE beds (
    Bed_ID              INT PRIMARY KEY,
    Department_ID       INT,
    Bed_Type            VARCHAR(20),
    Availability_Status VARCHAR(20),
    Admission_ID         INT NULL,
    FOREIGN KEY (Department_ID) REFERENCES departments(Department_ID),
    FOREIGN KEY (Admission_ID) REFERENCES admissions(Admission_ID)
);

-- -------------------------------------------------------------
CREATE TABLE billing (
    Bill_ID             INT PRIMARY KEY,
    Patient_ID           INT,
    Admission_ID          INT,
    Treatment_Cost         DECIMAL(12,2),
    Medicine_Cost          DECIMAL(12,2),
    Lab_Cost               DECIMAL(12,2),
    Insurance_Amount       DECIMAL(12,2),
    Patient_Payment        DECIMAL(12,2),
    Total_Amount            DECIMAL(12,2),
    Payment_Status          VARCHAR(20),
    FOREIGN KEY (Patient_ID) REFERENCES patients(Patient_ID),
    FOREIGN KEY (Admission_ID) REFERENCES admissions(Admission_ID)
);

-- -------------------------------------------------------------
CREATE TABLE lab_tests (
    Test_ID       INT PRIMARY KEY,
    Patient_ID    INT,
    Doctor_ID     INT,
    Test_Name     VARCHAR(100),
    Test_Date     DATE,
    Test_Cost     DECIMAL(10,2),
    Test_Result   VARCHAR(20),
    Test_Status   VARCHAR(20),
    FOREIGN KEY (Patient_ID) REFERENCES patients(Patient_ID),
    FOREIGN KEY (Doctor_ID) REFERENCES doctors(Doctor_ID)
);

-- -------------------------------------------------------------
CREATE TABLE medications (
    Medication_ID   INT PRIMARY KEY,
    Admission_ID    INT,
    Patient_ID      INT,
    Medicine_Name   VARCHAR(100),
    Dosage          VARCHAR(20),
    Frequency       VARCHAR(30),
    Cost            DECIMAL(10,2),
    FOREIGN KEY (Admission_ID) REFERENCES admissions(Admission_ID),
    FOREIGN KEY (Patient_ID) REFERENCES patients(Patient_ID)
);

-- Helpful indexes for analytical queries
CREATE INDEX idx_admissions_dept ON admissions(Department_ID);
CREATE INDEX idx_admissions_date ON admissions(Admission_Date);
CREATE INDEX idx_appointments_dept ON appointments(Department_ID);
CREATE INDEX idx_appointments_date ON appointments(Appointment_Date);
CREATE INDEX idx_billing_admission ON billing(Admission_ID);
