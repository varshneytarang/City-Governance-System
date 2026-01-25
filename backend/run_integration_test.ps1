# Start server in background
Write-Host "🚀 Starting backend server..." -ForegroundColor Green
$serverJob = Start-Job -ScriptBlock {
    Set-Location "D:\City-Governance-System\backend"
    & ".\venv\Scripts\python.exe" "main.py"
}

# Wait for server to start
Start-Sleep -Seconds 5

# Run tests
Write-Host "🧪 Running API integration tests..." -ForegroundColor Green
Set-Location "D:\City-Governance-System\backend"
& ".\venv\Scripts\python.exe" "test_api_integration.py"

# Stop server
Write-Host "🛑 Stopping server..." -ForegroundColor Yellow
Stop-Job -Job $serverJob
Remove-Job -Job $serverJob

Write-Host "✅ Test complete!" -ForegroundColor Green
