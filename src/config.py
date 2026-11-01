"""
Configuration file for the Financial Fraud Detection & Analytics System.
Defines project paths, column schemas, and application constants.
"""

import sys
from pathlib import Path

# Project Root Directory
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Data Directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = DATA_DIR / "reports"

# Raw Data Files
RAW_TRAIN_FILE = RAW_DATA_DIR / "fraudTrain.csv"
RAW_TEST_FILE = RAW_DATA_DIR / "fraudTest.csv"

# Processed Data Files
PROCESSED_PARQUET_FILE = PROCESSED_DATA_DIR / "fraud_data.parquet"
PROCESSED_SAMPLE_FILE = PROCESSED_DATA_DIR / "fraud_sample_100k.parquet"
BUSINESS_INSIGHTS_JSON = PROCESSED_DATA_DIR / "business_insights.json"

# Unnecessary / PII columns to remove for public analytics
DROP_COLUMNS = [
    "Unnamed: 0",
    "cc_num",
    "first",
    "last",
    "street",
    "zip",
]

# Primary schema definition
EXPECTED_COLUMNS = [
    "trans_date_trans_time",
    "merchant",
    "category",
    "amt",
    "gender",
    "city",
    "state",
    "lat",
    "long",
    "city_pop",
    "job",
    "dob",
    "trans_num",
    "unix_time",
    "merch_lat",
    "merch_long",
    "is_fraud",
]

# Physical constants
EARTH_RADIUS_KM = 6371.0

# Dashboard Design Tokens & Colors
COLOR_PRIMARY = "#1E3A8A"     # Deep Navy
COLOR_SECONDARY = "#0EA5E9"   # Electric Blue
COLOR_ACCENT = "#EF4444"      # Crimson / Red (Fraud)
COLOR_SUCCESS = "#10B981"     # Emerald Green (Legitimate)
COLOR_WARNING = "#F59E0B"     # Amber
COLOR_BG_DARK = "#0F172A"     # Slate 900
COLOR_CARD_DARK = "#1E293B"   # Slate 800
COLOR_TEXT_LIGHT = "#F8FAFC"  # Slate 50
COLOR_MUTED = "#94A3B8"       # Slate 400
