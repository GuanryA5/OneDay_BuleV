# Windows 开发环境设置指南

本指南详细说明如何在 **Windows 11 + Git Bash** 环境下设置 BlueV 项目的完整开发环境。

## 🎯 环境要求

### 必需软件
- **Windows 11** (推荐) 或 Windows 10
- **Git for Windows** (包含 Git Bash)
- **Anaconda** 或 **Miniconda** (Python 环境管理)
- **Visual Studio Code** (推荐 IDE)

### 可选软件
- **Windows Terminal** (更好的终端体验)
- **PowerShell 7+** (现代化 PowerShell)

## 🚀 快速开始

### 方法 1: 自动化脚本 (推荐)

#### Git Bash 环境
```bash
# 克隆项目
git clone https://github.com/GuanryA5/OneDay_BuleV.git
cd OneDay_BuleV

# 运行自动化设置脚本
bash scripts/setup-env.sh
```

#### PowerShell 环境
```powershell
# 克隆项目
git clone https://github.com/GuanryA5/OneDay_BuleV.git
cd OneDay_BuleV

# 设置执行策略 (如果需要)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 运行自动化设置脚本
.\scripts\setup-env.ps1
```

#### Python 任务管理
```bash
# 使用 Python 任务管理脚本
python scripts/tasks.py setup

# 查看所有可用任务
python scripts/tasks.py --help
```

### 方法 2: 手动设置

#### 1. 创建 Conda 环境
```bash
# 创建专用环境
conda create -n bluev-dev python=3.12.11 -y

# 激活环境
conda activate bluev-dev
```

#### 2. 安装核心依赖
```bash
# 安装科学计算包 (通过 Conda 优化)
conda install -c conda-forge pyside6 opencv numpy pillow -y

# 安装项目依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

#### 3. 设置开发工具
```bash
# 安装 Pre-commit hooks
pre-commit install --install-hooks

# 验证环境
python -c "import PySide6; print(f'PySide6: {PySide6.__version__}')"
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
```

## 🔧 开发工具使用

### 代码质量检查
```bash
# 代码检查 (Ruff)
ruff check .

# 代码格式化 (Ruff)
ruff format .

# 类型检查 (MyPy)
mypy bluev/ --show-error-codes --pretty
```

### 测试运行
```bash
# 运行所有测试
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ -v --cov=bluev --cov-report=html
```

### 文档服务
```bash
# 启动文档服务器
mkdocs serve

# 构建文档
mkdocs build
```

### 任务管理脚本
```bash
# 使用 Python 任务管理脚本
python scripts/tasks.py lint          # 代码检查
python scripts/tasks.py format        # 代码格式化
python scripts/tasks.py test -v       # 运行测试
python scripts/tasks.py docs          # 启动文档服务器
python scripts/tasks.py clean         # 清理临时文件
```

## 🐛 常见问题解决

### 1. Conda 环境问题

**问题**: `conda activate` 命令不工作
```bash
# 解决方案: 初始化 Conda
conda init bash
# 重启 Git Bash 或运行
source ~/.bash_profile
```

**问题**: 环境创建失败
```bash
# 解决方案: 清理并重建
conda env remove -n bluev-dev -y
conda clean --all -y
conda create -n bluev-dev python=3.12.11 -y
```

### 2. 依赖安装问题

**问题**: PySide6 安装失败
```bash
# 解决方案: 使用 Conda 安装
conda install -c conda-forge pyside6 -y
```

**问题**: PyAutoGUI 导入错误
```bash
# 解决方案: 重新安装
pip uninstall PyAutoGUI -y
pip install PyAutoGUI --no-cache-dir
```

### 3. Pre-commit 问题

**问题**: Pre-commit hooks 失败
```bash
# 解决方案: 清理并重新安装
pre-commit clean
pre-commit install --install-hooks
```

**问题**: Ruff 检查失败
```bash
# 解决方案: 自动修复
ruff check . --fix
ruff format .
```

### 4. 路径和权限问题

**问题**: 脚本执行权限不足
```bash
# Git Bash 解决方案
chmod +x scripts/setup-env.sh

# PowerShell 解决方案
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**问题**: 路径格式问题
- 在 Git Bash 中使用正斜杠: `/d/dev/OneDay_BuleV`
- 在 PowerShell 中使用反斜杠: `D:\dev\OneDay_BuleV`
- Python 脚本会自动处理路径格式

## 📊 环境验证

### 完整验证脚本
```bash
# 激活环境
conda activate bluev-dev

# 验证 Python 版本
python --version

# 验证核心依赖
python -c "
import sys
print(f'Python: {sys.version}')

import PySide6
print(f'PySide6: {PySide6.__version__}')

import cv2
print(f'OpenCV: {cv2.__version__}')

import numpy
print(f'NumPy: {numpy.__version__}')

import pyautogui
print(f'PyAutoGUI: {pyautogui.__version__}')

print('✅ 所有核心依赖验证通过!')
"

# 验证开发工具
ruff --version
mypy --version
pytest --version
mkdocs --version

# 运行快速测试
python scripts/tasks.py lint
```

## 🔄 CI/CD 环境一致性

本地开发环境与 GitHub Actions CI 环境保持高度一致:

| 组件 | 本地环境 | CI 环境 | 兼容性 |
|------|----------|---------|--------|
| **操作系统** | Windows 11 | Windows 2022 | ✅ 完全兼容 |
| **Python** | 3.12.11 (Conda) | 3.12.3 (Actions) | ✅ 功能兼容 |
| **包管理** | Conda + pip | Conda + pip | ✅ 完全一致 |
| **Shell** | Git Bash | bash -l | ✅ 完全兼容 |
| **工具链** | Ruff + MyPy + pytest | Ruff + MyPy + pytest | ✅ 完全一致 |

## 📚 相关文档

- [最佳实践指南](best-practices.md)
- [DevOps 指南](devops-guide.md)
- [故障排除](troubleshooting.md)
- [项目状态](project-status.md)

## 🆘 获取帮助

如果遇到问题:

1. **查看日志**: 检查终端输出的错误信息
2. **查看文档**: 参考相关文档和故障排除指南
3. **重新设置**: 使用 `python scripts/tasks.py setup --force` 强制重建环境
4. **提交 Issue**: 在 GitHub 仓库中提交问题报告

---

**最后更新**: 2025-01-09
**适用版本**: BlueV v1.0+
**环境**: Windows 11 + Git Bash + Conda
