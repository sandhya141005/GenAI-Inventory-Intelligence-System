# PowerShell script to seed demo data

Write-Host "🚀 Seeding McKinsey Executive Demo Data..." -ForegroundColor Cyan
Write-Host ""

$env:PYTHONPATH = (Get-Location).Path

python scripts/generate_demo_data.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Demo data seeded successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Start the backend: uvicorn app.main:app --reload" -ForegroundColor White
    Write-Host "   2. Start the frontend: npm run dev" -ForegroundColor White
    Write-Host "   3. Login with: demo@mckinsey.com / demo1234" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Failed to seed demo data" -ForegroundColor Red
    Write-Host "Check error messages above" -ForegroundColor Red
    exit 1
}
