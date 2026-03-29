# OpenClaw 配置迁移脚本
# 用法: ./install.ps1 [-Backup]

param(
    [switch]$Backup
)

$ErrorActionPreference = "Stop"

# 检测目标路径
if ($IsWindows -or $env:OS -eq "Windows_NT") {
    $targetBase = "$env:USERPROFILE\.qclaw\workspace"
} else {
    $targetBase = "$env:HOME/.openclaw/workspace"
}

$filesDir = Join-Path $PSScriptRoot "files"

Write-Host "目标路径: $targetBase" -ForegroundColor Cyan

# 创建目录
if (-not (Test-Path $targetBase)) {
    New-Item -ItemType Directory -Force -Path $targetBase | Out-Null
    Write-Host "创建目录: $targetBase" -ForegroundColor Green
}

$rulesDir = Join-Path $targetBase "rules"
$memoryDir = Join-Path $targetBase "memory"

if (-not (Test-Path $rulesDir)) {
    New-Item -ItemType Directory -Force -Path $rulesDir | Out-Null
}
if (-not (Test-Path $memoryDir)) {
    New-Item -ItemType Directory -Force -Path $memoryDir | Out-Null
}

# 备份现有文件
if ($Backup) {
    $backupDir = Join-Path $PSScriptRoot "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    
    Get-ChildItem -Path $filesDir -Recurse -File | ForEach-Object {
        $relativePath = $_.FullName.Substring($filesDir.Length + 1)
        $targetFile = Join-Path $targetBase $relativePath
        
        if (Test-Path $targetFile) {
            $backupFile = Join-Path $backupDir $relativePath
            $backupFileDir = Split-Path $backupFile -Parent
            if (-not (Test-Path $backupFileDir)) {
                New-Item -ItemType Directory -Force -Path $backupFileDir | Out-Null
            }
            Copy-Item $targetFile $backupFile -Force
            Write-Host "备份: $relativePath" -ForegroundColor Yellow
        }
    }
    
    Write-Host "备份目录: $backupDir" -ForegroundColor Yellow
}

# 复制文件
$copied = 0
Get-ChildItem -Path $filesDir -Recurse -File | ForEach-Object {
    $relativePath = $_.FullName.Substring($filesDir.Length + 1)
    $targetFile = Join-Path $targetBase $relativePath
    
    Copy-Item $_.FullName $targetFile -Force
    Write-Host "安装: $relativePath" -ForegroundColor Green
    $copied++
}

Write-Host "`n完成! 共复制 $copied 个文件" -ForegroundColor Cyan
Write-Host "重启 OpenClaw/QClaw 后生效" -ForegroundColor Magenta
