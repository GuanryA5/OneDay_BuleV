# -*- coding: utf-8 -*-
"""
配置模块单元测试
"""

import os
from unittest.mock import patch

from bluev.config import Config


class TestConfig:
    """配置类测试"""

    def test_default_config(self):
        """测试默认配置"""
        config = Config()

        assert config.APP_NAME == "BlueV"
        assert config.APP_VERSION == "0.1.0"
        assert config.DEBUG is False
        assert config.LOG_LEVEL == "INFO"
        assert config.WINDOW_WIDTH == 1200
        assert config.WINDOW_HEIGHT == 800

    def test_env_override(self):
        """测试环境变量覆盖"""
        with patch.dict(
            os.environ,
            {
                "APP_NAME": "TestBlueV",
                "DEBUG": "true",
                "WINDOW_WIDTH": "1600",
                "LOG_LEVEL": "DEBUG",
            },
        ):
            config = Config()

            assert config.APP_NAME == "TestBlueV"
            assert config.DEBUG is True
            assert config.WINDOW_WIDTH == 1600
            assert config.LOG_LEVEL == "DEBUG"

    def test_path_resolution(self):
        """测试路径解析"""
        config = Config()

        # 所有路径都应该是绝对路径
        assert config.DATA_DIR.is_absolute()
        assert config.TEMP_DIR.is_absolute()
        assert config.LOGS_DIR.is_absolute()
        assert config.WORKFLOWS_DIR.is_absolute()
        assert config.SCREENSHOTS_DIR.is_absolute()
        assert config.RESOURCES_DIR.is_absolute()

    def test_bool_env_parsing(self):
        """测试布尔环境变量解析"""
        Config()  # Just test instantiation

        # 测试各种布尔值表示
        test_cases = [
            ("true", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("invalid", False),  # 无效值应该返回默认值
        ]

        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"DEBUG": env_value}):
                test_config = Config()
                assert test_config.DEBUG == expected

    def test_int_env_parsing(self):
        """测试整数环境变量解析"""
        Config()  # Just test instantiation

        # 测试有效整数
        with patch.dict(os.environ, {"WINDOW_WIDTH": "1920"}):
            test_config = Config()
            assert test_config.WINDOW_WIDTH == 1920

        # 测试无效整数（应该使用默认值）
        with patch.dict(os.environ, {"WINDOW_WIDTH": "invalid"}):
            test_config = Config()
            assert test_config.WINDOW_WIDTH == 1200  # 默认值

    def test_config_methods(self):
        """测试配置方法"""
        config = Config()

        # 测试 get 方法
        assert config.get("APP_NAME") == "BlueV"
        assert config.get("NON_EXISTENT", "default") == "default"

        # 测试 set 方法
        config.set("TEST_KEY", "test_value")
        assert config.get("TEST_KEY") == "test_value"

        # 测试 to_dict 方法
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert "APP_NAME" in config_dict
        assert config_dict["APP_NAME"] == "BlueV"

    def test_database_url(self):
        """测试数据库URL生成"""
        config = Config()

        expected_db_path = config.DATA_DIR / "bluev.db"
        expected_url = f"sqlite:///{expected_db_path}"

        assert config.DATABASE_URL == expected_url

    def test_repr(self):
        """测试字符串表示"""
        config = Config()
        repr_str = repr(config)

        assert "Config" in repr_str
        assert config.APP_NAME in repr_str
        assert str(config.DEBUG) in repr_str
