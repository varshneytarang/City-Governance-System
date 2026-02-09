# Agent Constellation Video Optimizer
# This script optimizes your video for web playback
# Requires: FFmpeg (download from https://ffmpeg.org)

param(
    [Parameter(Mandatory=$true)]
    [string]$InputVideo,
    
    [string]$OutputDir = "public\videos",
    
    [switch]$SkipMobile,
    
    [switch]$SkipWebM,
    
    [int]$Quality = 23  # Lower = better quality, larger file (18-28 recommended)
)

# Check if FFmpeg is installed
function Test-FFmpeg {
    try {
        $null = ffmpeg -version 2>&1
        return $true
    }
    catch {
        return $false
    }
}

# Display file size
function Get-FileSize {
    param([string]$Path)
    if (Test-Path $Path) {
        $size = (Get-Item $Path).Length / 1MB
        return "{0:N2} MB" -f $size
    }
    return "N/A"
}

# Main script
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   AGENT CONSTELLATION VIDEO OPTIMIZER                    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check FFmpeg
if (-not (Test-FFmpeg)) {
    Write-Host "❌ ERROR: FFmpeg is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install FFmpeg from: https://ffmpeg.org/download.html" -ForegroundColor Yellow
    Write-Host "Or use Chocolatey: choco install ffmpeg" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✅ FFmpeg detected" -ForegroundColor Green

# Check input file
if (-not (Test-Path $InputVideo)) {
    Write-Host "❌ ERROR: Input file not found: $InputVideo" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Input file found: $InputVideo" -ForegroundColor Green
Write-Host "   Original size: $(Get-FileSize $InputVideo)" -ForegroundColor White
Write-Host ""

# Create output directory
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
Write-Host "📁 Output directory: $OutputDir" -ForegroundColor Cyan
Write-Host ""

# Progress indicator
$totalSteps = 4
if ($SkipMobile) { $totalSteps-- }
if ($SkipWebM) { $totalSteps-- }
$currentStep = 0

# 1. Main MP4 (1080p, 60fps)
$currentStep++
Write-Host "[$currentStep/$totalSteps] 📹 Creating main MP4 (1080p 60fps)..." -ForegroundColor Yellow
Write-Host "    Quality: CRF $Quality (lower = better, 18-28 recommended)" -ForegroundColor Gray

$mp4Output = Join-Path $OutputDir "agent-constellation-loop.mp4"

ffmpeg -i $InputVideo `
    -c:v libx264 `
    -profile:v high `
    -level 4.2 `
    -preset slow `
    -crf $Quality `
    -movflags +faststart `
    -pix_fmt yuv420p `
    -vf "scale=1920:1080:flags=lanczos" `
    -r 60 `
    -an `
    $mp4Output -y 2>&1 | Out-Null

if (Test-Path $mp4Output) {
    Write-Host "    ✅ Created: $(Get-FileSize $mp4Output)" -ForegroundColor Green
} else {
    Write-Host "    ❌ Failed to create MP4" -ForegroundColor Red
}
Write-Host ""

# 2. WebM version
if (-not $SkipWebM) {
    $currentStep++
    Write-Host "[$currentStep/$totalSteps] 🎥 Creating WebM version (fallback)..." -ForegroundColor Yellow
    
    $webmOutput = Join-Path $OutputDir "agent-constellation-loop.webm"
    
    ffmpeg -i $InputVideo `
        -c:v libvpx-vp9 `
        -b:v 2M `
        -maxrate 3M `
        -bufsize 6M `
        -vf "scale=1920:1080:flags=lanczos" `
        -r 60 `
        -an `
        $webmOutput -y 2>&1 | Out-Null
    
    if (Test-Path $webmOutput) {
        Write-Host "    ✅ Created: $(Get-FileSize $webmOutput)" -ForegroundColor Green
    } else {
        Write-Host "    ❌ Failed to create WebM" -ForegroundColor Red
    }
    Write-Host ""
}

# 3. Mobile version
if (-not $SkipMobile) {
    $currentStep++
    Write-Host "[$currentStep/$totalSteps] 📱 Creating mobile version (720p 30fps)..." -ForegroundColor Yellow
    
    $mobileOutput = Join-Path $OutputDir "agent-constellation-mobile.mp4"
    
    ffmpeg -i $InputVideo `
        -c:v libx264 `
        -profile:v main `
        -crf ($Quality + 5) `
        -movflags +faststart `
        -pix_fmt yuv420p `
        -vf "scale=1280:720:flags=lanczos" `
        -r 30 `
        -an `
        $mobileOutput -y 2>&1 | Out-Null
    
    if (Test-Path $mobileOutput) {
        Write-Host "    ✅ Created: $(Get-FileSize $mobileOutput)" -ForegroundColor Green
    } else {
        Write-Host "    ❌ Failed to create mobile version" -ForegroundColor Red
    }
    Write-Host ""
}

# 4. Poster frame
$currentStep++
Write-Host "[$currentStep/$totalSteps] 🖼️  Extracting poster frame..." -ForegroundColor Yellow

$posterOutput = Join-Path $OutputDir "agent-constellation-poster.jpg"

ffmpeg -i $InputVideo `
    -ss 00:00:02 `
    -vframes 1 `
    -q:v 2 `
    $posterOutput -y 2>&1 | Out-Null

if (Test-Path $posterOutput) {
    Write-Host "    ✅ Created: $(Get-FileSize $posterOutput)" -ForegroundColor Green
} else {
    Write-Host "    ❌ Failed to create poster" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅ OPTIMIZATION COMPLETE                               ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Output Files:" -ForegroundColor Cyan
Write-Host ""

Get-ChildItem "$OutputDir\agent-constellation-*" | ForEach-Object {
    $icon = switch ($_.Extension) {
        ".mp4"  { "🎬" }
        ".webm" { "🎥" }
        ".jpg"  { "🖼️ " }
        default { "📄" }
    }
    $size = "{0:N2} MB" -f ($_.Length / 1MB)
    Write-Host "  $icon $($_.Name.PadRight(40)) $size" -ForegroundColor White
}

Write-Host ""
Write-Host "📍 Files saved to: $OutputDir" -ForegroundColor Cyan
Write-Host ""

# Calculate compression ratio
$originalSize = (Get-Item $InputVideo).Length
$mainOutputSize = (Get-Item $mp4Output).Length
$compressionRatio = [math]::Round((1 - ($mainOutputSize / $originalSize)) * 100, 1)

if ($compressionRatio -gt 0) {
    Write-Host "💾 Compression: $compressionRatio% smaller than original" -ForegroundColor Green
} else {
    Write-Host "⚠️  Note: Output is larger than input (Quality=$Quality may be too high)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Review the video files" -ForegroundColor White
Write-Host "   2. Test playback in browser" -ForegroundColor White
Write-Host "   3. Deploy to your frontend/public/videos/ folder" -ForegroundColor White
Write-Host "   4. Update component import in your React app" -ForegroundColor White
Write-Host ""

# Quality recommendations
if ($Quality -gt 26) {
    Write-Host "💡 Tip: Quality setting is high ($Quality). Consider lowering for smaller file size." -ForegroundColor Yellow
    Write-Host "   Run again with: -Quality 23" -ForegroundColor Gray
    Write-Host ""
} elseif ($Quality -lt 20) {
    Write-Host "💡 Tip: Quality setting is very low ($Quality). Files will be small but may look pixelated." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "✨ Done!" -ForegroundColor Green
Write-Host ""
