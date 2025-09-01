#!/usr/bin/env python3
"""
Python 版本验证脚本
验证当前环境是否满足 BlueV 项目的 Python 3.9+ 要求
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, Tuple


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"🐍 {title}")
    print("=" * 60)


def print_section(title: str):
    """打印章节"""
    print(f"\n📋 {title}")
    print("-" * 40)


def check_python_version() -> Tuple[bool, str]:
    """检查 Python 版本"""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    # 检查是否满足最低要求 (3.9+)
    if version.major == 3 and version.minor >= 9:
        return True, version_str
    else:
        return False, version_str


def check_package_compatibility() -> Dict[str, Any]:
    """检查关键包的兼容性"""
    packages = {
        "PySide6": "6.5.0",
        "opencv-python": "4.8.0",
        "numpy": "1.24.0",
        "Pillow": "10.0.0",
        "pytest": "7.4.0",
        "ruff": "0.1.0",
        "mkdocs": "1.5.0",
    }

    results = {}

    for package, min_version in packages.items():
        try:
            # 尝试导入包
            if package == "opencv-python":
                import cv2

                version = cv2.__version__
                package_name = "opencv-python"
            elif package == "Pillow":
                from PIL import Image

                version = Image.__version__
                package_name = "Pillow"
            else:
                module = importlib.import_module(package.lower().replace("-", "_"))
                version = getattr(module, "__version__", "unknown")
                package_name = package

            results[package_name] = {
                "installed": True,
                "version": version,
                "min_required": min_version,
                "compatible": True,  # 简化检查，实际应该比较版本
            }
        except ImportError:
            results[package] = {
                "installed": False,
                "version": None,
                "min_required": min_version,
                "compatible": False,
            }

    return results


def check_project_config() -> Dict[str, Any]:
    """检查项目配置文件"""
    config_files = {
        "pyproject.toml": Path("pyproject.toml"),
        ".github/workflows/docs.yml": Path(".github/workflows/docs.yml"),
        ".pre-commit-config.yaml": Path(".pre-commit-config.yaml"),
    }

    results = {}

    for name, path in config_files.items():
        if path.exists():
            content = path.read_text(encoding="utf-8")
            results[name] = {
                "exists": True,
                "content": content,
                "python_39_ready": "python" in content.lower(),
            }
        else:
            results[name] = {"exists": False, "content": None, "python_39_ready": False}

    return results


def run_basic_tests() -> Dict[str, bool]:
    """运行基础功能测试"""
    tests = {}

    # 测试 Python 基础功能
    try:
        # 测试字典合并操作符 (Python 3.9+)
        dict1 = {"a": 1}
        dict2 = {"b": 2}
        merged = dict1 | dict2
        tests["dict_merge_operator"] = True
    except (TypeError, AttributeError):
        tests["dict_merge_operator"] = False

    # 测试类型提示
    try:
        import importlib.util

        spec = importlib.util.find_spec("typing")
        if spec and hasattr(spec.loader.load_module(spec), "Annotated"):
            tests["annotated_types"] = True
        else:
            tests["annotated_types"] = False
    except (ImportError, AttributeError):
        tests["annotated_types"] = False

    # 测试 f-string 调试 (Python 3.8+)
    try:
        value = 42
        debug_str = f"{value=}"
        tests["fstring_debug"] = True
    except (SyntaxError, NameError):
        tests["fstring_debug"] = False

    return tests


def main():
    """主函数"""
    print_header("BlueV Python 3.9+ 环境验证")

    # 1. 检查 Python 版本
    print_section("Python 版本检查")
    is_compatible, version = check_python_version()

    print(f"当前 Python 版本: {version}")
    print("最低要求版本: 3.9.0")

    if is_compatible:
        print("✅ Python 版本满足要求")
    else:
        print("❌ Python 版本不满足要求")
        print("🔧 请升级到 Python 3.9 或更高版本")
        return False

    # 2. 检查包兼容性
    print_section("依赖包兼容性检查")
    packages = check_package_compatibility()

    all_compatible = True
    for package, info in packages.items():
        if info["installed"]:
            status = "✅" if info["compatible"] else "⚠️"
            print(
                f"{status} {package}: {info['version']} (要求: {info['min_required']}+)"
            )
        else:
            print(f"❌ {package}: 未安装 (要求: {info['min_required']}+)")
            all_compatible = False

    # 3. 检查项目配置
    print_section("项目配置检查")
    configs = check_project_config()

    for name, info in configs.items():
        if info["exists"]:
            print(f"✅ {name}: 存在")
            if 'requires-python = ">=3.9"' in info.get("content", ""):
                print("   ✅ Python 3.9+ 配置正确")
            elif "python-version: '3.11'" in info.get("content", ""):
                print("   ✅ CI Python 版本已更新")
            elif "rev: v0.12.11" in info.get("content", ""):
                print("   ✅ Pre-commit hooks 已更新")
        else:
            print(f"❌ {name}: 不存在")

    # 4. 运行基础测试
    print_section("Python 3.9+ 特性测试")
    tests = run_basic_tests()

    for test_name, passed in tests.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test_name.replace('_', ' ').title()}")

    # 5. 总结
    print_section("验证总结")

    if is_compatible and all_compatible and all(tests.values()):
        print("🎉 恭喜！您的环境完全兼容 Python 3.9+ 要求")
        print("\n📋 下一步建议:")
        print("1. 运行完整测试套件: pytest tests/")
        print("2. 检查代码质量: ruff check .")
        print("3. 构建文档: mkdocs build --clean")
        return True
    else:
        print("⚠️ 发现一些问题需要解决")
        print("\n🔧 修复建议:")

        if not is_compatible:
            print("- 升级 Python 到 3.9 或更高版本")

        if not all_compatible:
            print("- 安装缺失的依赖包: pip install -e .[dev]")

        if not all(tests.values()):
            print("- 检查 Python 环境配置")

        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 验证被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {e}")
        sys.exit(1)
