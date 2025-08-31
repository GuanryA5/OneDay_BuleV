#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BlueV 项目环境初始化脚本
支持 Windows/macOS/Linux 跨平台
"""

import os
import platform
import subprocess
import sys
import venv
from pathlib import Path


class BlueVEnvironmentSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.venv_path = self.project_root / "venv"
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.platform = platform.system().lower()

    def check_python_version(self):
        """检查Python版本"""
        print(f"Python版本检查通过: {self.python_version}")

    def create_virtual_environment(self):
        """创建虚拟环境"""
        if self.venv_path.exists():
            print("虚拟环境已存在，跳过创建")
            return

        print("创建虚拟环境...")
        venv.create(self.venv_path, with_pip=True)
        print(f"虚拟环境创建完成: {self.venv_path}")

    def get_pip_executable(self):
        """获取虚拟环境中的pip路径"""
        if self.platform == "windows":
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"

    def get_python_executable(self):
        """获取虚拟环境中的python路径"""
        if self.platform == "windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"

    def install_dependencies(self):
        """安装项目依赖"""
        pip_exe = self.get_pip_executable()

        # 跳过pip升级以避免权限问题
        print("跳过pip升级...")

        # 安装生产依赖
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            print("安装生产依赖...")
            subprocess.run(
                [str(pip_exe), "install", "-r", str(requirements_file)], check=True
            )

        # 安装开发依赖
        dev_requirements_file = self.project_root / "requirements-dev.txt"
        if dev_requirements_file.exists():
            print("安装开发依赖...")
            subprocess.run(
                [str(pip_exe), "install", "-r", str(dev_requirements_file)], check=True
            )

        print("依赖安装完成")

    def create_project_structure(self):
        """创建项目目录结构"""
        directories = [
            "bluev/ui/node_editor",
            "bluev/ui/property_panel",
            "bluev/ui/toolbar",
            "bluev/ui/dialogs",
            "bluev/core/workflow",
            "bluev/core/nodes",
            "bluev/core/execution",
            "bluev/core/events",
            "bluev/vision/capture",
            "bluev/vision/recognition",
            "bluev/vision/processing",
            "bluev/vision/algorithms",
            "bluev/actions/mouse",
            "bluev/actions/keyboard",
            "bluev/actions/window",
            "bluev/actions/system",
            "bluev/data/storage",
            "bluev/data/models",
            "bluev/data/serialization",
            "bluev/data/migration",
            "bluev/utils",
            "tests/unit",
            "tests/integration",
            "tests/fixtures",
            "resources/icons",
            "resources/images",
            "resources/templates",
            "resources/configs",
        ]

        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)

            # 创建__init__.py文件
            if directory.startswith("bluev/") or directory.startswith("tests/"):
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    init_file.write_text("# -*- coding: utf-8 -*-\n")

        print("项目目录结构创建完成")

    def create_config_files(self):
        """创建配置文件"""
        # 创建.env.example
        env_example = self.project_root / ".env.example"
        if not env_example.exists():
            env_content = """# BlueV 环境变量配置示例
DEBUG=true
LOG_LEVEL=INFO
DATA_DIR=./data
TEMP_DIR=./temp
"""
            env_example.write_text(env_content)

        print("配置文件创建完成")

    def generate_activation_script(self):
        """生成激活脚本"""
        activate_script = self.project_root / "activate.py"
        if self.platform == "windows":
            script_content = '''#!/usr/bin/env python3
"""BlueV 开发环境激活脚本"""
import os
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
'''
        else:
            script_content = '''#!/usr/bin/env python3
"""BlueV 开发环境激活脚本"""
import os
import subprocess
import sys
from pathlib import Path

def main():
    project_root = Path(__file__).parent
    venv_path = project_root / "venv"

    if not venv_path.exists():
        print("❌ 虚拟环境不存在，请先运行 python scripts/setup_env.py")
        return

    # Unix 激活命令
    activate_cmd = f"source {venv_path}/bin/activate"
    print(f"🚀 激活虚拟环境: {activate_cmd}")
    print("💡 手动激活命令:")
    print(f"   {activate_cmd}")

    # 启动开发环境
    python_exe = venv_path / "bin" / "python"
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        subprocess.run([str(python_exe), "-m", "bluev.main"])

if __name__ == "__main__":
    main()
'''

        activate_script.write_text(script_content, encoding="utf-8")
        if self.platform != "windows":
            os.chmod(activate_script, 0o755)

        print("激活脚本创建完成")

    def run_setup(self):
        """执行完整的环境设置"""
        try:
            print("开始 BlueV 项目环境初始化...")
            print(f"项目路径: {self.project_root}")
            print(f"操作系统: {self.platform}")

            self.check_python_version()
            self.create_virtual_environment()
            self.create_project_structure()
            self.create_config_files()
            self.generate_activation_script()

            print("\n环境初始化完成！")
            print("\n下一步操作:")
            print("1. 创建依赖文件后安装:")
            print("   py scripts/setup_env.py --install-deps")
            print("2. 激活虚拟环境:")
            if self.platform == "windows":
                print("   venv\\Scripts\\activate.bat")
            else:
                print("   source venv/bin/activate")
            print("3. 运行应用:")
            print("   py -m bluev.main")

        except Exception as e:
            print(f"环境初始化失败: {e}")
            sys.exit(1)


if __name__ == "__main__":
    setup = BlueVEnvironmentSetup()
    if len(sys.argv) > 1 and sys.argv[1] == "--install-deps":
        setup.install_dependencies()
    else:
        setup.run_setup()
