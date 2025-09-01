#!/usr/bin/env python3
"""
BlueV 项目任务管理脚本
用途: 提供跨平台的开发任务自动化

使用方法:
    python scripts/tasks.py <task_name> [options]

可用任务:
    setup       - 设置开发环境
    test        - 运行测试
    lint        - 代码检查
    format      - 代码格式化
    type-check  - 类型检查
    docs        - 启动文档服务器
    clean       - 清理临时文件
    build       - 构建项目
    dev         - 开发模式启动
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)


class Colors:
    """终端颜色定义"""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"  # No Color


def log_info(message: str) -> None:
    """输出信息日志"""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")


def log_success(message: str) -> None:
    """输出成功日志"""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")


def log_warning(message: str) -> None:
    """输出警告日志"""
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")


def log_error(message: str) -> None:
    """输出错误日志"""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


def run_command(
    cmd: List[str], check: bool = True, capture_output: bool = False
) -> subprocess.CompletedProcess:
    """运行命令"""
    log_info(f"执行命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, check=check, capture_output=capture_output, text=True
        )
        if result.returncode == 0:
            log_success("命令执行成功")
        return result
    except subprocess.CalledProcessError as e:
        log_error(f"命令执行失败: {e}")
        if not check:
            return e
        sys.exit(1)


def check_conda_env() -> bool:
    """检查 Conda 环境是否存在"""
    try:
        result = run_command(["conda", "env", "list"], capture_output=True)
        return "bluev-dev" in result.stdout
    except Exception:
        return False


def ensure_conda_env() -> None:
    """确保 Conda 环境存在"""
    if not check_conda_env():
        log_warning("bluev-dev 环境不存在，请先运行 setup 任务")
        sys.exit(1)


def task_setup(args) -> None:
    """设置开发环境"""
    log_info("🚀 设置 BlueV 开发环境")

    # 检查 Conda
    try:
        run_command(["conda", "--version"], capture_output=True)
    except Exception:
        log_error("Conda 未找到，请先安装 Anaconda 或 Miniconda")
        sys.exit(1)

    # 创建或更新环境
    if check_conda_env() and not args.force:
        log_info("bluev-dev 环境已存在，跳过创建")
    else:
        if args.force:
            log_info("强制重建环境...")
            run_command(
                ["conda", "env", "remove", "-n", "bluev-dev", "-y"], check=False
            )

        log_info("创建 Conda 环境...")
        run_command(["conda", "create", "-n", "bluev-dev", "python=3.12.11", "-y"])

    # 安装依赖
    log_info("安装依赖...")
    run_command(
        [
            "conda",
            "install",
            "-n",
            "bluev-dev",
            "-c",
            "conda-forge",
            "pyside6",
            "opencv",
            "numpy",
            "pillow",
            "-y",
        ]
    )
    run_command(
        ["conda", "run", "-n", "bluev-dev", "pip", "install", "-r", "requirements.txt"]
    )
    run_command(
        [
            "conda",
            "run",
            "-n",
            "bluev-dev",
            "pip",
            "install",
            "-r",
            "requirements-dev.txt",
        ]
    )

    # 设置 pre-commit
    run_command(
        ["conda", "run", "-n", "bluev-dev", "pre-commit", "install", "--install-hooks"]
    )

    log_success("🎉 开发环境设置完成！")


def task_test(args) -> None:
    """运行测试"""
    ensure_conda_env()
    log_info("🧪 运行测试套件")

    cmd = ["conda", "run", "-n", "bluev-dev", "pytest"]

    if args.verbose:
        cmd.append("-v")
    if args.coverage:
        cmd.extend(["--cov=bluev", "--cov-report=html", "--cov-report=term-missing"])
    if args.pattern:
        cmd.extend(["-k", args.pattern])

    cmd.append("tests/")
    run_command(cmd)


def task_lint(args) -> None:
    """代码检查"""
    ensure_conda_env()
    log_info("🔍 运行代码检查")

    cmd = ["conda", "run", "-n", "bluev-dev", "ruff", "check", "."]
    if args.fix:
        cmd.append("--fix")

    run_command(cmd, check=False)


def task_format(args) -> None:
    """代码格式化"""
    ensure_conda_env()
    log_info("✨ 格式化代码")

    run_command(["conda", "run", "-n", "bluev-dev", "ruff", "format", "."])


def task_type_check(args) -> None:
    """类型检查"""
    ensure_conda_env()
    log_info("🔍 运行类型检查")

    run_command(
        [
            "conda",
            "run",
            "-n",
            "bluev-dev",
            "mypy",
            "bluev/",
            "--show-error-codes",
            "--pretty",
        ],
        check=False,
    )


def task_docs(args) -> None:
    """启动文档服务器"""
    ensure_conda_env()
    log_info("📚 启动文档服务器")

    cmd = ["conda", "run", "-n", "bluev-dev", "mkdocs", "serve"]
    if args.port:
        cmd.extend(["--dev-addr", f"localhost:{args.port}"])

    run_command(cmd)


def task_clean(args) -> None:
    """清理临时文件"""
    log_info("🧹 清理临时文件")

    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        ".pytest_cache",
        ".coverage",
        "htmlcov/",
        "dist/",
        "build/",
        "*.egg-info/",
        ".mypy_cache/",
        ".ruff_cache/",
    ]

    for pattern in patterns:
        for path in Path(".").glob(pattern):
            if path.is_file():
                path.unlink()
                log_info(f"删除文件: {path}")
            elif path.is_dir():
                import shutil

                shutil.rmtree(path)
                log_info(f"删除目录: {path}")


def task_build(args) -> None:
    """构建项目"""
    ensure_conda_env()
    log_info("🔨 构建项目")

    # 清理旧构建
    task_clean(args)

    # 运行测试
    log_info("运行测试...")
    run_command(["conda", "run", "-n", "bluev-dev", "pytest", "tests/", "-v"])

    # 构建包
    run_command(["conda", "run", "-n", "bluev-dev", "python", "-m", "build"])

    log_success("🎉 项目构建完成！")


def task_dev(args) -> None:
    """开发模式启动"""
    ensure_conda_env()
    log_info("🚀 启动开发模式")

    run_command(["conda", "run", "-n", "bluev-dev", "python", "-m", "bluev"])

def task_health(args) -> None:
    """环境健康检查"""
    log_info("🏥 运行环境健康检查")

    cmd = ["python", "scripts/health-check.py"]
    if args.fix:
        cmd.append("--fix")
    if args.output:
        cmd.extend(["--output", args.output])

    run_command(cmd, check=False)

def task_deps(args) -> None:
    """依赖版本监控"""
    log_info("📦 运行依赖版本监控")

    cmd = ["python", "scripts/dependency-monitor.py"]
    if args.security:
        cmd.append("--security-scan")
    if args.output:
        cmd.extend(["--output", args.output])

    run_command(cmd, check=False)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="BlueV 项目任务管理")
    subparsers = parser.add_subparsers(dest="task", help="可用任务")

    # setup 任务
    setup_parser = subparsers.add_parser("setup", help="设置开发环境")
    setup_parser.add_argument("--force", action="store_true", help="强制重建环境")

    # test 任务
    test_parser = subparsers.add_parser("test", help="运行测试")
    test_parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    test_parser.add_argument(
        "-c", "--coverage", action="store_true", help="生成覆盖率报告"
    )
    test_parser.add_argument("-k", "--pattern", help="测试模式匹配")

    # lint 任务
    lint_parser = subparsers.add_parser("lint", help="代码检查")
    lint_parser.add_argument("--fix", action="store_true", help="自动修复问题")

    # format 任务
    subparsers.add_parser("format", help="代码格式化")

    # type-check 任务
    subparsers.add_parser("type-check", help="类型检查")

    # docs 任务
    docs_parser = subparsers.add_parser("docs", help="启动文档服务器")
    docs_parser.add_argument("-p", "--port", type=int, default=8000, help="端口号")

    # clean 任务
    subparsers.add_parser("clean", help="清理临时文件")

    # build 任务
    subparsers.add_parser("build", help="构建项目")

    # dev 任务
    subparsers.add_parser("dev", help="开发模式启动")

    # health 任务
    health_parser = subparsers.add_parser("health", help="环境健康检查")
    health_parser.add_argument("--fix", action="store_true", help="尝试自动修复问题")
    health_parser.add_argument("--output", help="输出报告到文件")

    # deps 任务
    deps_parser = subparsers.add_parser("deps", help="依赖版本监控")
    deps_parser.add_argument("--security", action="store_true", help="包含安全扫描")
    deps_parser.add_argument("--output", help="输出报告到文件")

    args = parser.parse_args()

    if not args.task:
        parser.print_help()
        return

    # 执行任务
    task_func = globals().get(f"task_{args.task.replace('-', '_')}")
    if task_func:
        task_func(args)
    else:
        log_error(f"未知任务: {args.task}")
        sys.exit(1)


if __name__ == "__main__":
    main()
