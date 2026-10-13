# SPICEE 🌿
**Aplikasi manajemen keuangan dan asisten AI untuk UMKM rempah & produk khas Indonesia**

SPICEE membantu pelaku UMKM mencatat keuangan, menghitung Harga Pokok Produksi (HPP), dan berkonsultasi dengan asisten AI seputar rempah, jamu, PIRT, dan BPOM.

---

## Fitur

| Fitur | Deskripsi |
|---|---|
| **Keuangan** | Catat pemasukan & pengeluaran, lihat ringkasan laba, insight AI mingguan |
| **HPP** | Hitung Harga Pokok Produksi dan saran harga jual otomatis |
| **Chat AI** | Asisten SPICEE berbasis Gemini — seputar rempah, jamu, PIRT, BPOM |

---

## Arsitektur

```
Frontend (Vue 3 + Tailwind CSS)
        |
        v HTTP REST
Backend FastAPI :8000
        |               |
        v               v
   Supabase DB     Langflow :7860
   (PostgreSQL)    (Gemini AI)
```

---

## Tech Stack

- **Frontend:** Vue 3 (CDN), Tailwind CSS (CDN) — single file `frontend/HACK.html`
- **Backend:** FastAPI (Python 3.12), Uvicorn
- **Database:** Supabase (PostgreSQL)
- **AI:** Langflow + Google Gemini (`gemini-flash-lite-latest`)

---

## Cara Menjalankan

### Prasyarat
- Python 3.12+
- Langflow berjalan lokal di port `7860`
- Akun Supabase dengan tabel yang sudah dibuat (lihat `backend/schema.sql`)

### 1. Clone & Setup Backend

```powershell
git clone https://github.com/faidzabdl/spicee.git
cd spicee/backend

python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
# Edit .env dengan kredensial Supabase dan Langflow kamu
```

### 2. Setup Database

Jalankan SQL di `backend/schema.sql` melalui Supabase Dashboard > SQL Editor.

Opsional — insert data demo:
```powershell
.\venv\Scripts\python.exe seed.py
.\venv\Scripts\python.exe seed_extended.py
```

### 3. Jalankan Semua Service

```powershell
.\start.ps1
```

### 4. Akses Aplikasi

| Service | URL |
|---|---|
| Frontend | http://localhost:3000/HACK.html |
| API Docs | http://localhost:8000/docs |
| Langflow | http://127.0.0.1:7860 |

---

## API Endpoints

| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/` | Health check |
| POST | `/transaksi` | Tambah transaksi baru |
| GET | `/transaksi` | Daftar transaksi (dengan filter) |
| GET | `/ringkasan` | Ringkasan keuangan + insight AI |
| POST | `/hpp` | Hitung HPP dan saran harga jual |
| POST | `/chat` | Chat dengan asisten AI SPICEE |

---

## Environment Variables

Salin `backend/.env.example` ke `backend/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
LANGFLOW_BASE_URL=http://127.0.0.1:7860
LANGFLOW_API_KEY=your-langflow-api-key
LANGFLOW_CHAT_FLOW_ID=your-chat-flow-id
LANGFLOW_DIAGNOSIS_FLOW_ID=your-diagnosis-flow-id
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Menjalankan Tests

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest test_api.py -v
```

---

## Struktur Proyek

```
spicee/
├── frontend/
│   └── HACK.html
├── backend/
│   ├── main.py
│   ├── db.py
│   ├── models.py
│   ├── langflow_client.py
│   ├── routers/
│   │   ├── transaksi.py
│   │   ├── hpp.py
│   │   └── chat.py
│   ├── schema.sql
│   ├── seed.py
│   ├── seed_extended.py
│   ├── requirements.txt
│   └── .env.example
├── start.ps1
├── stop.ps1
└── .gitignore
```
