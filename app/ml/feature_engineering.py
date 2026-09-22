import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    'air_temp', 'process_temp', 'rpm', 'torque', 'tool_wear',
    'temp_diff', 'angular_velocity', 'power', 'wear_torque',
    'type_L', 'type_M', 'type_H'
]

TARGET_FAILURE_MODES = ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']

def compute_physics_features(df_or_dict):
    """
    Computes domain physics features from raw sensor telemetry.
    Accepts pandas DataFrame or dict/Pydantic object.
    """
    if isinstance(df_or_dict, dict):
        df = pd.DataFrame([df_or_dict])
        is_dict = True
    else:
        df = df_or_dict.copy()
        is_dict = False

    # Extract base columns (handle column name mappings from AI4I or API schemas)
    air_temp = df['Air temperature [K]'] if 'Air temperature [K]' in df.columns else df.get('air_temp', 300.0)
    process_temp = df['Process temperature [K]'] if 'Process temperature [K]' in df.columns else df.get('process_temp', 310.0)
    rpm = df['Rotational speed [rpm]'] if 'Rotational speed [rpm]' in df.columns else df.get('rpm', 1500.0)
    torque = df['Torque [Nm]'] if 'Torque [Nm]' in df.columns else df.get('torque', 40.0)
    tool_wear = df['Tool wear [min]'] if 'Tool wear [min]' in df.columns else df.get('tool_wear', 100.0)
    prod_type = df['Type'] if 'Type' in df.columns else df.get('product_type', 'M')

    # Convert to numeric float arrays
    air_temp = pd.to_numeric(air_temp, errors='coerce').fillna(300.0)
    process_temp = pd.to_numeric(process_temp, errors='coerce').fillna(310.0)
    rpm = pd.to_numeric(rpm, errors='coerce').fillna(1500.0)
    torque = pd.to_numeric(torque, errors='coerce').fillna(40.0)
    tool_wear = pd.to_numeric(tool_wear, errors='coerce').fillna(100.0)

    # Physics feature calculations
    temp_diff = process_temp - air_temp
    angular_velocity = rpm * (2.0 * np.pi / 60.0)  # rad/s
    power = torque * angular_velocity              # Watts
    wear_torque = tool_wear * torque              # Overstrain indicator

    # Product type one-hot encoding
    if isinstance(prod_type, pd.Series):
        type_L = (prod_type == 'L').astype(float)
        type_M = (prod_type == 'M').astype(float)
        type_H = (prod_type == 'H').astype(float)
    else:
        pt = str(prod_type).upper()
        type_L = 1.0 if pt == 'L' else 0.0
        type_M = 1.0 if pt == 'M' else 0.0
        type_H = 1.0 if pt == 'H' else 0.0

    features_df = pd.DataFrame({
        'air_temp': air_temp,
        'process_temp': process_temp,
        'rpm': rpm,
        'torque': torque,
        'tool_wear': tool_wear,
        'temp_diff': temp_diff,
        'angular_velocity': angular_velocity,
        'power': power,
        'wear_torque': wear_torque,
        'type_L': type_L,
        'type_M': type_M,
        'type_H': type_H
    })

    return features_df
