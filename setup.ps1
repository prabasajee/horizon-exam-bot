# Horizon Exam Bot Setup Script for Windows
# Run this script in PowerShell to set up the application

Write-Host "🚀 Horizon Exam Bot Setup Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check Python installation
Write-Host "`n📋 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.7+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check pip installation
Write-Host "`n📋 Checking pip installation..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pip not found. Please install pip" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`n📋 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "📁 Virtual environment already exists" -ForegroundColor Blue
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment created successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "`n📋 Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`n📋 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host "`n📋 Creating application directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "data" | Out-Null
Write-Host "✅ Directories created successfully" -ForegroundColor Green

# Run tests
Write-Host "`n📋 Running setup tests..." -ForegroundColor Yellow
python test_setup.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Setup tests passed" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed, but you can still try running the application" -ForegroundColor Yellow
}

# Final instructions
Write-Host "`n🎉 Setup completed!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "📚 Horizon Exam Bot is ready to use!" -ForegroundColor Green
Write-Host "`n🚀 To start the application:" -ForegroundColor Yellow
Write-Host "   python run.py" -ForegroundColor White
Write-Host "`n🌐 Then open your browser to:" -ForegroundColor Yellow
Write-Host "   http://localhost:5000" -ForegroundColor White
Write-Host "`n⏹️  To stop the server:" -ForegroundColor Yellow
Write-Host "   Press Ctrl+C" -ForegroundColor White
Write-Host "`n📖 For more information, see README.md" -ForegroundColor Blue

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
