#!/usr/bin/env python3
"""
CI/CD 健康检查脚本
验证 CI/CD 配置是否正确，并提供修复建议
"""

import sys
from pathlib import Path
from typing import List

import yaml


class CICDHealthChecker:
    """CI/CD 健康检查器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.issues = []
        self.warnings = []

    def log_issue(self, category: str, message: str, severity: str = "ERROR"):
        """记录问题"""
        issue = {"category": category, "message": message, "severity": severity}
        if severity == "ERROR":
            self.issues.append(issue)
        else:
            self.warnings.append(issue)

        icon = "❌" if severity == "ERROR" else "⚠️"
        print(f"  {icon} [{category}] {message}")

    def check_github_workflows(self) -> bool:
        """检查 GitHub Actions 工作流配置"""
        print("🔍 检查 GitHub Actions 工作流...")

        workflows_dir = self.project_root / ".github" / "workflows"
        if not workflows_dir.exists():
            self.log_issue("GitHub Actions", "工作流目录不存在")
            return False

        # 检查 CI 工作流
        ci_file = workflows_dir / "ci.yml"
        if not ci_file.exists():
            self.log_issue("GitHub Actions", "CI 工作流文件不存在")
            return False

        try:
            with open(ci_file, encoding="utf-8") as f:
                ci_config = yaml.safe_load(f)

            # 检查触发条件 ('on' 是 YAML 关键字，可能被解析为布尔值)
            if "on" not in ci_config and True not in ci_config:
                self.log_issue("CI Config", "缺少触发条件配置")

            # 检查作业配置
            if "jobs" not in ci_config:
                self.log_issue("CI Config", "缺少作业配置")
            else:
                jobs = ci_config["jobs"]
                if "test" not in jobs:
                    self.log_issue("CI Config", "缺少测试作业")

                # 检查矩阵配置
                test_job = jobs.get("test", {})
                if "strategy" in test_job and "matrix" in test_job["strategy"]:
                    matrix = test_job["strategy"]["matrix"]
                    if "python-version" not in matrix:
                        self.log_issue("CI Config", "缺少 Python 版本矩阵")
                    if "os" not in matrix:
                        self.log_issue("CI Config", "缺少操作系统矩阵")

            print("  ✅ CI 工作流配置正常")

        except yaml.YAMLError as e:
            self.log_issue("CI Config", f"YAML 格式错误: {e}")
            return False
        except Exception as e:
            self.log_issue("CI Config", f"配置检查失败: {e}")
            return False

        # 检查文档工作流
        docs_file = workflows_dir / "docs.yml"
        if docs_file.exists():
            try:
                with open(docs_file, encoding="utf-8") as f:
                    yaml.safe_load(f)  # Just validate, don't store
                print("  ✅ 文档工作流配置正常")
            except yaml.YAMLError as e:
                self.log_issue("Docs Config", f"文档工作流 YAML 格式错误: {e}")
        else:
            self.log_issue("GitHub Actions", "文档工作流文件不存在", "WARNING")

        return True

    def check_dependencies(self) -> bool:
        """检查依赖文件"""
        print("🔍 检查依赖文件...")

        # 检查 requirements.txt
        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            self.log_issue("Dependencies", "requirements.txt 不存在")
            return False

        # 检查 requirements-dev.txt
        dev_req_file = self.project_root / "requirements-dev.txt"
        if not dev_req_file.exists():
            self.log_issue("Dependencies", "requirements-dev.txt 不存在")
            return False

        # 检查 pyproject.toml
        pyproject_file = self.project_root / "pyproject.toml"
        if not pyproject_file.exists():
            self.log_issue("Dependencies", "pyproject.toml 不存在", "WARNING")
        else:
            try:
                content = pyproject_file.read_text(encoding="utf-8")
                if "[tool.ruff" not in content:
                    self.log_issue("Dependencies", "pyproject.toml 缺少 Ruff 配置")
            except Exception as e:
                self.log_issue("Dependencies", f"pyproject.toml 读取失败: {e}")

        print("  ✅ 依赖文件检查完成")
        return True

    def check_pre_commit_config(self) -> bool:
        """检查 pre-commit 配置"""
        print("🔍 检查 pre-commit 配置...")

        config_file = self.project_root / ".pre-commit-config.yaml"
        if not config_file.exists():
            self.log_issue("Pre-commit", "配置文件不存在")
            return False

        try:
            with open(config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if "repos" not in config:
                self.log_issue("Pre-commit", "缺少仓库配置")
                return False

            # 检查是否有 Ruff 配置
            has_ruff = False
            for repo in config["repos"]:
                if "ruff" in repo.get("repo", ""):
                    has_ruff = True
                    break

            if not has_ruff:
                self.log_issue("Pre-commit", "缺少 Ruff 配置", "WARNING")

            print("  ✅ Pre-commit 配置正常")
            return True

        except yaml.YAMLError as e:
            self.log_issue("Pre-commit", f"配置文件格式错误: {e}")
            return False
        except Exception as e:
            self.log_issue("Pre-commit", f"配置检查失败: {e}")
            return False

    def check_mkdocs_config(self) -> bool:
        """检查 MkDocs 配置"""
        print("🔍 检查 MkDocs 配置...")

        config_file = self.project_root / "mkdocs.yml"
        if not config_file.exists():
            self.log_issue("MkDocs", "配置文件不存在", "WARNING")
            return False

        try:
            with open(config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            required_fields = ["site_name", "repo_url"]
            for field in required_fields:
                if field not in config:
                    self.log_issue("MkDocs", f"缺少必需字段: {field}")

            # 检查仓库 URL 是否正确
            repo_url = config.get("repo_url", "")
            if "GuanryA5/OneDay_BuleV" not in repo_url:
                self.log_issue("MkDocs", "仓库 URL 可能不正确", "WARNING")

            print("  ✅ MkDocs 配置正常")
            return True

        except yaml.YAMLError as e:
            self.log_issue("MkDocs", f"配置文件格式错误: {e}")
            return False
        except Exception as e:
            self.log_issue("MkDocs", f"配置检查失败: {e}")
            return False

    def check_git_configuration(self) -> bool:
        """检查 Git 配置"""
        print("🔍 检查 Git 配置...")

        # 检查 .gitignore
        gitignore_file = self.project_root / ".gitignore"
        if not gitignore_file.exists():
            self.log_issue("Git", ".gitignore 文件不存在", "WARNING")
        else:
            content = gitignore_file.read_text(encoding="utf-8")
            important_patterns = [
                ("__pycache__", "__pycache__"),
                ("*.pyc", "*.py[cod]"),  # *.py[cod] 包含 *.pyc
                (".env", ".env"),
                ("venv/", "venv/"),
                (".pytest_cache", ".pytest_cache"),
            ]

            for pattern_name, pattern_check in important_patterns:
                if pattern_check not in content and pattern_name not in content:
                    self.log_issue(
                        "Git", f".gitignore 缺少重要模式: {pattern_name}", "WARNING"
                    )

        # 检查是否在 Git 仓库中
        git_dir = self.project_root / ".git"
        if not git_dir.exists():
            self.log_issue("Git", "不在 Git 仓库中")
            return False

        print("  ✅ Git 配置检查完成")
        return True

    def check_directory_structure(self) -> bool:
        """检查目录结构"""
        print("🔍 检查项目目录结构...")

        required_dirs = ["bluev", "tests", "docs", "scripts", ".github/workflows"]

        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                self.log_issue("Directory Structure", f"缺少目录: {dir_name}")

        # 检查重要文件
        required_files = ["README.md", "requirements.txt", "requirements-dev.txt"]

        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                self.log_issue("Directory Structure", f"缺少文件: {file_name}")

        print("  ✅ 目录结构检查完成")
        return True

    def generate_fix_suggestions(self) -> List[str]:
        """生成修复建议"""
        suggestions = []

        if self.issues:
            suggestions.append("🔧 修复建议:")

            for issue in self.issues:
                category = issue["category"]
                message = issue["message"]

                if category == "GitHub Actions":
                    if "工作流目录不存在" in message:
                        suggestions.append("  • 创建 .github/workflows/ 目录")
                    elif "CI 工作流文件不存在" in message:
                        suggestions.append("  • 从模板创建 .github/workflows/ci.yml")

                elif category == "Dependencies":
                    if "requirements.txt 不存在" in message:
                        suggestions.append("  • 运行: pip freeze > requirements.txt")
                    elif "requirements-dev.txt 不存在" in message:
                        suggestions.append("  • 创建开发依赖文件")

                elif category == "Pre-commit":
                    if "配置文件不存在" in message:
                        suggestions.append("  • 创建 .pre-commit-config.yaml 配置文件")
                        suggestions.append("  • 运行: pre-commit install")

                elif category == "Git":
                    if "不在 Git 仓库中" in message:
                        suggestions.append("  • 运行: git init")
                        suggestions.append(
                            "  • 运行: git remote add origin https://github.com/GuanryA5/OneDay_BuleV.git"
                        )

        return suggestions

    def run_health_check(self) -> bool:
        """运行完整的健康检查"""
        print("🚀 开始 CI/CD 健康检查...\n")

        checks = [
            ("目录结构", self.check_directory_structure),
            ("Git 配置", self.check_git_configuration),
            ("依赖文件", self.check_dependencies),
            ("Pre-commit 配置", self.check_pre_commit_config),
            ("GitHub Actions", self.check_github_workflows),
            ("MkDocs 配置", self.check_mkdocs_config),
        ]

        results = []
        for check_name, check_func in checks:
            try:
                result = check_func()
                results.append(result)
            except Exception as e:
                self.log_issue(check_name, f"检查过程中发生异常: {e}")
                results.append(False)
            print()

        return all(results)

    def print_summary(self):
        """打印检查总结"""
        print("=" * 60)
        print("📊 CI/CD 健康检查总结")
        print("=" * 60)

        total_issues = len(self.issues)
        total_warnings = len(self.warnings)

        print(f"严重问题: {total_issues}")
        print(f"警告: {total_warnings}")

        if total_issues == 0:
            print("\n🎉 CI/CD 配置健康，可以正常使用！")
            if total_warnings > 0:
                print("⚠️ 有一些警告，建议优化但不影响基本功能。")
        else:
            print(
                f"\n❌ 发现 {total_issues} 个严重问题，需要修复后才能正常使用 CI/CD。"
            )

        # 显示修复建议
        suggestions = self.generate_fix_suggestions()
        if suggestions:
            print("\n" + "\n".join(suggestions))

        return total_issues == 0


def main():
    """主函数"""
    checker = CICDHealthChecker()
    checker.run_health_check()
    healthy = checker.print_summary()

    return healthy


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
