#!/bin/bash
# BlueV 开发环境设置脚本 (Windows + Git Bash 兼容)
# 用途: 一键设置完整的开发环境

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 未找到，请先安装"
        return 1
    fi
    return 0
}

# 主函数
main() {
    echo "🚀 BlueV Windows + Git Bash 环境设置"
    echo "======================================"

    # 检查必要工具
    log_info "检查必要工具..."

    if ! check_command "conda"; then
        log_error "Conda 未找到，请先安装 Anaconda 或 Miniconda"
        exit 1
    fi

    if ! check_command "git"; then
        log_error "Git 未找到，请先安装 Git"
        exit 1
    fi

    log_success "必要工具检查通过"

    # 检查或创建 Conda 环境
    log_info "检查 Conda 环境..."

    if conda env list | grep -q "bluev-dev"; then
        log_success "bluev-dev 环境已存在"
    else
        log_info "创建 bluev-dev Conda 环境..."
        conda create -n bluev-dev python=3.12.11 -y
        log_success "bluev-dev 环境创建完成"
    fi

    # 激活环境
    log_info "激活 bluev-dev 环境..."
    eval "$(conda shell.bash hook)"
    conda activate bluev-dev

    # 验证环境激活
    if [[ "$CONDA_DEFAULT_ENV" != "bluev-dev" ]]; then
        log_error "环境激活失败"
        exit 1
    fi

    log_success "环境激活成功: $CONDA_DEFAULT_ENV"

    # 安装依赖
    log_info "安装核心依赖 (Conda)..."
    conda install -c conda-forge pyside6 opencv numpy pillow -y

    log_info "安装项目依赖 (pip)..."
    pip install -r requirements.txt

    log_info "安装开发依赖 (pip)..."
    pip install -r requirements-dev.txt

    # 设置 Pre-commit hooks
    log_info "设置 Pre-commit hooks..."
    pre-commit install --install-hooks

    # 验证环境
    log_info "验证环境配置..."

    # 检查关键依赖
    python -c "import PySide6; print(f'✅ PySide6: {PySide6.__version__}')"
    python -c "import cv2; print(f'✅ OpenCV: {cv2.__version__}')"
    python -c "import numpy; print(f'✅ NumPy: {numpy.__version__}')"
    python -c "import pyautogui; print(f'✅ PyAutoGUI: {pyautogui.__version__}')"

    # 运行代码检查
    log_info "运行代码质量检查..."
    ruff check . --quiet || log_warning "代码检查发现问题，请修复"

    # 完成
    echo ""
    echo "======================================"
    log_success "🎉 BlueV 开发环境设置完成！"
    echo ""
    echo "📋 下一步操作:"
    echo "  1. 激活环境: conda activate bluev-dev"
    echo "  2. 运行测试: python -m pytest tests/"
    echo "  3. 启动应用: python -m bluev"
    echo "  4. 查看文档: mkdocs serve"
    echo ""
    echo "🔧 常用命令:"
    echo "  • 代码检查: ruff check ."
    echo "  • 代码格式化: ruff format ."
    echo "  • 类型检查: mypy bluev/"
    echo "  • 运行测试: pytest tests/ -v"
    echo ""
}

# 执行主函数
main "$@"
