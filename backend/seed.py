"""
Seed data demo untuk SPICEE.
Jalankan: venv/Scripts/python.exe seed.py
"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


def seed():
    print("=== SPICEE Seed Data ===\n")

    # ── Produk ──────────────────────────────────────────────
    print("Inserting produk...")
    produk_data = [
        {"nama": "Jamu Kunyit Asam",   "kategori": "jamu",    "satuan": "botol",  "harga_jual": 8000},
        {"nama": "Bubuk Jahe Merah",   "kategori": "rempah",  "satuan": "gram",   "harga_jual": 25000},
        {"nama": "Temulawak Instant",  "kategori": "olahan",  "satuan": "sachet", "harga_jual": 5000},
    ]
    r = sb.table("produk").insert(produk_data).execute()
    produk_ids = [p["id"] for p in r.data]
    print(f"  {len(r.data)} produk inserted")
    for p in r.data:
        print(f"    - {p['nama']} ({p['id']})")

    # ── Transaksi ────────────────────────────────────────────
    print("\nInserting transaksi...")
    transaksi_data = [
        {
            "tanggal": "2025-07-01", "jenis": "masuk", "kategori": "penjualan",
            "akun": "usaha", "keterangan": "Jual Jamu Kunyit Asam 20 botol",
            "jumlah": 160000, "produk_id": produk_ids[0],
        },
        {
            "tanggal": "2025-07-02", "jenis": "masuk", "kategori": "penjualan",
            "akun": "usaha", "keterangan": "Jual Bubuk Jahe Merah 500g",
            "jumlah": 125000, "produk_id": produk_ids[1],
        },
        {
            "tanggal": "2025-07-03", "jenis": "masuk", "kategori": "penjualan",
            "akun": "usaha", "keterangan": "Jual Temulawak Instant 30 sachet",
            "jumlah": 150000, "produk_id": produk_ids[2],
        },
        {
            "tanggal": "2025-07-04", "jenis": "keluar", "kategori": "bahan_baku",
            "akun": "usaha", "keterangan": "Beli kunyit 2kg",
            "jumlah": 30000, "produk_id": None,
        },
        {
            "tanggal": "2025-07-05", "jenis": "keluar", "kategori": "bahan_baku",
            "akun": "usaha", "keterangan": "Beli jahe merah 1kg",
            "jumlah": 40000, "produk_id": None,
        },
        {
            "tanggal": "2025-07-06", "jenis": "keluar", "kategori": "operasional",
            "akun": "usaha", "keterangan": "Biaya listrik bulan ini",
            "jumlah": 50000, "produk_id": None,
        },
        {
            "tanggal": "2025-07-07", "jenis": "masuk", "kategori": "lainnya",
            "akun": "pribadi", "keterangan": "Transfer dari rekening pribadi",
            "jumlah": 200000, "produk_id": None,
        },
        {
            "tanggal": "2025-07-08", "jenis": "keluar", "kategori": "lainnya",
            "akun": "pribadi", "keterangan": "Keperluan pribadi",
            "jumlah": 75000, "produk_id": None,
        },
    ]
    r = sb.table("transaksi").insert(transaksi_data).execute()
    print(f"  {len(r.data)} transaksi inserted")

    # ── Summary ──────────────────────────────────────────────
    print("\n=== Seed selesai ===")
    total_masuk  = sum(t["jumlah"] for t in transaksi_data if t["jenis"] == "masuk")
    total_keluar = sum(t["jumlah"] for t in transaksi_data if t["jenis"] == "keluar")
    print(f"  Total masuk  : Rp {total_masuk:,.0f}")
    print(f"  Total keluar : Rp {total_keluar:,.0f}")
    print(f"  Laba         : Rp {total_masuk - total_keluar:,.0f}")


if __name__ == "__main__":
    seed()
