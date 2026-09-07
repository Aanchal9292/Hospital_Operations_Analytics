"""
Hospital Operations Analytics - Exploratory Data Analysis
Generates summary statistics and charts for patient demographics,
admission trends, waiting times, and length of stay.

Outputs PNG charts into ../python/eda_charts/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

DATA_DIR = "../data"
OUT_DIR = "eda_charts"
os.makedirs(OUT_DIR, exist_ok=True)
sns.set_theme(style="whitegrid")

patients = pd.read_csv(f"{DATA_DIR}/patients.csv")
departments = pd.read_csv(f"{DATA_DIR}/departments.csv")
admissions = pd.read_csv(f"{DATA_DIR}/admissions.csv", parse_dates=["Admission_Date", "Discharge_Date"])
appointments = pd.read_csv(f"{DATA_DIR}/appointments.csv")
billing = pd.read_csv(f"{DATA_DIR}/billing.csv")

admissions = admissions.merge(departments, on="Department_ID")
appointments = appointments.merge(departments, on="Department_ID")

admissions["Length_of_Stay"] = (admissions["Discharge_Date"] - admissions["Admission_Date"]).dt.days

# ---------------------------------------------------------------------
# 1. Patient demographics
# ---------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
sns.histplot(patients["Age"], bins=20, ax=axes[0], color="#4C72B0")
axes[0].set_title("Patient Age Distribution")
sns.countplot(x="Gender", data=patients, ax=axes[1], palette="viridis")
axes[1].set_title("Patient Gender Distribution")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/patient_demographics.png", dpi=130)
plt.close()

# ---------------------------------------------------------------------
# 2. Admission trends (monthly)
# ---------------------------------------------------------------------
monthly = admissions.set_index("Admission_Date").resample("ME").size()
plt.figure(figsize=(10, 4.5))
monthly.plot(marker="o", color="#C44E52")
plt.title("Monthly Admission Trend")
plt.ylabel("Admissions")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/monthly_admission_trend.png", dpi=130)
plt.close()

# ---------------------------------------------------------------------
# 3. Department-wise admissions & emergency vs regular
# ---------------------------------------------------------------------
plt.figure(figsize=(9, 5))
order = admissions["Department_Name"].value_counts().index
sns.countplot(y="Department_Name", data=admissions, order=order, hue="Admission_Type")
plt.title("Admissions by Department (Emergency vs Regular)")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/admissions_by_department.png", dpi=130)
plt.close()

# ---------------------------------------------------------------------
# 4. Waiting time analysis
# ---------------------------------------------------------------------
plt.figure(figsize=(9, 5))
order = appointments.groupby("Department_Name")["Waiting_Time"].mean().sort_values(ascending=False).index
sns.boxplot(x="Waiting_Time", y="Department_Name", data=appointments, order=order, palette="mako")
plt.title("Waiting Time Distribution by Department")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/waiting_time_by_department.png", dpi=130)
plt.close()

# ---------------------------------------------------------------------
# 5. Length of stay analysis
# ---------------------------------------------------------------------
los_df = admissions.dropna(subset=["Length_of_Stay"])
plt.figure(figsize=(9, 5))
order = los_df.groupby("Department_Name")["Length_of_Stay"].mean().sort_values(ascending=False).index
sns.barplot(x="Length_of_Stay", y="Department_Name", data=los_df, order=order,
            estimator=np.mean, palette="rocket")
plt.title("Average Length of Stay by Department")
plt.xlabel("Days")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/avg_length_of_stay.png", dpi=130)
plt.close()

# ---------------------------------------------------------------------
# 6. Revenue by department
# ---------------------------------------------------------------------
rev = billing.merge(admissions[["Admission_ID", "Department_Name"]], on="Admission_ID")
rev_by_dept = rev.groupby("Department_Name")["Total_Amount"].sum().sort_values(ascending=False)
plt.figure(figsize=(9, 5))
rev_by_dept.plot(kind="barh", color="#55A868")
plt.title("Total Revenue by Department")
plt.xlabel("Revenue (₹)")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/revenue_by_department.png", dpi=130)
plt.close()

# ---------------------------------------------------------------------
# Outlier detection example: unusually long stays (IQR method)
# ---------------------------------------------------------------------
q1, q3 = los_df["Length_of_Stay"].quantile([0.25, 0.75])
iqr = q3 - q1
upper_bound = q3 + 1.5 * iqr
outliers = los_df[los_df["Length_of_Stay"] > upper_bound]

# ---------------------------------------------------------------------
# Print summary
# ---------------------------------------------------------------------
print("=== EDA Summary ===")
print(f"Total patients            : {len(patients)}")
print(f"Total admissions          : {len(admissions)}")
print(f"Avg length of stay (days) : {los_df['Length_of_Stay'].mean():.2f}")
print(f"Median length of stay     : {los_df['Length_of_Stay'].median():.1f}")
print(f"Long-stay outliers (> {upper_bound:.1f} days): {len(outliers)} admissions")
print(f"Avg waiting time (min)    : {appointments['Waiting_Time'].mean():.1f}")
print(f"Total revenue             : ₹{billing['Total_Amount'].sum():,.2f}")
print(f"Avg revenue per patient   : ₹{billing['Total_Amount'].sum() / billing['Patient_ID'].nunique():,.2f}")
print(f"\nCharts saved to: {OUT_DIR}/")
