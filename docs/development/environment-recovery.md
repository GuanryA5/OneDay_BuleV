# BlueV 环境故障恢复指南

本指南提供了在 Windows + Git Bash 环境下遇到开发环境问题时的系统性恢复方案。

## 🚨 快速诊断

### 自动化健康检查
```bash
# 运行完整的环境健康检查
python scripts/health-check.py --verbose

# 尝试自动修复问题
python scripts/health-check.py --fix

# 生成详细报告
python scripts/health-check.py --output health-report.json
```

### 依赖状态检查
```bash
# 检查依赖版本状态
python scripts/dependency-monitor.py

# 包含安全扫描
python scripts/dependency-monitor.py --security-scan

# 生成依赖报告
python scripts/dependency-monitor.py --output dependency-report.json
```

## 🔧 常见问题与解决方案

### 1. Conda 环境问题

#### 问题：`conda activate` 不工作
```bash
# 症状
conda activate bluev-dev
# 错误: CommandNotFoundError: Your shell has not been properly configured

# 解决方案
conda init bash
source ~/.bash_profile
# 或重启 Git Bash
```

#### 问题：环境损坏或依赖冲突
```bash
# 完全重建环境
conda env remove -n bluev-dev -y
conda clean --all -y

# 重新创建环境
python scripts/tasks.py setup --force
# 或手动创建
conda create -n bluev-dev python=3.12.11 -y
conda activate bluev-dev
conda install -c conda-forge pyside6 opencv numpy pillow -y
pip install -r requirements.txt -r requirements-dev.txt
```

#### 问题：Conda 环境路径问题
```bash
# 检查环境位置
conda env list

# 如果路径有问题，重新初始化
conda init --all
# 重启终端
```

### 2. 依赖安装问题

#### 问题：PySide6 安装失败
```bash
# 症状
pip install PySide6
# 错误: Failed building wheel for PySide6

# 解决方案 1: 使用 Conda
conda install -c conda-forge pyside6 -y

# 解决方案 2: 清理缓存重试
pip cache purge
pip install PySide6 --no-cache-dir

# 解决方案 3: 使用预编译版本
pip install PySide6-Essentials
```

#### 问题：PyAutoGUI 导入错误
```bash
# 症状
import pyautogui
# 错误: ImportError: No module named 'pyautogui'

# 解决方案
pip uninstall PyAutoGUI -y
pip install PyAutoGUI --no-cache-dir

# Windows 特定问题
pip install pillow --upgrade
```

#### 问题：OpenCV 导入问题
```bash
# 症状
import cv2
# 错误: ImportError: DLL load failed

# 解决方案 1: 重新安装
conda uninstall opencv -y
conda install -c conda-forge opencv -y

# 解决方案 2: 使用 pip 版本
pip uninstall opencv-python -y
pip install opencv-python-headless
```

### 3. Pre-commit 和代码质量工具问题

#### 问题：Pre-commit hooks 失败
```bash
# 症状
git commit -m "test"
# 错误: pre-commit hook failed

# 解决方案 1: 重新安装 hooks
pre-commit clean
pre-commit install --install-hooks

# 解决方案 2: 更新 hooks
pre-commit autoupdate

# 解决方案 3: 跳过 hooks (临时)
git commit -m "test" --no-verify
```

#### 问题：Ruff 检查失败
```bash
# 症状
ruff check .
# 错误: 大量格式问题

# 解决方案: 自动修复
ruff check . --fix
ruff format .

# 如果仍有问题，检查配置
cat pyproject.toml | grep -A 10 "\[tool.ruff\]"
```

#### 问题：MyPy 类型检查错误
```bash
# 症状
mypy bluev/
# 错误: 大量类型错误

# 解决方案 1: 安装类型存根
pip install types-requests types-setuptools

# 解决方案 2: 更新 MyPy 配置
# 编辑 pyproject.toml 中的 [tool.mypy] 部分

# 解决方案 3: 临时忽略
mypy bluev/ --ignore-missing-imports
```

### 4. 文档系统问题

#### 问题：MkDocs 服务器启动失败
```bash
# 症状
mkdocs serve
# 错误: Config file 'mkdocs.yml' does not exist

# 解决方案 1: 检查工作目录
pwd
# 应该在项目根目录

# 解决方案 2: 检查配置文件
ls -la mkdocs.yml
cat mkdocs.yml | head -10

# 解决方案 3: 重新安装 MkDocs
pip uninstall mkdocs mkdocs-material -y
pip install mkdocs mkdocs-material mkdocstrings[python]
```

#### 问题：文档构建警告
```bash
# 症状
mkdocs build
# 警告: 大量文件未找到

# 解决方案: 清理导航配置
# 编辑 mkdocs.yml，移除不存在的文件引用
```

### 5. Git 和版本控制问题

#### 问题：Git 配置问题
```bash
# 症状
git status
# 错误: fatal: not a git repository

# 解决方案 1: 检查是否在正确目录
pwd
ls -la .git

# 解决方案 2: 重新初始化 (谨慎)
git init
git remote add origin https://github.com/GuanryA5/OneDay_BuleV.git
```

#### 问题：文件权限问题
```bash
# 症状
bash scripts/setup-env.sh
# 错误: Permission denied

# 解决方案
chmod +x scripts/setup-env.sh
chmod +x scripts/*.sh
```

### 6. CI/CD 环境不一致

#### 问题：本地通过但 CI 失败
```bash
# 检查环境一致性
python scripts/health-check.py --verbose

# 检查 Python 版本
python --version
# 本地: 3.12.11, CI: 3.12.3 (兼容)

# 检查依赖版本
pip freeze > current-deps.txt
# 对比 requirements-lock.txt
```

#### 问题：CI 配置错误
```bash
# 检查 CI 配置
cat .github/workflows/ci.yml | grep -A 5 "python-version"

# 验证 Windows 环境
cat .github/workflows/ci.yml | grep "runs-on"
# 应该都是 windows-latest
```

## 🔄 系统性恢复流程

### Level 1: 轻度修复 (5-10 分钟)
```bash
# 1. 重新激活环境
conda activate bluev-dev

# 2. 更新依赖
pip install -r requirements.txt -r requirements-dev.txt --upgrade

# 3. 重新安装 hooks
pre-commit install --install-hooks

# 4. 运行健康检查
python scripts/health-check.py
```

### Level 2: 中度修复 (15-30 分钟)
```bash
# 1. 清理缓存
conda clean --all -y
pip cache purge
pre-commit clean

# 2. 重新安装核心依赖
conda install -c conda-forge pyside6 opencv numpy pillow -y --force-reinstall

# 3. 重新安装开发工具
pip install ruff mypy pytest mkdocs pre-commit --force-reinstall

# 4. 验证环境
python scripts/tasks.py test
python scripts/tasks.py lint
```

### Level 3: 完全重建 (30-60 分钟)
```bash
# 1. 备份重要文件
cp requirements-lock.txt requirements-lock.backup
cp environment.yml environment.backup

# 2. 完全删除环境
conda env remove -n bluev-dev -y

# 3. 重新创建环境
python scripts/tasks.py setup --force

# 4. 验证所有功能
python scripts/health-check.py --fix
python scripts/dependency-monitor.py
python scripts/tasks.py test -v
```

## 📊 监控和预防

### 定期健康检查
```bash
# 每周运行一次完整检查
python scripts/health-check.py --output weekly-health.json

# 每月运行依赖监控
python scripts/dependency-monitor.py --security-scan --output monthly-deps.json
```

### 自动化监控脚本
```bash
# 创建定期检查脚本
cat > scripts/weekly-check.sh << 'EOF'
#!/bin/bash
echo "$(date): 开始每周健康检查"
python scripts/health-check.py --output "health-$(date +%Y%m%d).json"
python scripts/dependency-monitor.py --output "deps-$(date +%Y%m%d).json"
echo "$(date): 检查完成"
EOF

chmod +x scripts/weekly-check.sh
```

### 环境快照
```bash
# 创建环境快照
conda env export > environment-snapshot-$(date +%Y%m%d).yml
pip freeze > requirements-snapshot-$(date +%Y%m%d).txt

# 保存项目状态
git status > git-status-$(date +%Y%m%d).txt
```

## 🆘 紧急联系和资源

### 获取帮助的优先级
1. **自动化工具**: 使用健康检查和依赖监控脚本
2. **文档查阅**: 查看相关文档和故障排除指南
3. **社区资源**: 查看 GitHub Issues 和相关项目文档
4. **重新设置**: 使用完全重建流程

### 有用的命令速查
```bash
# 环境信息
conda info
conda env list
python --version
pip --version

# 项目状态
git status
git log --oneline -5
ls -la

# 快速修复
python scripts/tasks.py setup --force
python scripts/health-check.py --fix
```

---

**最后更新**: 2025-01-09
**适用版本**: BlueV v1.0+
**环境**: Windows 11 + Git Bash + Conda
