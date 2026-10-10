from fastapi import APIRouter
from models import HPPRequest, HPPResponse, BahanRincian

router = APIRouter(tags=["HPP"])


@router.post("/hpp", response_model=HPPResponse)
def hitung_hpp(req: HPPRequest):
    rincian = []
    total_hpp = 0.0

    for bahan in req.bahan:
        subtotal = bahan.jumlah * bahan.harga_per_satuan
        total_hpp += subtotal
        rincian.append(BahanRincian(
            nama=bahan.nama,
            jumlah=bahan.jumlah,
            satuan=bahan.satuan,
            harga_per_satuan=bahan.harga_per_satuan,
            subtotal=subtotal,
        ))

    # Saran harga jual: HPP / (1 - margin/100)
    # Jika margin 100% → hindari division by zero, kembalikan HPP * 2
    if req.margin_persen >= 100:
        saran_harga_jual = total_hpp * 2
    else:
        saran_harga_jual = total_hpp / (1 - req.margin_persen / 100)

    return HPPResponse(
        nama_produk=req.nama_produk,
        total_hpp=round(total_hpp, 2),
        saran_harga_jual=round(saran_harga_jual, 2),
        rincian_bahan=rincian,
    )
