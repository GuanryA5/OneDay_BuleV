# Python 版本升级指南

## 📋 概述

本文档记录了 BlueV 项目从 Python 3.8+ 升级到 Python 3.9+ 的过程和相关配置更改。

## 🎯 升级目标

- **原版本要求**: Python 3.8+
- **新版本要求**: Python 3.9+
- **推荐版本**: Python 3.11 (用于 CI/CD)

## 📝 配置文件更改

### 1. pyproject.toml

```toml
# 更改前
requires-python = ">=3.8"
python_version = "3.8"

# 更改后
requires-python = ">=3.9"
python_version = "3.9"
```

**分类器更新**:
```toml
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",  # 移除 3.8
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",  # 新增 3.12
]
```

### 2. GitHub Actions 工作流

**文档部署工作流** (`.github/workflows/docs.yml`):
```yaml
# 更改前
python-version: '3.10'

# 更改后
python-version: '3.11'
```

### 3. Pre-commit 配置

同时更新了 pre-commit hooks 版本:
```yaml
# ruff 版本
rev: v0.12.11  # 从 v0.1.9 升级

# pre-commit-hooks 版本
rev: v6.0.0    # 从 v4.5.0 升级
```

## 🔄 升级步骤

### 1. 检查当前 Python 版本

```bash
python --version
```

### 2. 更新虚拟环境（如果需要）

如果当前使用 Python 3.8，建议重新创建虚拟环境：

```bash
# 删除旧环境
rm -rf venv

# 创建新环境 (Python 3.9+)
python3.9 -m venv venv
# 或
python3.11 -m venv venv

# 激活环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -e .[dev]
```

### 3. 更新 pre-commit hooks

```bash
pre-commit autoupdate
pre-commit install
```

## ✅ 验证升级

### 1. 检查 Python 版本兼容性

```bash
python -c "import sys; print(f'Python {sys.version}')"
```

### 2. 运行测试套件

```bash
pytest tests/
```

### 3. 检查代码质量

```bash
ruff check .
ruff format .
```

### 4. 验证文档构建

```bash
mkdocs build --clean --strict
```

## 🎯 Python 3.9+ 的优势

### 新特性支持

1. **字典合并操作符** (`|` 和 `|=`)
2. **改进的类型提示**
3. **更好的错误消息**
4. **性能改进**

### 示例代码

```python
# Python 3.9+ 字典合并
config = base_config | user_config

# 改进的类型提示
from typing import Annotated
def process_data(data: Annotated[str, "用户输入数据"]) -> bool:
    return True
```

## 🚨 注意事项

### 兼容性检查

- 确保所有依赖包支持 Python 3.9+
- 检查第三方库的版本兼容性
- 验证 CI/CD 环境的 Python 版本

### 潜在问题

1. **依赖包兼容性**: 某些老版本包可能不支持 Python 3.9+
2. **语法变更**: 检查是否使用了已弃用的语法
3. **性能差异**: 新版本可能有性能变化

## 📊 升级检查清单

- [x] 更新 `pyproject.toml` 中的 `requires-python`
- [x] 更新 `pyproject.toml` 中的 `python_version` (mypy)
- [x] 更新分类器中的 Python 版本列表
- [x] 更新 GitHub Actions 中的 Python 版本
- [x] 更新 pre-commit hooks 版本
- [ ] 重新创建虚拟环境（如需要）
- [ ] 运行完整测试套件
- [ ] 验证 CI/CD 流程
- [ ] 更新文档和 README

## 🔗 相关资源

- [Python 3.9 新特性](https://docs.python.org/3/whatsnew/3.9.html)
- [Python 3.10 新特性](https://docs.python.org/3/whatsnew/3.10.html)
- [Python 3.11 新特性](https://docs.python.org/3/whatsnew/3.11.html)
- [Ruff 配置文档](https://docs.astral.sh/ruff/)

---

**升级完成日期**: 2025-08-31
**升级负责人**: AI Assistant
**验证状态**: ✅ 配置已更新，等待测试验证
