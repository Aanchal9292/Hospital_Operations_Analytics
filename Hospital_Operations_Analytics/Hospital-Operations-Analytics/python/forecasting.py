"""
Hospital Operations Analytics - Forecasting
Simple, explainable forecasting for monthly patient admissions and
estimated bed requirements, plus an optional length-of-stay
classification model (Short / Medium / Long).

This is intentionally kept to well-understood, easily explained
methods (linear trend + seasonal averages, and a decision tree
classifier) so it is suitable for a portfolio project and can be
clearly described in an interview.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

DATA_DIR = "../data"

# ---------------------------------------------------------------------
# 1. Monthly admission forecasting (linear trend)
# ---------------------------------------------------------------------
admissions = pd.read_csv(f"{DATA_DIR}/admissions.csv", parse_dates=["Admission_Date"])
monthly = admissions.set_index("Admission_Date").resample("ME").size().reset_index(name="admissions")
monthly["t"] = np.arange(len(monthly))

X = monthly[["t"]]
y = monthly["admissions"]
model = LinearRegression().fit(X, y)

future_t = np.arange(len(monthly), len(monthly) + 3).reshape(-1, 1)
forecast = model.predict(future_t)

print("=== Monthly Admission Forecast (next 3 months) ===")
last_date = monthly["Admission_Date"].max()
for i, val in enumerate(forecast, start=1):
    future_month = (last_date + pd.DateOffset(months=i)).strftime("%Y-%m")
    print(f"  {future_month}: {max(0, round(val))} admissions (predicted)")

# ---------------------------------------------------------------------
# 2. Estimated bed requirement from forecasted admissions + avg LOS
# ---------------------------------------------------------------------
admissions_los = pd.read_csv(f"{DATA_DIR}/admissions.csv", parse_dates=["Admission_Date", "Discharge_Date"])
admissions_los["LOS"] = (admissions_los["Discharge_Date"] - admissions_los["Admission_Date"]).dt.days
avg_los = admissions_los["LOS"].mean()

print(f"\n=== Estimated Bed Requirement ===")
print(f"Average length of stay: {avg_los:.2f} days")
for i, val in enumerate(forecast, start=1):
    est_beds_needed = round(max(0, val) * avg_los / 30)  # patient-days / days in month
    future_month = (last_date + pd.DateOffset(months=i)).strftime("%Y-%m")
    print(f"  {future_month}: ~{est_beds_needed} beds needed on an average day")

# ---------------------------------------------------------------------
# 3. Length-of-stay classification model (Short / Medium / Long)
# ---------------------------------------------------------------------
print("\n=== Length-of-Stay Classification Model ===")
print("NOTE: This is an analytical/operational planning model only,")
print("      not a clinical decision-making tool.\n")

df = admissions_los.dropna(subset=["LOS"]).copy()
departments = pd.read_csv(f"{DATA_DIR}/departments.csv")
df = df.merge(departments, on="Department_ID")

# bucket LOS into 3 classes
df["LOS_Class"] = pd.cut(df["LOS"], bins=[-1, 2, 6, 100], labels=["Short", "Medium", "Long"])

le_dept = LabelEncoder()
le_type = LabelEncoder()
le_diag = LabelEncoder()

df["Department_enc"] = le_dept.fit_transform(df["Department_Name"])
df["Admission_Type_enc"] = le_type.fit_transform(df["Admission_Type"])
df["Diagnosis_enc"] = le_diag.fit_transform(df["Diagnosis"])

features = ["Department_enc", "Admission_Type_enc", "Diagnosis_enc"]
X = df[features]
y = df["LOS_Class"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
clf = DecisionTreeClassifier(max_depth=5, random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

print(classification_report(y_test, y_pred, zero_division=0))

feat_importance = pd.Series(clf.feature_importances_, index=features).sort_values(ascending=False)
print("Feature importance:")
print(feat_importance)
