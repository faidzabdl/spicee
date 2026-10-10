from fastapi import APIRouter
from db import supabase
from models import TransaksiCreate, TransaksiResponse, RingkasanResponse
from typing import Optional
from datetime import date

router = APIRouter(tags=["Transaksi"])


@router.post("/transaksi", response_model=TransaksiResponse, status_code=201)
def tambah_transaksi(transaksi: TransaksiCreate):
    data = transaksi.model_dump()
    # Konversi date ke string untuk Supabase
    if data.get("tanggal"):
        data["tanggal"] = str(data["tanggal"])
    result = supabase.table("transaksi").insert(data).execute()
    return result.data[0]


@router.get("/transaksi", response_model=list[TransaksiResponse])
def daftar_transaksi(
    akun: Optional[str] = None,
    kategori: Optional[str] = None,
    jenis: Optional[str] = None,
    dari: Optional[date] = None,
    sampai: Optional[date] = None,
):
    query = supabase.table("transaksi").select("*").order("created_at", desc=True)

    if akun:
        query = query.eq("akun", akun)
    if kategori:
        query = query.eq("kategori", kategori)
    if jenis:
        query = query.eq("jenis", jenis)
    if dari:
        query = query.gte("tanggal", str(dari))
    if sampai:
        query = query.lte("tanggal", str(sampai))

    result = query.execute()
    return result.data


@router.get("/ringkasan", response_model=RingkasanResponse)
async def ringkasan(
    akun: Optional[str] = None,
    dari: Optional[date] = None,
    sampai: Optional[date] = None,
):
    query = supabase.table("transaksi").select("jenis, jumlah, tanggal")

    if akun:
        query = query.eq("akun", akun)
    if dari:
        query = query.gte("tanggal", str(dari))
    if sampai:
        query = query.lte("tanggal", str(sampai))

    result = query.execute()
    rows = result.data

    total_masuk = sum(r["jumlah"] for r in rows if r["jenis"] == "masuk")
    total_keluar = sum(r["jumlah"] for r in rows if r["jenis"] == "keluar")
    laba = total_masuk - total_keluar

    # Hitung breakdown mingguan untuk konteks Gemini
    def _week_key(tgl_str: str) -> str:
        """Kembalikan label minggu dari string tanggal YYYY-MM-DD."""
        try:
            from datetime import date as _date
            d = _date.fromisoformat(tgl_str)
            # Senin awal minggu
            monday = d - __import__('datetime').timedelta(days=d.weekday())
            sunday = monday + __import__('datetime').timedelta(days=6)
            return f"{monday.strftime('%d %b')}–{sunday.strftime('%d %b %Y')}"
        except Exception:
            return "?"

    weekly: dict = {}
    for r in rows:
        wk = _week_key(r.get("tanggal", ""))
        if wk not in weekly:
            weekly[wk] = {"masuk": 0, "keluar": 0}
        if r["jenis"] == "masuk":
            weekly[wk]["masuk"] += r["jumlah"]
        else:
            weekly[wk]["keluar"] += r["jumlah"]

    # Diagnosis insight dari Langflow (non-blocking)
    insight = None
    try:
        from langflow_client import call_diagnosis_flow
        insight = await call_diagnosis_flow({
            "total_masuk": total_masuk,
            "total_keluar": total_keluar,
            "laba": laba,
            "jumlah_transaksi": len(rows),
            "breakdown_mingguan": weekly,
        })
    except Exception:
        pass

    return RingkasanResponse(
        total_masuk=total_masuk,
        total_keluar=total_keluar,
        laba=laba,
        insight=insight,
    )
