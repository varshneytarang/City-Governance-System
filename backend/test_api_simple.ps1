# Simple API Integration Test using Invoke-RestMethod
Write-Host "================================================================================"
Write-Host "API INTEGRATION TESTING - Fire & Water Agents" -ForegroundColor Green
Write-Host "================================================================================"

$baseUrl = "http://localhost:8000"

# Test 1: Fire Agent - Emergency Response
Write-Host "`nTEST 1: Fire Agent - Building Fire Emergency" -ForegroundColor Yellow
Write-Host "================================================================================"

$fireRequest = @{
    user_id = 1
    emergency_type = "fire"
    location = @{
        address = "Test Building, Delhi"
        latitude = 28.6139
        longitude = 77.2090
    }
    description = "Major fire in commercial building"
    casualties = 3
    building_type = "commercial"
    fire_intensity = "major"
    priority = "critical"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/fire/emergency" -Method Post -Body $fireRequest -ContentType "application/json" -TimeoutSec 30
    
    Write-Host "API Response Received" -ForegroundColor Green
    Write-Host "Request ID: $($response.request_id)"
    Write-Host "Decision: $($response.decision)"
    Write-Host "Reasoning: $($response.reasoning)"
    Write-Host "Risk Level: $($response.risk_level)"
    Write-Host "Estimated Cost: Rs.$($response.estimated_cost)"
    Write-Host "Estimated Duration: $($response.estimated_duration) minutes"
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

# Test 2: Water Agent - Road Digging Request
Write-Host "`nTEST 2: Water Agent - Road Digging Permission" -ForegroundColor Yellow
Write-Host "================================================================================"

$waterRequest = @{
    request_type = "road_digging"
    location = "Main Street, Block A"
    priority = "medium"
    requester = "Engineering Department"
    coordinates = @(28.6139, 77.2090)
    details = @{
        purpose = "Infrastructure upgrade"
        depth = 2.0
        duration = 14
    }
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/water/request" -Method Post -Body $waterRequest -ContentType "application/json" -TimeoutSec 30
    
    Write-Host "API Response Received" -ForegroundColor Green
    Write-Host "Request ID: $($response.request_id)"
    Write-Host "Decision: $($response.decision)"
    Write-Host "Reasoning: $($response.reasoning)"
    Write-Host "Risk Score: $($response.risk_score)"
    Write-Host "Estimated Cost: Rs.$($response.estimated_cost)"
    Write-Host "Estimated Duration: $($response.estimated_duration_days) days"
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`nTEST SUMMARY" -ForegroundColor Green
Write-Host "================================================================================"
Write-Host "Fire Agent - Emergency Response: Tested"
Write-Host "Water Agent - Road Digging: Tested"
Write-Host "`nAPI Integration Tests Complete!" -ForegroundColor Green
Write-Host "================================================================================"
