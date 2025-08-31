#!/usr/bin/env python3
"""
BlueV 错误处理和恢复机制
提供常见问题的自动诊断和修复功能
"""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class ErrorRecoverySystem:
    """错误恢复系统"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.venv_path = self.project_root / "venv"
        self.recovery_log = []

    def log_action(self, action: str, success: bool = True, details: str = ""):
        """记录恢复操作"""
        status = "✅" if success else "❌"
        log_entry = f"{status} {action}"
        if details:
            log_entry += f": {details}"
        self.recovery_log.append(log_entry)
        print(log_entry)

    def check_python_environment(self) -> Tuple[bool, str]:
        """检查 Python 环境"""
        print("🔍 检查 Python 环境...")

        # 检查虚拟环境
        if not self.venv_path.exists():
            return False, "虚拟环境不存在"

        # 检查 Python 可执行文件
        python_exe = self.venv_path / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = self.venv_path / "bin" / "python"
            if not python_exe.exists():
                return False, "Python 可执行文件不存在"

        # 检查 Python 版本
        try:
            result = subprocess.run(
                [str(python_exe), "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log_action("Python 环境正常", True, version)
                return True, version
            else:
                return False, "Python 版本检查失败"
        except Exception as e:
            return False, f"Python 环境检查异常: {e}"

    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """检查依赖包"""
        print("🔍 检查依赖包...")

        python_exe = self.venv_path / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = self.venv_path / "bin" / "python"

        missing_packages = []
        required_packages = [
            "PySide6",
            "opencv-python",
            "numpy",
            "Pillow",
            "pydantic",
            "loguru",
            "click",
            "pytest",
            "ruff",
        ]

        for package in required_packages:
            try:
                result = subprocess.run(
                    [
                        str(python_exe),
                        "-c",
                        f"import {package.replace('-', '_').split('[')[0]}",
                    ],
                    capture_output=True,
                    timeout=10,
                )

                if result.returncode != 0:
                    missing_packages.append(package)
            except Exception:
                missing_packages.append(package)

        if missing_packages:
            self.log_action("依赖检查", False, f"缺少包: {', '.join(missing_packages)}")
            return False, missing_packages
        else:
            self.log_action("依赖检查", True, "所有依赖包正常")
            return True, []

    def fix_dependencies(self, missing_packages: List[str]) -> bool:
        """修复缺失的依赖包"""
        print("🔧 修复依赖包...")

        python_exe = self.venv_path / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = self.venv_path / "bin" / "python"

        try:
            # 升级 pip
            subprocess.run(
                [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
                check=True,
                timeout=120,
            )

            # 安装缺失的包
            if missing_packages:
                subprocess.run(
                    [str(python_exe), "-m", "pip", "install"] + missing_packages,
                    check=True,
                    timeout=300,
                )

            # 安装项目依赖
            requirements_file = self.project_root / "requirements.txt"
            if requirements_file.exists():
                subprocess.run(
                    [
                        str(python_exe),
                        "-m",
                        "pip",
                        "install",
                        "-r",
                        str(requirements_file),
                    ],
                    check=True,
                    timeout=300,
                )

            dev_requirements_file = self.project_root / "requirements-dev.txt"
            if dev_requirements_file.exists():
                subprocess.run(
                    [
                        str(python_exe),
                        "-m",
                        "pip",
                        "install",
                        "-r",
                        str(dev_requirements_file),
                    ],
                    check=True,
                    timeout=300,
                )

            self.log_action("依赖修复", True, "所有依赖包已安装")
            return True

        except subprocess.CalledProcessError as e:
            self.log_action("依赖修复", False, f"安装失败: {e}")
            return False
        except Exception as e:
            self.log_action("依赖修复", False, f"修复异常: {e}")
            return False

    def check_git_status(self) -> Tuple[bool, str]:
        """检查 Git 状态"""
        print("🔍 检查 Git 状态...")

        try:
            # 检查是否在 Git 仓库中
            result = subprocess.run(
                ["git", "status"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=10,
            )

            if result.returncode == 0:
                # 检查是否有未提交的更改
                result2 = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=10,
                )

                if result2.stdout.strip():
                    changes = len(result2.stdout.strip().split("\n"))
                    self.log_action("Git 状态", True, f"发现 {changes} 个未提交的更改")
                    return True, f"{changes} 个未提交的更改"
                else:
                    self.log_action("Git 状态", True, "工作目录干净")
                    return True, "工作目录干净"
            else:
                return False, "不在 Git 仓库中或 Git 命令失败"

        except Exception as e:
            return False, f"Git 状态检查异常: {e}"

    def check_pre_commit_hooks(self) -> Tuple[bool, str]:
        """检查 pre-commit hooks"""
        print("🔍 检查 pre-commit hooks...")

        hooks_dir = self.project_root / ".git" / "hooks"
        pre_commit_hook = hooks_dir / "pre-commit"

        if not pre_commit_hook.exists():
            return False, "pre-commit hook 未安装"

        # 检查 pre-commit 配置文件
        config_file = self.project_root / ".pre-commit-config.yaml"
        if not config_file.exists():
            return False, "pre-commit 配置文件不存在"

        self.log_action("Pre-commit hooks", True, "配置正常")
        return True, "配置正常"

    def fix_pre_commit_hooks(self) -> bool:
        """修复 pre-commit hooks"""
        print("🔧 修复 pre-commit hooks...")

        python_exe = self.venv_path / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = self.venv_path / "bin" / "python"

        try:
            # 安装 pre-commit
            subprocess.run(
                [str(python_exe), "-m", "pip", "install", "pre-commit"],
                check=True,
                timeout=120,
            )

            # 安装 hooks
            subprocess.run(
                [str(python_exe), "-m", "pre_commit", "install"],
                check=True,
                timeout=60,
                cwd=self.project_root,
            )

            self.log_action("Pre-commit 修复", True, "hooks 已重新安装")
            return True

        except Exception as e:
            self.log_action("Pre-commit 修复", False, f"修复失败: {e}")
            return False

    def check_ruff_config(self) -> Tuple[bool, str]:
        """检查 Ruff 配置"""
        print("🔍 检查 Ruff 配置...")

        pyproject_file = self.project_root / "pyproject.toml"
        if not pyproject_file.exists():
            return False, "pyproject.toml 不存在"

        try:
            content = pyproject_file.read_text(encoding="utf-8")
            if "[tool.ruff" in content:
                self.log_action("Ruff 配置", True, "配置文件存在")
                return True, "配置正常"
            else:
                return False, "Ruff 配置缺失"
        except Exception as e:
            return False, f"配置文件读取失败: {e}"

    def clean_cache_files(self) -> bool:
        """清理缓存文件"""
        print("🧹 清理缓存文件...")

        cache_patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            ".pytest_cache",
            ".ruff_cache",
            ".mypy_cache",
            "*.egg-info",
            "build/",
            "dist/",
            "site/",
        ]

        cleaned_count = 0
        for pattern in cache_patterns:
            for path in self.project_root.glob(pattern):
                try:
                    if path.is_file():
                        path.unlink()
                        cleaned_count += 1
                    elif path.is_dir():
                        shutil.rmtree(path)
                        cleaned_count += 1
                except Exception:
                    pass  # 忽略清理失败的文件

        self.log_action("缓存清理", True, f"清理了 {cleaned_count} 个缓存文件/目录")
        return True

    def run_full_diagnosis(self) -> Dict[str, bool]:
        """运行完整诊断"""
        print("🚀 开始系统诊断和恢复...\n")

        results = {}

        # 1. 检查 Python 环境
        python_ok, python_msg = self.check_python_environment()
        results["python_environment"] = python_ok

        # 2. 检查依赖包
        deps_ok, missing_deps = self.check_dependencies()
        results["dependencies"] = deps_ok

        if not deps_ok:
            # 尝试修复依赖
            fix_ok = self.fix_dependencies(missing_deps)
            results["dependency_fix"] = fix_ok

        # 3. 检查 Git 状态
        git_ok, git_msg = self.check_git_status()
        results["git_status"] = git_ok

        # 4. 检查 pre-commit hooks
        hooks_ok, hooks_msg = self.check_pre_commit_hooks()
        results["pre_commit_hooks"] = hooks_ok

        if not hooks_ok:
            # 尝试修复 hooks
            fix_hooks_ok = self.fix_pre_commit_hooks()
            results["pre_commit_fix"] = fix_hooks_ok

        # 5. 检查 Ruff 配置
        ruff_ok, ruff_msg = self.check_ruff_config()
        results["ruff_config"] = ruff_ok

        # 6. 清理缓存
        cache_ok = self.clean_cache_files()
        results["cache_cleanup"] = cache_ok

        return results

    def print_recovery_summary(self, results: Dict[str, bool]):
        """打印恢复总结"""
        print("\n" + "=" * 60)
        print("📊 系统诊断和恢复总结")
        print("=" * 60)

        print("\n恢复操作日志:")
        for log_entry in self.recovery_log:
            print(f"  {log_entry}")

        print("\n诊断结果:")
        passed = sum(1 for result in results.values() if result)
        total = len(results)

        for check_name, result in results.items():
            status = "✅ 正常" if result else "❌ 异常"
            print(f"  {status} {check_name.replace('_', ' ').title()}")

        print(f"\n总体状态: {passed}/{total} 项检查通过")

        if passed == total:
            print("🎉 系统状态良好，所有检查通过！")
            return True
        else:
            print("⚠️ 发现问题，请查看上述日志进行手动修复。")
            return False


def main():
    """主函数"""
    recovery = ErrorRecoverySystem()
    results = recovery.run_full_diagnosis()
    success = recovery.print_recovery_summary(results)

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
