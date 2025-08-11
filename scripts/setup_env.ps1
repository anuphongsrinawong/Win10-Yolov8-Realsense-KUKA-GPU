param(
    [ValidateSet("GPU", "CPU")] [string]$Device = "GPU",
    [switch]$WithRealSense,
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

Write-Host "[1/5] Create virtual environment (.venv)" -ForegroundColor Cyan
& $Python -m venv .venv

Write-Host "[2/5] Activate .venv" -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

Write-Host "[3/5] Upgrade pip/setuptools/wheel" -ForegroundColor Cyan
$VenvPy = Join-Path (Resolve-Path .).Path '.venv\Scripts\python.exe'
& $VenvPy -m pip install --upgrade pip setuptools wheel

Write-Host "[4/5] Install PyTorch for Device: $Device" -ForegroundColor Cyan
if ($Device -eq "GPU") {
    # Choose CUDA build that matches your system (example: cu118)
    & $VenvPy -m pip install torch==2.3.0+cu118 torchvision==0.18.0+cu118 torchaudio==2.3.0+cu118 -f https://download.pytorch.org/whl/torch_stable.html
} else {
    & $VenvPy -m pip install torch==2.3.0 torchvision==0.18.0 torchaudio==2.3.0
}

Write-Host "[5/5] Install project dependencies (requirements.txt)" -ForegroundColor Cyan
& $VenvPy -m pip install -r requirements.txt

if ($WithRealSense) {
    Write-Host "[+] Install pyrealsense2" -ForegroundColor Green
    try {
        & $VenvPy -m pip install pyrealsense2 --only-binary=:all: -i https://pypi.org/simple
    } catch {
        & $VenvPy -m pip install pyrealsense2
    }
}

Write-Host "Done" -ForegroundColor Green

