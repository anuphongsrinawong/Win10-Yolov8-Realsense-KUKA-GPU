param(
    [ValidateSet("GPU", "CPU")] [string]$Device = "GPU",
    [double]$Conf = 0.5
)

& .\.venv\Scripts\Activate.ps1
python -m src.app --source realsense --device $Device --conf $Conf --show

