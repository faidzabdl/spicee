import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test normal — 2 bahan, margin 30%
print("=== Test POST /hpp — normal ===")
r = client.post("/hpp", json={
    "nama_produk": "Jamu Kunyit Asam",
    "bahan": [
        {"nama": "Kunyit", "jumlah": 200, "satuan": "gram", "harga_per_satuan": 5},
        {"nama": "Gula Aren", "jumlah": 100, "satuan": "gram", "harga_per_satuan": 3},
        {"nama": "Asam Jawa", "jumlah": 50, "satuan": "gram", "harga_per_satuan": 4},
        {"nama": "Kemasan botol", "jumlah": 1, "satuan": "pcs", "harga_per_satuan": 1500},
    ],
    "margin_persen": 30
})
print(f"  Status: {r.status_code}")
d = r.json()
print(f"  nama_produk      : {d['nama_produk']}")
print(f"  total_hpp        : Rp {d['total_hpp']:,.2f}")
print(f"  saran_harga_jual : Rp {d['saran_harga_jual']:,.2f}")
print(f"  rincian_bahan    : {len(d['rincian_bahan'])} item")
for b in d["rincian_bahan"]:
    print(f"    - {b['nama']}: {b['jumlah']} {b['satuan']} x Rp {b['harga_per_satuan']} = Rp {b['subtotal']:,.2f}")

# Test margin 0%
print("\n=== Test POST /hpp — margin 0% ===")
r = client.post("/hpp", json={
    "nama_produk": "Bubuk Jahe Merah",
    "bahan": [
        {"nama": "Jahe Merah", "jumlah": 500, "satuan": "gram", "harga_per_satuan": 20},
    ],
    "margin_persen": 0
})
print(f"  Status: {r.status_code}")
d = r.json()
print(f"  total_hpp        : Rp {d['total_hpp']:,.2f}")
print(f"  saran_harga_jual : Rp {d['saran_harga_jual']:,.2f} (sama dengan HPP karena margin 0%)")

# Test margin 50%
print("\n=== Test POST /hpp — margin 50% ===")
r = client.post("/hpp", json={
    "nama_produk": "Temulawak Instant",
    "bahan": [
        {"nama": "Temulawak", "jumlah": 300, "satuan": "gram", "harga_per_satuan": 8},
        {"nama": "Gula", "jumlah": 150, "satuan": "gram", "harga_per_satuan": 2},
    ],
    "margin_persen": 50
})
print(f"  Status: {r.status_code}")
d = r.json()
print(f"  total_hpp        : Rp {d['total_hpp']:,.2f}")
print(f"  saran_harga_jual : Rp {d['saran_harga_jual']:,.2f}")

# Test bahan kosong — harus error validasi
print("\n=== Test POST /hpp — bahan kosong (expect 422) ===")
r = client.post("/hpp", json={
    "nama_produk": "Test",
    "bahan": [],
    "margin_persen": 30
})
print(f"  Status: {r.status_code} (expect 422)")

print("\n=== Semua test HPP selesai ===")
