param(
    [string]$RepoUrl = "",
    [string]$Branch = "main",
    [string]$Message = "update",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path .git)) {
    git init
    if ($RepoUrl -ne "") {
        git remote add origin $RepoUrl
    }
}

git add -A
git commit -m $Message 2>$null | Out-Null

if ($RepoUrl -ne "") {
    git branch -M $Branch
}

if ($Force) {
    git push -u origin $Branch --force
} else {
    git push -u origin $Branch
}

Write-Host "Push เสร็จสิ้น ✅" -ForegroundColor Green

