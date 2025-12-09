import time
import json
import random
import requests
import numpy as np
from itertools import cycle

# ==============================================================================
# KONFIGURASI
# ==============================================================================
API_URL = "http://localhost:8000/predict" 
INTERVAL = 2  # Detik

# Daftar 69 Fitur (Sesuai Scaler)
FEATURE_COLS = [
    'Protocol', 'Flow Duration', 'Tot Fwd Pkts', 'Tot Bwd Pkts',
    'TotLen Fwd Pkts', 'TotLen Bwd Pkts', 'Fwd Pkt Len Max', 'Fwd Pkt Len Min',
    'Fwd Pkt Len Mean', 'Fwd Pkt Len Std', 'Bwd Pkt Len Max', 'Bwd Pkt Len Min',
    'Bwd Pkt Len Mean', 'Bwd Pkt Len Std', 'Flow Byts/s', 'Flow Pkts/s',
    'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min',
    'Fwd IAT Tot', 'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max', 'Fwd IAT Min',
    'Bwd IAT Tot', 'Bwd IAT Mean', 'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min',
    'Fwd PSH Flags', 'Fwd URG Flags', 'Fwd Header Len', 'Bwd Header Len',
    'Fwd Pkts/s', 'Bwd Pkts/s', 'Pkt Len Min', 'Pkt Len Max', 'Pkt Len Mean',
    'Pkt Len Std', 'Pkt Len Var', 'FIN Flag Cnt', 'SYN Flag Cnt', 'RST Flag Cnt',
    'PSH Flag Cnt', 'ACK Flag Cnt', 'URG Flag Cnt', 'CWE Flag Count',
    'ECE Flag Cnt', 'Down/Up Ratio', 'Pkt Size Avg', 'Fwd Seg Size Avg',
    'Bwd Seg Size Avg', 'Subflow Fwd Pkts', 'Subflow Fwd Byts', 'Subflow Bwd Pkts',
    'Subflow Bwd Byts', 'Init Fwd Win Byts', 'Init Bwd Win Byts',
    'Fwd Act Data Pkts', 'Fwd Seg Size Min', 'Active Mean', 'Active Std',
    'Active Max', 'Active Min', 'Idle Mean', 'Idle Std', 'Idle Max', 'Idle Min'
]

# ==============================================================================
# FUNGSI GENERATOR DATA (Raw Data - No Scaler)
# ==============================================================================
def generate_sample(attack_type):
    """
    Membuat data dummy berdasarkan karakteristik serangan agar terlihat agak 'real'.
    Nilai dikembalikan dalam bentuk Raw (belum di-scale).
    """
    
    # --- 1. SETTING DASAR BERDASARKAN TIPE SERANGAN ---
    if attack_type == 'DDoS':
        # Ciri: Port Web, Durasi Pendek, Paket Banyak, IAT Kecil
        flow_duration = random.randint(1000, 500000)
        tot_fwd_pkts = random.randint(100, 5000)
        tot_bwd_pkts = random.randint(0, 100)
        flow_iat_mean = random.uniform(0.1, 10.0) # Cepat
        
    elif attack_type == 'Brute Force':
        # Ciri: Port SSH/FTP, Durasi Sedang, Paket Sedikit tapi konstan
        flow_duration = random.randint(1000000, 5000000)
        tot_fwd_pkts = random.randint(10, 50)
        tot_bwd_pkts = random.randint(10, 40)
        flow_iat_mean = random.uniform(1000, 50000)

    elif attack_type == 'Other': # Malware/Botnet
        # Ciri: High Ports, Komunikasi aneh
        flow_duration = random.randint(50000, 1000000)
        tot_fwd_pkts = random.randint(5, 20)
        tot_bwd_pkts = random.randint(2, 10)
        flow_iat_mean = random.uniform(500, 20000)
        
    else: # Benign (Normal)
        # Ciri: Random Port, Traffic Seimbang
        flow_duration = random.randint(10000, 10000000)
        tot_fwd_pkts = random.randint(5, 100)
        tot_bwd_pkts = random.randint(5, 100)
        flow_iat_mean = random.uniform(1000, 100000)

    # --- 2. POPULASI FITUR ---
    data = {}
    
    data['Protocol'] = random.choice([6, 17]) # TCP/UDP
    data['Flow Duration'] = float(flow_duration)
    data['Tot Fwd Pkts'] = float(tot_fwd_pkts)
    data['Tot Bwd Pkts'] = float(tot_bwd_pkts)
    data['TotLen Fwd Pkts'] = float(tot_fwd_pkts * random.randint(40, 1500))
    data['TotLen Bwd Pkts'] = float(tot_bwd_pkts * random.randint(40, 1500))
    data['Fwd Pkt Len Max'] = float(random.randint(500, 1500))
    data['Fwd Pkt Len Min'] = float(random.randint(0, 60))
    data['Fwd Pkt Len Mean'] = random.uniform(40, 500)
    data['Fwd Pkt Len Std'] = random.uniform(10, 200)
    data['Bwd Pkt Len Max'] = float(random.randint(500, 1500))
    data['Bwd Pkt Len Min'] = float(random.randint(0, 60))
    data['Bwd Pkt Len Mean'] = random.uniform(40, 500)
    data['Bwd Pkt Len Std'] = random.uniform(10, 200)
    data['Flow Byts/s'] = random.uniform(0, 1000000)
    data['Flow Pkts/s'] = random.uniform(0, 50000)
    data['Flow IAT Mean'] = flow_iat_mean
    data['Flow IAT Std'] = flow_iat_mean * 0.5
    data['Flow IAT Max'] = flow_iat_mean * 2
    data['Flow IAT Min'] = flow_iat_mean * 0.1
    data['Fwd IAT Tot'] = float(flow_duration)
    data['Fwd IAT Mean'] = flow_iat_mean
    data['Fwd IAT Std'] = flow_iat_mean * 0.4
    data['Fwd IAT Max'] = flow_iat_mean * 1.5
    data['Fwd IAT Min'] = flow_iat_mean * 0.1
    data['Bwd IAT Tot'] = float(random.randint(0, flow_duration))
    data['Bwd IAT Mean'] = flow_iat_mean
    data['Bwd IAT Std'] = flow_iat_mean * 0.4
    data['Bwd IAT Max'] = flow_iat_mean * 1.5
    data['Bwd IAT Min'] = flow_iat_mean * 0.1
    data['Fwd PSH Flags'] = float(random.choice([0, 1]))
    data['Fwd URG Flags'] = 0.0
    data['Fwd Header Len'] = float(tot_fwd_pkts * 20)
    data['Bwd Header Len'] = float(tot_bwd_pkts * 20)
    data['Fwd Pkts/s'] = random.uniform(0, 1000)
    data['Bwd Pkts/s'] = random.uniform(0, 1000)
    data['Pkt Len Min'] = float(random.randint(0, 40))
    data['Pkt Len Max'] = float(random.randint(1000, 1500))
    data['Pkt Len Mean'] = random.uniform(50, 1000)
    data['Pkt Len Std'] = random.uniform(10, 300)
    data['Pkt Len Var'] = data['Pkt Len Std'] ** 2
    data['FIN Flag Cnt'] = float(random.choice([0, 1]))
    data['SYN Flag Cnt'] = float(random.choice([0, 1]))
    data['RST Flag Cnt'] = float(random.choice([0, 1]))
    data['PSH Flag Cnt'] = float(random.choice([0, 1]))
    data['ACK Flag Cnt'] = float(random.choice([0, 1]))
    data['URG Flag Cnt'] = 0.0
    data['CWE Flag Count'] = 0.0
    data['ECE Flag Cnt'] = 0.0
    data['Down/Up Ratio'] = float(random.randint(0, 2))
    data['Pkt Size Avg'] = data['Pkt Len Mean']
    data['Fwd Seg Size Avg'] = data['Fwd Pkt Len Mean']
    data['Bwd Seg Size Avg'] = data['Bwd Pkt Len Mean']
    data['Subflow Fwd Pkts'] = float(tot_fwd_pkts)
    data['Subflow Fwd Byts'] = data['TotLen Fwd Pkts']
    data['Subflow Bwd Pkts'] = float(tot_bwd_pkts)
    data['Subflow Bwd Byts'] = data['TotLen Bwd Pkts']
    data['Init Fwd Win Byts'] = float(random.randint(1000, 65535))
    data['Init Bwd Win Byts'] = float(random.randint(1000, 65535))
    data['Fwd Act Data Pkts'] = float(random.randint(0, tot_fwd_pkts))
    data['Fwd Seg Size Min'] = 20.0
    data['Active Mean'] = random.uniform(0, 100000)
    data['Active Std'] = 0.0
    data['Active Max'] = data['Active Mean']
    data['Active Min'] = data['Active Mean']
    data['Idle Mean'] = random.uniform(0, 1000000)
    data['Idle Std'] = 0.0
    data['Idle Max'] = data['Idle Mean']
    data['Idle Min'] = data['Idle Mean']

    # Pastikan urutan key sesuai dengan FEATURE_COLS
    ordered_data = {k: data.get(k, 0) for k in FEATURE_COLS}
    return ordered_data

# ==============================================================================
# MAIN LOOP SIMULASI
# ==============================================================================
if __name__ == "__main__":
    print(f"[*] Traffic Simulator Started...")
    print(f"[*] Target API: {API_URL}")
    print(f"[*] Interval: {INTERVAL} seconds")
    print("="*60)

    # Cycle agar kita mengirim jenis serangan secara bergantian
    attack_cycle = cycle(['Benign', 'DDoS', 'Brute Force', 'Benign', 'Other'])

    try:
        while True:
            # 1. Pilih Tipe Serangan
            current_attack = next(attack_cycle)
            
            # 2. Generate Data (Raw - No Scaling)
            payload = generate_sample(current_attack)
            
            # 3. Kirim ke API Endpoint
            try:
                try:
                    response = requests.post(API_URL, json=payload, timeout=2)
                    status_code = response.status_code
                    if status_code == 200:
                        server_msg = response.json()
                        pred_class = server_msg.get('prediction_class')
                        conf = server_msg.get('confidence')
                        status_str = f"[{status_code}] OK -> {pred_class} ({conf:.2f})"
                    else:
                        status_str = f"[{status_code}] Error"
                        server_msg = response.text
                except requests.exceptions.RequestException:
                    status_str = "[FAILED CONNECTION]"
                    server_msg = "Server Not Reachable"

                # 4. Logging di Terminal
                print(f"\n[OUTGOING] Type: {current_attack.upper()}")
                print(f"   -> Flow Dur: {payload['Flow Duration']:.1f}")
                print(f"   -> Tot Fwd Pkts: {payload['Tot Fwd Pkts']}")
                print(f"   -> API Status: {status_str}")
                
            except Exception as e:
                print(f"[ERROR] {e}")

            # 5. Tunggu
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("\n[!] Simulation Stopped by User.")