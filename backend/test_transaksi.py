import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test GET /transaksi
print("=== Test GET /transaksi ===")
r = client.get("/transaksi")
print(f"  Status: {r.status_code}")
data = r.json()
print(f"  Count: {len(data)} transaksi")
if data:
    print(f"  Sample: {data[0]['keterangan']} - Rp {data[0]['jumlah']:,.0f}")

# Test filter akun
print("\n=== Test GET /transaksi?akun=usaha ===")
r = client.get("/transaksi?akun=usaha")
print(f"  Status: {r.status_code}, Count: {len(r.json())}")

# Test filter jenis
print("\n=== Test GET /transaksi?jenis=masuk ===")
r = client.get("/transaksi?jenis=masuk")
print(f"  Status: {r.status_code}, Count: {len(r.json())}")

# Test filter kombinasi
print("\n=== Test GET /transaksi?akun=usaha&jenis=keluar ===")
r = client.get("/transaksi?akun=usaha&jenis=keluar")
print(f"  Status: {r.status_code}, Count: {len(r.json())}")

# Test filter tanggal
print("\n=== Test GET /transaksi?dari=2025-07-01&sampai=2025-07-03 ===")
r = client.get("/transaksi?dari=2025-07-01&sampai=2025-07-03")
print(f"  Status: {r.status_code}, Count: {len(r.json())} (expect 3)")

# Test GET /ringkasan
print("\n=== Test GET /ringkasan ===")
r = client.get("/ringkasan")
print(f"  Status: {r.status_code}")
d = r.json()
print(f"  total_masuk  : Rp {d['total_masuk']:,.0f}")
print(f"  total_keluar : Rp {d['total_keluar']:,.0f}")
print(f"  laba         : Rp {d['laba']:,.0f}")
insight = d.get("insight")
print(f"  insight      : {'(ada)' if insight else 'null'}")

# Test GET /ringkasan?akun=usaha
print("\n=== Test GET /ringkasan?akun=usaha ===")
r = client.get("/ringkasan?akun=usaha")
d = r.json()
print(f"  Status: {r.status_code}")
print(f"  total_masuk  : Rp {d['total_masuk']:,.0f}")
print(f"  total_keluar : Rp {d['total_keluar']:,.0f}")
print(f"  laba         : Rp {d['laba']:,.0f}")

# Test POST /transaksi
print("\n=== Test POST /transaksi ===")
r = client.post("/transaksi", json={
    "tanggal": "2025-07-10",
    "jenis": "masuk",
    "kategori": "penjualan",
    "akun": "usaha",
    "keterangan": "Test transaksi baru",
    "jumlah": 50000
})
print(f"  Status: {r.status_code}")
if r.status_code == 201:
    print(f"  ID: {r.json()['id']}")
else:
    print(f"  Error: {r.json()}")

print("\n=== Semua test selesai ===")
