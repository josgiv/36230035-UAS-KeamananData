# Network Intrusion Detection System (IDS) - Based on CSE-CIC-IDS2018

**Ujian Akhir Semester (UAS) - Keamanan Data**

| Identitas | Detail |
| :--- | :--- |
| **Nama** | **Josia Given Santoso** |
| **NIM** | **36230035** |
| **Dosen Pengampu** | **Alaniah Nisrina, B.Eng., M.Eng.** |

---

## � Deskripsi Proyek
Sistem ini adalah implementasi **Intrusion Detection System (IDS)** Berbasis Anomaly Detection menggunakan Machine Learning. Sistem dirancang secara modular dengan arsitektur modern yang memisahkan Backend, Frontend, dan Data Simulation.

### Fitur Utama
1.  **Backend API (FastAPI)**: Server inferensi berkinerja tinggi yang memuat model XGBoost.
2.  **Modern Dashboard (Next.js 14 + Shadcn UI)**: Antarmuka visual yang real-time, responsif, dan estetis untuk memantau lalu lintas jaringan.
3.  **Real-time Simulation**: Skrip Python yang mensimulasikan karakteristik serangan (DDoS, Brute Force, Botnet) untuk pengujian langsung.
4.  **Reproducibility**: Dikemas dengan panduan instalasi lengkap untuk memastikan dapat dijalankan di lingkungan apa pun.

---

## 📁 Struktur Direktori Lengkap

Berikut adalah struktur file proyek ini:

```text
36230035_KeamananData_UAS/
├── .gitignore
├── feature_list.txt            # Daftar 69 fitur yang digunakan model
├── inspect_models.py           # Script utilitas inspeksi model
├── main.py                     # 🚀 LAUNCHER UTAMA (Jalankan ini!)
├── README.md                   # Dokumentasi ini
├── requirements.txt            # Dependensi Python
├── src/
│   ├── app/
│   │   ├── __pycache__/
│   │   ├── api.py              # Backend FastAPI (Port 8000)
│   │   ├── dummy_data_stream.py# Simulator Trafik (Client)
│   │   ├── model_loader.py     # Logic Loading Model & Scaler
│   │   ├── type_definitions.py # Skema Validasi Data (Pydantic)
│   │   └── web/
│   │       ├── streamlit.py    # (Legacy/Deprecated) Dashboard lama
│   │       └── ddos-protection-full/   # 🌟 DASHBOARD UTAMA (Next.js)
│   │           ├── src/
│   │           │   ├── app/
│   │           │   │   ├── globals.css     # Styling (Tailwind v3)
│   │           │   │   ├── layout.tsx
│   │           │   │   └── page.tsx        # Logic Dashboard
│   │           │   ├── components/ui/      # Komponen Shadcn
│   │           │   └── lib/utils.ts
│   │           ├── public/
│   │           ├── .gitignore
│   │           ├── next.config.ts
│   │           ├── package.json
│   │           ├── postcss.config.mjs
│   │           ├── tailwind.config.ts
│   │           └── tsconfig.json
│   └── models_dev/
│       ├── datasets/           
│       ├── models/             # Artefak Model Siap Pakai
│       │   ├── decision_tree.joblib
│       │   ├── logistic_regression.joblib
│       │   ├── random_forest.joblib
│       │   ├── scaler.joblib   # Scaler (StandardScaler)
│       │   └── xgboost.joblib  # Model Utama (XGBoost)
│       └── notebooks/
│           └── 36230035_KeamananData_UAS_Final.ipynb  # Notebook Eksperimen & Training
```

---

## 🛠️ Panduan Instalasi & Reproducibility (Wajib Dibaca)

Ikuti langkah-langkah ini secara berurutan untuk menjalankan sistem.

### 1. Prasyarat
- **Python 3.10+**
- **Node.js 18+** & **nam**
- **Internet Acccess** (untuk mengunduh library)

### 2. Setup Environment Python
Install seluruh library Python yang dibutuhkan dari root directory:

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Frontend (Next.js)
Anda **WAJIB** melakukan instalasi di folder web terlebih dahulu agar dashboard bisa berjalan.

```bash
# 1. Masuk ke direktori web
cd src/app/web/ddos-protection-full

# 2. Install dependencies node modules
npm install

# 3. Kembali ke root directory
cd ../../../..
```

*(Pastikan kembali ke folder `36230035_KeamananData_UAS` sebelum lanjut)*

### 4. Menjalankan Sistem
Cukup jalankan satu perintah ini. Script ini akan menyalakan API, Dashboard, dan Simulator sekaligus.

```bash
python main.py
```

Tunggu beberapa detik hingga muncul pesan `[SUCCESS] All Systems Operational`.

---

## 🖥️ Akses Aplikasi

| Komponen | URL / Port | Deskripsi |
| :--- | :--- | :--- |
| **Web Dashboard** | **http://localhost:3000** | Antarmuka monitoring utama. Buka di browser. |
| **API Server** | http://localhost:8000 | Backend server. Endpoint `/docs` tersedia untuk Swagger UI. |
| **Traffic Simulator** | (Background Process) | Berjalan di terminal, mencetak log pengiriman data. |

---

## � Dataset (Sumber Data)

Model dilatih menggunakan dataset **CSE-CIC-IDS2018**.
Jika Anda ingin menjalankan ulang Notebook pelatihan (`src/models_dev/notebooks/36230035_KeamananData_UAS_Final.ipynb`), silakan unduh dataset dari Kaggle:

1.  **URL**: [Kaggle CSE-CIC-IDS2018](https://www.kaggle.com/datasets/soleshuc/cse-cic-ids2018)
2.  **Instruksi**:
    - Download file, ekstrak.
    - Letakkan file `.parquet` atau `.csv` di folder `src/models_dev/datasets/`.
    - Sesuaikan path di notebook jika perlu.

*Catatan: Sistem ini sudah menyertakan model terlatih (`xgboost.joblib`), jadi Anda TIDAK perlu mengunduh dataset untuk sekadar menjalankan aplikasi demo.*

---

## � Catatan Penting
- **Port Conflict**: Jika port 3000 atau 8000 sedang dipakai, matikan aplikasi lain atau edit `main.py`.
- **Tailwind Version**: Dashboard ini menggunakan Tailwind v3 agar kompatibel dengan Shadcn UI. Jangan di-upgrade ke v4 manual.
- **Model Input**: Model menerima 69 fitur spesifik (lihat `feature_list.txt`).

---
**Tugas UAS Keamanan Data 2025**

| Identitas | Detail |
| :--- | :--- |
| **Nama** | **Josia Given Santoso** |
| **NIM** | **36230035** |
| **Dosen Pengampu** | **Alaniah Nisrina, B.Eng., M.Eng.** |
