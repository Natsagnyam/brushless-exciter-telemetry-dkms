import numpy as np
from sklearn.ensemble import IsolationForest

def generate_telemetry_data(n_samples=1000):
    """Generates synthetic normal telemetry data (voltage & frequency) 
       with a few injected anomalies (failures)."""
    np.random.seed(42)
    
    # Normal operating data: Voltage around 230V, Frequency around 50Hz
    voltage_normal = np.random.normal(loc=230.0, scale=1.5, size=n_samples)
    frequency_normal = np.random.normal(loc=50.0, scale=0.2, size=n_samples)
    
    normal_data = np.column_stack((voltage_normal, frequency_normal))
    
    # Inject a few synthetic anomalies (e.g., voltage sag/spike, frequency drop)
    anomalies = np.array([
        [215.0, 48.5],  # Voltage sag & frequency drop
        [245.2, 51.1],  # Voltage spike
        [228.1, 45.0],  # Severe frequency crash
        [239.8, 52.0]   # Overfrequency spike
    ])
    
    # Combine normal data and anomalies
    dataset = np.vstack((normal_data, anomalies))
    return dataset

def main():
    print("[*] Generating synthetic power telemetry dataset...")
    data = generate_telemetry_data(n_samples=1000)
    
    print("[*] Training Isolation Forest anomaly detection model...")
    # contamination = estimated proportion of outliers in the data (~0.5%)
    model = IsolationForest(contamination=0.005, random_state=42)
    model.fit(data)
    
    # Predict anomalies (-1 for anomaly, 1 for normal)
    predictions = model.predict(data)
    
    # Extract anomaly indices
    anomaly_indices = np.where(predictions == -1)[0]
    
    print(f"\n[+] Analysis Complete. Total samples analyzed: {len(data)}")
    print(f"[+] Anomalies detected: {len(anomaly_indices)}")
    
    print("\n--- Detected Anomalous Telemetry Points ---")
    for idx in anomaly_indices:
        volt, freq = data[idx]
        print(f"Sample Index {idx:4d} -> Voltage: {volt:6.2f} V, Frequency: {freq:5.2f} Hz [ANOMALY]")

if __name__ == "__main__":
    main()