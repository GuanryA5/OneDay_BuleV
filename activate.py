#!/usr/bin/env python3
"""BlueV 开发环境激活脚本"""

import subprocess
import sys
from pathlib import Path


def main():
    project_root = Path(__file__).parent
    venv_path = project_root / "venv"

    if not venv_path.exists():
        print("❌ 虚拟环境不存在，请先运行 python scripts/setup_env.py")
        return

    # Windows 激活命令
    activate_cmd = str(venv_path / "Scripts" / "activate.bat")
    print(f"🚀 激活虚拟环境: {activate_cmd}")
    print("💡 手动激活命令:")
    print(f"   {activate_cmd}")

    # 启动开发环境
    python_exe = venv_path / "Scripts" / "python.exe"
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        subprocess.run([str(python_exe), "-m", "bluev.main"])


if __name__ == "__main__":
    main()
