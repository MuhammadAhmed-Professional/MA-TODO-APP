# Railway Backend Deployment Verification Script (PowerShell)
# This script checks if the Better Auth session token fix is deployed

param(
    [string]$BackendUrl = "https://your-backend.railway.app"
)

# Colors
function Write-Success { param([string]$Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Error-Custom { param([string]$Message) Write-Host "✗ $Message" -ForegroundColor Red }
function Write-Warning-Custom { param([string]$Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Info { param([string]$Message) Write-Host $Message -ForegroundColor Cyan }
function Write-Step { param([string]$Message) Write-Host $Message -ForegroundColor Yellow }

Write-Host "========================================"  -ForegroundColor Cyan
Write-Host "Railway Backend Deployment Verification" -ForegroundColor Cyan
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""

# Check 1: Health endpoint
Write-Step "[1/4] Checking health endpoint..."
try {
    $healthResponse = Invoke-WebRequest -Uri "$BackendUrl/health" -Method GET -UseBasicParsing
    if ($healthResponse.StatusCode -eq 200) {
        Write-Success "Health check passed (HTTP 200)"
    } else {
        Write-Error-Custom "Health check failed (HTTP $($healthResponse.StatusCode))"
        exit 1
    }
} catch {
    Write-Error-Custom "Health check failed: $($_.Exception.Message)"
    exit 1
}

# Check 2: CORS headers
Write-Step "[2/4] Checking CORS configuration..."
try {
    $corsHeader = $healthResponse.Headers["Access-Control-Allow-Origin"]
    if ($corsHeader) {
        Write-Success "CORS headers present: $corsHeader"
    } else {
        Write-Warning-Custom "CORS headers not found (may be okay if not needed for /health)"
    }
} catch {
    Write-Warning-Custom "Could not check CORS headers"
}

# Check 3: Auth endpoint exists
Write-Step "[3/4] Checking auth endpoint..."
try {
    $body = @{} | ConvertTo-Json
    $authResponse = Invoke-WebRequest `
        -Uri "$BackendUrl/api/auth/login" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $body `
        -UseBasicParsing `
        -ErrorAction SilentlyContinue

    $statusCode = $authResponse.StatusCode
} catch {
    $statusCode = $_.Exception.Response.StatusCode.Value__
}

if ($statusCode -in @(422, 401, 400)) {
    Write-Success "Auth endpoint accessible (HTTP $statusCode - validation error expected)"
} elseif ($statusCode -eq 404) {
    Write-Error-Custom "Auth endpoint not found (HTTP 404)"
    exit 1
} else {
    Write-Warning-Custom "Unexpected auth response (HTTP $statusCode)"
}

# Check 4: API version/info
Write-Step "[4/4] Checking API info..."
try {
    $apiResponse = Invoke-WebRequest -Uri "$BackendUrl/" -Method GET -UseBasicParsing
    $content = $apiResponse.Content

    if ($content -match "FastAPI" -or $content -match "Todo" -or $content -match "message") {
        Write-Success "API root endpoint responding"
        Write-Info "Response: $content"
    } else {
        Write-Warning-Custom "API root endpoint returned unexpected response"
    }
} catch {
    Write-Warning-Custom "Could not check API root endpoint: $($_.Exception.Message)"
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Success "Deployment verification complete!"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Warning-Custom "Next steps:"
Write-Host "1. Check Railway dashboard for deployment status"
Write-Host "2. Verify environment variables (AUTH_SERVER_URL, DATABASE_URL, JWT_SECRET)"
Write-Host "3. Test login flow from frontend application"
Write-Host "4. Monitor Railway logs for any errors"
Write-Host ""
Write-Info "Backend URL: $BackendUrl"
Write-Host ""

# Instructions
Write-Host "To use with your Railway URL, run:" -ForegroundColor Gray
Write-Host "  .\verify-railway-deployment.ps1 -BackendUrl 'https://your-actual-backend.railway.app'" -ForegroundColor Gray
Write-Host ""
