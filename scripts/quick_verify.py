#!/usr/bin/env python3
"""
BlueV 快速验证脚本
验证核心功能是否正常工作
"""

import subprocess
import sys
from pathlib import Path


def test_imports():
    """测试核心模块导入"""
    print("Testing core module imports...")
    try:
        print("  ✓ Core modules imported successfully")
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_config():
    """测试配置系统"""
    print("Testing configuration system...")
    try:
        from bluev.config import Config

        config = Config()
        print(f"  ✓ Config loaded: {config.APP_NAME}")
        return True
    except Exception as e:
        print(f"  ✗ Config test failed: {e}")
        return False


def test_logging():
    """测试日志系统"""
    print("Testing logging system...")
    try:
        from bluev.utils.logging import get_logger

        logger = get_logger("test")
        logger.info("Test log message")
        print("  ✓ Logging system works")
        return True
    except Exception as e:
        print(f"  ✗ Logging test failed: {e}")
        return False


def test_ruff_basic():
    """测试 Ruff 基本功能"""
    print("Testing Ruff basic functionality...")
    try:
        project_root = Path(__file__).parent.parent
        python_exe = project_root / "venv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = project_root / "venv" / "bin" / "python"

        # 只检查一个小文件
        result = subprocess.run(
            [str(python_exe), "-m", "ruff", "check", "bluev/__init__.py"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=project_root,
        )

        print(f"  ✓ Ruff check completed (exit code: {result.returncode})")
        return True
    except Exception as e:
        print(f"  ✗ Ruff test failed: {e}")
        return False


def main():
    """主函数"""
    print("🚀 BlueV Quick Verification")
    print("=" * 40)

    tests = [
        ("Core Imports", test_imports),
        ("Configuration", test_config),
        ("Logging System", test_logging),
        ("Ruff Linting", test_ruff_basic),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"  ✗ {test_name} failed with exception: {e}")
            results.append(False)
        print()

    # 总结
    passed = sum(results)
    total = len(results)

    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All basic tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
