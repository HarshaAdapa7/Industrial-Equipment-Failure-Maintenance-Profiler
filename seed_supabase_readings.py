import os
import pandas as pd
import psycopg2
import json
import uuid
from datetime import datetime, timedelta
from app.ml.model_loader import get_model_service
from app.ml.shap_explainer import get_shap_service

conn_str = "postgresql://postgres.frfkburreisufcdkqpji:Harsha%409515445632@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require"

def seed_telemetry_readings():
    print("Loading dataset and initializing ML models...")
    model_service = get_model_service()
    shap_service = get_shap_service()

    data_path = os.path.join(os.path.dirname(__file__), 'app', 'data', 'ai4i2020.csv')
    df = pd.read_csv(data_path)

    # Pick 50 sample readings from dataset to seed initial time-series curves
    sample_df = df.iloc[100:150].copy()

    conn = psycopg2.connect(conn_str)
    conn.autocommit = True
    cursor = conn.cursor()

    machine_ids = ['m1_cnc_mill', 'm2_precision_lathe', 'm3_heavy_mill']
    base_time = datetime.utcnow() - timedelta(minutes=50)

    print(f"Seeding 50 telemetry readings and ML predictions for each machine into Supabase Cloud PostgreSQL...")

    for m_id in machine_ids:
        for idx, (_, row) in enumerate(sample_df.iterrows()):
            reading_time = base_time + timedelta(minutes=idx)
            reading_id = str(uuid.uuid4())
            pred_id = str(uuid.uuid4())

            air_temp = float(row['Air temperature [K]'])
            process_temp = float(row['Process temperature [K]'])
            rpm = float(row['Rotational speed [rpm]'])
            torque = float(row['Torque [Nm]'])
            tool_wear = float(row['Tool wear [min]'])
            prod_type = str(row['Type'])

            reading_dict = {
                'air_temp': air_temp,
                'process_temp': process_temp,
                'rpm': rpm,
                'torque': torque,
                'tool_wear': tool_wear,
                'product_type': prod_type
            }

            # Predict via ML Pipeline
            pred_res = model_service.predict_reading(reading_dict)
            shap_res = shap_service.explain_prediction(reading_dict)

            # Insert Sensor Reading
            cursor.execute("""
                INSERT INTO public.sensor_readings (id, machine_id, timestamp, air_temp, process_temp, rpm, torque, tool_wear, derived_features)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                reading_id, m_id, reading_time, air_temp, process_temp, rpm, torque, tool_wear,
                json.dumps(pred_res['features'])
            ))

            # Insert Prediction
            cursor.execute("""
                INSERT INTO public.predictions (id, machine_id, timestamp, any_failure, risk_score, health_score, anomaly_score, label_probs, shap_values)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                pred_id, m_id, reading_time, pred_res['any_failure'], pred_res['risk_score'], pred_res['health_score'],
                pred_res['anomaly_score'], json.dumps(pred_res['label_probs']), json.dumps(shap_res.get('feature_attributions', []))
            ))

    print("SUCCESS! Initial telemetry time-series curves seeded into Supabase Cloud Database!")
    cursor.close()
    conn.close()

if __name__ == '__main__':
    seed_telemetry_readings()
