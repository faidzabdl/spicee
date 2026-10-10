# SPICEE - Start All Services
# Jalankan script ini untuk menghidupkan semua service SPICEE
# Usage: .\start.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   SPICEE - Starting All Services" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ── Cek ngrok ────────────────────────────────────────────
$ngrokPath = Join-Path $rootDir "ngrok.exe"
$ngrokAvailable = Test-Path $ngrokPath
if (-not $ngrokAvailable) {
    # Cek di PATH
    $ngrokInPath = Get-Command ngrok -ErrorAction SilentlyContinue
    if ($ngrokInPath) { $ngrokPath = "ngrok"; $ngrokAvailable = $true }
}

# ── Start Backend ─────────────────────────────────────────
Write-Host "[1/3] Starting Backend (FastAPI :8000)..." -ForegroundColor Cyan
$backendLog = Join-Path $rootDir "backend\backend.log"
$backendProc = Start-Process -FilePath "powershell" `
    -ArgumentList "-NoProfile -Command `"Set-Location '$rootDir\backend'; .\venv\Scripts\python.exe -m uvicorn main:app --port 8000 2>&1 | Tee-Object -FilePath '$backendLog'`"" `
    -PassThru -WindowStyle Normal
Write-Host "   PID: $($backendProc.Id) | Log: backend\backend.log" -ForegroundColor Gray
Start-Sleep -Seconds 3

# Verifikasi backend
try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -UseBasicParsing -TimeoutSec 5
    Write-Host "   Backend OK: $($r.Content)" -ForegroundColor Green
} catch {
    Write-Host "   Backend belum merespons - tunggu beberapa detik" -ForegroundColor Yellow
}

# ── Start Frontend ────────────────────────────────────────
Write-Host ""
Write-Host "[2/3] Starting Frontend (HTTP :3000)..." -ForegroundColor Cyan
$frontendProc = Start-Process -FilePath "powershell" `
    -ArgumentList "-NoProfile -Command `"Set-Location '$rootDir\frontend'; python -m http.server 3000`"" `
    -PassThru -WindowStyle Normal
Write-Host "   PID: $($frontendProc.Id)" -ForegroundColor Gray
Write-Host "   Frontend URL: http://localhost:3000/HACK.html" -ForegroundColor Green

# ── Start ngrok ───────────────────────────────────────────
Write-Host ""
Write-Host "[3/3] Starting ngrok tunnel (backend :8000)..." -ForegroundColor Cyan

if ($ngrokAvailable) {
    $ngrokLog = Join-Path $rootDir "ngrok.log"
    $ngrokProc = Start-Process -FilePath $ngrokPath `
        -ArgumentList "http 8000 --log=stdout" `
        -PassThru -WindowStyle Normal -RedirectStandardOutput $ngrokLog
    Write-Host "   PID: $($ngrokProc.Id)" -ForegroundColor Gray
    Start-Sleep -Seconds 3

    # Ambil URL ngrok dari API lokal
    try {
        $tunnels = Invoke-WebRequest -Uri "http://127.0.0.1:4040/api/tunnels" -UseBasicParsing -TimeoutSec 5
        $tunnelData = $tunnels.Content | ConvertFrom-Json
        $publicUrl = $tunnelData.tunnels[0].public_url
        if ($publicUrl -match "^http://") {
            $publicUrl = $publicUrl -replace "^http://", "https://"
        }
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Yellow
        Write-Host "   NGROK PUBLIC URL (Backend API):" -ForegroundColor Yellow
        Write-Host "   $publicUrl" -ForegroundColor White
        Write-Host "========================================" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   Update API_URL di frontend/HACK.html:" -ForegroundColor Cyan
        Write-Host "   const API_URL = '$publicUrl';" -ForegroundColor White
        Write-Host ""

        # Auto-update HACK.html dengan URL ngrok terbaru
        $hackPath = Join-Path $rootDir "frontend\HACK.html"
        $hackContent = Get-Content $hackPath -Raw -Encoding UTF8
        $updatedContent = $hackContent -replace "const API_URL = '[^']*';", "const API_URL = '$publicUrl';"
        Set-Content -Path $hackPath -Value $updatedContent -Encoding UTF8
        Write-Host "   HACK.html sudah di-update otomatis dengan URL baru!" -ForegroundColor Green

    } catch {
        Write-Host "   Ngrok berjalan tapi URL belum siap. Buka http://127.0.0.1:4040 untuk lihat URL." -ForegroundColor Yellow
    }
} else {
    Write-Host "   ngrok.exe tidak ditemukan di folder ini atau PATH." -ForegroundColor Red
    Write-Host "   Download dari: https://ngrok.com/download" -ForegroundColor Yellow
    Write-Host "   Taruh ngrok.exe di: $rootDir" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Tanpa ngrok, akses lokal tetap bisa:" -ForegroundColor Cyan
    Write-Host "   Frontend : http://localhost:3000/HACK.html" -ForegroundColor White
    Write-Host "   Backend  : http://localhost:8000/docs" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Semua service berjalan!" -ForegroundColor Green
Write-Host "   Frontend : http://localhost:3000/HACK.html" -ForegroundColor White
Write-Host "   Backend  : http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Langflow : http://127.0.0.1:7860" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Tekan Enter untuk menutup jendela ini..." -ForegroundColor Gray
Read-Host

