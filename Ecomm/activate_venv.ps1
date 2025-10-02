# Activate Django Virtual Environment in VSCode PowerShell
Write-Host "Activating virtual environment..." -ForegroundColor Green

# Set execution policy for this session only (avoids permanent change)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Activate your venv
& "$PSScriptRoot\.venv\Scripts\Activate.ps1"

Write-Host "Virtual environment activated!" -ForegroundColor Yellow
