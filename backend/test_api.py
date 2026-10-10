"""
SPICEE Backend — End-to-End Test Suite
Jalankan: venv/Scripts/python.exe -m pytest test_api.py -v
"""
import sys
import os
import pytest

sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from main import app
from db import supabase

client = TestClient(app)

# ─────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────

def test_health_check():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["app"] == "SPICEE API"


# ─────────────────────────────────────────────────
# CORS headers
# ─────────────────────────────────────────────────

def test_cors_headers():
    r = client.get("/", headers={"Origin": "http://localhost:3000"})
    assert r.status_code == 200
    assert "access-control-allow-origin" in r.headers


# ─────────────────────────────────────────────────
# Transaksi
# ─────────────────────────────────────────────────

def test_get_transaksi_all():
    r = client.get("/transaksi")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) > 0


def test_get_transaksi_filter_akun_usaha():
    r = client.get("/transaksi?akun=usaha")
    assert r.status_code == 200
    data = r.json()
    assert all(t["akun"] == "usaha" for t in data)


def test_get_transaksi_filter_akun_pribadi():
    r = client.get("/transaksi?akun=pribadi")
    assert r.status_code == 200
    data = r.json()
    assert all(t["akun"] == "pribadi" for t in data)


def test_get_transaksi_filter_jenis_masuk():
    r = client.get("/transaksi?jenis=masuk")
    assert r.status_code == 200
    data = r.json()
    assert all(t["jenis"] == "masuk" for t in data)


def test_get_transaksi_filter_jenis_keluar():
    r = client.get("/transaksi?jenis=keluar")
    assert r.status_code == 200
    data = r.json()
    assert all(t["jenis"] == "keluar" for t in data)


def test_get_transaksi_filter_tanggal():
    r = client.get("/transaksi?dari=2025-07-01&sampai=2025-07-03")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3


def test_get_transaksi_filter_kosong():
    r = client.get("/transaksi?dari=2099-01-01&sampai=2099-01-02")
    assert r.status_code == 200
    assert r.json() == []


def test_post_transaksi_valid():
    payload = {
        "tanggal": "2025-07-15",
        "jenis": "masuk",
        "kategori": "penjualan",
        "akun": "usaha",
        "keterangan": "Test e2e transaksi",
        "jumlah": 99000,
    }
    r = client.post("/transaksi", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["jumlah"] == 99000
    assert data["akun"] == "usaha"
    assert "id" in data


def test_post_transaksi_jumlah_nol_invalid():
    payload = {
        "tanggal": "2025-07-15",
        "jenis": "masuk",
        "kategori": "penjualan",
        "akun": "usaha",
        "jumlah": 0,
    }
    r = client.post("/transaksi", json=payload)
    assert r.status_code == 422


def test_post_transaksi_jumlah_negatif_invalid():
    payload = {
        "tanggal": "2025-07-15",
        "jenis": "masuk",
        "kategori": "penjualan",
        "akun": "usaha",
        "jumlah": -5000,
    }
    r = client.post("/transaksi", json=payload)
    assert r.status_code == 422


# ─────────────────────────────────────────────────
# Ringkasan
# ─────────────────────────────────────────────────

def test_get_ringkasan():
    r = client.get("/ringkasan")
    assert r.status_code == 200
    d = r.json()
    assert "total_masuk" in d
    assert "total_keluar" in d
    assert "laba" in d
    assert d["laba"] == d["total_masuk"] - d["total_keluar"]


def test_get_ringkasan_laba_kalkulasi_benar():
    r = client.get("/ringkasan")
    d = r.json()
    assert d["total_masuk"] > 0
    assert d["total_keluar"] > 0
    assert d["laba"] == d["total_masuk"] - d["total_keluar"]


def test_get_ringkasan_filter_akun():
    r = client.get("/ringkasan?akun=usaha")
    assert r.status_code == 200
    d = r.json()
    assert "total_masuk" in d
    assert "laba" in d


def test_get_ringkasan_has_insight_field():
    r = client.get("/ringkasan")
    assert r.status_code == 200
    assert "insight" in r.json()


# ─────────────────────────────────────────────────
# HPP
# ─────────────────────────────────────────────────

def test_post_hpp_normal():
    r = client.post("/hpp", json={
        "nama_produk": "Jamu Kunyit",
        "bahan": [
            {"nama": "Kunyit", "jumlah": 200, "satuan": "gram", "harga_per_satuan": 5},
            {"nama": "Gula", "jumlah": 100, "satuan": "gram", "harga_per_satuan": 3},
        ],
        "margin_persen": 30,
    })
    assert r.status_code == 200
    d = r.json()
    assert d["nama_produk"] == "Jamu Kunyit"
    assert d["total_hpp"] == 1300.0   # 200*5 + 100*3
    assert abs(d["saran_harga_jual"] - 1857.14) < 1
    assert len(d["rincian_bahan"]) == 2


def test_post_hpp_margin_nol():
    r = client.post("/hpp", json={
        "nama_produk": "Test",
        "bahan": [{"nama": "Bahan A", "jumlah": 100, "satuan": "gram", "harga_per_satuan": 10}],
        "margin_persen": 0,
    })
    assert r.status_code == 200
    d = r.json()
    # margin 0% → saran harga = HPP
    assert d["saran_harga_jual"] == d["total_hpp"]


def test_post_hpp_subtotal_per_bahan():
    r = client.post("/hpp", json={
        "nama_produk": "Test",
        "bahan": [
            {"nama": "X", "jumlah": 10, "satuan": "pcs", "harga_per_satuan": 500},
        ],
        "margin_persen": 20,
    })
    assert r.status_code == 200
    d = r.json()
    assert d["rincian_bahan"][0]["subtotal"] == 5000.0


def test_post_hpp_bahan_kosong_invalid():
    r = client.post("/hpp", json={
        "nama_produk": "Test",
        "bahan": [],
        "margin_persen": 30,
    })
    assert r.status_code == 422


def test_post_hpp_harga_nol_invalid():
    r = client.post("/hpp", json={
        "nama_produk": "Test",
        "bahan": [{"nama": "X", "jumlah": 10, "satuan": "gram", "harga_per_satuan": 0}],
        "margin_persen": 30,
    })
    assert r.status_code == 422


# ─────────────────────────────────────────────────
# Chat
# ─────────────────────────────────────────────────

def test_post_chat_langflow_aktif():
    r = client.post("/chat", json={
        "session_id": "e2e-test-001",
        "message": "Apa itu temulawak?",
    })
    assert r.status_code == 200
    d = r.json()
    assert d["session_id"] == "e2e-test-001"
    assert isinstance(d["reply"], str)
    assert len(d["reply"]) > 0
    assert d["saved"] is True


def test_post_chat_history_tersimpan():
    session = "e2e-history-check-001"
    client.post("/chat", json={"session_id": session, "message": "Tes simpan history"})
    rows = supabase.table("chats").select("role").eq("session_id", session).execute()
    roles = [r["role"] for r in rows.data]
    assert "user" in roles
    assert "assistant" in roles


def test_post_chat_fallback_langflow_mati():
    """Test fallback saat LANGFLOW_BASE_URL diganti ke port yang tidak ada."""
    import langflow_client as lf_module
    original_url = lf_module.LANGFLOW_BASE_URL
    lf_module.LANGFLOW_BASE_URL = "http://127.0.0.1:9999"
    try:
        r = client.post("/chat", json={
            "session_id": "e2e-fallback-001",
            "message": "Test fallback",
        })
        assert r.status_code == 200
        d = r.json()
        assert d["saved"] is False
        assert "tidak tersedia" in d["reply"]
    finally:
        lf_module.LANGFLOW_BASE_URL = original_url


def test_post_chat_message_kosong_invalid():
    r = client.post("/chat", json={
        "session_id": "e2e-test-002",
        "message": "",
    })
    assert r.status_code == 422
