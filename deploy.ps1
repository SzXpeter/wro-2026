param(
    [string]$ConfigFile = "$PSScriptRoot\pi.env",
    [string]$WslDistro  = "Debian"
)

# env beolvasás
foreach ($line in Get-Content $ConfigFile) {
    if ($line -match '^\s*([^#][^=]+)=(.*)$') {
        Set-Variable -Name $matches[1].Trim() -Value $matches[2].Trim()
    }
}

$target = "${PI_USER}@${PI_HOST}:${PI_REMOTE_PATH}"

# Windows útvonal -> WSL útvonal (/mnt/c/...)
$wslRoot = (wsl -d $WslDistro wslpath -a "$PSScriptRoot")
if ($LASTEXITCODE -ne 0 -or -not $wslRoot) {
    Write-Error "wslpath sikertelen ($WslDistro)"
    exit 1
}
$wslRoot = $wslRoot.Trim()

$rsh = "sshpass -p $PI_PASSWORD ssh -o StrictHostKeyChecking=no"

Write-Host "Deploy -> $target"

# python/
wsl -d $WslDistro bash -c "rsync -avz -e '$rsh' '$wslRoot/python/' '$target/'"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# build/*.so
wsl -d $WslDistro bash -c "rsync -avz -e '$rsh' --include='*.so' --exclude='*' '$wslRoot/build/' '$target/lib/'"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Deploy kész. Futtatás a Pi-n..."

wsl -d $WslDistro bash -c "$rsh -t ${PI_USER}@${PI_HOST} 'cd ${PI_REMOTE_PATH} && python3 -u main.py'"
exit $LASTEXITCODE
