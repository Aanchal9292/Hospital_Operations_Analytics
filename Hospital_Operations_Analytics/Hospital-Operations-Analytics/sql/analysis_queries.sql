-- =============================================================
-- Hospital Operations Analytics - Analysis Queries
-- =============================================================
USE hospital_analytics;

-- -------------------------------------------------------------
-- 1. Total patients, admissions, discharges (top-line KPIs)
-- -------------------------------------------------------------
SELECT
    (SELECT COUNT(*) FROM patients)                                   AS total_patients,
    (SELECT COUNT(*) FROM admissions)                                 AS total_admissions,
    (SELECT COUNT(*) FROM admissions WHERE Discharge_Date IS NOT NULL) AS total_discharges;

-- -------------------------------------------------------------
-- 2. Admissions by department
-- -------------------------------------------------------------
SELECT d.Department_Name,
       COUNT(a.Admission_ID) AS total_admissions
FROM admissions a
JOIN departments d ON a.Department_ID = d.Department_ID
GROUP BY d.Department_Name
ORDER BY total_admissions DESC;

-- -------------------------------------------------------------
-- 3. Average length of stay by department
-- -------------------------------------------------------------
SELECT d.Department_Name,
       ROUND(AVG(DATEDIFF(a.Discharge_Date, a.Admission_Date)), 2) AS avg_length_of_stay
FROM admissions a
JOIN departments d ON a.Department_ID = d.Department_ID
WHERE a.Discharge_Date IS NOT NULL
GROUP BY d.Department_Name
ORDER BY avg_length_of_stay DESC;

-- -------------------------------------------------------------
-- 4. Average waiting time by department
-- -------------------------------------------------------------
SELECT d.Department_Name,
       ROUND(AVG(ap.Waiting_Time), 2) AS avg_waiting_time_minutes
FROM appointments ap
JOIN departments d ON ap.Department_ID = d.Department_ID
GROUP BY d.Department_Name
ORDER BY avg_waiting_time_minutes DESC;

-- -------------------------------------------------------------
-- 5. Bed occupancy rate by department
-- -------------------------------------------------------------
SELECT d.Department_Name,
       COUNT(*) AS total_beds,
       SUM(CASE WHEN b.Availability_Status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_beds,
       ROUND(
           SUM(CASE WHEN b.Availability_Status = 'Occupied' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
       ) AS occupancy_rate_pct
FROM beds b
JOIN departments d ON b.Department_ID = d.Department_ID
GROUP BY d.Department_Name
ORDER BY occupancy_rate_pct DESC;

-- -------------------------------------------------------------
-- 6. Appointment completion & cancellation rate
-- -------------------------------------------------------------
SELECT
    ROUND(SUM(Status = 'Completed')   * 100.0 / COUNT(*), 2) AS completion_rate_pct,
    ROUND(SUM(Status = 'Cancelled')   * 100.0 / COUNT(*), 2) AS cancellation_rate_pct,
    ROUND(SUM(Status = 'No-show')     * 100.0 / COUNT(*), 2) AS no_show_rate_pct,
    ROUND(SUM(Status = 'Rescheduled') * 100.0 / COUNT(*), 2) AS reschedule_rate_pct
FROM appointments;

-- -------------------------------------------------------------
-- 7. Doctor workload ranking (CTE + window function)
-- -------------------------------------------------------------
WITH doctor_load AS (
    SELECT dr.Doctor_ID,
           dr.Doctor_Name,
           d.Department_Name,
           COUNT(DISTINCT ap.Appointment_ID) AS total_appointments,
           COUNT(DISTINCT a.Admission_ID)    AS total_admissions
    FROM doctors dr
    JOIN departments d ON dr.Department_ID = d.Department_ID
    LEFT JOIN appointments ap ON ap.Doctor_ID = dr.Doctor_ID
    LEFT JOIN admissions a ON a.Doctor_ID = dr.Doctor_ID
    GROUP BY dr.Doctor_ID, dr.Doctor_Name, d.Department_Name
)
SELECT *,
       RANK() OVER (ORDER BY total_appointments + total_admissions DESC) AS workload_rank
FROM doctor_load
ORDER BY workload_rank
LIMIT 20;

-- -------------------------------------------------------------
-- 8. Monthly admission trend (window function - running total)
-- -------------------------------------------------------------
WITH monthly AS (
    SELECT DATE_FORMAT(Admission_Date, '%Y-%m') AS admission_month,
           COUNT(*) AS admissions_count
    FROM admissions
    GROUP BY admission_month
)
SELECT admission_month,
       admissions_count,
       SUM(admissions_count) OVER (ORDER BY admission_month) AS running_total_admissions,
       ROUND(AVG(admissions_count) OVER (
           ORDER BY admission_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       ), 1) AS three_month_moving_avg
FROM monthly
ORDER BY admission_month;

-- -------------------------------------------------------------
-- 9. Revenue by department (with % of total using window function)
-- -------------------------------------------------------------
SELECT d.Department_Name,
       ROUND(SUM(bl.Total_Amount), 2) AS department_revenue,
       ROUND(SUM(bl.Total_Amount) * 100.0 / SUM(SUM(bl.Total_Amount)) OVER (), 2) AS pct_of_total_revenue
FROM billing bl
JOIN admissions a ON bl.Admission_ID = a.Admission_ID
JOIN departments d ON a.Department_ID = d.Department_ID
GROUP BY d.Department_Name
ORDER BY department_revenue DESC;

-- -------------------------------------------------------------
-- 10. Top diagnoses driving longest average stay (subquery)
-- -------------------------------------------------------------
SELECT Diagnosis,
       COUNT(*) AS cases,
       ROUND(AVG(DATEDIFF(Discharge_Date, Admission_Date)), 2) AS avg_stay_days
FROM admissions
WHERE Discharge_Date IS NOT NULL
GROUP BY Diagnosis
HAVING cases >= (SELECT COUNT(*) / 40 FROM admissions)  -- filter out rare diagnoses
ORDER BY avg_stay_days DESC
LIMIT 10;

-- -------------------------------------------------------------
-- 11. Patient readmissions within 30 days of discharge
-- -------------------------------------------------------------
WITH ranked AS (
    SELECT Patient_ID,
           Admission_ID,
           Admission_Date,
           Discharge_Date,
           LEAD(Admission_Date) OVER (PARTITION BY Patient_ID ORDER BY Admission_Date) AS next_admission_date
    FROM admissions
    WHERE Discharge_Date IS NOT NULL
)
SELECT Patient_ID,
       Admission_ID,
       Discharge_Date,
       next_admission_date,
       DATEDIFF(next_admission_date, Discharge_Date) AS days_to_readmission
FROM ranked
WHERE next_admission_date IS NOT NULL
  AND DATEDIFF(next_admission_date, Discharge_Date) <= 30
ORDER BY days_to_readmission;

-- -------------------------------------------------------------
-- 12. Average revenue per patient
-- -------------------------------------------------------------
SELECT ROUND(SUM(Total_Amount) / (SELECT COUNT(DISTINCT Patient_ID) FROM billing), 2)
       AS avg_revenue_per_patient
FROM billing;

-- -------------------------------------------------------------
-- 13. Insurance vs out-of-pocket payment split
-- -------------------------------------------------------------
SELECT
    ROUND(SUM(Insurance_Amount), 2)   AS total_insurance_paid,
    ROUND(SUM(Patient_Payment), 2)    AS total_patient_paid,
    ROUND(SUM(Insurance_Amount) * 100.0 / SUM(Total_Amount), 2) AS insurance_share_pct
FROM billing;

-- -------------------------------------------------------------
-- 14. Departments with high volume AND high waiting time AND high
--     bed occupancy — operational bottleneck flag
-- -------------------------------------------------------------
WITH vol AS (
    SELECT Department_ID, COUNT(*) AS admissions_count
    FROM admissions GROUP BY Department_ID
),
wait AS (
    SELECT Department_ID, AVG(Waiting_Time) AS avg_wait
    FROM appointments GROUP BY Department_ID
),
occ AS (
    SELECT Department_ID,
           SUM(Availability_Status = 'Occupied') * 100.0 / COUNT(*) AS occupancy_pct
    FROM beds GROUP BY Department_ID
)
SELECT d.Department_Name,
       v.admissions_count,
       ROUND(w.avg_wait, 1) AS avg_wait_minutes,
       ROUND(o.occupancy_pct, 1) AS occupancy_pct
FROM departments d
JOIN vol v ON v.Department_ID = d.Department_ID
JOIN wait w ON w.Department_ID = d.Department_ID
JOIN occ o ON o.Department_ID = d.Department_ID
WHERE v.admissions_count > (SELECT AVG(admissions_count) FROM vol)
  AND w.avg_wait > (SELECT AVG(avg_wait) FROM wait)
ORDER BY v.admissions_count DESC;

-- -------------------------------------------------------------
-- 15. Lab test revenue and abnormal-result rate by test
-- -------------------------------------------------------------
SELECT Test_Name,
       COUNT(*) AS total_tests,
       ROUND(SUM(Test_Cost), 2) AS total_revenue,
       ROUND(SUM(Test_Result = 'Abnormal') * 100.0 / COUNT(*), 2) AS abnormal_rate_pct
FROM lab_tests
GROUP BY Test_Name
ORDER BY total_revenue DESC;
