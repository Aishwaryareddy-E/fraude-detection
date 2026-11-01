# 📖 Financial Transaction Data Dictionary

## 1. Overview
This data dictionary documents the raw inputs and engineered features of the **Financial Fraud Detection & Analytics System** sourced from `archive (8).zip` (`fraudTrain.csv` and `fraudTest.csv`).

Total Records: **1,852,394**  
Historical Fraud Cases: **9,651** (0.5210% prevalence)  
Temporal Period: **January 1, 2019 – December 31, 2020**  

---

## 2. Raw Dataset Fields

| Column Name | Data Type | Description | Analytical Treatment |
| :--- | :--- | :--- | :--- |
| `Unnamed: 0` | Integer | Row index from original CSV export | **Dropped** (redundant identifier) |
| `trans_date_trans_time` | String (Timestamp) | Date and time the transaction was initiated | Converted to datetime; extracted temporal features |
| `cc_num` | Integer / String | Credit card account number | **Dropped** (PII protection) |
| `merchant` | String | Merchant or vendor name (prefixed with `fraud_`) | Retained; stripped prefix for readability |
| `category` | String (Categorical) | Merchant merchant category code (MCC grouping) | Key dimension for fraud vulnerability profiling |
| `amt` | Float | Transaction dollar value | Core numerical metric; audited for `amt > 0` |
| `first` | String | Cardholder first name | **Dropped** (PII protection) |
| `last` | String | Cardholder last name | **Dropped** (PII protection) |
| `gender` | Categorical (`M`/`F`) | Cardholder gender | Retained for demographic analysis |
| `street` | String | Cardholder residential street address | **Dropped** (PII protection) |
| `city` | String | Cardholder residential city | Retained for localized analytics |
| `state` | String (2-letter) | Cardholder residential US state | Retained for state-level choropleth mapping |
| `zip` | Integer | Cardholder residential postal code | **Dropped** (redundant with city/state) |
| `lat` | Float | Cardholder residential latitude in degrees | Validated in range `[-90, 90]`; used for Haversine |
| `long` | Float | Cardholder residential longitude in degrees | Validated in range `[-180, 180]`; used for Haversine |
| `city_pop` | Integer | Resident population of cardholder's city | Retained as demographic density metric |
| `job` | String | Cardholder declared profession | Retained for occupational profiling |
| `dob` | String (Date) | Cardholder date of birth (`YYYY-MM-DD`) | Converted to datetime; used to compute exact age |
| `trans_num` | String | Unique transaction alphanumeric identifier | Retained as foreign key for ledger audit |
| `unix_time` | Integer | Epoch timestamp in seconds | Retained for chronological indexing |
| `merch_lat` | Float | Merchant point-of-sale latitude | Validated in range `[-90, 90]`; used for Haversine |
| `merch_long` | Float | Merchant point-of-sale longitude | Validated in range `[-180, 180]`; used for Haversine |
| `is_fraud` | Integer (`0`/`1`) | Target label: 1 = Historically identified fraud, 0 = Legitimate | Core analytical ground truth |

---

## 3. Engineered Forensic Features

| Feature Name | Derived Type | Derivation Logic | Business Purpose |
| :--- | :--- | :--- | :--- |
| `source_dataset` | Categorical | `"Train"` if from `fraudTrain.csv`, `"Test"` if from `fraudTest.csv` | Audit trail and data provenance preservation |
| `clean_merchant` | String | `merchant.str.replace('^fraud_', '')` | User-friendly commercial entity identification |
| `year` | Int16 | `dt.year` (2019 or 2020) | Multi-year longitudinal comparison |
| `month` | Int8 | `dt.month` (1 to 12) | Seasonal pattern tracking |
| `day` | Int8 | `dt.day` (1 to 31) | Intra-month transaction profiling |
| `hour` | Int8 | `dt.hour` (0 to 23) | Diurnal attack cycle detection |
| `day_name` | Categorical | `dt.day_name()` (Monday to Sunday) | Weekly operational analysis |
| `year_month` | String | `dt.to_period('M')` (`YYYY-MM`) | Continuous monthly volume tracking |
| `is_weekend` | Int8 | `1` if Saturday or Sunday, else `0` | Weekend vs weekday behavioral shift |
| `time_of_day` | Categorical | `Night (00-06)`, `Morning (06-12)`, `Afternoon (12-18)`, `Evening (18-24)` | Consolidated diurnal periods |
| `age` | Int16 | Exact calendar age accounting for month and day of birth | Precise customer age distribution |
| `age_group` | Categorical | `<25`, `25-34`, `35-49`, `50-64`, `65+` | Demographic risk stratification |
| `distance_km` | Float32 | Haversine distance between `(lat, long)` and `(merch_lat, merch_long)` | Physical cardholder-to-merchant distance in km |
| `distance_bin` | Categorical | `< 5 km`, `5 - 20 km`, `20 - 50 km`, `50 - 100 km`, `> 100 km` | Distance tier risk segmentation |
| `amount_tier` | Categorical | `$0 - $25`, `$25 - $50`, `$50 - $100`, `$100 - $500`, `$500 - $1000`, `> $1000` | Commercial ticket size segmentation |

---

## 4. Key Formulas

### A. Haversine Great-Circle Distance
$$ d = 2R \arcsin\left(\sqrt{\sin^2\frac{\Delta\phi}{2} + \cos\phi_1\cos\phi_2 \sin^2\frac{\Delta\lambda}{2}}\right) $$
Where $R = 6,371\text{ km}$, $\phi$ is latitude in radians, and $\lambda$ is longitude in radians.

### B. Exact Age Calculation
$$ \text{Age} = \text{Year}_{\text{trans}} - \text{Year}_{\text{dob}} - \mathbb{I}\left[(\text{Month}_{\text{trans}} < \text{Month}_{\text{dob}}) \lor (\text{Month}_{\text{trans}} = \text{Month}_{\text{dob}} \land \text{Day}_{\text{trans}} < \text{Day}_{\text{dob}})\right] $$

### C. Systemic Fraud Rate
$$ \text{Fraud Rate (\%)} = \frac{\sum \text{is\_fraud}}{\text{Total Transactions}} \times 100 $$
