# Complete Demo Setup Script for Windows
# Generates data and creates demo user via API

Write-Host "🚀 Complete McKinsey Demo Setup" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# Step 1: Generate demo data
Write-Host "Step 1: Generating demo data..." -ForegroundColor Yellow
python scripts/generate_demo_data_simple.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Failed to generate demo data" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Demo data generated successfully!" -ForegroundColor Green
Write-Host ""

# Step 2: Create demo user via API
Write-Host "Step 2: Creating demo user via API..." -ForegroundColor Yellow
Write-Host "   Make sure backend is running on http://localhost:8000" -ForegroundColor White
Write-Host ""

# Check if backend is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "   ✅ Backend is running" -ForegroundColor Green
    
    # Try to create user
    $body = @{
        email = "demo@mckinsey.com"
        password = "demo1234"
        full_name = "McKinsey Demo User"
    } | ConvertTo-Json
    
    try {
        $userResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/signup" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body `
            -ErrorAction Stop
        
        Write-Host ""
        Write-Host "   ✅ Demo user created successfully!" -ForegroundColor Green
        Write-Host "   Email: demo@mckinsey.com" -ForegroundColor White
        Write-Host "   Password: demo1234" -ForegroundColor White
    }
    catch {
        if ($_.Exception.Response.StatusCode -eq 409) {
            Write-Host ""
            Write-Host "   ✅ Demo user already exists" -ForegroundColor Green
            Write-Host "   Email: demo@mckinsey.com" -ForegroundColor White
            Write-Host "   Password: demo1234" -ForegroundColor White
        }
        else {
            Write-Host ""
            Write-Host "   ⚠️  Could not create user via API" -ForegroundColor Yellow
            Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "   You can create the user manually:" -ForegroundColor White
            Write-Host "   1. Visit http://localhost:3000/signup" -ForegroundColor White
            Write-Host "   2. Use: demo@mckinsey.com / demo1234" -ForegroundColor White
        }
    }
}
catch {
    Write-Host ""
    Write-Host "   ⚠️  Backend not running" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   To complete setup:" -ForegroundColor White
    Write-Host "   1. Start backend: uvicorn app.main:app --reload" -ForegroundColor White
    Write-Host "   2. Run this script again to create user" -ForegroundColor White
    Write-Host "   OR create user manually at http://localhost:3000/signup" -ForegroundColor White
}

Write-Host ""
Write-Host "=" * 60
Write-Host "✨ SETUP COMPLETE" -ForegroundColor Green
Write-Host "=" * 60
Write-Host ""
Write-Host "📊 Data Generated:" -ForegroundColor Cyan
Write-Host "   • 56 automotive products" -ForegroundColor White
Write-Host "   • 10 stores/warehouses" -ForegroundColor White
Write-Host "   • ~9,000 sales transactions (90 days)" -ForegroundColor White
Write-Host "   • 7 inventory transfers" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Demo Credentials:" -ForegroundColor Cyan
Write-Host "   Email: demo@mckinsey.com" -ForegroundColor White
Write-Host "   Password: demo1234" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Ensure backend is running: uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "   2. Start frontend: npm run dev" -ForegroundColor White
Write-Host "   3. Open http://localhost:3000 and login" -ForegroundColor White
Write-Host ""
Write-Host "=" * 60
