# DevOps 工具链故障排除指南

## 🚨 快速诊断

遇到问题时，首先运行自动诊断脚本：

```bash
# 运行完整系统诊断
python scripts/error_recovery.py

# 运行快速验证
python scripts/quick_verify.py

# 运行性能基准测试
python scripts/performance_benchmark.py
```

## 🔧 常见问题解决方案

### 1. Pre-commit Hooks 问题

#### 问题：Pre-commit hooks 安装失败

**症状**:
```bash
pre-commit install
# 报错：command not found 或权限错误
```

**解决方案**:
```bash
# 方案 1: 重新安装 pre-commit
pip uninstall pre-commit
pip install pre-commit

# 方案 2: 使用虚拟环境中的 pre-commit
venv/Scripts/python -m pip install pre-commit
venv/Scripts/python -m pre_commit install

# 方案 3: 检查权限（Linux/macOS）
sudo chown -R $USER:$USER .git/hooks/
```

#### 问题：Pre-commit hooks 执行超时

**症状**:
```bash
git commit -m "test"
# hooks 运行很长时间后超时
```

**解决方案**:
```bash
# 方案 1: 清理缓存
pre-commit clean
pre-commit install

# 方案 2: 跳过 hooks（紧急情况）
git commit -m "emergency fix" --no-verify

# 方案 3: 手动运行检查
ruff check . --fix
ruff format .
git add .
git commit -m "fix: code quality improvements"
```

#### 问题：Ruff 在 pre-commit 中失败

**症状**:
```bash
ruff....................................................................Failed
- hook id: ruff
- exit code: 1
```

**解决方案**:
```bash
# 查看具体错误
ruff check .

# 自动修复可修复的问题
ruff check . --fix

# 手动修复剩余问题后重新提交
git add .
git commit -m "fix: resolve ruff issues"
```

### 2. Ruff 配置问题

#### 问题：Ruff 配置不生效

**症状**:
- Ruff 使用默认配置而不是项目配置
- 某些规则没有被应用

**解决方案**:
```bash
# 检查配置文件位置
ls -la pyproject.toml

# 验证配置语法
python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb')))"

# 查看当前配置
ruff check --show-settings
```

#### 问题：Ruff 检查过于严格

**症状**:
- 大量误报
- 合理的代码被标记为错误

**解决方案**:
在 `pyproject.toml` 中调整配置：

```toml
[tool.ruff.lint]
# 添加需要忽略的规则
ignore = ["E501", "S101", "T201", "N818", "UP009", "新规则代码"]

# 或者针对特定文件忽略
[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]  # 测试文件允许 assert
"scripts/*" = ["T201"]  # 脚本文件允许 print
```

### 3. GitHub Actions CI/CD 问题

#### 问题：CI 流程失败

**症状**:
- GitHub Actions 工作流失败
- 测试在本地通过但在 CI 中失败

**解决方案**:
```bash
# 本地模拟 CI 环境
python -m pytest tests/ --cov=./bluev --cov-report=xml

# 检查平台特定问题
# Windows
pytest tests/ -v --tb=short

# Linux (使用 Docker)
docker run --rm -v $(pwd):/app -w /app python:3.8 bash -c "pip install -r requirements.txt && pytest"
```

#### 问题：依赖安装失败

**症状**:
```
ERROR: Could not find a version that satisfies the requirement
```

**解决方案**:
1. 检查 `requirements.txt` 中的版本约束
2. 更新 GitHub Actions 中的 Python 版本
3. 添加平台特定的依赖处理：

```yaml
- name: Install system dependencies (Linux)
  if: runner.os == 'Linux'
  run: |
    sudo apt-get update
    sudo apt-get install -y python3-dev
```

#### 问题：PySide6 在 CI 中失败

**症状**:
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
```

**解决方案**:
已在 CI 配置中添加虚拟显示器支持：

```yaml
- name: Install system dependencies (Linux)
  if: runner.os == 'Linux'
  run: |
    sudo apt-get update
    sudo apt-get install -y xvfb libxkbcommon-x11-0

- name: Run tests
  run: |
    if [ "$RUNNER_OS" == "Linux" ]; then
      xvfb-run -a python -m pytest tests/
    else
      python -m pytest tests/
    fi
```

### 4. 测试相关问题

#### 问题：测试覆盖率不足

**症状**:
```
TOTAL coverage: 65%
Required coverage: 80%
```

**解决方案**:
```bash
# 查看详细覆盖率报告
pytest --cov=bluev --cov-report=html
# 打开 htmlcov/index.html 查看详情

# 查看未覆盖的行
pytest --cov=bluev --cov-report=term-missing

# 添加测试用例覆盖缺失的代码
```

#### 问题：测试运行缓慢

**症状**:
- 测试执行时间过长
- CI 超时

**解决方案**:
```bash
# 并行运行测试
pip install pytest-xdist
pytest -n auto

# 只运行快速测试
pytest -m "not slow"

# 跳过集成测试
pytest tests/unit/
```

### 5. 文档构建问题

#### 问题：MkDocs 构建失败

**症状**:
```
mkdocs build
ERROR: Config file 'mkdocs.yml' does not exist
```

**解决方案**:
```bash
# 检查配置文件
ls -la mkdocs.yml

# 验证配置语法
mkdocs build --strict

# 安装缺失的插件
pip install mkdocs-material mkdocstrings[python]
```

#### 问题：文档部署失败

**症状**:
- GitHub Pages 部署失败
- 文档网站无法访问

**解决方案**:
1. 检查 GitHub Pages 设置
2. 确认 `.github/workflows/docs.yml` 配置正确
3. 手动触发部署：

```bash
# 本地构建测试
mkdocs build

# 手动部署到 GitHub Pages
mkdocs gh-deploy --force
```

### 6. 环境和依赖问题

#### 问题：虚拟环境损坏

**症状**:
```
ImportError: No module named 'bluev'
ModuleNotFoundError: No module named 'PySide6'
```

**解决方案**:
```bash
# 重建虚拟环境
rm -rf venv/
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### 问题：Python 版本不兼容

**症状**:
```
SyntaxError: invalid syntax (Python 3.7)
```

**解决方案**:
```bash
# 检查 Python 版本
python --version

# 使用正确的 Python 版本
python3.8 -m venv venv
# 或
py -3.8 -m venv venv
```

### 7. Git 和版本控制问题

#### 问题：Git hooks 权限错误

**症状**:
```
.git/hooks/pre-commit: Permission denied
```

**解决方案**:
```bash
# Linux/macOS
chmod +x .git/hooks/pre-commit

# Windows (使用 Git Bash)
git config core.filemode false
```

#### 问题：大文件提交被阻止

**症状**:
```
pre-commit hook failed: File size too large
```

**解决方案**:
```bash
# 检查大文件
find . -type f -size +10M

# 添加到 .gitignore
echo "large_file.bin" >> .gitignore

# 或者调整 pre-commit 配置
# 在 .pre-commit-config.yaml 中修改 check-added-large-files 的 args
```

## 🛠️ 高级故障排除

### 性能问题诊断

```bash
# 运行性能基准测试
python scripts/performance_benchmark.py

# 分析慢速测试
pytest --durations=10

# 检查内存使用
python -m memory_profiler scripts/performance_benchmark.py
```

### 网络问题

```bash
# 检查网络连接
ping github.com

# 使用镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ package_name

# 配置 Git 代理（如需要）
git config --global http.proxy http://proxy.example.com:8080
```

### 缓存问题

```bash
# 清理所有缓存
python scripts/error_recovery.py

# 手动清理
rm -rf __pycache__/
rm -rf .pytest_cache/
rm -rf .ruff_cache/
rm -rf .mypy_cache/
```

## 📞 获得帮助

### 自助资源

1. **运行诊断脚本**: `python scripts/error_recovery.py`
2. **查看日志**: 检查详细的错误信息
3. **搜索文档**: 在项目文档中搜索相关问题
4. **查看 GitHub Issues**: 搜索已知问题和解决方案

### 联系支持

如果问题仍未解决：

1. **创建 GitHub Issue**: 提供详细的错误信息和复现步骤
2. **包含环境信息**: Python 版本、操作系统、依赖版本
3. **提供日志**: 完整的错误日志和诊断脚本输出

### 问题报告模板

```markdown
## 问题描述
简要描述遇到的问题

## 环境信息
- 操作系统: Windows 10 / macOS 12 / Ubuntu 20.04
- Python 版本: 3.8.10
- 项目版本: v0.1.0

## 复现步骤
1. 执行命令 `xxx`
2. 出现错误 `yyy`

## 错误日志
```
粘贴完整的错误日志
```

## 期望行为
描述期望的正确行为

## 已尝试的解决方案
列出已经尝试过的解决方法
```

---

**记住**: 大多数问题都有标准的解决方案。遇到问题时保持冷静，按照本指南逐步排查，通常能够快速解决问题。
