from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID


# ─────────────────────────────────────────
# Transaksi
# ─────────────────────────────────────────

class TransaksiCreate(BaseModel):
    tanggal: date
    jenis: str  # masuk / keluar
    kategori: str  # penjualan / bahan_baku / operasional / lainnya
    akun: str  # usaha / pribadi
    keterangan: Optional[str] = None
    jumlah: float = Field(gt=0)
    produk_id: Optional[str] = None


class TransaksiResponse(BaseModel):
    id: str
    tanggal: str
    jenis: str
    kategori: str
    akun: str
    keterangan: Optional[str] = None
    jumlah: float
    produk_id: Optional[str] = None
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}


class RingkasanResponse(BaseModel):
    total_masuk: float
    total_keluar: float
    laba: float
    insight: Optional[str] = None


# ─────────────────────────────────────────
# HPP
# ─────────────────────────────────────────

class Bahan(BaseModel):
    nama: str
    jumlah: float = Field(gt=0)
    satuan: str
    harga_per_satuan: float = Field(gt=0)


class BahanRincian(Bahan):
    subtotal: float


class HPPRequest(BaseModel):
    nama_produk: str
    bahan: list[Bahan] = Field(min_length=1)
    margin_persen: float = Field(ge=0, le=100, default=30)


class HPPResponse(BaseModel):
    nama_produk: str
    total_hpp: float
    saran_harga_jual: float
    rincian_bahan: list[BahanRincian]


# ─────────────────────────────────────────
# Chat
# ─────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    saved: bool
