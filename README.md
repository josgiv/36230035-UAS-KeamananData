# Network Intrusion Detection System (IDS) - Based on CSE-CIC-IDS2018

**Ujian Akhir Semester (UAS) - Keamanan Data**

| Identitas | Detail |
| :--- | :--- |
| **Nama** | **Josia Given Santoso** |
| **NIM** | **36230035** |
| **Dosen Pengampu** | **Alaniah Nisrina, B.Eng., M.Eng.** |

---

## 🛡️ Deskripsi Proyek
Sistem ini adalah implementasi **Intrusion Detection System (IDS)** Berbasis Anomaly Detection menggunakan Machine Learning. Sistem dirancang secara modular dengan arsitektur modern yang memisahkan Backend, Frontend, dan Data Simulation.

### Fitur Utama
1.  **Dual Frontend Architecture**:
    *   **Primary (Next.js 14 + Shadcn UI)**: Antarmuka visual state-of-the-art dengan animasi Framer Motion, Recharts, dan desain responsif.
    *   **Fallback (Streamlit)**: Dashboard Python native yang berfungsi penuh sebagai backup otomatis jika Node.js tidak tersedia.
2.  **Backend API (FastAPI)**: Server inferensi berkinerja tinggi yang memuat model XGBoost.
3.  **Real-time Attack Simulation**: Engine simulasi serangan yang secara acak mengenerate tindakan mitigasi (Blocking, Throttling, Quarantine) berdasarkan prediksi model.
4.  **Auto-Recovery & Fallback**: Script launcher cerdas (`main.py`) yang mendeteksi lingkungan sistem dan memilih mode operasi yang sesuai.

---

## 📁 Struktur Direktori Lengkap

Berikut adalah struktur file proyek ini:

```text
36230035_KeamananData_UAS/
├── .gitignore
├── feature_list.txt            # Daftar 69 fitur yang digunakan model
├── inspect_models.py           # Script utilitas inspeksi model
├── main.py                     # 🚀 LAUNCHER UTAMA (Integrated Launcher)
├── README.md                   # Dokumentasi ini
├── requirements.txt            # Dependensi Python
├── src/
│   ├── app/
│   │   ├── __pycache__/
│   │   ├── api.py              # Backend FastAPI (Port 8000)
│   │   ├── model_loader.py     # Logic Loading Model & Scaler
│   │   ├── type_definitions.py # Skema Validasi Data (Pydantic)
│   │   └── web/
│   │       ├── streamlit.py    # 🛡️ STREAMLIT DASHBOARD (Fallback UI)
│   │       └── ddos-protection-full/   # 🌟 NEXT.JS DASHBOARD (Primary UI)
│   │           ├── src/
│   │           │   ├── app/
│   │           │   │   ├── globals.css     # Styling
│   │           │   │   └── page.tsx        # Logic Dashboard (React)
│   │           │   ├── components/ui/      # Komponen Shadcn
│   │           │   └── ...
│   └── models_dev/
│       ├── datasets/           
│       ├── models/             # Artefak Model Siap Pakai
│       │   ├── scaler.joblib   # Scaler (StandardScaler)
│       │   └── xgboost.joblib  # Model Utama (XGBoost)
│       └── notebooks/
│           └── 36230035_KeamananData_UAS_Final.ipynb  # Notebook Eksperimen
```

---

## 🛠️ Panduan Instalasi & Reproducibility (Wajib Dibaca)

Sistem ini memiliki mekanisme **Automatic Fallback**. Artinya, sistem akan berusaha menjalankan versi terbaik (Next.js), namun jika gagal, akan otomatis beralih ke versi aman (Streamlit).

### 1. Prasyarat
- **Python 3.10+** (Wajib)
- **Node.js 18+** (Opsional - Jika ada, tampilan Next.js akan aktif)

### 2. Setup Environment Python
Install seluruh library Python yang dibutuhkan dari root directory:

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Frontend (Opsional tapi Disarankan)
Jika Anda memiliki Node.js, lakukan langkah ini agar tampilan UI maksimal:

```bash
# 1. Masuk ke direktori web
cd src/app/web/ddos-protection-full

# 2. Install dependencies node modules
npm install

# 3. Kembali ke root directory
cd ../../../..
```

---

## 🚀 Cara Menjalankan Sistem
Cukup jalankan satu perintah ini. Launcher cerdas kami akan menangani sisanya.

```bash
python main.py
```

### Apa yang terjadi saat perintah ini dijalankan?
1.  **API Check**: Backend FastAPI dinyalakan pada port 8000.
2.  **Environment Check**: Script mengecek apakah `npm` terinstall di komputer Anda.
    *   **Kondisi A (Node.js Ada)**: Menjalankan Streamlit (Port 8501) DAN Next.js (Port 3000). Anda bisa memilih antarmuka yang disukai.
    *   **Kondisi B (Node.js Tidak Ada / Error)**: Menjalankan Streamlit (Port 8501) saja.
3.  **Logs**: Terminal akan menampilkan status live dari semua layanan.

---

## 🖥️ Akses Aplikasi

Setelah status `[SUCCESS]`, akses dashboard melalui:

| Komponen | Priority | URL | Fitur |
| :--- | :--- | :--- | :--- |
| **Next.js Dashboard** | Utama | **http://localhost:3000** | Animasi framer-motion, UI Premium, Interaktivitas Penuh. |
| **Streamlit Dashboard** | Fallback | **http://localhost:8501** | UI Native Python, Ringan, Logic Mirroring 100%. |
| **API Server** | Backend | http://localhost:8000 | Endpoint inferensi utama. |
| **API Health** | Monitor | http://localhost:8000/health | Cek status model loading. |

---

## 🧠 Detail Teknis: Streamlit Mirroring
Sebagai bagian dari pembaruan ini, `streamlit.py` telah ditulis ulang sepenuhnya untuk **meniru 100% logika dan tampilan** dari `page.tsx` (Next.js).

*   **Identitas Header**: Ditambahkan header custom HTML/CSS dengan detail Nama/NIM.
*   **Visual Similarity**: Menggunakan custom CSS injection untuk meniru tema "Dark Slate" dari Shadcn UI.
*   **Logic Parity**:
    *   Simulasi mitigasi ancaman (Block/Throttle/Quarantine) diporting dari TypeScript ke Python.
    *   Metrik (Total Analyzed, Benign, Threat Rate) dihitung dengan rumus identik.
    *   Visualisasi grafik (Area Chart & Pie Chart) menggunakan Plotly untuk meniru Recharts.
*   **Realtime**: Menggunakan `st.rerun()` loop untuk update otomatis setiap 2 detik.

---

**Tugas UAS Keamanan Data 2025**
| Identitas | Detail |
| :--- | :--- |
| **Nama** | **Josia Given Santoso** |
| **NIM** | **36230035** |
| **Dosen Pengampu** | **Alaniah Nisrina, B.Eng., M.Eng.** |
