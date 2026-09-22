import os
import pandas as pd
import requests
from app.config import settings

def sync_to_supabase():
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY

    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

    print(f"Connecting to Supabase project at {url}...")

    # Load dataset
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ai4i2020.csv')
    if not os.path.exists(data_path):
        print(f"Dataset missing at {data_path}")
        return

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} dataset records for Supabase cloud sync.")

    # 1. Create Organization in Supabase via REST
    org_payload = {
        "id": "org_default_1",
        "name": "Industrial Manufacturing Co.",
        "plan_type": "Enterprise"
    }

    try:
        res_org = requests.post(f"{url}/rest/v1/organizations", json=org_payload, headers=headers)
        print("Organization table status:", res_org.status_code, res_org.text[:150])
    except Exception as e:
        print("Org sync notice:", e)

    # 2. Create Machine Assets in Supabase via REST
    machines_payload = [
        {
            "id": "m1_cnc_mill",
            "org_id": "org_default_1",
            "name": "CNC Milling Machine #1",
            "product_type": "M",
            "description": "3-Axis Vertical CNC Milling Center",
            "asset_criticality": 2.0,
            "failure_cost": 200000.0,
            "pm_cost": 15000.0
        },
        {
            "id": "m2_precision_lathe",
            "org_id": "org_default_1",
            "name": "Precision Lathe #2",
            "product_type": "L",
            "description": "High Precision Turning Lathe",
            "asset_criticality": 1.2,
            "failure_cost": 120000.0,
            "pm_cost": 10000.0
        },
        {
            "id": "m3_heavy_mill",
            "org_id": "org_default_1",
            "name": "Heavy Industrial Mill #3",
            "product_type": "H",
            "description": "Heavy Duty Production Milling Asset",
            "asset_criticality": 2.8,
            "failure_cost": 350000.0,
            "pm_cost": 25000.0
        }
    ]

    try:
        res_m = requests.post(f"{url}/rest/v1/machines", json=machines_payload, headers=headers)
        print("Machines table status:", res_m.status_code, res_m.text[:150])
    except Exception as e:
        print("Machines sync notice:", e)

if __name__ == '__main__':
    sync_to_supabase()
