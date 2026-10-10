import sys
import os
sys.path.insert(0, '.')

# Simulasi Langflow mati dengan URL yang tidak ada
os.environ["LANGFLOW_BASE_URL"] = "http://127.0.0.1:9999"

import importlib
import langflow_client
importlib.reload(langflow_client)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("=== Test POST /chat — Langflow mati (fallback) ===")
r = client.post("/chat", json={
    "session_id": "test-fallback-001",
    "message": "Test fallback saat Langflow mati"
})
print(f"  Status : {r.status_code}")
d = r.json()
print(f"  saved  : {d['saved']} (expect False)")
print(f"  reply  : {d['reply']}")
