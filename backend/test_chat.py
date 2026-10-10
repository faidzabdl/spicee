import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from main import app
from db import supabase

client = TestClient(app)

SESSION_ID = "test-session-spicee-001"

# Test 1 — chat normal, Langflow aktif
print("=== Test POST /chat — pertanyaan rempah ===")
r = client.post("/chat", json={
    "session_id": SESSION_ID,
    "message": "Apa manfaat kunyit untuk kesehatan?"
})
print(f"  Status: {r.status_code}")
d = r.json()
print(f"  session_id : {d['session_id']}")
print(f"  saved      : {d['saved']}")
print(f"  reply      : {d['reply'][:120]}...")

# Test 2 — quick question HPP
print("\n=== Test POST /chat — quick question HPP ===")
r = client.post("/chat", json={
    "session_id": SESSION_ID,
    "message": "Apa itu HPP?"
})
print(f"  Status: {r.status_code}")
d = r.json()
print(f"  saved  : {d['saved']}")
print(f"  reply  : {d['reply'][:120]}...")

# Test 3 — quick question PIRT
print("\n=== Test POST /chat — quick question PIRT ===")
r = client.post("/chat", json={
    "session_id": SESSION_ID,
    "message": "Bagaimana cara daftar PIRT?"
})
print(f"  Status: {r.status_code}")
d = r.json()
print(f"  saved  : {d['saved']}")
print(f"  reply  : {d['reply'][:120]}...")

# Test 4 — cek history tersimpan di Supabase
print("\n=== Cek history di tabel chats ===")
rows = supabase.table("chats").select("role, message").eq("session_id", SESSION_ID).order("created_at").execute()
print(f"  Total rows: {len(rows.data)}")
for row in rows.data:
    print(f"  [{row['role']}]: {row['message'][:80]}...")

print("\n=== Semua test Chat selesai ===")
