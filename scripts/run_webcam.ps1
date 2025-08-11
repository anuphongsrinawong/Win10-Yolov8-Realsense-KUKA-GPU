param(
    [ValidateSet("GPU", "CPU")] [string]$Device = "GPU",
    [int]$WebcamIndex = 0,
    [double]$Conf = 0.5,
    [switch]$DisableCudnn
)

& .\.venv\Scripts\Activate.ps1
$argsList = @("--source", "webcam", "--device", $Device, "--webcam-index", $WebcamIndex, "--conf", $Conf, "--show")
if ($DisableCudnn) { $argsList += "--disable-cudnn" }
python -m src.app @argsList

