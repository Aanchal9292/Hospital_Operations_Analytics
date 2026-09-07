# Power BI Dashboard — Setup Guide

This environment can't run Power BI Desktop directly (it's a Windows/macOS
desktop app), so instead of a fake `.pbix`, this folder gives you everything
needed to build the real one in about 20–30 minutes: the data model, the
DAX measures, and the exact page/visual layout from the project spec.

## 1. Get Data
Open Power BI Desktop → **Get Data → Text/CSV** (or **MySQL database** if you
loaded the schema in `/sql`) → import all 9 tables from `/data`:
`patients, doctors, departments, admissions, appointments, beds, billing, lab_tests, medications`

## 2. Build relationships (Model view)
Power BI will mostly auto-detect these — verify each is a **many-to-one**,
single-direction filter from the fact tables up to the dimension tables:

- `admissions[Patient_ID]` → `patients[Patient_ID]`
- `admissions[Department_ID]` → `departments[Department_ID]`
- `admissions[Doctor_ID]` → `doctors[Doctor_ID]`
- `appointments[Patient_ID]` → `patients[Patient_ID]`
- `appointments[Doctor_ID]` → `doctors[Doctor_ID]`
- `appointments[Department_ID]` → `departments[Department_ID]`
- `beds[Department_ID]` → `departments[Department_ID]`
- `beds[Admission_ID]` → `admissions[Admission_ID]`
- `billing[Admission_ID]` → `admissions[Admission_ID]`
- `lab_tests[Patient_ID]` → `patients[Patient_ID]`
- `medications[Admission_ID]` → `admissions[Admission_ID]`

Also add a **Date table** (Modeling → New Table → see `dax_measures.txt` for
the `DateTable` formula) and mark it as a Date table, then relate it to
`admissions[Admission_Date]` and `appointments[Appointment_Date]` — this is
what makes month/quarter/year slicers work across the whole model.

## 3. Add measures
Copy the DAX from `dax_measures.txt` into new measures on the `admissions`
or `billing` table (a dedicated `_Measures` table is cleanest).

## 4. Build the 4 pages
Use the layout from the project's Section 17–20 (also summarized in the
main `README.md`):
1. **Executive Overview** — KPI cards + monthly trend + department bar + revenue trend + demographics
2. **Patient & Department Analysis** — patient count by dept, age/gender split, top diagnoses, avg LOS
3. **Hospital Operations** — bed utilization, waiting time, doctor workload, appointment completion/cancellation
4. **Financial Analysis** — total revenue, revenue by dept/treatment, insurance vs. patient payment, outstanding payments

Add slicers for **Date, Department, Gender, Age Group, Diagnosis, Admission
Type** on each page (or as a synced panel across all pages via
**View → Sync Slicers**).

## 5. Save
File → Save As → `hospital_operations_dashboard.pbix` in this folder.
