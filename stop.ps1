# SPICEE - Stop All Services
# Jalankan script ini untuk mematikan semua service SPICEE
# Usage: .\stop.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host "   SPICEE - Stopping All Services" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# Stop uvicorn (backend)
$uvicorn = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -match "uvicorn" 2>$null
}
if ($uvicorn) {
    $uvicorn | Stop-Process -Force
    Write-Host "   Backend (uvicorn) stopped." -ForegroundColor Green
}

# Stop semua python http.server (frontend)
Get-Process -Name "python" -ErrorAction SilentlyContinue | ForEach-Object {
    try { $_.Kill() } catch {}
}
Write-Host "   Frontend (http.server) stopped." -ForegroundColor Green

# Stop ngrok
Get-Process -Name "ngrok" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "   ngrok stopped." -ForegroundColor Green

Write-Host ""
Write-Host "   Semua service SPICEE sudah dimatikan." -ForegroundColor Green
Write-Host ""

