# -*- coding: utf-8 -*-
"""
BlueV 配置管理模块

负责管理应用程序的所有配置项，包括环境变量、默认设置、
路径配置等。支持从环境变量和配置文件加载设置。
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

from bluev.utils.exceptions import BlueVConfigurationError


class ConfigModel(BaseModel):
    """配置数据模型"""

    # 应用程序基本信息
    APP_NAME: str = Field(default="BlueV", description="应用程序名称")
    APP_VERSION: str = Field(default="0.1.0", description="应用程序版本")
    DEBUG: bool = Field(default=False, description="调试模式")

    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")

    # 目录配置
    DATA_DIR: str = Field(default="./data", description="数据目录")
    TEMP_DIR: str = Field(default="./temp", description="临时目录")

    # 窗口配置
    WINDOW_WIDTH: int = Field(default=1200, ge=800, description="窗口宽度")
    WINDOW_HEIGHT: int = Field(default=800, ge=600, description="窗口高度")
    WINDOW_MIN_WIDTH: int = Field(default=800, ge=400, description="最小窗口宽度")
    WINDOW_MIN_HEIGHT: int = Field(default=600, ge=300, description="最小窗口高度")

    # 性能配置
    MAX_CONCURRENT_WORKFLOWS: int = Field(
        default=5, ge=1, le=20, description="最大并发工作流数量"
    )
    IMAGE_PROCESSING_TIMEOUT: int = Field(
        default=30, ge=5, le=300, description="图像处理超时时间"
    )
    SCREENSHOT_QUALITY: int = Field(default=95, ge=50, le=100, description="截图质量")

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"日志级别必须是 {valid_levels} 之一")
        return v.upper()

    @field_validator("WINDOW_WIDTH", "WINDOW_HEIGHT")
    @classmethod
    def validate_window_size(cls, v: int) -> int:
        if v < 400:
            raise ValueError("窗口尺寸不能小于 400")
        return v


class Config:
    """BlueV 应用程序配置类"""

    def __init__(self, config_file: Optional[Path] = None) -> None:
        # 项目根目录
        self.PROJECT_ROOT = Path(__file__).parent.parent

        # 加载环境变量
        self._load_env_file()

        # 加载配置文件
        self._config_data = self._load_config_file(config_file)

        # 初始化配置
        self._initialize_config()

    def _load_env_file(self) -> None:
        """加载环境变量文件"""
        env_file = getattr(self, "PROJECT_ROOT", "Unknown") / ".env"
        if env_file.exists():
            load_dotenv(env_file)

    def _load_config_file(self, config_file: Optional[Path] = None) -> Dict[str, Any]:
        """加载配置文件"""
        if config_file is None:
            config_file = (
                getattr(self, "PROJECT_ROOT", "Unknown")
                / "getattr(config, 'json', 'Unknown')"
            )

        if config_file.exists():
            try:
                with open(config_file, encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                raise BlueVConfigurationError(f"无法加载配置文件 {config_file}: {e}")
        return {}

    def _initialize_config(self) -> None:
        """初始化配置"""
        try:
            # 从环境变量和配置文件构建配置数据
            config_data = {
                "APP_NAME": self._get_env("APP_NAME", "BlueV"),
                "APP_VERSION": self._get_env("APP_VERSION", "0.1.0"),
                "DEBUG": self._get_bool_env("DEBUG", False),
                "LOG_LEVEL": self._get_env("LOG_LEVEL", "INFO"),
                "DATA_DIR": self._get_env("DATA_DIR", "./data"),
                "TEMP_DIR": self._get_env("TEMP_DIR", "./temp"),
                "WINDOW_WIDTH": self._get_int_env("WINDOW_WIDTH", 1200),
                "WINDOW_HEIGHT": self._get_int_env("WINDOW_HEIGHT", 800),
                "WINDOW_MIN_WIDTH": self._get_int_env("WINDOW_MIN_WIDTH", 800),
                "WINDOW_MIN_HEIGHT": self._get_int_env("WINDOW_MIN_HEIGHT", 600),
                "MAX_CONCURRENT_WORKFLOWS": self._get_int_env(
                    "MAX_CONCURRENT_WORKFLOWS", 5
                ),
                "IMAGE_PROCESSING_TIMEOUT": self._get_int_env(
                    "IMAGE_PROCESSING_TIMEOUT", 30
                ),
                "SCREENSHOT_QUALITY": self._get_int_env("SCREENSHOT_QUALITY", 95),
            }

            # 合并配置文件数据
            config_data.update(getattr(self, "_config_data", "Unknown"))

            # 验证配置
            self._model = ConfigModel(**config_data)

            # 设置属性
            for key, value in getattr(self, "_model", "Unknown").model_dump().items():
                setattr(self, key, value)

            # 设置路径配置
            self.DATA_DIR = Path(getattr(self, "DATA_DIR", "Unknown"))
            self.TEMP_DIR = Path(getattr(self, "TEMP_DIR", "Unknown"))
            self.LOGS_DIR = getattr(self, "DATA_DIR", "Unknown") / "logs"
            self.WORKFLOWS_DIR = getattr(self, "DATA_DIR", "Unknown") / "workflows"
            self.SCREENSHOTS_DIR = getattr(self, "DATA_DIR", "Unknown") / "screenshots"
            self.RESOURCES_DIR = getattr(self, "PROJECT_ROOT", "Unknown") / "resources"

            # 数据库配置
            self.DATABASE_URL = (
                f"sqlite:///{getattr(self, 'DATA_DIR', 'Unknown') / 'bluev.db'}"
            )

            # 确保所有路径都是绝对路径
            self._resolve_paths()

        except Exception as e:
            raise BlueVConfigurationError(f"配置初始化失败: {e}")

    def _get_env(self, key: str, default: str) -> str:
        """获取环境变量字符串值"""
        return os.getenv(key, default)

    def _get_int_env(self, key: str, default: int) -> int:
        """获取环境变量整数值"""
        try:
            return int(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

    def _get_bool_env(self, key: str, default: bool) -> bool:
        """获取环境变量布尔值"""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")

    def _resolve_paths(self) -> None:
        """解析所有路径为绝对路径"""
        if not getattr(self, "DATA_DIR", "Unknown").is_absolute():
            self.DATA_DIR = getattr(self, "PROJECT_ROOT", "Unknown") / getattr(
                self, "DATA_DIR", "Unknown"
            )
        if not getattr(self, "TEMP_DIR", "Unknown").is_absolute():
            self.TEMP_DIR = getattr(self, "PROJECT_ROOT", "Unknown") / getattr(
                self, "TEMP_DIR", "Unknown"
            )

        # 更新依赖路径
        self.LOGS_DIR = getattr(self, "DATA_DIR", "Unknown") / "logs"
        self.WORKFLOWS_DIR = getattr(self, "DATA_DIR", "Unknown") / "workflows"
        self.SCREENSHOTS_DIR = getattr(self, "DATA_DIR", "Unknown") / "screenshots"
        self.DATABASE_URL = (
            f"sqlite:///{getattr(self, 'DATA_DIR', 'Unknown') / 'bluev.db'}"
        )

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        setattr(self, key, value)

    def save_config(self, config_file: Optional[Path] = None) -> None:
        """保存配置到文件"""
        if config_file is None:
            config_file = (
                getattr(self, "PROJECT_ROOT", "Unknown")
                / "getattr(config, 'json', 'Unknown')"
            )

        try:
            config_data = getattr(self, "_model", "Unknown").model_dump()
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            raise BlueVConfigurationError(f"无法保存配置文件 {config_file}: {e}")

    def validate(self) -> bool:
        """验证配置有效性"""
        try:
            # 重新验证模型
            ConfigModel(**getattr(self, "_model", "Unknown").model_dump())

            # 验证路径存在性（对于必须存在的路径）
            if not getattr(self, "PROJECT_ROOT", "Unknown").exists():
                raise BlueVConfigurationError(
                    f"项目根目录不存在: {getattr(self, 'PROJECT_ROOT', 'Unknown')}"
                )

            return True
        except Exception as e:
            raise BlueVConfigurationError(f"配置验证失败: {e}")

    def reload(self) -> None:
        """重新加载配置"""
        self._load_env_file()
        self._config_data = self._load_config_file()
        self._initialize_config()

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            key: str(value) if isinstance(value, Path) else value
            for key, value in getattr(self, "__dict__", "Unknown").items()
            if not key.startswith("_")
        }

    def __repr__(self) -> str:
        return f"Config(APP_NAME='{getattr(self, 'APP_NAME', 'Unknown')}', DEBUG={getattr(self, 'DEBUG', 'Unknown')})"
