# 增量测试安装脚本
# 用法: ./test-install.ps1 -Stage 1|2|3|4

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet(1,2,3,4)]
    [int]$Stage
)

$ErrorActionPreference = "Stop"

# 检测目标路径
if ($IsWindows -or $env:OS -eq "Windows_NT") {
    $targetBase = "$env:USERPROFILE\.qclaw\workspace"
} else {
    $targetBase = "$env:HOME/.openclaw/workspace"
}

$filesDir = Join-Path $PSScriptRoot "files"

Write-Host "测试阶段 $Stage" -ForegroundColor Cyan
Write-Host "目标路径: $targetBase`n" -ForegroundColor Gray

# 创建目录
if (-not (Test-Path $targetBase)) {
    New-Item -ItemType Directory -Force -Path $targetBase | Out-Null
}

# 按阶段定义要安装的文件
$stageFiles = @{
    1 = @(
        "SOUL.md",
        "USER.md",
        "IDENTITY.md"
    )
    2 = @(
        "SOUL.md",
        "USER.md",
        "IDENTITY.md",
        "AGENTS.md",
        "TOOLS.md"
    )
    3 = @(
        "SOUL.md",
        "USER.md",
        "IDENTITY.md",
        "AGENTS.md",
        "TOOLS.md",
        "rules/code.md",
        "rules/memory.md"
    )
    4 = @(
        "SOUL.md",
        "USER.md",
        "IDENTITY.md",
        "AGENTS.md",
        "TOOLS.md",
        "HEARTBEAT.md",
        "SELF_IMPROVEMENT.md",
        "CONFIG_MAP.md",
        "rules/code.md",
        "rules/memory.md",
        "rules/proactive.md",
        "rules/research.md",
        "rules/toolchain.md",
        "rules/rule-evolution.md",
        "rules/dev-mode.md"
    )
}

$files = $stageFiles[$Stage]

# 确保子目录存在
if ($Stage -ge 3) {
    $rulesDir = Join-Path $targetBase "rules"
    if (-not (Test-Path $rulesDir)) {
        New-Item -ItemType Directory -Force -Path $rulesDir | Out-Null
    }
}

# 复制文件
foreach ($file in $files) {
    $srcFile = Join-Path $filesDir $file
    $dstFile = Join-Path $targetBase $file
    
    if (Test-Path $srcFile) {
        Copy-Item $srcFile $dstFile -Force
        Write-Host "[OK] $file" -ForegroundColor Green
    } else {
        Write-Host "[跳过] $file (源文件不存在)" -ForegroundColor Yellow
    }
}

Write-Host "`n阶段 $Stage 安装完成" -ForegroundColor Cyan
Write-Host "重启 OpenClaw/QClaw 后生效" -ForegroundColor Magenta
Write-Host "`n测试要点:" -ForegroundColor White

switch ($Stage) {
    1 {
        Write-Host "  - AI 是否按 DevCore 风格说话？"
        Write-Host "  - 是否理解极简指令？"
    }
    2 {
        Write-Host "  - 说'开启计划模式' → 是否输出详细计划？"
        Write-Host "  - 删除文件 → 是否先确认？"
    }
    3 {
        Write-Host "  - 说'审查代码' → 是否加载 code.md 规范？"
        Write-Host "  - 说'按规范写' → 是否走 Python 规范？"
    }
    4 {
        Write-Host "  - 犯错后是否引用历史教训？"
        Write-Host "  - 定时任务是否触发？"
        Write-Host "  - 所有规则是否生效？"
    }
}
