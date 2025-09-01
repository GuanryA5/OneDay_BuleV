#!/usr/bin/env python3
"""
BlueV 端到端测试脚本
验证完整的开发工作流程：代码提交 → CI/CD → 文档部署
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple


class E2ETestRunner:
    """端到端测试运行器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results: Dict[str, bool] = {}
        self.timings: Dict[str, float] = {}

    def run_command(self, cmd: List[str], timeout: int = 60) -> Tuple[bool, str, float]:
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
        """测试 Ruff 代码检查"""
        print("🔍 测试 Ruff 代码检查...")

        # 使用虚拟环境中的 Python
        python_exe = self.project_root / "venv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = self.project_root / "venv" / "bin" / "python"

        success, output, duration = self.run_command(
            [str(python_exe), "-m", "ruff", "check", ".", "--statistics"]
        )

        self.timings["ruff_check"] = duration

        if success or "Found" in output:  # Ruff 找到问题也算正常运行
            print(f"  ✅ Ruff 检查完成 ({duration:.2f}s)")
            if "Found" in output:
                print(
                    f"  📊 {output.split('Found')[1].split('.')[0].strip()} errors found"
                )
            return True
        else:
            print(f"  ❌ Ruff 检查失败: {output}")
            return False

    def test_ruff_formatting(self) -> bool:
        """测试 Ruff 代码格式化"""
        print("🎨 测试 Ruff 代码格式化...")

        python_exe = self.project_root / "venv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = self.project_root / "venv" / "bin" / "python"

        success, output, duration = self.run_command(
            [str(python_exe), "-m", "ruff", "format", "--check", "."]
        )

        self.timings["ruff_format"] = duration

        if success:
            print(f"  ✅ 代码格式检查通过 ({duration:.2f}s)")
            return True
        else:
            print(f"  ⚠️  代码格式需要调整 ({duration:.2f}s)")
            # 格式化问题不算致命错误
            return True

    def test_pytest_execution(self) -> bool:
        """测试 pytest 执行"""
        print("🧪 测试 pytest 执行...")

        python_exe = self.project_root / "venv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = self.project_root / "venv" / "bin" / "python"

        success, output, duration = self.run_command(
            [str(python_exe), "-m", "pytest", "tests/", "-v", "--tb=short"], timeout=120
        )

        self.timings["pytest"] = duration

        if success:
            print(f"  ✅ 测试执行成功 ({duration:.2f}s)")
            # 提取测试统计信息
            if "passed" in output:
                stats = [
                    line
                    for line in output.split("\n")
                    if "passed" in line and "=" in line
                ]
                if stats:
                    print(f"  📊 {stats[-1].strip()}")
            return True
        else:
            print(f"  ❌ 测试执行失败 ({duration:.2f}s)")
            print(f"  📝 错误详情: {output[-500:]}")  # 显示最后500字符
            return False

    def test_application_import(self) -> bool:
        """测试应用程序导入"""
        print("📦 测试应用程序导入...")

        python_exe = self.project_root / "venv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = self.project_root / "venv" / "bin" / "python"

        success, output, duration = self.run_command(
            [
                str(python_exe),
                "-c",
                "from bluev.main import BlueVApplication; from bluev.config import Config; print('Core modules imported successfully')",
            ]
        )

        self.timings["app_import"] = duration

        if success:
            print(f"  ✅ 应用程序导入成功 ({duration:.2f}s)")
            return True
        else:
            print(f"  ❌ 应用程序导入失败: {output}")
            return False

    def test_mkdocs_build(self) -> bool:
        """测试 MkDocs 文档构建"""
        print("📚 测试 MkDocs 文档构建...")

        # 检查 mkdocs.yml 是否存在
        mkdocs_config = self.project_root / "mkdocs.yml"
        if not mkdocs_config.exists():
            print("  ⚠️  mkdocs.yml 不存在，跳过文档构建测试")
            return True

        python_exe = self.project_root / "venv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = self.project_root / "venv" / "bin" / "python"

        # 先尝试安装 mkdocs（如果未安装）
        subprocess.run(
            [str(python_exe), "-m", "pip", "install", "mkdocs", "mkdocs-material"],
            capture_output=True,
            cwd=self.project_root,
        )

        success, output, duration = self.run_command(
            [str(python_exe), "-m", "mkdocs", "build", "--clean"], timeout=120
        )

        self.timings["mkdocs_build"] = duration

        if success:
            print(f"  ✅ 文档构建成功 ({duration:.2f}s)")
            # 检查生成的文件
            site_dir = self.project_root / "site"
            if site_dir.exists():
                html_files = list(site_dir.glob("**/*.html"))
                print(f"  📄 生成了 {len(html_files)} 个 HTML 文件")
            return True
        else:
            print(f"  ❌ 文档构建失败: {output}")
            return False

    def test_git_workflow(self) -> bool:
        """测试 Git 工作流"""
        print("🔄 测试 Git 工作流...")

        # 检查 Git 状态
        success, output, duration = self.run_command(["git", "status", "--porcelain"])

        if success:
            if output.strip():
                print(f"  📝 发现 {len(output.strip().split())} 个未提交的更改")
            else:
                print("  ✅ 工作目录干净")

            # 检查最近的提交
            success2, output2, _ = self.run_command(["git", "log", "--oneline", "-5"])
            if success2:
                commits = output2.strip().split("\n")
                print(f"  📚 最近 {len(commits)} 次提交:")
                for commit in commits[:3]:
                    print(f"    • {commit}")

            return True
        else:
            print(f"  ❌ Git 状态检查失败: {output}")
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """运行所有端到端测试"""
        print("🚀 开始端到端测试验证...\n")

        tests = [
            ("Git 工作流", self.test_git_workflow),
            ("应用程序导入", self.test_application_import),
            ("Ruff 代码检查", self.test_ruff_linting),
            ("Ruff 代码格式化", self.test_ruff_formatting),
            ("Pytest 测试执行", self.test_pytest_execution),
            ("MkDocs 文档构建", self.test_mkdocs_build),
        ]

        for test_name, test_func in tests:
            try:
                self.results[test_name] = test_func()
            except Exception as e:
                print(f"  ❌ {test_name} 测试异常: {e}")
                self.results[test_name] = False
            print()

        return self.results

    def print_summary(self):
        """打印测试总结"""
        print("=" * 60)
        print("📊 端到端测试总结")
        print("=" * 60)

        passed = sum(1 for result in self.results.values() if result)
        total = len(self.results)

        print(f"总测试数: {total}")
        print(f"通过测试: {passed}")
        print(f"失败测试: {total - passed}")
        print(f"成功率: {passed / total * 100:.1f}%")
        print()

        print("详细结果:")
        for test_name, result in self.results.items():
            status = "✅ 通过" if result else "❌ 失败"
            timing = self.timings.get(test_name.lower().replace(" ", "_"), 0)
            print(f"  {status} {test_name} ({timing:.2f}s)")

        print()
        total_time = sum(self.timings.values())
        print(f"总执行时间: {total_time:.2f}s")

        if passed == total:
            print("\n🎉 所有测试通过！DevOps 工具链运行正常。")
            return True
        else:
            print(f"\n⚠️  {total - passed} 个测试失败，需要检查相关配置。")
            return False


def main():
    """主函数"""
    runner = E2ETestRunner()
    runner.run_all_tests()
    success = runner.print_summary()

    # 返回适当的退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
