# SPICEE Backend — Implementation Plan

## Overview

SPICEE adalah backend untuk aplikasi UMKM rempah/produk khas Indonesia.
Stack: **FastAPI (Python)** + **Supabase (supabase-py)** + **Langflow (lokal, port 7860)** + **Google Gemini** (via Langflow).

Scope plan ini: Backend API, Supabase schema, Langflow flow, testing, lalu deployment.
Frontend (React + Tailwind) dikerjakan tim lain dan akan diintegrasikan setelah backend stabil.

**Urutan prioritas:** Backend FastAPI → Supabase → Langflow/Gemini → Deploy

## Keputusan Desain yang Sudah Dikonfirmasi

| # | Topik | Keputusan |
|---|-------|-----------|
| 1 | Supabase project | Sudah dibuat — project ID `lzuksiztjaxdtgisdmie` |
| 2 | Langflow Flow | **3 flow sudah siap** — lihat tabel flow di bawah |
| 3 | Knowledge base | Disematkan langsung di system prompt flow Chat (tidak pakai RAG terpisah) |
| 4 | CORS origins | `localhost:3000` dan `localhost:5173` — user akan memberitahu jika ada tambahan |

## Langflow Flows yang Sudah Siap

| Flow | ID | Dipakai di | Status |
|------|----|------------|--------|
| SPICEE Chat Assistant | `3fe1e5e9-15ee-4709-a3d2-02efeb2d9de8` | `POST /chat` | ✅ Dibuat & tested |
| UMKM Extraction | `a7040b70-6599-42e9-99de-5ea8fb35e7b6` | Post-MVP: input transaksi via chat | ✅ Existing, tested |
| UMKM Diagnosis | `5c85ca63-570f-4069-ab1f-e972c3732762` | `GET /ringkasan` — field `insight` | ✅ Existing |

**SPICEE Chat Assistant** menggunakan model `gemini-flash-lite-latest` via Google Generative AI.
System prompt sudah dikonfigurasi dengan persona empati + PIRT/BPOM reminder. Tested dan menghasilkan respons berkualitas.

---

## Arsitektur

```
Frontend React + Tailwind (tim lain)
  Halaman: Keuangan | HPP | Chat
        │
        ▼ HTTP (CORS enabled)
  FastAPI Backend
  ├── GET  /              (health check)
  ├── POST /transaksi
  ├── GET  /transaksi
  ├── GET  /ringkasan     → opsional: kirim data ke UMKM Diagnosis flow untuk insight
  ├── POST /hpp
  └── POST /chat          → SPICEE Chat Assistant flow (Gemini)
        │                        │
        ▼                        ▼
   Supabase DB             Langflow :7860
   ├── produk              ├── SPICEE Chat Assistant  (3fe1e5e9)
   ├── transaksi           ├── UMKM Diagnosis         (5c85ca63)
   └── chats               └── UMKM Extraction        (a7040b70) ← post-MVP
```

---

## 1. Supabase Schema

### Tabel `produk`

| Kolom       | Tipe      | Keterangan                       |
|-------------|-----------|----------------------------------|
| id          | uuid PK   | default gen_random_uuid()        |
| nama        | text      | nama produk                      |
| kategori    | text      | rempah / jamu / olahan / lainnya |
| satuan      | text      | botol / gram / pcs / dll         |
| harga_jual  | numeric   | harga jual saat ini              |
| created_at  | timestamp | default now()                    |

### Tabel `transaksi`

| Kolom       | Tipe      | Keterangan                                    |
|-------------|-----------|-----------------------------------------------|
| id          | uuid PK   | default gen_random_uuid()                     |
| tanggal     | date      | tanggal transaksi                             |
| jenis       | text      | masuk / keluar                                |
| kategori    | text      | penjualan / bahan_baku / operasional / dll    |
| akun        | text      | usaha / pribadi                               |
| keterangan  | text      | deskripsi bebas                               |
| jumlah      | numeric   | nominal rupiah                                |
| produk_id   | uuid FK   | nullable, ref ke produk.id                    |
| created_at  | timestamp | default now()                                 |

### Tabel `chats`

| Kolom      | Tipe      | Keterangan                 |
|------------|-----------|----------------------------|
| id         | uuid PK   | default gen_random_uuid()  |
| session_id | text      | identifier sesi percakapan |
| role       | text      | user / assistant           |
| message    | text      | isi pesan                  |
| created_at | timestamp | default now()              |

**Relasi:** `transaksi.produk_id` → `produk.id` (nullable FK)

---

## 2. Endpoint API

### GET `/`
Health check.

**Response:** `200` `{ "status": "ok", "app": "SPICEE API" }`

---

### POST `/transaksi`
Tambah transaksi baru.

**Request body:**
```json
{
  "tanggal": "2025-01-15",
  "jenis": "masuk",
  "kategori": "penjualan",
  "akun": "usaha",
  "keterangan": "Jual jamu kunyit 10 botol",
  "jumlah": 80000,
  "produk_id": null
}
```
**Response:** `201` + objek transaksi yang dibuat.

---

### GET `/transaksi`
Daftar transaksi dengan filter opsional.

**Query params:**
- `akun` — `usaha` / `pribadi`
- `kategori` — filter kategori
- `jenis` — `masuk` / `keluar`
- `dari` — tanggal mulai (YYYY-MM-DD)
- `sampai` — tanggal akhir (YYYY-MM-DD)

**Response:** `200` + array transaksi, diurutkan `created_at` DESC.

---

### GET `/ringkasan`
Ringkasan keuangan — digunakan oleh 3 kartu di halaman Keuangan frontend.

**Query params:** `akun` (opsional), `dari`, `sampai`

**Response:**
```json
{
  "total_masuk": 500000,
  "total_keluar": 200000,
  "laba": 300000
}
```

---

### POST `/hpp`
Hitung Harga Pokok Produksi — digunakan halaman HPP frontend.

**Request body:**
```json
{
  "nama_produk": "Jamu Kunyit",
  "bahan": [
    { "nama": "Kunyit", "jumlah": 200, "satuan": "gram", "harga_per_satuan": 5000 },
    { "nama": "Gula", "jumlah": 100, "satuan": "gram", "harga_per_satuan": 2000 }
  ],
  "margin_persen": 30
}
```
**Response:**
```json
{
  "nama_produk": "Jamu Kunyit",
  "total_hpp": 11000,
  "saran_harga_jual": 14300,
  "rincian_bahan": [
    { "nama": "Kunyit", "jumlah": 200, "satuan": "gram", "harga_per_satuan": 5000, "subtotal": 1000000 },
    { "nama": "Gula", "jumlah": 100, "satuan": "gram", "harga_per_satuan": 2000, "subtotal": 200000 }
  ]
}
```
Formula: `saran_harga_jual = total_hpp / (1 - margin_persen / 100)`

---

### POST `/chat`
Kirim pesan ke AI via Langflow — digunakan halaman Chat frontend (termasuk quick questions).

**Request body:**
```json
{
  "session_id": "user-abc-123",
  "message": "Apa manfaat jahe merah untuk jamu?"
}
```
**Response:**
```json
{
  "session_id": "user-abc-123",
  "reply": "Jahe merah memiliki kandungan gingerol yang lebih tinggi...",
  "saved": true
}
```
Jika Langflow error → return mock reply, `saved: false`.

---

## 3. Arsitektur Langflow

### Flow SPICEE Chat Assistant — sudah live ✅

```
ChatInput (session_id + message)
      │
      ▼
 Prompt Template (system prompt persona SPICEE)
      │
      ▼
 Language Model (gemini-flash-lite-latest via Google Generative AI)
      │
      ▼
 ChatOutput (reply text)
```

**Tidak menggunakan RAG/Vector Store terpisah** — knowledge tentang rempah, PIRT, BPOM, dan HPP
disematkan langsung di system prompt. Cukup untuk scope hackathon dan sudah terbukti menghasilkan
respons berkualitas tinggi.

### System Prompt yang Sudah Dikonfigurasi
Persona: empati, praktis, Bahasa Indonesia, relevan UMKM.
Topik: jahe, jahe merah, kunyit, temulawak, sereh, kayu manis, lada, cengkeh, vanili, kelor, kencur, lengkuas,
cara pengolahan, jamu, HPP, PIRT, BPOM, tips bisnis UMKM.
Rule: selalu ingatkan PIRT/BPOM bila konteks produksi/penjualan.

### Flow UMKM Diagnosis — dipakai untuk insight ringkasan
Input: data keuangan (total masuk, keluar, laba, produk terlaris).
Output: insight dan rekomendasi tindakan untuk UMKM.
Diintegrasikan ke `GET /ringkasan` sebagai field opsional `insight`.

### Flow UMKM Extraction — post-MVP
Input: teks natural bahasa Indonesia.
Output: JSON terstruktur `{ entry_type, item_name, amount, quantity, unit, notes }`.
**Tidak dipakai di MVP.** Akan digunakan setelah core backend stabil untuk fitur input transaksi via chat.

### Fallback Mock Response (untuk demo)
Jika Langflow tidak bisa dihubungi:
```
"Maaf, asisten SPICEE sedang tidak tersedia. Silakan coba lagi dalam beberapa saat."
```

---

## 4. Integrasi Backend ↔ Langflow

FastAPI memanggil Langflow via HTTP API endpoint `/api/v1/run/{flow_id}`.

### POST /chat → SPICEE Chat Assistant
```
FastAPI POST /chat
    │
    ├── Kirim POST ke {LANGFLOW_BASE_URL}/api/v1/run/{LANGFLOW_CHAT_FLOW_ID}
    │       headers: { x-api-key: LANGFLOW_API_KEY }
    │       body: { "input_value": message, "session_id": session_id }
    │       timeout: 30 detik
    │
    ├── Jika sukses:
    │       └── Ambil reply dari outputs[0].outputs[0].results.message.text
    │
    ├── Jika timeout/error:
    │       └── Return mock reply, saved=false
    │
    ├── Simpan { session_id, role: "user", message } ke tabel chats
    ├── Simpan { session_id, role: "assistant", message: reply } ke tabel chats
    │
    └── Return { session_id, reply, saved } ke client
```

### GET /ringkasan → UMKM Diagnosis (opsional, non-blocking)
```
FastAPI GET /ringkasan
    │
    ├── Hitung total_masuk, total_keluar, laba dari Supabase
    │
    ├── Kirim data keuangan ke {LANGFLOW_BASE_URL}/api/v1/run/{LANGFLOW_DIAGNOSIS_FLOW_ID}
    │       timeout: 15 detik (non-blocking — jika gagal, insight = null)
    │
    └── Return { total_masuk, total_keluar, laba, insight }
```

File `langflow_client.py` menangani semua call ke Langflow secara terpisah dari route.
Path response Langflow: `outputs[0].outputs[0].results.message.text` (sudah diverifikasi).

---

## 5. Environment Variables

```env
# Supabase
SUPABASE_URL=https://lzuksiztjaxdtgisdmie.supabase.co
SUPABASE_KEY=sb_publishable_k6IROn9v-6GZCz0gT5F8vg_AcUXxfZ1

# Langflow
LANGFLOW_BASE_URL=http://127.0.0.1:7860
LANGFLOW_API_KEY=sk-_vmqse3w_DC2gRjdBqLs6jATpFEWh07iuXZOYPX0YRE
LANGFLOW_CHAT_FLOW_ID=3fe1e5e9-15ee-4709-a3d2-02efeb2d9de8
LANGFLOW_DIAGNOSIS_FLOW_ID=5c85ca63-570f-4069-ab1f-e972c3732762
LANGFLOW_EXTRACTION_FLOW_ID=a7040b70-6599-42e9-99de-5ea8fb35e7b6

# App
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

`ALLOWED_ORIGINS` digunakan CORSMiddleware FastAPI agar frontend React bisa connect.
Semua nilai di atas sudah dikonfirmasi dari `persiapan.txt`.

---

## 6. Seed Data Demo

### Produk (3 item)
1. Jamu Kunyit Asam — kategori: jamu — satuan: botol — harga: Rp 8.000
2. Bubuk Jahe Merah — kategori: rempah — satuan: gram — harga: Rp 25.000
3. Temulawak Instant — kategori: olahan — satuan: sachet — harga: Rp 5.000

### Transaksi (8 item)
| # | Jenis  | Kategori    | Akun    | Keterangan                        | Jumlah     |
|---|--------|-------------|---------|-----------------------------------|------------|
| 1 | masuk  | penjualan   | usaha   | Jual Jamu Kunyit 20 botol         | Rp 160.000 |
| 2 | masuk  | penjualan   | usaha   | Jual Bubuk Jahe Merah 500g        | Rp 125.000 |
| 3 | masuk  | penjualan   | usaha   | Jual Temulawak Instant 30 sachet  | Rp 150.000 |
| 4 | keluar | bahan_baku  | usaha   | Beli kunyit 2kg                   | Rp 30.000  |
| 5 | keluar | bahan_baku  | usaha   | Beli jahe merah 1kg               | Rp 40.000  |
| 6 | keluar | operasional | usaha   | Biaya listrik bulan ini           | Rp 50.000  |
| 7 | masuk  | lainnya     | pribadi | Transfer dari rekening pribadi    | Rp 200.000 |
| 8 | keluar | lainnya     | pribadi | Keperluan pribadi                 | Rp 75.000  |

---

## 7. Urutan Pengerjaan (berdasarkan dependency)

### Sub-Task 1 — Setup Project FastAPI
- **Status:** `[ ] pending`
- **Intent:** Buat struktur FastAPI minimal yang bisa dijalankan, dengan CORS langsung dikonfigurasi.
- **Expected Outcomes:** `uvicorn main:app --reload` jalan, Swagger docs terbuka di `/docs`, CORS ready untuk frontend React.
- **Todo:**
  - [ ] Buat `requirements.txt` (fastapi, uvicorn, supabase, python-dotenv, httpx)
  - [ ] Buat `main.py` dengan app FastAPI, CORSMiddleware, dan health check `GET /`
  - [ ] Buat `.env.example` dengan semua variabel yang diperlukan
  - [ ] Verifikasi server jalan tanpa error

---

### Sub-Task 2 — Konfigurasi Supabase
- **Status:** `[ ] pending`
- **Intent:** Buat tabel di Supabase dan koneksi dari FastAPI.
- **Expected Outcomes:** Koneksi Supabase berhasil, tabel terbuat, seed data tersedia.
- **Todo:**
  - [ ] Buat tabel `produk`, `transaksi`, `chats` di Supabase (SQL editor di dashboard)
  - [ ] Buat `db.py` — inisialisasi Supabase client dari env vars
  - [ ] Test koneksi dengan query sederhana
  - [ ] Buat dan jalankan `seed.py` — insert 3 produk + 8 transaksi

---

### Sub-Task 3 — Endpoint Transaksi & Ringkasan
- **Status:** `[ ] pending`
- **Intent:** Implementasi endpoint keuangan yang digunakan halaman Keuangan frontend.
- **Expected Outcomes:** Semua endpoint merespons benar, filter berjalan, response shape sesuai yang diexpect frontend.
- **Todo:**
  - [ ] Buat Pydantic models untuk request/response transaksi
  - [ ] Implementasi `POST /transaksi`
  - [ ] Implementasi `GET /transaksi` dengan semua filter (akun, kategori, jenis, dari, sampai)
  - [ ] Implementasi `GET /ringkasan` — kalkulasi total_masuk, total_keluar, laba
  - [ ] Test manual via Swagger UI dengan seed data

---

### Sub-Task 4 — Endpoint HPP
- **Status:** `[ ] pending`
- **Intent:** Kalkulator HPP dan saran harga jual untuk halaman HPP frontend.
- **Expected Outcomes:** `POST /hpp` mengembalikan total_hpp, saran_harga_jual, dan rincian_bahan.
- **Todo:**
  - [ ] Buat Pydantic models untuk Bahan dan HPP request/response
  - [ ] Implementasi kalkulasi HPP: sum(jumlah × harga_per_satuan) per bahan
  - [ ] Implementasi saran harga jual: `HPP / (1 - margin_persen / 100)`
  - [ ] Test manual via Swagger UI

---

### Sub-Task 5 — Integrasi Langflow & Endpoint Chat
- **Status:** `[ ] pending`
- **Intent:** Hubungkan FastAPI ke flow Langflow yang sudah siap, simpan history chat ke Supabase.
- **Expected Outcomes:** `POST /chat` mengirim ke SPICEE Chat flow, mendapat reply Gemini, menyimpan ke tabel chats, fallback mock berjalan saat Langflow mati. `GET /ringkasan` menyertakan field `insight` dari UMKM Diagnosis flow.
- **Catatan:** Semua flow sudah siap dan sudah ditest. Tidak perlu setup flow baru.
- **Todo:**
  - [ ] Buat `langflow_client.py` dengan dua fungsi:
    - `call_chat_flow(message, session_id)` → call `LANGFLOW_CHAT_FLOW_ID`, timeout 30s, fallback mock
    - `call_diagnosis_flow(data_keuangan)` → call `LANGFLOW_DIAGNOSIS_FLOW_ID`, timeout 15s, fallback null
  - [ ] Path response Langflow: `outputs[0].outputs[0].results.message.text`
  - [ ] Implementasi `POST /chat` — call chat flow, simpan ke chats, return `{ session_id, reply, saved }`
  - [ ] Update `GET /ringkasan` — tambah call ke diagnosis flow, return `{ total_masuk, total_keluar, laba, insight }`
  - [ ] Test `POST /chat`: kirim "Apa manfaat jahe merah?" → dapat reply Gemini → cek tabel chats
  - [ ] Test fallback `POST /chat`: matikan Langflow → dapat mock response, `saved: false`
  - [ ] Test `GET /ringkasan` dengan insight: ada data transaksi → insight tidak null

---

### Sub-Task 6 — End-to-End Testing
- **Status:** `[ ] pending`
- **Intent:** Verifikasi seluruh backend sebelum integrasi frontend.
- **Expected Outcomes:** Semua endpoint lulus test, tidak ada unhandled exception, siap dikonsumsi frontend.
- **Todo:**
  - [ ] Buat `test_api.py` dengan pytest + httpx
  - [ ] Test `POST /transaksi` — data tersimpan di Supabase
  - [ ] Test `GET /transaksi` — semua kombinasi filter
  - [ ] Test `GET /ringkasan` — kalkulasi benar dengan data seed
  - [ ] Test `POST /hpp` — margin 30%, 0%, bahan kosong
  - [ ] Test `POST /chat` — Langflow aktif: dapat reply nyata
  - [ ] Test `POST /chat` — Langflow mati: dapat mock response
  - [ ] Konfirmasi CORS header ada di semua response
  - [ ] Semua test hijau

---

### Sub-Task 7 — Deployment (setelah semua stabil)
- **Status:** `[ ] pending`
- **Intent:** Deploy backend ke platform publik agar bisa diakses tim frontend dan juri hackathon.
- **Expected Outcomes:** Backend live di URL publik, semua endpoint berjalan, Swagger docs accessible.
- **Catatan:** Langflow tetap lokal — deployment ini hanya untuk FastAPI backend. Saat demo, backend dan Langflow jalan di mesin yang sama.
- **Todo:**
  - [ ] Tentukan platform: Railway atau Render (rekomendasi: Railway untuk kemudahan)
  - [ ] Buat `Dockerfile` atau konfigurasi platform
  - [ ] Set semua env vars di platform deploy
  - [ ] Update `LANGFLOW_BASE_URL` jika ada perubahan
  - [ ] Konfirmasi semua endpoint live dan Swagger docs accessible
  - [ ] Share base URL ke tim frontend

---

## 8. Testing Plan

| Endpoint        | Happy Path                    | Edge Case                            |
|-----------------|-------------------------------|--------------------------------------|
| GET /           | status ok                     | —                                    |
| POST /transaksi | data tersimpan, return 201    | jumlah negatif, jenis tidak valid    |
| GET /transaksi  | return array transaksi        | filter kombinasi, result kosong      |
| GET /ringkasan  | total_masuk/keluar/laba benar | tidak ada transaksi, filter akun     |
| POST /hpp       | total + saran harga benar     | bahan kosong, margin 0%, margin 100% |
| POST /chat      | reply dari Gemini, saved=true | Langflow mati → mock + saved=false   |

---

## 9. Risiko Teknis & Mitigasi

| Risiko                                 | Probabilitas | Mitigasi                                                          |
|----------------------------------------|--------------|-------------------------------------------------------------------|
| Langflow timeout saat demo             | Tinggi       | Mock response fallback di `langflow_client.py`                    |
| Gemini API quota habis                 | Sedang       | Mock response siap, quick questions bisa di-hardcode jika perlu   |
| CORS error saat frontend connect       | Sedang       | `CORSMiddleware` dikonfigurasi di Sub-Task 1, paling awal         |
| Supabase free tier rate limit          | Rendah       | Query efisien, tidak ada loop query berlebihan                    |
| Flow ID Langflow berubah saat restart  | Rendah       | Simpan Flow ID di `.env`, dokumentasikan cara update              |
| Response shape tidak sesuai frontend   | Sedang       | Dokumentasikan response shape di plan ini, align sebelum integrasi|

---

## 10. Definition of Done — Backend MVP

- [ ] `GET /` health check merespons `200 ok`
- [ ] `POST /transaksi` menyimpan data ke Supabase dan return `201`
- [ ] `GET /transaksi` mengembalikan list dengan semua filter berjalan
- [ ] `GET /ringkasan` mengembalikan `total_masuk`, `total_keluar`, `laba` yang benar
- [ ] `POST /hpp` mengembalikan `total_hpp`, `saran_harga_jual`, `rincian_bahan`
- [ ] `POST /chat` mendapat reply dari Gemini via Langflow
- [ ] `POST /chat` fallback mock berjalan saat Langflow dimatikan
- [ ] Semua chat tersimpan di tabel `chats`
- [ ] Seed data demo tersedia (3 produk, 8 transaksi)
- [ ] CORS dikonfigurasi untuk frontend React (`localhost:3000`, `localhost:5173`)
- [ ] Swagger UI (`/docs`) terbuka dan semua endpoint terdokumentasi otomatis
- [ ] Tidak ada unhandled exception saat demo flow normal
- [ ] Semua test di `test_api.py` hijau

---

## Catatan

- **Fitur input transaksi via chat** menggunakan UMKM Extraction flow (`a7040b70-...`) yang sudah siap — **tidak dikerjakan di MVP**. Ditambahkan setelah core backend stabil.
- **3 flow Langflow sudah selesai dibuat dan ditest** sebelum implementasi backend dimulai. Sub-Task 5 hanya perlu menulis `langflow_client.py` dan endpoint.
- **Response path Langflow yang sudah diverifikasi:** `outputs[0].outputs[0].results.message.text`
- GitHub dan struktur folder dikelola anggota tim lain — tidak termasuk scope plan ini.
- Frontend baru diintegrasikan setelah Sub-Task 6 selesai.
- `GET /ringkasan` mengembalikan field `insight` (nullable) dari UMKM Diagnosis flow — frontend bisa tampilkan atau sembunyikan berdasarkan null check.
