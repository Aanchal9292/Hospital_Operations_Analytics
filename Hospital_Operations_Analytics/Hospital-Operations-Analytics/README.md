# Hospital Operations Analytics

An end-to-end data analytics project analyzing hospital operations — patient
admissions, appointments, bed utilization, doctor workload, departmental
performance, waiting times, and revenue — using **Excel, MySQL, Python, and
Power BI**.

```
Raw Hospital Data → Excel (cleaning) → MySQL (storage + SQL analysis)
                  → Python (EDA + forecasting) → Power BI (dashboard)
                  → Business Insights → Management Recommendations
```

This repo is fully runnable end-to-end: a synthetic-but-realistic dataset
(3,000 patients / 4,500 admissions / 9,000 appointments across 8 departments
and 2 years) is generated, cleaned, loaded into a relational schema, analyzed
in SQL and Python, and packaged for a Power BI dashboard.

---

## Folder structure

```
Hospital-Operations-Analytics/
│
├── data/                          # Generated + cleaned datasets
│   ├── patients.csv / .xlsx
│   ├── doctors.csv / .xlsx
│   ├── departments.csv
│   ├── admissions.csv / .xlsx
│   ├── appointments.csv / .xlsx
│   ├── appointments_RAW_uncleaned.csv   # demonstrates raw-data messiness
│   ├── appointments_cleaned.csv
│   ├── beds.csv
│   ├── billing.csv / .xlsx
│   ├── lab_tests.csv
│   └── medications.csv
│
├── sql/
│   ├── database_schema.sql        # CREATE TABLE + FK + indexes
│   ├── data_import.sql            # LOAD DATA INFILE for all 9 tables
│   └── analysis_queries.sql       # 15 queries: joins, CTEs, subqueries, window fns
│
├── python/
│   ├── generate_data.py           # synthetic data generator (run this first)
│   ├── data_cleaning.py / .ipynb  # dept-name standardization, dedup, validation
│   ├── exploratory_analysis.py / .ipynb   # demographics, trends, waits, LOS + charts
│   ├── forecasting.py / .ipynb    # admission forecast, bed demand, LOS classifier
│   └── eda_charts/                # PNG output from the EDA notebook
│
├── powerbi/
│   ├── README_PowerBI_Setup.md    # step-by-step dashboard build guide
│   └── dax_measures.txt           # all DAX measures + date table
│
├── excel/
│   └── hospital_data_cleaning.xlsx  # before/after cleaning workbook
│
└── README.md
```

## How to reproduce this

```bash
cd python
python generate_data.py          # writes all CSVs to ../data
python data_cleaning.py          # standardizes + dedups appointments data
python exploratory_analysis.py   # writes charts to eda_charts/
python forecasting.py            # admission forecast + LOS model
```

Then, to load into MySQL:
```bash
mysql -u root -p < ../sql/database_schema.sql
mysql -u root -p --local-infile=1 hospital_analytics < ../sql/data_import.sql
mysql -u root -p hospital_analytics < ../sql/analysis_queries.sql
```

Then follow `powerbi/README_PowerBI_Setup.md` to build the 4-page dashboard.

---

## Key KPIs modeled

| KPI | Formula |
|---|---|
| Bed Occupancy Rate | Occupied Beds / Total Beds × 100 |
| Appointment Completion Rate | Completed / Total Appointments × 100 |
| Cancellation Rate | Cancelled / Total Appointments × 100 |
| Average Revenue per Patient | Total Revenue / Distinct Patients |
| Average Length of Stay | AVG(Discharge Date − Admission Date) |

## Dashboard pages
1. **Executive Overview** — top-line KPI cards, monthly admission trend, department mix, revenue trend, demographics
2. **Patient & Department Analysis** — patient volume, age/gender split, top diagnoses, avg length of stay by department
3. **Hospital Operations** — bed utilization, waiting time, doctor workload, appointment completion/cancellation
4. **Financial Analysis** — total revenue, revenue by department/treatment, insurance vs. patient payment, outstanding balances

---

## Business insights (computed from this dataset)

1. **Emergency dominates volume and drives real pressure.** Emergency accounts
   for the highest admission count (~1,115 of 4,500, ~25%) *and* the highest
   average appointment waiting time (~40 min) — the classic sign of a
   department that needs more staffing or a faster triage process.
2. **Waiting time doesn't track volume everywhere.** General Medicine has
   roughly two-thirds of Emergency's admission volume but the second-highest
   average wait (~35 min), while higher-volume departments like Orthopedics
   and Cardiology see noticeably shorter waits — suggesting a scheduling or
   staffing gap specific to General Medicine rather than a simple capacity
   problem.
3. **Revenue concentration.** The top 3 departments by revenue (Emergency,
   Cardiology, Neurology) generate just over half of total hospital revenue
   (~54%), even though they account for well under half of total admissions —
   these are the highest-value service lines to protect and invest in.
4. **Seasonality in admissions.** Monthly admissions fluctuate in a ~160–220
   range with recurring dips in February and rises toward the December /
   July–September window — useful for staffing and procurement planning
   ahead of predictable peaks.
5. **Neurological and orthopedic diagnoses drive the longest stays.**
   Parkinson's Disease, Migraine (complex/recurrent cases), Stroke, Epilepsy,
   and Spinal Disc Herniation top the list of diagnoses by average length of
   stay (7+ days), well above the hospital-wide average of ~3.8 days — these
   patients disproportionately consume bed-days and should be the focus of
   any length-of-stay reduction initiative.

*(Full query logic for each of these lives in `sql/analysis_queries.sql`;
the Python EDA notebook reproduces them with charts.)*

---

## Resume description

**Hospital Operations Analytics | Python, MySQL, Power BI, Excel**
Developed an end-to-end hospital operations analytics solution to analyze
patient admissions, appointments, bed utilization, doctor workload,
departmental performance, waiting times, and revenue. Cleaned and
transformed hospital data using Excel and Python, designed a relational
database in MySQL, performed advanced SQL analysis using joins, CTEs and
window functions, and developed an interactive Power BI dashboard with
DAX-based KPIs and dynamic filtering. Identified operational trends and
bottlenecks to support data-driven hospital capacity and resource planning.

## Interview explanation (talk track)

> "My project is Hospital Operations Analytics, an end-to-end pipeline built
> with Excel, MySQL, Python and Power BI. I started with a raw hospital
> dataset covering patients, doctors, departments, admissions, appointments,
> beds, billing, and lab tests. I used Excel to clean and standardize the
> data — things like collapsing inconsistent department name entries and
> handling missing waiting-time values. I then designed a relational schema
> in MySQL and wrote SQL using joins, CTEs, subqueries and window functions
> to compute metrics like department-wise admissions, average length of
> stay, bed occupancy, and 30-day readmissions. In Python, I ran exploratory
> analysis on demographics, admission trends and waiting times, and built a
> simple forecasting model for future bed demand plus a length-of-stay
> classifier. Finally, I connected everything to Power BI for a four-page
> interactive dashboard with KPI cards, department and financial views, and
> slicers for date, department, and demographics. The goal wasn't just
> visualizing the data — it was surfacing operational bottlenecks, like
> Emergency's high volume and wait times, or which departments generate
> disproportionate revenue, that hospital management could act on."

---

## Skills demonstrated
**Excel** — cleaning, pivot tables, formulas, validation
**MySQL** — schema design, joins, aggregations, CTEs, subqueries, window functions
**Python** — Pandas, NumPy, EDA, cleaning, Matplotlib/Seaborn, scikit-learn
**Power BI** — data modeling, DAX, KPI design, interactive dashboards, slicers
**Business** — KPI development, operational analysis, resource planning, data storytelling
