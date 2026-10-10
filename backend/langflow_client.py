import httpx
import os
from dotenv import load_dotenv

load_dotenv()

LANGFLOW_BASE_URL = os.getenv("LANGFLOW_BASE_URL", "http://127.0.0.1:7860")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "")
LANGFLOW_CHAT_FLOW_ID = os.getenv("LANGFLOW_CHAT_FLOW_ID", "")
LANGFLOW_DIAGNOSIS_FLOW_ID = os.getenv("LANGFLOW_DIAGNOSIS_FLOW_ID", "")

MOCK_REPLY = "Maaf, asisten SPICEE sedang tidak tersedia. Silakan coba lagi dalam beberapa saat."

HEADERS = {
    "x-api-key": LANGFLOW_API_KEY,
    "Content-Type": "application/json",
}


def _extract_text(response_json: dict) -> str:
    """Ambil teks reply dari struktur response Langflow."""
    try:
        return response_json["outputs"][0]["outputs"][0]["results"]["message"]["text"]
    except (KeyError, IndexError, TypeError):
        return ""


async def call_chat_flow(message: str, session_id: str) -> tuple[str, bool]:
    """
    Panggil SPICEE Chat Assistant flow di Langflow.
    Returns: (reply_text, success)
    """
    if not LANGFLOW_CHAT_FLOW_ID:
        return MOCK_REPLY, False

    url = f"{LANGFLOW_BASE_URL}/api/v1/run/{LANGFLOW_CHAT_FLOW_ID}"
    payload = {
        "input_value": message,
        "session_id": session_id,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=HEADERS)
            response.raise_for_status()
            reply = _extract_text(response.json())
            if not reply:
                return MOCK_REPLY, False
            return reply, True
    except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError):
        return MOCK_REPLY, False
    except Exception:
        return MOCK_REPLY, False


def _parse_diagnosis_text(raw: str) -> str | None:
    """
    Diagnosis flow kadang return JSON string.
    Parse dan ambil field yang paling berguna untuk ditampilkan ke user.
    """
    if not raw:
        return None
    import json
    try:
        # Bersihkan markdown code block jika ada
        clean = raw.strip()
        if clean.startswith("```"):
            parts = clean.split("```")
            clean = parts[1] if len(parts) > 1 else clean
            if clean.startswith("json"):
                clean = clean[4:]
        data = json.loads(clean.strip())
        if isinstance(data, dict):
            # Ambil field terbaik secara berurutan
            for field in ("summary", "message", "insight"):
                val = data.get(field)
                if val and isinstance(val, str) and val.strip():
                    return val.strip()
            # Gabung summary + rekomendasi pertama jika ada
            summary = data.get("summary", "")
            recs = data.get("recommendations", [])
            if recs and isinstance(recs, list):
                action = recs[0].get("action", "")
                if action:
                    return f"{summary} Rekomendasi: {action}".strip()
            return summary or None
    except Exception:
        pass
    # Bukan JSON — return as-is jika tidak mengandung { } dan cukup pendek
    if len(raw) < 400 and "{" not in raw:
        return raw.strip()
    return None


async def call_diagnosis_flow(data_keuangan: dict) -> str | None:
    """
    Panggil UMKM Diagnosis flow untuk insight keuangan.
    Non-blocking — returns None jika gagal.
    """
    if not LANGFLOW_DIAGNOSIS_FLOW_ID:
        return None

    url = f"{LANGFLOW_BASE_URL}/api/v1/run/{LANGFLOW_DIAGNOSIS_FLOW_ID}"
    total_masuk  = data_keuangan['total_masuk']
    total_keluar = data_keuangan['total_keluar']
    laba         = data_keuangan['laba']
    jumlah_tx    = data_keuangan.get('jumlah_transaksi', 0)
    breakdown    = data_keuangan.get('breakdown_mingguan', {})
    rasio = (laba / total_masuk * 100) if total_masuk > 0 else 0

    # Susun baris breakdown mingguan (urut tanggal)
    breakdown_lines = ""
    if breakdown:
        sorted_weeks = sorted(breakdown.items())
        rows_text = []
        for wk, val in sorted_weeks:
            laba_mg = val['masuk'] - val['keluar']
            rows_text.append(
                f"  - {wk}: masuk Rp {val['masuk']:,.0f}, "
                f"keluar Rp {val['keluar']:,.0f}, laba Rp {laba_mg:,.0f}"
            )
        breakdown_lines = "\nRincian per minggu:\n" + "\n".join(rows_text)

    message = (
        f"Data keuangan UMKM rempah ({jumlah_tx} transaksi, Oktober 2026):"
        f"{breakdown_lines}\n"
        f"Total keseluruhan: pemasukan Rp {total_masuk:,.0f}, "
        f"pengeluaran Rp {total_keluar:,.0f}, "
        f"laba bersih Rp {laba:,.0f} (margin {rasio:.0f}%). "
        f"Berikan insight singkat berdasarkan tren mingguan di atas "
        f"dan 1-2 rekomendasi tindakan konkret untuk UMKM ini."
    )
    payload = {
        "input_value": message,
        "session_id": "diagnosis-internal",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload, headers=HEADERS)
            response.raise_for_status()
            raw = _extract_text(response.json())
            return _parse_diagnosis_text(raw)
    except Exception:
        return None
