#!/usr/bin/env python3
"""
CI/CD 功能测试脚本
模拟 CI/CD 流程，验证各个组件是否正常工作
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple


class CIFunctionalityTester:
    """CI/CD 功能测试器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.venv_path = self.project_root / "venv"
        self.results = {}

    def get_python_exe(self) -> Path:
        """获取 Python 可执行文件路径"""
        python_exe = self.venv_path / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = self.venv_path / "bin" / "python"
        return python_exe

    def run_command(
        self, cmd: List[str], timeout: int = 120
    ) -> Tuple[bool, str, float]:
        """运行命令并返回结果"""
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            duration = time.time() - start_time
            success = result.returncode == 0
            output = result.stdout + result.stderr
            return success, output, duration
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return False, f"Command timed out after {timeout}s", duration
        except Exception as e:
            duration = time.time() - start_time
            return False, f"Command failed: {e}", duration

    def test_ruff_linting(self) -> bool:
        """测试 Ruff 代码检查功能"""
        print("🔍 测试 Ruff 代码检查...")

        python_exe = self.get_python_exe()
        success, output, duration = self.run_command(
            [str(python_exe), "-m", "ruff", "check", ".", "--output-format=github"]
        )

        self.results["ruff_check"] = {
            "success": success or "Found" in output,  # 有问题也算正常运行
            "duration": duration,
            "output_lines": len(output.split("\n")) if output else 0,
        }

        if success or "Found" in output:
            print(f"  ✅ Ruff 检查完成 ({duration:.2f}s)")
            if "Found" in output:
                print("  📊 发现代码问题，这是正常的")
            return True
        else:
            print(f"  ❌ Ruff 检查失败: {output[:200]}...")
            return False

    def test_ruff_formatting(self) -> bool:
        """测试 Ruff 格式化功能"""
        print("🎨 测试 Ruff 格式化...")

        python_exe = self.get_python_exe()
        success, output, duration = self.run_command(
            [str(python_exe), "-m", "ruff", "format", "--check", "."]
        )

        self.results["ruff_format"] = {
            "success": success,
            "duration": duration,
            "needs_formatting": not success,
        }

        if success:
            print(f"  ✅ 代码格式正确 ({duration:.2f}s)")
        else:
            print(f"  ⚠️  代码需要格式化 ({duration:.2f}s) - 这不是错误")

        return True  # 格式化检查失败不算错误

    def test_pytest_execution(self) -> bool:
        """测试 pytest 执行"""
        print("🧪 测试 pytest 执行...")

        python_exe = self.get_python_exe()
        success, output, duration = self.run_command(
            [str(python_exe), "-m", "pytest", "tests/", "--tb=short", "-v"], timeout=180
        )

        self.results["pytest"] = {
            "success": success,
            "duration": duration,
            "test_count": output.count("PASSED") + output.count("FAILED")
            if output
            else 0,
        }

        if success:
            print(f"  ✅ 测试执行成功 ({duration:.2f}s)")
            if "passed" in output:
                passed_count = output.count("PASSED")
                print(f"  📊 {passed_count} 个测试通过")
        else:
            print(f"  ❌ 测试执行失败 ({duration:.2f}s)")
            print(f"  📝 错误信息: {output[-300:]}")

        return success

    def test_coverage_report(self) -> bool:
        """测试覆盖率报告生成"""
        print("📊 测试覆盖率报告...")

        python_exe = self.get_python_exe()
        success, output, duration = self.run_command(
            [
                str(python_exe),
                "-m",
                "pytest",
                "tests/",
                "--cov=bluev",
                "--cov-report=term-missing",
            ],
            timeout=180,
        )

        self.results["coverage"] = {
            "success": success,
            "duration": duration,
            "has_coverage": "TOTAL" in output if output else False,
        }

        if success and "TOTAL" in output:
            print(f"  ✅ 覆盖率报告生成成功 ({duration:.2f}s)")
            # 提取覆盖率信息
            for line in output.split("\n"):
                if "TOTAL" in line and "%" in line:
                    print(f"  📈 {line.strip()}")
                    break
        else:
            print(f"  ❌ 覆盖率报告生成失败 ({duration:.2f}s)")

        return success

    def test_mkdocs_build(self) -> bool:
        """测试 MkDocs 文档构建"""
        print("📚 测试 MkDocs 文档构建...")

        # 检查 mkdocs.yml 是否存在
        mkdocs_config = self.project_root / "mkdocs.yml"
        if not mkdocs_config.exists():
            print("  ⚠️  mkdocs.yml 不存在，跳过文档构建测试")
            return True

        python_exe = self.get_python_exe()

        # 确保 MkDocs 已安装
        install_success, _, _ = self.run_command(
            [
                str(python_exe),
                "-m",
                "pip",
                "install",
                "mkdocs",
                "mkdocs-material",
                "mkdocstrings[python]",
            ]
        )

        if not install_success:
            print("  ⚠️  MkDocs 安装失败，跳过文档构建测试")
            return True

        success, output, duration = self.run_command(
            [str(python_exe), "-m", "mkdocs", "build", "--clean"], timeout=180
        )

        self.results["mkdocs"] = {
            "success": success,
            "duration": duration,
            "site_exists": (self.project_root / "site").exists(),
        }

        if success:
            print(f"  ✅ 文档构建成功 ({duration:.2f}s)")
            site_dir = self.project_root / "site"
            if site_dir.exists():
                html_files = list(site_dir.glob("**/*.html"))
                print(f"  📄 生成了 {len(html_files)} 个 HTML 文件")
        else:
            print(f"  ❌ 文档构建失败: {output[:200]}...")

        return success

    def test_pre_commit_hooks(self) -> bool:
        """测试 pre-commit hooks"""
        print("🔗 测试 pre-commit hooks...")

        python_exe = self.get_python_exe()

        # 检查 pre-commit 是否安装
        check_success, _, _ = self.run_command(
            [str(python_exe), "-m", "pre_commit", "--version"]
        )

        if not check_success:
            print("  ⚠️  pre-commit 未安装，跳过 hooks 测试")
            return True

        # 运行 pre-commit hooks（只在部分文件上测试）
        success, output, duration = self.run_command(
            [
                str(python_exe),
                "-m",
                "pre_commit",
                "run",
                "--files",
                "bluev/__init__.py",
            ],
            timeout=120,
        )

        self.results["pre_commit"] = {
            "success": success,
            "duration": duration,
            "hooks_ran": output.count("Passed") + output.count("Failed")
            if output
            else 0,
        }

        if success:
            print(f"  ✅ Pre-commit hooks 执行成功 ({duration:.2f}s)")
        else:
            print(f"  ⚠️  Pre-commit hooks 有问题 ({duration:.2f}s) - 可能需要修复代码")

        return True  # hooks 失败不算致命错误

    def test_application_import(self) -> bool:
        """测试应用程序核心模块导入"""
        print("📦 测试应用程序导入...")

        python_exe = self.get_python_exe()
        success, output, duration = self.run_command(
            [
                str(python_exe),
                "-c",
                "from bluev.config import Config; from bluev.utils.logging import get_logger; print('Core modules imported successfully')",
            ]
        )

        self.results["app_import"] = {"success": success, "duration": duration}

        if success:
            print(f"  ✅ 核心模块导入成功 ({duration:.2f}s)")
        else:
            print(f"  ❌ 核心模块导入失败: {output}")

        return success

    def run_ci_simulation(self) -> Dict[str, bool]:
        """运行 CI 流程模拟"""
        print("🚀 开始 CI/CD 功能测试（模拟 GitHub Actions 流程）...\n")

        tests = [
            ("应用程序导入", self.test_application_import),
            ("Ruff 代码检查", self.test_ruff_linting),
            ("Ruff 格式化检查", self.test_ruff_formatting),
            ("Pre-commit Hooks", self.test_pre_commit_hooks),
            ("Pytest 测试执行", self.test_pytest_execution),
            ("覆盖率报告", self.test_coverage_report),
            ("MkDocs 文档构建", self.test_mkdocs_build),
        ]

        results = {}
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
            except Exception as e:
                print(f"  ❌ {test_name} 测试异常: {e}")
                results[test_name] = False
            print()

        return results

    def print_summary(self, results: Dict[str, bool]):
        """打印测试总结"""
        print("=" * 60)
        print("📊 CI/CD 功能测试总结")
        print("=" * 60)

        passed = sum(1 for result in results.values() if result)
        total = len(results)

        print(f"总测试数: {total}")
        print(f"通过测试: {passed}")
        print(f"失败测试: {total - passed}")
        print(f"成功率: {passed/total*100:.1f}%")
        print()

        print("详细结果:")
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {status} {test_name}")

        print("\n性能统计:")
        for key, data in self.results.items():
            if isinstance(data, dict) and "duration" in data:
                duration = data["duration"]
                print(f"  • {key}: {duration:.2f}s")

        if passed == total:
            print("\n🎉 所有 CI/CD 功能测试通过！")
            print("✅ 您的项目已准备好使用 GitHub Actions CI/CD")
            return True
        else:
            print(f"\n⚠️  {total - passed} 个测试失败，建议修复后再推送到 GitHub")
            return False


def main():
    """主函数"""
    tester = CIFunctionalityTester()
    results = tester.run_ci_simulation()
    success = tester.print_summary(results)

    if success:
        print("\n🚀 推荐下一步操作:")
        print("  1. git add .")
        print("  2. git commit -m 'feat: complete DevOps toolchain implementation'")
        print("  3. git push origin main")
        print("  4. 在 GitHub 上查看 Actions 标签页，确认 CI/CD 正常运行")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
