# -*- coding: utf-8 -*-
"""
pytest 配置文件

定义测试夹具、配置和共享的测试工具。
"""

import sys
from pathlib import Path

import pytest

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import after path setup
from bluev.config import Config  # noqa: E402


@pytest.fixture
def config():
    """测试配置夹具"""
    config = Config()
    # 使用测试专用的目录
    config.DATA_DIR = Path("./test_data")
    config.TEMP_DIR = Path("./test_temp")
    config.DEBUG = True
    config.LOG_LEVEL = "DEBUG"
    return config


@pytest.fixture
def mock_qt_app():
    """模拟 Qt 应用程序夹具"""
    from PySide6.QtWidgets import QApplication

    # 检查是否已有应用程序实例
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    yield app

    # 清理（如果需要）
    # app.quit()


@pytest.fixture
def temp_dir(tmp_path):
    """临时目录夹具"""
    return tmp_path


@pytest.fixture
def sample_workflow_data():
    """示例工作流数据夹具"""
    return {
        "id": "test_workflow_001",
        "name": "测试工作流",
        "description": "用于测试的示例工作流",
        "nodes": [
            {
                "id": "node_001",
                "type": "screenshot",
                "position": {"x": 100, "y": 100},
                "properties": {},
            },
            {
                "id": "node_002",
                "type": "find_image",
                "position": {"x": 300, "y": 100},
                "properties": {"template_path": "test_template.png", "threshold": 0.8},
            },
        ],
        "connections": [
            {
                "from_node": "node_001",
                "from_output": "screenshot",
                "to_node": "node_002",
                "to_input": "image",
            }
        ],
    }


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """自动清理测试文件夹具"""
    yield

    # 测试后清理
    import shutil

    test_dirs = ["test_data", "test_temp", "test_logs"]
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            shutil.rmtree(test_dir, ignore_errors=True)
