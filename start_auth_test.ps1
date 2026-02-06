# Quick Start Script - Login/Register Testing
# Run this to set up and test the authentication pages

Write-Host "`n🔐 City Governance - Authentication Setup & Test" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# Step 1: Check if database migration is needed
Write-Host "📋 STEP 1: Database Setup" -ForegroundColor Yellow
Write-Host "Run this command to create auth tables:" -ForegroundColor White
Write-Host "  psql -U postgres -d city_governance -f backend\migrations\auth_schema.sql`n" -ForegroundColor Green

$response = Read-Host "Have you run the database migration? (y/n)"
if ($response -ne 'y') {
    Write-Host "`n⚠️  Please run the database migration first!" -ForegroundColor Red
    Write-Host "Command: psql -U postgres -d city_governance -f backend\migrations\auth_schema.sql" -ForegroundColor Yellow
    exit
}

# Step 2: Test Backend
Write-Host "`n📡 STEP 2: Testing Backend Auth Endpoints..." -ForegroundColor Yellow
Write-Host "Running test script...`n" -ForegroundColor White

python test_auth_endpoints.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Backend tests failed! Check if backend is running on port 8000" -ForegroundColor Red
    exit
}

# Step 3: Frontend URLs
Write-Host "`n🌐 STEP 3: Frontend Testing URLs" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`nYour frontend is running. Open these URLs in your browser:" -ForegroundColor White
Write-Host ""
Write-Host "  🏠 Home Page:     http://localhost:3000/" -ForegroundColor Green
Write-Host "  🔐 Login Page:    http://localhost:3000/#login" -ForegroundColor Green
Write-Host "  📝 Register Page: http://localhost:3000/#register" -ForegroundColor Green
Write-Host "  🧪 API Test:      http://localhost:3000/#test" -ForegroundColor Green
Write-Host ""

# Step 4: Test Accounts
Write-Host "`n👤 STEP 4: Test Accounts" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "`nUse these pre-configured accounts to test login:" -ForegroundColor White
Write-Host ""
Write-Host "  Admin Account:" -ForegroundColor Magenta
Write-Host "    Email:    admin@citygovernance.in" -ForegroundColor White
Write-Host "    Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "  Fire Department:" -ForegroundColor Magenta
Write-Host "    Email:    fire.dept@citygovernance.in" -ForegroundColor White
Write-Host "    Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "  Water Department:" -ForegroundColor Magenta
Write-Host "    Email:    water.dept@citygovernance.in" -ForegroundColor White
Write-Host "    Password: admin123" -ForegroundColor White
Write-Host ""

# Step 5: Testing Checklist
Write-Host "`n✅ STEP 5: Testing Checklist" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test these features:" -ForegroundColor White
Write-Host "  ☐ Login page loads with two columns" -ForegroundColor White
Write-Host "  ☐ Animations visible on right side" -ForegroundColor White
Write-Host "  ☐ Login with test account works" -ForegroundColor White
Write-Host "  ☐ Register page loads correctly" -ForegroundColor White
Write-Host "  ☐ Password strength indicator works" -ForegroundColor White
Write-Host "  ☐ Create new account works" -ForegroundColor White
Write-Host "  ☐ Form validations show errors" -ForegroundColor White
Write-Host "  ☐ Navigation between pages works" -ForegroundColor White
Write-Host ""

# Step 6: Verify in Browser Console
Write-Host "`n🔍 STEP 6: Verify Login Success" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "`nAfter logging in, open browser console (F12) and run:" -ForegroundColor White
Write-Host ""
Write-Host "  localStorage.getItem('city_governance_token')" -ForegroundColor Green
Write-Host ""
Write-Host "You should see a JWT token if login was successful!`n" -ForegroundColor White

# Quick Open Browser
Write-Host "`n🚀 Quick Actions" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
$openBrowser = Read-Host "`nOpen login page in browser now? (y/n)"
if ($openBrowser -eq 'y') {
    Start-Process "http://localhost:3000/#login"
    Write-Host "✅ Browser opened!`n" -ForegroundColor Green
}

Write-Host "`n📖 For detailed testing guide, see:" -ForegroundColor Yellow
Write-Host "   TESTING_GUIDE.md`n" -ForegroundColor Cyan

Write-Host "Happy Testing! 🎉`n" -ForegroundColor Green
