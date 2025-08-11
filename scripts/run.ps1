param(
    [ValidateSet("webcam", "realsense")] [string]$Source = "webcam",
    [ValidateSet("GPU", "CPU")] [string]$Device = "GPU",
    [string]$Model = "yolov8n.pt",
    [double]$Conf = 0.5,
    [switch]$Show,
    [switch]$Save,
    [int]$WebcamIndex = 0,
    [switch]$DisableCudnn,
    [switch]$SendToKuka,
    [string]$KukaHost = "127.0.0.1",
    [int]$KukaPort = 30010,
    [ValidateSet("udp", "tcp")] [string]$KukaProtocol = "udp"
)

$ErrorActionPreference = "Stop"

& .\.venv\Scripts\Activate.ps1

$argsList = @()
$argsList += @("--source", $Source)
$argsList += @("--device", $Device)
$argsList += @("--model", $Model)
$argsList += @("--conf", $Conf)
$argsList += @("--webcam-index", $WebcamIndex)
if ($Show) { $argsList += "--show" }
if ($Save) { $argsList += "--save" }
if ($DisableCudnn) { $argsList += "--disable-cudnn" }
if ($SendToKuka) {
    $argsList += "--send-to-kuka"
    $argsList += @("--kuka-host", $KukaHost)
    $argsList += @("--kuka-port", $KukaPort)
    $argsList += @("--kuka-protocol", $KukaProtocol)
}

python -m src.app @argsList

