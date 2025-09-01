#!/usr/bin/env python3
"""
BlueV 环境健康检查脚本
用途: 全面检查开发环境的健康状态和配置正确性

使用方法:
    python scripts/health-check.py [--fix] [--verbose]
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class Colors:
    """终端颜色定义"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class HealthChecker:
    """环境健康检查器"""

    def __init__(self, fix_issues: bool = False, verbose: bool = False):
        self.fix_issues = fix_issues
        self.verbose = verbose
        self.issues = []
        self.warnings = []
        self.successes = []

    def log_info(self, message: str) -> None:
        """输出信息日志"""
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

    def log_success(self, message: str) -> None:
        """输出成功日志"""
        print(f"{Colors.GREEN}[✅]{Colors.NC} {message}")
        self.successes.append(message)

    def log_warning(self, message: str) -> None:
        """输出警告日志"""
        print(f"{Colors.YELLOW}[⚠️]{Colors.NC} {message}")
        self.warnings.append(message)

    def log_error(self, message: str) -> None:
        """输出错误日志"""
        print(f"{Colors.RED}[❌]{Colors.NC} {message}")
        self.issues.append(message)

    def run_command(self, cmd: List[str], capture_output: bool = True) -> Optional[subprocess.CompletedProcess]:
        """运行命令并返回结果"""
        try:
            result = subprocess.run(cmd, capture_output=capture_output, text=True, check=False)
            return result
        except Exception as e:
            if self.verbose:
                self.log_error(f"命令执行失败 {' '.join(cmd)}: {e}")
            return None

    def check_system_requirements(self) -> None:
        """检查系统要求"""
        self.log_info("🔍 检查系统要求...")

        # 检查 Python 版本
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if sys.version_info >= (3, 12):
            self.log_success(f"Python 版本: {python_version}")
        else:
            self.log_error(f"Python 版本过低: {python_version} (需要 >= 3.12)")

        # 检查 Conda
        conda_result = self.run_command(["conda", "--version"])
        if conda_result and conda_result.returncode == 0:
            conda_version = conda_result.stdout.strip()
            self.log_success(f"Conda 可用: {conda_version}")
        else:
            self.log_error("Conda 未找到或不可用")

        # 检查 Git
        git_result = self.run_command(["git", "--version"])
        if git_result and git_result.returncode == 0:
            git_version = git_result.stdout.strip()
            self.log_success(f"Git 可用: {git_version}")
        else:
            self.log_error("Git 未找到或不可用")

    def check_conda_environment(self) -> bool:
        """检查 Conda 环境"""
        self.log_info("🔍 检查 Conda 环境...")

        # 检查 bluev-dev 环境是否存在
        env_result = self.run_command(["conda", "env", "list"])
        if env_result and env_result.returncode == 0:
            if "bluev-dev" in env_result.stdout:
                self.log_success("bluev-dev 环境存在")
                return True
            else:
                self.log_error("bluev-dev 环境不存在")
                if self.fix_issues:
                    self.log_info("尝试创建 bluev-dev 环境...")
                    create_result = self.run_command([
                        "conda", "create", "-n", "bluev-dev", "python=3.12.11", "-y"
                    ])
                    if create_result and create_result.returncode == 0:
                        self.log_success("bluev-dev 环境创建成功")
                        return True
                return False
        else:
            self.log_error("无法检查 Conda 环境")
            return False

    def check_dependencies(self) -> None:
        """检查依赖包"""
        self.log_info("🔍 检查依赖包...")

        # 核心依赖列表
        core_deps = [
            'PySide6', 'cv2', 'numpy', 'PIL', 'pyautogui', 'pynput',
            'sqlalchemy', 'pydantic', 'dotenv', 'loguru', 'click'
        ]

        # 开发依赖列表
        dev_deps = ['pytest', 'ruff', 'mypy', 'mkdocs', 'pre_commit']

        # 检查核心依赖
        for dep in core_deps:
            if self.check_package(dep):
                self.log_success(f"核心依赖 {dep} 可用")
            else:
                self.log_error(f"核心依赖 {dep} 缺失")

        # 检查开发依赖
        for dep in dev_deps:
            if self.check_package(dep):
                self.log_success(f"开发依赖 {dep} 可用")
            else:
                self.log_warning(f"开发依赖 {dep} 缺失")

    def check_package(self, package_name: str) -> bool:
        """检查单个包是否可用"""
        try:
            if package_name == 'cv2':
                import cv2  # noqa: F401
            elif package_name == 'PIL':
                from PIL import Image  # noqa: F401
            elif package_name == 'dotenv':
                from dotenv import load_dotenv  # noqa: F401
            elif package_name == 'pre_commit':
                import pre_commit  # noqa: F401
            else:
                importlib.import_module(package_name)
            return True
        except ImportError:
            return False

    def check_project_structure(self) -> None:
        """检查项目结构"""
        self.log_info("🔍 检查项目结构...")

        required_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "environment.yml",
            "mkdocs.yml",
            ".pre-commit-config.yaml",
            "pyproject.toml"
        ]

        required_dirs = [
            "bluev/",
            "tests/",
            "docs/",
            "scripts/",
            ".github/workflows/"
        ]

        # 检查必需文件
        for file_path in required_files:
            if (PROJECT_ROOT / file_path).exists():
                self.log_success(f"必需文件存在: {file_path}")
            else:
                self.log_error(f"必需文件缺失: {file_path}")

        # 检查必需目录
        for dir_path in required_dirs:
            if (PROJECT_ROOT / dir_path).exists():
                self.log_success(f"必需目录存在: {dir_path}")
            else:
                self.log_error(f"必需目录缺失: {dir_path}")

    def check_git_configuration(self) -> None:
        """检查 Git 配置"""
        self.log_info("🔍 检查 Git 配置...")

        # 检查 pre-commit hooks
        pre_commit_hook = PROJECT_ROOT / ".git" / "hooks" / "pre-commit"
        if pre_commit_hook.exists():
            self.log_success("Pre-commit hooks 已安装")
        else:
            self.log_warning("Pre-commit hooks 未安装")
            if self.fix_issues:
                self.log_info("尝试安装 pre-commit hooks...")
                install_result = self.run_command([
                    "conda", "run", "-n", "bluev-dev", "pre-commit", "install"
                ])
                if install_result and install_result.returncode == 0:
                    self.log_success("Pre-commit hooks 安装成功")

        # 检查 Git 状态
        status_result = self.run_command(["git", "status", "--porcelain"])
        if status_result and status_result.returncode == 0:
            if status_result.stdout.strip():
                self.log_warning("工作目录有未提交的更改")
            else:
                self.log_success("工作目录干净")

    def check_ci_configuration(self) -> None:
        """检查 CI 配置"""
        self.log_info("🔍 检查 CI 配置...")

        ci_file = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        if ci_file.exists():
            try:
                with open(ci_file, encoding='utf-8') as f:
                    ci_config = yaml.safe_load(f)

                # 检查 Python 版本
                python_version = ci_config.get('env', {}).get('PYTHON_VERSION')
                if python_version:
                    self.log_success(f"CI Python 版本: {python_version}")
                else:
                    self.log_warning("CI 配置中未找到 Python 版本")

                # 检查作业平台
                jobs = ci_config.get('jobs', {})
                windows_jobs = sum(1 for job in jobs.values()
                                 if job.get('runs-on') == 'windows-latest')
                total_jobs = len(jobs)

                if windows_jobs == total_jobs and total_jobs > 0:
                    self.log_success(f"所有 CI 作业使用 Windows: {windows_jobs}/{total_jobs}")
                else:
                    self.log_warning(f"部分 CI 作业未使用 Windows: {windows_jobs}/{total_jobs}")

            except Exception as e:
                self.log_error(f"CI 配置文件解析失败: {e}")
        else:
            self.log_error("CI 配置文件不存在")

    def generate_report(self) -> Dict:
        """生成健康检查报告"""
        from datetime import datetime

        total_checks = len(self.successes) + len(self.warnings) + len(self.issues)
        success_rate = len(self.successes) / total_checks * 100 if total_checks > 0 else 0

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_checks": total_checks,
            "successes": len(self.successes),
            "warnings": len(self.warnings),
            "issues": len(self.issues),
            "success_rate": round(success_rate, 1),
            "details": {
                "successes": self.successes,
                "warnings": self.warnings,
                "issues": self.issues
            }
        }

        return report

    def run_full_check(self) -> Dict:
        """运行完整的健康检查"""
        print(f"{Colors.CYAN}🏥 BlueV 环境健康检查{Colors.NC}")
        print("=" * 50)

        # 执行各项检查
        self.check_system_requirements()
        env_exists = self.check_conda_environment()

        if env_exists:
            self.check_dependencies()
        else:
            self.log_warning("跳过依赖检查 (Conda 环境不存在)")

        self.check_project_structure()
        self.check_git_configuration()
        self.check_ci_configuration()

        # 生成报告
        report = self.generate_report()

        # 输出总结
        print("\n" + "=" * 50)
        print(f"{Colors.CYAN}📊 健康检查总结{Colors.NC}")
        print(f"总检查项: {report['total_checks']}")
        print(f"✅ 成功: {report['successes']}")
        print(f"⚠️ 警告: {report['warnings']}")
        print(f"❌ 问题: {report['issues']}")
        print(f"成功率: {report['success_rate']}%")

        # 健康等级评估
        if report['success_rate'] >= 90:
            print(f"{Colors.GREEN}🎉 环境健康状态: 优秀{Colors.NC}")
        elif report['success_rate'] >= 75:
            print(f"{Colors.YELLOW}⚠️ 环境健康状态: 良好{Colors.NC}")
        elif report['success_rate'] >= 60:
            print(f"{Colors.YELLOW}⚠️ 环境健康状态: 一般{Colors.NC}")
        else:
            print(f"{Colors.RED}❌ 环境健康状态: 需要修复{Colors.NC}")

        return report

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="BlueV 环境健康检查")
    parser.add_argument("--fix", action="store_true", help="尝试自动修复发现的问题")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--output", help="输出报告到 JSON 文件")

    args = parser.parse_args()

    # 切换到项目根目录
    import os
    os.chdir(PROJECT_ROOT)

    # 运行健康检查
    checker = HealthChecker(fix_issues=args.fix, verbose=args.verbose)
    report = checker.run_full_check()

    # 保存报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n📄 报告已保存到: {args.output}")

    # 返回适当的退出码
    if report['issues'] > 0:
        sys.exit(1)
    elif report['warnings'] > 0:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
