"""
Hospital Operations Analytics - Synthetic Data Generator
Generates realistic, internally-consistent hospital data across all tables:
patients, doctors, departments, admissions, appointments, beds, billing,
lab_tests, medications.

Run:  python generate_data.py
Output: CSVs in ../data/
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RNG = np.random.default_rng(42)
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)
DAYS_RANGE = (END_DATE - START_DATE).days

N_PATIENTS = 3000
N_DOCTORS = 60
N_ADMISSIONS = 4500
N_APPOINTMENTS = 9000
N_LAB_TESTS = 3500
N_MEDICATIONS_PER_ADM = (1, 4)

# ---------------------------------------------------------------------------
# 1. Departments
# ---------------------------------------------------------------------------
departments = pd.DataFrame({
    "Department_ID": range(1, 9),
    "Department_Name": [
        "Cardiology", "Neurology", "Orthopedics", "General Medicine",
        "Pediatrics", "Dermatology", "Emergency", "Gynecology"
    ],
    "Location": [f"Block {chr(65+i)}, Floor {(i % 4) + 1}" for i in range(8)],
    "Capacity": [40, 25, 35, 50, 30, 15, 45, 28]
})

# Weight departments so Emergency & General Medicine see more volume (mirrors real hospitals)
dept_weights = np.array([0.12, 0.08, 0.11, 0.16, 0.10, 0.05, 0.24, 0.14])
dept_weights = dept_weights / dept_weights.sum()

# ---------------------------------------------------------------------------
# 2. Doctors
# ---------------------------------------------------------------------------
first_names = ["Aarav","Vivaan","Aditya","Ishaan","Kabir","Anaya","Diya","Myra",
               "Sara","Priya","Rohan","Karan","Neha","Pooja","Arjun","Sanya",
               "Vikram","Meera","Rahul","Ananya","Nikhil","Tara","Dev","Riya"]
last_names = ["Sharma","Verma","Gupta","Malhotra","Kapoor","Nair","Iyer","Reddy",
              "Chawla","Bose","Mehta","Joshi","Rao","Singh","Khan","Das"]

specializations_map = {
    "Cardiology": ["Interventional Cardiology", "Cardiac Surgery", "Electrophysiology"],
    "Neurology": ["Stroke Care", "Epileptology", "Neurosurgery"],
    "Orthopedics": ["Joint Replacement", "Sports Medicine", "Spine Surgery"],
    "General Medicine": ["Internal Medicine", "Diabetology", "General Practice"],
    "Pediatrics": ["Neonatology", "Pediatric Care", "Child Immunology"],
    "Dermatology": ["Cosmetic Dermatology", "Clinical Dermatology"],
    "Emergency": ["Emergency Medicine", "Trauma Care"],
    "Gynecology": ["Obstetrics", "Gynecologic Oncology", "Reproductive Medicine"],
}

doc_dept = RNG.choice(departments["Department_ID"], size=N_DOCTORS, p=dept_weights)
doctors = pd.DataFrame({
    "Doctor_ID": range(1, N_DOCTORS + 1),
    "Doctor_Name": ["Dr. " + RNG.choice(first_names) + " " + RNG.choice(last_names)
                     for _ in range(N_DOCTORS)],
    "Department_ID": doc_dept,
})
doctors["Specialization"] = doctors["Department_ID"].apply(
    lambda d: RNG.choice(specializations_map[departments.set_index("Department_ID").loc[d, "Department_Name"]])
)
doctors["Experience"] = RNG.integers(1, 30, size=N_DOCTORS)

# ---------------------------------------------------------------------------
# 3. Patients
# ---------------------------------------------------------------------------
cities = ["Delhi","Mumbai","Bengaluru","Hyderabad","Pune","Chennai","Kolkata",
          "Jaipur","Lucknow","Ahmedabad","Hapur","Meerut","Ghaziabad"]

patients = pd.DataFrame({
    "Patient_ID": range(1, N_PATIENTS + 1),
    "Name": [RNG.choice(first_names) + " " + RNG.choice(last_names) for _ in range(N_PATIENTS)],
    "Age": RNG.integers(0, 95, size=N_PATIENTS),
    "Gender": RNG.choice(["Male", "Female", "Other"], size=N_PATIENTS, p=[0.49, 0.49, 0.02]),
    "City": RNG.choice(cities, size=N_PATIENTS),
    "Registration_Date": [
        (START_DATE - timedelta(days=int(RNG.integers(0, 800)))).date()
        for _ in range(N_PATIENTS)
    ],
})

# ---------------------------------------------------------------------------
# 4. Admissions
# ---------------------------------------------------------------------------
diagnoses_by_dept = {
    "Cardiology": ["Hypertension", "Myocardial Infarction", "Arrhythmia", "Heart Failure"],
    "Neurology": ["Stroke", "Migraine", "Epilepsy", "Parkinson's Disease"],
    "Orthopedics": ["Fracture", "Osteoarthritis", "ACL Tear", "Spinal Disc Herniation"],
    "General Medicine": ["Diabetes Mellitus", "Pneumonia", "Typhoid", "Viral Fever"],
    "Pediatrics": ["Neonatal Jaundice", "Bronchiolitis", "Asthma", "Gastroenteritis"],
    "Dermatology": ["Psoriasis", "Eczema", "Acne", "Skin Infection"],
    "Emergency": ["Road Traffic Accident", "Acute Abdomen", "Poisoning", "Chest Pain"],
    "Gynecology": ["Normal Delivery", "C-Section", "PCOS", "Ovarian Cyst"],
}

adm_dept_ids = RNG.choice(departments["Department_ID"], size=N_ADMISSIONS, p=dept_weights)
dept_lookup = departments.set_index("Department_ID")["Department_Name"]

admission_type = RNG.choice(["Emergency", "Regular"], size=N_ADMISSIONS, p=[0.35, 0.65])

# length of stay depends loosely on department (Emergency/Gynecology shorter, Neurology longer)
los_base = {
    "Cardiology": 5, "Neurology": 7, "Orthopedics": 6, "General Medicine": 4,
    "Pediatrics": 3, "Dermatology": 2, "Emergency": 2, "Gynecology": 3
}

admission_dates = [START_DATE + timedelta(days=int(RNG.integers(0, DAYS_RANGE))) for _ in range(N_ADMISSIONS)]
los_days = []
for d in adm_dept_ids:
    base = los_base[dept_lookup[d]]
    los_days.append(max(1, int(RNG.poisson(base))))

discharge_dates = [ad + timedelta(days=los) for ad, los in zip(admission_dates, los_days)]

# small % still admitted (no discharge date) - only for recent admissions
still_admitted_mask = (np.array(admission_dates) > (END_DATE - timedelta(days=10))) & (RNG.random(N_ADMISSIONS) < 0.3)

admissions = pd.DataFrame({
    "Admission_ID": range(1, N_ADMISSIONS + 1),
    "Patient_ID": RNG.choice(patients["Patient_ID"], size=N_ADMISSIONS),
    "Department_ID": adm_dept_ids,
    "Doctor_ID": [RNG.choice(doctors.loc[doctors["Department_ID"] == d, "Doctor_ID"].values)
                  if len(doctors.loc[doctors["Department_ID"] == d]) > 0
                  else RNG.choice(doctors["Doctor_ID"])
                  for d in adm_dept_ids],
    "Admission_Date": [d.date() for d in admission_dates],
    "Discharge_Date": [dd.date() if not sa else None for dd, sa in zip(discharge_dates, still_admitted_mask)],
    "Diagnosis": [RNG.choice(diagnoses_by_dept[dept_lookup[d]]) for d in adm_dept_ids],
    "Admission_Type": admission_type,
})

# ---------------------------------------------------------------------------
# 5. Appointments
# ---------------------------------------------------------------------------
appt_dept_ids = RNG.choice(departments["Department_ID"], size=N_APPOINTMENTS, p=dept_weights)
appt_dates = [START_DATE + timedelta(days=int(RNG.integers(0, DAYS_RANGE))) for _ in range(N_APPOINTMENTS)]

# waiting time in minutes: Emergency & General Medicine trend higher
wait_base = {
    "Cardiology": 25, "Neurology": 30, "Orthopedics": 20, "General Medicine": 35,
    "Pediatrics": 18, "Dermatology": 15, "Emergency": 40, "Gynecology": 22
}
waiting_times = [max(0, int(RNG.normal(wait_base[dept_lookup[d]], 12))) for d in appt_dept_ids]

status_probs = [0.78, 0.10, 0.08, 0.04]  # Completed, Cancelled, No-show, Rescheduled
statuses = RNG.choice(["Completed", "Cancelled", "No-show", "Rescheduled"],
                       size=N_APPOINTMENTS, p=status_probs)

appointments = pd.DataFrame({
    "Appointment_ID": range(1, N_APPOINTMENTS + 1),
    "Patient_ID": RNG.choice(patients["Patient_ID"], size=N_APPOINTMENTS),
    "Doctor_ID": [RNG.choice(doctors.loc[doctors["Department_ID"] == d, "Doctor_ID"].values)
                  if len(doctors.loc[doctors["Department_ID"] == d]) > 0
                  else RNG.choice(doctors["Doctor_ID"])
                  for d in appt_dept_ids],
    "Department_ID": appt_dept_ids,
    "Appointment_Date": [d.date() for d in appt_dates],
    "Appointment_Time": [f"{RNG.integers(8,18):02d}:{RNG.choice([0,15,30,45]):02d}" for _ in range(N_APPOINTMENTS)],
    "Waiting_Time": waiting_times,
    "Status": statuses,
})

# ---------------------------------------------------------------------------
# 6. Beds
# ---------------------------------------------------------------------------
bed_rows = []
bed_id = 1
active_admissions = admissions[admissions["Discharge_Date"].isna()].copy()
for _, row in departments.iterrows():
    dept_id = row["Department_ID"]
    capacity = row["Capacity"]
    dept_active_adm = active_admissions[active_admissions["Department_ID"] == dept_id]["Admission_ID"].tolist()
    for i in range(capacity):
        if i < len(dept_active_adm):
            status = "Occupied"
            adm_id = dept_active_adm[i]
        else:
            status = RNG.choice(["Available", "Maintenance"], p=[0.9, 0.1])
            adm_id = None
        bed_rows.append({
            "Bed_ID": bed_id,
            "Department_ID": dept_id,
            "Bed_Type": RNG.choice(["General", "ICU", "Private"], p=[0.6, 0.2, 0.2]),
            "Availability_Status": status,
            "Admission_ID": adm_id,
        })
        bed_id += 1
beds = pd.DataFrame(bed_rows)

# ---------------------------------------------------------------------------
# 7. Billing (one row per admission)
# ---------------------------------------------------------------------------
cost_base = {
    "Cardiology": 85000, "Neurology": 95000, "Orthopedics": 70000, "General Medicine": 35000,
    "Pediatrics": 30000, "Dermatology": 15000, "Emergency": 40000, "Gynecology": 45000
}

billing_rows = []
for _, adm in admissions.iterrows():
    dept_name = dept_lookup[adm["Department_ID"]]
    base = cost_base[dept_name]
    treatment_cost = max(2000, RNG.normal(base, base * 0.25))
    medicine_cost = treatment_cost * RNG.uniform(0.05, 0.15)
    lab_cost = treatment_cost * RNG.uniform(0.03, 0.10)
    total = treatment_cost + medicine_cost + lab_cost
    insurance_pct = RNG.choice([0, 0.5, 0.8, 1.0], p=[0.3, 0.25, 0.25, 0.2])
    insurance_amt = total * insurance_pct
    patient_payment = total - insurance_amt
    billing_rows.append({
        "Bill_ID": adm["Admission_ID"],
        "Patient_ID": adm["Patient_ID"],
        "Admission_ID": adm["Admission_ID"],
        "Treatment_Cost": round(treatment_cost, 2),
        "Medicine_Cost": round(medicine_cost, 2),
        "Lab_Cost": round(lab_cost, 2),
        "Insurance_Amount": round(insurance_amt, 2),
        "Patient_Payment": round(patient_payment, 2),
        "Total_Amount": round(total, 2),
        "Payment_Status": RNG.choice(["Paid", "Partially Paid", "Pending"], p=[0.75, 0.15, 0.10]),
    })
billing = pd.DataFrame(billing_rows)

# ---------------------------------------------------------------------------
# 8. Lab Tests
# ---------------------------------------------------------------------------
test_names = ["CBC", "Lipid Profile", "Liver Function Test", "Kidney Function Test",
              "Blood Sugar (Fasting)", "Thyroid Panel", "X-Ray", "MRI Scan", "CT Scan",
              "ECG", "Urine Routine", "COVID-19 RT-PCR"]

lab_dates = [START_DATE + timedelta(days=int(RNG.integers(0, DAYS_RANGE))) for _ in range(N_LAB_TESTS)]
lab_tests = pd.DataFrame({
    "Test_ID": range(1, N_LAB_TESTS + 1),
    "Patient_ID": RNG.choice(patients["Patient_ID"], size=N_LAB_TESTS),
    "Doctor_ID": RNG.choice(doctors["Doctor_ID"], size=N_LAB_TESTS),
    "Test_Name": RNG.choice(test_names, size=N_LAB_TESTS),
    "Test_Date": [d.date() for d in lab_dates],
    "Test_Cost": RNG.integers(300, 8000, size=N_LAB_TESTS),
    "Test_Result": RNG.choice(["Normal", "Abnormal", "Borderline"], size=N_LAB_TESTS, p=[0.65, 0.2, 0.15]),
    "Test_Status": RNG.choice(["Completed", "Pending"], size=N_LAB_TESTS, p=[0.92, 0.08]),
})

# ---------------------------------------------------------------------------
# 9. Medications (linked to admissions)
# ---------------------------------------------------------------------------
med_names = ["Paracetamol", "Amoxicillin", "Ibuprofen", "Metformin", "Amlodipine",
             "Atorvastatin", "Omeprazole", "Azithromycin", "Cetirizine", "Insulin",
             "Aspirin", "Losartan"]

med_rows = []
med_id = 1
for _, adm in admissions.iterrows():
    n_meds = RNG.integers(N_MEDICATIONS_PER_ADM[0], N_MEDICATIONS_PER_ADM[1] + 1)
    for _ in range(n_meds):
        med_rows.append({
            "Medication_ID": med_id,
            "Admission_ID": adm["Admission_ID"],
            "Patient_ID": adm["Patient_ID"],
            "Medicine_Name": RNG.choice(med_names),
            "Dosage": RNG.choice(["250mg", "500mg", "5mg", "10mg", "1 unit"]),
            "Frequency": RNG.choice(["Once daily", "Twice daily", "Thrice daily", "As needed"]),
            "Cost": round(RNG.uniform(20, 1200), 2),
        })
        med_id += 1
medications = pd.DataFrame(med_rows)

# ---------------------------------------------------------------------------
# Introduce light realistic messiness (so the Excel-cleaning stage has a purpose)
# ---------------------------------------------------------------------------
messy_departments = departments.copy()
# Add duplicate-style raw entries as a separate "raw" export to demonstrate cleaning
raw_dept_names_variants = {
    "Cardiology": ["Cardiology", "cardiology", "CARDIOLOGY", "Cardio"],
    "Emergency": ["Emergency", "emergency", "ER"],
}
appointments_raw_demo = appointments.copy()
# inject a few missing waiting times and duplicate rows to mimic raw hospital exports
dup_idx = RNG.choice(appointments_raw_demo.index, size=15, replace=False)
appointments_raw_demo = pd.concat([appointments_raw_demo, appointments_raw_demo.loc[dup_idx]], ignore_index=True)
missing_idx = RNG.choice(appointments_raw_demo.index, size=40, replace=False)
appointments_raw_demo.loc[missing_idx, "Waiting_Time"] = np.nan

# ---------------------------------------------------------------------------
# Save all outputs
# ---------------------------------------------------------------------------
out_dir = "../data"
patients.to_csv(f"{out_dir}/patients.csv", index=False)
doctors.to_csv(f"{out_dir}/doctors.csv", index=False)
departments.to_csv(f"{out_dir}/departments.csv", index=False)
admissions.to_csv(f"{out_dir}/admissions.csv", index=False)
appointments.to_csv(f"{out_dir}/appointments.csv", index=False)
beds.to_csv(f"{out_dir}/beds.csv", index=False)
billing.to_csv(f"{out_dir}/billing.csv", index=False)
lab_tests.to_csv(f"{out_dir}/lab_tests.csv", index=False)
medications.to_csv(f"{out_dir}/medications.csv", index=False)
appointments_raw_demo.to_csv(f"{out_dir}/appointments_RAW_uncleaned.csv", index=False)

print("Generated tables:")
for name, df in [("patients", patients), ("doctors", doctors), ("departments", departments),
                  ("admissions", admissions), ("appointments", appointments), ("beds", beds),
                  ("billing", billing), ("lab_tests", lab_tests), ("medications", medications)]:
    print(f"  {name:15s} {len(df):>6d} rows")
