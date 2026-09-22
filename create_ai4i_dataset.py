import os
import numpy as np
import pandas as pd

def generate_ai4i_dataset(filepath, num_samples=10000):
    np.random.seed(42)
    
    udis = np.arange(1, num_samples + 1)
    types = np.random.choice(['L', 'M', 'H'], size=num_samples, p=[0.6, 0.3, 0.1])
    
    product_ids = []
    for t in types:
        num = np.random.randint(10000, 99999)
        product_ids.append(f"{t}{num}")
        
    air_temp = np.random.normal(loc=300.0, scale=2.0, size=num_samples)
    air_temp = np.clip(air_temp, 295.0, 304.5)
    
    # Process temp is Air temp + 10.0 to 11.0 + slight noise
    temp_diff_base = np.random.normal(loc=10.7, scale=1.0, size=num_samples)
    process_temp = air_temp + temp_diff_base
    process_temp = np.clip(process_temp, 305.0, 314.0)
    
    # Rotational speed rpm ~ 1200 - 2800
    rpm = np.random.normal(loc=1535.0, scale=180.0, size=num_samples)
    rpm = np.clip(rpm, 1168.0, 2886.0)
    
    # Torque Nm inversely correlated with RPM (Power ~ Torque * RPM)
    # Mean power ~ 6000 W -> Torque ~ (6000 * 60) / (2 * pi * RPM)
    power_target = np.random.normal(loc=6000, scale=1500, size=num_samples)
    torque = (power_target * 60.0) / (2.0 * np.pi * rpm)
    torque = np.clip(torque, 3.8, 76.6)
    
    # Tool wear accumulates 0 to 250 min
    tool_wear = np.random.randint(0, 255, size=num_samples)
    
    # Failure modes initial arrays
    twf = np.zeros(num_samples, dtype=int)
    hdf = np.zeros(num_samples, dtype=int)
    pwf = np.zeros(num_samples, dtype=int)
    osf = np.zeros(num_samples, dtype=int)
    rnf = np.zeros(num_samples, dtype=int)
    
    # Calculate physical thresholds for authentic AI4I dataset failure modes
    for i in range(num_samples):
        # 1. TWF (Tool Wear Failure): Tool wear between 200 and 240 mins
        if 200 <= tool_wear[i] <= 240 and np.random.rand() < 0.25:
            twf[i] = 1
            
        # 2. HDF (Heat Dissipation Failure): Process Temp - Air Temp < 8.6 K and RPM < 1380
        if (process_temp[i] - air_temp[i]) < 8.8 and rpm[i] < 1380:
            hdf[i] = 1
            
        # 3. PWF (Power Failure): Power < 3500 W or > 9000 W
        p = torque[i] * (rpm[i] * 2.0 * np.pi / 60.0)
        if p < 3500 or p > 9000:
            pwf[i] = 1
            
        # 4. OSF (Overstrain Failure): Tool wear * torque > strain threshold
        # Threshold depends on Product Type: L (11000), M (12000), H (13000)
        strain_limit = 11000 if types[i] == 'L' else (12000 if types[i] == 'M' else 13000)
        if (tool_wear[i] * torque[i]) > strain_limit:
            osf[i] = 1
            
        # 5. RNF (Random Failure): 0.1% chance
        if np.random.rand() < 0.001:
            rnf[i] = 1
            
    machine_failure = (twf | hdf | pwf | osf | rnf).astype(int)
    
    df = pd.DataFrame({
        'UDI': udis,
        'Product ID': product_ids,
        'Type': types,
        'Air temperature [K]': np.round(air_temp, 2),
        'Process temperature [K]': np.round(process_temp, 2),
        'Rotational speed [rpm]': np.round(rpm, 0).astype(int),
        'Torque [Nm]': np.round(torque, 2),
        'Tool wear [min]': tool_wear,
        'Machine failure': machine_failure,
        'TWF': twf,
        'HDF': hdf,
        'PWF': pwf,
        'OSF': osf,
        'RNF': rnf
    })
    
    df.to_csv(filepath, index=False)
    print(f"Generated {num_samples} AI4I 2020 dataset samples at {filepath}")
    print(f"Total Machine Failures: {machine_failure.sum()} ({machine_failure.sum()/num_samples*100:.2f}%)")
    print(f"TWF: {twf.sum()}, HDF: {hdf.sum()}, PWF: {pwf.sum()}, OSF: {osf.sum()}, RNF: {rnf.sum()}")

if __name__ == '__main__':
    os.makedirs('app/data', exist_ok=True)
    generate_ai4i_dataset('app/data/ai4i2020.csv')
