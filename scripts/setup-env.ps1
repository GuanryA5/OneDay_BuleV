# BlueV 开发环境设置脚本 (PowerShell 版本)
# 用途: Windows 原生 PowerShell 环境下的一键设置

param(
    [switch]$Force,
    [switch]$SkipTests
)

# 错误处理
$ErrorActionPreference = "Stop"

# 颜色函数
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# 检查命令是否存在
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# 主函数
function Main {
    Write-Host "🚀 BlueV Windows PowerShell 环境设置" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan

    # 检查必要工具
    Write-Info "检查必要工具..."

    if (-not (Test-Command "conda")) {
        Write-Error "Conda 未找到，请先安装 Anaconda 或 Miniconda"
        exit 1
    }

    if (-not (Test-Command "git")) {
        Write-Error "Git 未找到，请先安装 Git"
        exit 1
    }

    Write-Success "必要工具检查通过"

    # 检查或创建 Conda 环境
    Write-Info "检查 Conda 环境..."

    $envExists = conda env list | Select-String "bluev-dev"

    if ($envExists -and -not $Force) {
        Write-Success "bluev-dev 环境已存在"
    }
    else {
        if ($Force -and $envExists) {
            Write-Info "强制重建 bluev-dev 环境..."
            conda env remove -n bluev-dev -y
        }

        Write-Info "创建 bluev-dev Conda 环境..."
        conda create -n bluev-dev python=3.12.11 -y
        Write-Success "bluev-dev 环境创建完成"
    }

    # 激活环境并安装依赖
    Write-Info "激活环境并安装依赖..."

    # 使用 conda run 在指定环境中执行命令
    Write-Info "安装核心依赖 (Conda)..."
    conda install -n bluev-dev -c conda-forge pyside6 opencv numpy pillow -y

    Write-Info "安装项目依赖 (pip)..."
    conda run -n bluev-dev pip install -r requirements.txt

    Write-Info "安装开发依赖 (pip)..."
    conda run -n bluev-dev pip install -r requirements-dev.txt

    # 设置 Pre-commit hooks
    Write-Info "设置 Pre-commit hooks..."
    conda run -n bluev-dev pre-commit install --install-hooks

    # 验证环境
    Write-Info "验证环境配置..."

    try {
        conda run -n bluev-dev python -c "import PySide6; print(f'✅ PySide6: {PySide6.__version__}')"
        conda run -n bluev-dev python -c "import cv2; print(f'✅ OpenCV: {cv2.__version__}')"
        conda run -n bluev-dev python -c "import numpy; print(f'✅ NumPy: {numpy.__version__}')"
        conda run -n bluev-dev python -c "import pyautogui; print(f'✅ PyAutoGUI: {pyautogui.__version__}')"
    }
    catch {
        Write-Warning "依赖验证时出现问题: $_"
    }

    # 运行代码检查
    if (-not $SkipTests) {
        Write-Info "运行代码质量检查..."
        try {
            conda run -n bluev-dev ruff check . --quiet
        }
        catch {
            Write-Warning "代码检查发现问题，请修复"
        }
    }

    # 完成
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Success "🎉 BlueV 开发环境设置完成！"
    Write-Host ""
    Write-Host "📋 下一步操作:" -ForegroundColor Yellow
    Write-Host "  1. 激活环境: conda activate bluev-dev"
    Write-Host "  2. 运行测试: python -m pytest tests/"
    Write-Host "  3. 启动应用: python -m bluev"
    Write-Host "  4. 查看文档: mkdocs serve"
    Write-Host ""
    Write-Host "🔧 常用命令:" -ForegroundColor Yellow
    Write-Host "  • 代码检查: ruff check ."
    Write-Host "  • 代码格式化: ruff format ."
    Write-Host "  • 类型检查: mypy bluev/"
    Write-Host "  • 运行测试: pytest tests/ -v"
    Write-Host ""
    Write-Host "💡 PowerShell 使用提示:" -ForegroundColor Cyan
    Write-Host "  • 如果遇到执行策略问题，运行: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
    Write-Host "  • 重新运行并强制重建环境: .\scripts\setup-env.ps1 -Force"
    Write-Host "  • 跳过测试快速设置: .\scripts\setup-env.ps1 -SkipTests"
}

# 执行主函数
try {
    Main
}
catch {
    Write-Error "设置过程中发生错误: $_"
    exit 1
}
