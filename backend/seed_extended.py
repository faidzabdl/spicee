"""
SPICEE — Extended Seed Data (2026-10-01 s/d 2026-10-11)

Menambahkan 18 transaksi simulasi UMKM rempah selama 11 hari.
AMAN dijalankan berulang — duplikat dicegah via kombinasi tanggal + keterangan.
Data lama TIDAK dihapus atau ditimpa.

Cara menjalankan:
  cd backend
  .\\venv\\Scripts\\python.exe seed_extended.py
"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

TRANSAKSI_BARU = [
    # ── MINGGU 1 (01–05 Oktober 2026) ───────────────────────
    {"tanggal": "2026-10-01", "jenis": "masuk",  "kategori": "penjualan",   "akun": "usaha",   "keterangan": "Jual Jamu Kunyit Asam 15 botol",   "jumlah": 120000},
    {"tanggal": "2026-10-01", "jenis": "keluar", "kategori": "bahan_baku",  "akun": "usaha",   "keterangan": "Restok kunyit 3kg",                 "jumlah": 45000},
    {"tanggal": "2026-10-02", "jenis": "masuk",  "kategori": "penjualan",   "akun": "usaha",   "keterangan": "Jual Bubuk Jahe Merah 400g",        "jumlah": 100000},
    {"tanggal": "2026-10-03", "jenis": "masuk",  "kategori": "penjualan",   "akun": "usaha",   "keterangan": "Jual Temulawak Instant 20 sachet",  "jumlah": 100000},
    {"tanggal": "2026-10-03", "jenis": "keluar", "kategori": "bahan_baku",  "akun": "usaha",   "keterangan": "Beli jahe merah 2kg",               "jumlah": 80000},
    {"tanggal": "2026-10-04", "jenis": "masuk",  "kategori": "penjualan",   "akun": "usaha",   "keterangan": "Jual Jamu Kunyit Asam 10 botol",    "jumlah": 80000},
    {"tanggal": "2026-10-05", "jenis": "masuk",  "kategori": "penjualan",   "akun": "usaha",   "keterangan": "Jual Bubuk Jahe Merah 200g",        "jumlah": 50000},
    {"tanggal": "2026-10-05", "jenis": "keluar", "kategori": "operasional", "akun": "usaha",   "keterangan": "Beli kemasan botol 50pcs",          "jumlah": 35000},
    # ── MINGGU 2 (06–11 Oktober 2026) ───────────────────────
    {"tanggal": "2026-10-06", "jenis": "masuk",  "kategori": "penjualan",   "akun": "usaha",   "keterangan": "Jual Temulawak Instant 35 sachet",  "jumlah": 175000},
    {"tanggal": "2026-10-06", "jenis": "keluar", "kategori": "bahan_baku",  "akun": "usaha",   "keterangan": "Restok temulawak 2kg",              "jumlah": 50000},
    {"tanggal": "2026-10-07", "jenis": "masuk",  "kategori": "penjualan",   "akun": "usaha",   "keterangan": "Jual Jamu Kunyit Asam 25 botol",    "jumlah": 200000},
    {"tanggal": "2026-10-08", "jenis": "keluar", "kategori": "bahan_baku",  "akun": "usaha",   "keterangan": "Beli gula merah 5kg",               "jumlah": 60000},
    {"tanggal": "2026-10-09", "jenis": "masuk",  "kategori": "penjualan",   "akun": "usaha",   "keterangan": "Jual Bubuk Jahe Merah 600g",        "jumlah": 150000},
    {"tanggal": "2026-10-10", "jenis": "masuk",  "kategori": "penjualan",   "akun": "usaha",   "keterangan": "Jual Temulawak Instant 15 sachet",  "jumlah": 75000},
    {"tanggal": "2026-10-10", "jenis": "keluar", "kategori": "operasional", "akun": "usaha",   "keterangan": "Beli gas LPG 3kg",                  "jumlah": 22000},
    {"tanggal": "2026-10-11", "jenis": "masuk",  "kategori": "penjualan",   "akun": "usaha",   "keterangan": "Jual Jamu Kunyit Asam 12 botol",    "jumlah": 96000},
    {"tanggal": "2026-10-11", "jenis": "keluar", "kategori": "bahan_baku",  "akun": "usaha",   "keterangan": "Restok jahe merah 1kg",             "jumlah": 40000},
    {"tanggal": "2026-10-11", "jenis": "keluar", "kategori": "lainnya",     "akun": "pribadi", "keterangan": "Keperluan rumah tangga",            "jumlah": 90000},
]


def seed_extended():
    print("=== SPICEE Extended Seed (2026-10-01 s/d 2026-10-11) ===\n")

    # ── Guard duplikat: cek via kombinasi tanggal + keterangan ──
    # Query semua tanggal Oktober 2026 yang ada di DB
    res = sb.table("transaksi").select("tanggal, keterangan") \
        .gte("tanggal", "2026-10-01").lte("tanggal", "2026-10-11").execute()
    existing = {(r["tanggal"], r["keterangan"]) for r in res.data if r.get("keterangan")}

    to_insert = [
        t for t in TRANSAKSI_BARU
        if (t["tanggal"], t["keterangan"]) not in existing
    ]
    skipped = len(TRANSAKSI_BARU) - len(to_insert)

    if skipped > 0:
        print(f"  SKIP: {skipped} transaksi dilewati (sudah ada di database)")

    if not to_insert:
        print("  Semua transaksi sudah ada. Tidak ada yang diinsert.")
        _print_summary_local()
        return

    # ── Insert ────────────────────────────────────────────────
    print(f"  Inserting {len(to_insert)} transaksi baru...")
    r = sb.table("transaksi").insert(to_insert).execute()
    print(f"  OK: {len(r.data)} transaksi berhasil diinsert.\n")

    _print_summary_db()


def _print_summary_local():
    masuk  = sum(t["jumlah"] for t in TRANSAKSI_BARU if t["jenis"] == "masuk")
    keluar = sum(t["jumlah"] for t in TRANSAKSI_BARU if t["jenis"] == "keluar")
    print(f"\n  [Ringkasan data lokal - {len(TRANSAKSI_BARU)} baris]")
    print(f"    Masuk  : Rp {masuk:>12,}")
    print(f"    Keluar : Rp {keluar:>12,}")
    print(f"    Laba   : Rp {masuk - keluar:>12,}")


def _print_summary_db():
    rows = sb.table("transaksi").select("jenis, jumlah, akun").execute().data

    semua_masuk  = sum(r["jumlah"] for r in rows if r["jenis"] == "masuk")
    semua_keluar = sum(r["jumlah"] for r in rows if r["jenis"] == "keluar")
    usaha_masuk  = sum(r["jumlah"] for r in rows if r["jenis"] == "masuk"  and r["akun"] == "usaha")
    usaha_keluar = sum(r["jumlah"] for r in rows if r["jenis"] == "keluar" and r["akun"] == "usaha")

    print("=== Verifikasi dari Database ===")
    print(f"  Total baris transaksi di DB : {len(rows)}")
    print(f"\n  [Semua Akun — tampil di /ringkasan frontend]")
    print(f"    Masuk  : Rp {semua_masuk:>12,}")
    print(f"    Keluar : Rp {semua_keluar:>12,}")
    print(f"    Laba   : Rp {semua_masuk - semua_keluar:>12,}")
    print(f"\n  [Akun Usaha saja]")
    print(f"    Masuk  : Rp {usaha_masuk:>12,}")
    print(f"    Keluar : Rp {usaha_keluar:>12,}")
    print(f"    Laba   : Rp {usaha_masuk - usaha_keluar:>12,}")
    print("\n=== Selesai ===")


if __name__ == "__main__":
    seed_extended()
