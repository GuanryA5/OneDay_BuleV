@echo off
REM BlueV Windows 开发环境快速设置脚本
REM 适用于 Windows 10/11 开发环境

echo ========================================
echo BlueV Windows 开发环境设置
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 未安装或不在 PATH 中
    echo 请先安装 Python 3.8+ 并添加到 PATH
    pause
    exit /b 1
)

echo ✅ Python 已安装
python --version

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
) else (
    echo ✅ 虚拟环境已存在
)

REM 激活虚拟环境
echo 🔄 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级 pip
echo 📦 升级 pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 📦 安装项目依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 项目依赖安装失败
    pause
    exit /b 1
)

echo 📦 安装开发依赖...
pip install -r requirements-dev.txt
if %errorlevel% neq 0 (
    echo ❌ 开发依赖安装失败
    pause
    exit /b 1
)

REM 安装 pre-commit hooks
echo 🔗 安装 pre-commit hooks...
pre-commit install
if %errorlevel% neq 0 (
    echo ⚠️  pre-commit hooks 安装失败，但不影响开发
)

REM 运行健康检查
echo 🔍 运行系统健康检查...
python scripts\ci_health_check.py
if %errorlevel% neq 0 (
    echo ⚠️  健康检查发现问题，请查看上述输出
)

echo.
echo ========================================
echo ✅ Windows 开发环境设置完成！
echo ========================================
echo.
echo 🚀 可用命令:
echo   • 代码检查: ruff check .
echo   • 代码格式化: ruff format .
echo   • 运行测试: pytest tests/
echo   • 启动应用: python -m bluev.main
echo   • 构建文档: mkdocs serve
echo.
echo 📚 更多信息请查看:
echo   • docs/development/devops-guide.md
echo   • docs/development/troubleshooting.md
echo.
pause
