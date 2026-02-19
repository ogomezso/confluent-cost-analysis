import os
import requests
import warnings
from datetime import date, timedelta
from collections import defaultdict

# Suppress SSL warnings on macOS
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*urllib3 v2 only supports OpenSSL.*')

# ----------------------------
# CONFIGURATION
# ----------------------------
# Get all input from user prompts
import sys

print("Confluent Cloud Cost Analysis")
print("============================")
print("")
sys.stdout.flush()

try:
    CCLOUD_API_KEY = raw_input("Enter Confluent Cloud API Key: ")
except NameError:
    CCLOUD_API_KEY = input("Enter Confluent Cloud API Key: ")

try:
    CCLOUD_API_SECRET = raw_input("Enter Confluent Cloud API Secret: ")
except NameError:
    CCLOUD_API_SECRET = input("Enter Confluent Cloud API Secret: ")

try:
    CLUSTER_ID = raw_input("Enter Cluster ID (LKC): ")
except NameError:
    CLUSTER_ID = input("Enter Cluster ID (LKC): ")

print("")  # Add spacing
sys.stdout.flush()

try:
    REFERENCE_DATE_input = raw_input("Enter Reference Date (YYYY-MM-DD, optional, press Enter for today): ")
except NameError:
    REFERENCE_DATE_input = input("Enter Reference Date (YYYY-MM-DD, optional, press Enter for today): ")

try:
    PERIOD_MONTHS_input = raw_input("Enter Number of Months to Analyze (default: 1): ")
except NameError:
    PERIOD_MONTHS_input = input("Enter Number of Months to Analyze (default: 1): ")

# Process optional inputs
REFERENCE_DATE = REFERENCE_DATE_input.strip() if REFERENCE_DATE_input.strip() else None
PERIOD_MONTHS = PERIOD_MONTHS_input.strip() if PERIOD_MONTHS_input.strip() else "1"

print("")  # Add spacing
print(f"Analyzing cluster {CLUSTER_ID} for {PERIOD_MONTHS} month(s)...")
if REFERENCE_DATE:
    print(f"Reference date: {REFERENCE_DATE}")
else:
    print(f"Reference date: Today ({date.today()})")
print("")
sys.stdout.flush()

# Range: N months before the reference date
today = date.today()
if REFERENCE_DATE:
    reference_date = date.fromisoformat(REFERENCE_DATE)
else:
    reference_date = today

# Calculate start date by subtracting N months from reference date
period_months = int(PERIOD_MONTHS)
start_year = reference_date.year - (period_months - reference_date.month + 11) // 12
start_month = (reference_date.month - period_months - 1) % 12 + 1
start_date = date(start_year, start_month, 1)

# End date is the reference date
end_date = reference_date

# API limit: start_date cannot be more than 1 year in the past
# Calculate minimum allowed date      
min_allowed_date = date(today.year - 1, today.month, today.day)

# Adjust start_date if it's before the API limit
if start_date < min_allowed_date:
    import sys
    print(f"Warning: start_date {start_date} is before API limit ({min_allowed_date}).", file=sys.stderr)
    print(f"Adjusting start_date to {min_allowed_date}.", file=sys.stderr)
    start_date = min_allowed_date

# Adjust end_date to not exceed today
if end_date > today:
    end_date = today

BASE_URL = "https://api.confluent.cloud/billing/v1/costs"

if not CCLOUD_API_KEY or not CCLOUD_API_SECRET:
    raise SystemExit("API Key and Secret are required")

if not CLUSTER_ID:
    raise SystemExit("Cluster ID is required")  

# ----------------------------
# COST API CALL (monthly, as API only allows 1 month maximum)
# ----------------------------
auth = (CCLOUD_API_KEY, CCLOUD_API_SECRET)
items = []

# Iterate month by month
current = start_date
month_count = 0
while current < end_date:
    month_count += 1
    sys.stdout.write(f"Fetching data for month {month_count}: {current.strftime('%Y-%m')}...")
    sys.stdout.flush()
    
    # Calculate month end (first day of next month)
    if current.month == 12:
        month_end = date(current.year + 1, 1, 1)
    else:
        month_end = date(current.year, current.month + 1, 1)
    # Don't exceed end_date
    if month_end > end_date:
        month_end = end_date

    params = {
        "start_date": current.isoformat(),
        "end_date": month_end.isoformat(),
        "page_size": 1000,
    }
    resp = requests.get(BASE_URL, params=params, auth=auth)
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} for {current} - {month_end}", file=__import__('sys').stderr)
        print(resp.text, file=__import__('sys').stderr)
        resp.raise_for_status()
    data = resp.json()
    items.extend(data.get("data", data))

    current = month_end

# ----------------------------
# MONTHLY AGGREGATION
# ----------------------------
gb_write = defaultdict(float)
gb_read = defaultdict(float)
storage_gb = defaultdict(float)

for row in items:
    product = row.get("product")
    line_type = row.get("line_type")
    quantity = row.get("quantity", 0.0)
    resource = row.get("resource", {}) or {}
    resource_id = resource.get("id")
    start = row.get("start_date")  # "2026-01-01"
    
    if product != "KAFKA":
        continue
    if resource_id != CLUSTER_ID:
        continue
    if line_type not in ("KAFKA_NETWORK_WRITE", "KAFKA_NETWORK_READ", "KAFKA_STORAGE"):
        continue
    if not start:
        continue

    month = start[:7]  # "YYYY-MM"
    if line_type == "KAFKA_NETWORK_WRITE":
        gb_write[month] += float(quantity)
    elif line_type == "KAFKA_NETWORK_READ":
        gb_read[month] += float(quantity)
    elif line_type == "KAFKA_STORAGE":
        storage_gb[month] += float(quantity)

# ----------------------------
# CSV OUTPUT (for Excel)
# ----------------------------
print("")
print("Analysis complete! Generating CSV output...")

# Generate filename with cluster ID
output_filename = f"confluent_cost_analysis_{CLUSTER_ID}.csv"

with open(output_filename, 'w') as f:
    f.write("Month,GB_Write,GB_Read,Storage_GB,GB_Total\n")
    
    all_months = sorted(set(gb_write.keys()) | set(gb_read.keys()) | set(storage_gb.keys()))
    for m in all_months:
        gw = gb_write.get(m, 0.0)
        gr = gb_read.get(m, 0.0)
        sg = storage_gb.get(m, 0.0)
        gt = gw + gr
        f.write(f"{m},{gw:.2f},{gr:.2f},{sg:.2f},{gt:.2f}\n")

print(f"CSV saved to: {output_filename}")