-- ============================================================
-- SPICEE — Supabase Schema
-- Jalankan di: Supabase Dashboard → SQL Editor → New Query
-- ============================================================

-- Tabel produk
CREATE TABLE IF NOT EXISTS produk (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nama        TEXT NOT NULL,
    kategori    TEXT NOT NULL CHECK (kategori IN ('rempah', 'jamu', 'olahan', 'lainnya')),
    satuan      TEXT NOT NULL,
    harga_jual  NUMERIC(15, 2) NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabel transaksi
CREATE TABLE IF NOT EXISTS transaksi (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tanggal     DATE NOT NULL,
    jenis       TEXT NOT NULL CHECK (jenis IN ('masuk', 'keluar')),
    kategori    TEXT NOT NULL,
    akun        TEXT NOT NULL CHECK (akun IN ('usaha', 'pribadi')),
    keterangan  TEXT,
    jumlah      NUMERIC(15, 2) NOT NULL CHECK (jumlah > 0),
    produk_id   UUID REFERENCES produk(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabel chats
CREATE TABLE IF NOT EXISTS chats (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  TEXT NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    message     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index untuk performa query yang sering dipakai
CREATE INDEX IF NOT EXISTS idx_transaksi_akun       ON transaksi(akun);
CREATE INDEX IF NOT EXISTS idx_transaksi_jenis      ON transaksi(jenis);
CREATE INDEX IF NOT EXISTS idx_transaksi_tanggal    ON transaksi(tanggal);
CREATE INDEX IF NOT EXISTS idx_transaksi_kategori   ON transaksi(kategori);
CREATE INDEX IF NOT EXISTS idx_chats_session_id     ON chats(session_id);
