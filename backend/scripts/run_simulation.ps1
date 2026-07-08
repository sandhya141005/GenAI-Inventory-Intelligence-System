#!/usr/bin/env pwsh

Write-Host "🚀 Starting Business Simulation..." -ForegroundColor Cyan
Write-Host ""

$env:PYTHONPATH = (Get-Location).Path

python scripts/run_simulation.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Simulation completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Start the backend: uvicorn app.main:app --reload" -ForegroundColor White
    Write-Host "   2. Start the frontend: npm run dev" -ForegroundColor White
    Write-Host "   3. Login with: ops@stocklens.com / stocklens2024" -ForegroundColor White
    Write-Host "   4. Realm Code: SL24" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Simulation failed" -ForegroundColor Red
    Write-Host "Check error messages above" -ForegroundColor Red
    exit 1
}
