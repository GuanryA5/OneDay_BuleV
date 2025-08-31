# -*- coding: utf-8 -*-
"""
BlueV 日志系统配置

提供统一的日志配置和管理功能，支持文件日志、控制台日志、
日志轮转等功能。
"""

import sys
from datetime import datetime
from typing import Optional

from loguru import logger

from bluev.config import Config


def setup_logging(config: Config) -> None:
    """设置日志系统

    Args:
        config: 应用程序配置对象
    """
    # 移除默认的日志处理器
    logger.remove()

    # 确保日志目录存在
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # 控制台日志配置
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # 文件日志配置
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )

    # 添加控制台日志处理器
    logger.add(
        sys.stdout,
        format=console_format,
        level=config.LOG_LEVEL,
        colorize=True,
        backtrace=config.DEBUG,
        diagnose=config.DEBUG,
    )

    # 添加文件日志处理器 - 普通日志
    logger.add(
        config.LOGS_DIR / "bluev.log",
        format=file_format,
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )

    # 添加文件日志处理器 - 错误日志
    logger.add(
        config.LOGS_DIR / "bluev_error.log",
        format=file_format,
        level="ERROR",
        rotation="5 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )

    # 记录启动信息
    logger.info(f"BlueV {config.APP_VERSION} 启动")
    logger.info(f"调试模式: {config.DEBUG}")
    logger.info(f"日志级别: {config.LOG_LEVEL}")
    logger.info(f"项目根目录: {config.PROJECT_ROOT}")
    logger.info(f"数据目录: {config.DATA_DIR}")


class StructuredLogger:
    """结构化日志记录器"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logger.bind(name=name)

    def _log_structured(self, level: str, message: str, **kwargs):
        """记录结构化日志"""
        extra_data = {
            "timestamp": datetime.now().isoformat(),
            "logger_name": self.name,
            **kwargs,
        }

        # 使用 loguru 的 bind 方法添加额外数据
        bound_logger = self.logger.bind(**extra_data)
        getattr(bound_logger, level.lower())(message)

    def debug(self, message: str, **kwargs):
        """调试日志"""
        self._log_structured("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs):
        """信息日志"""
        self._log_structured("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """警告日志"""
        self._log_structured("WARNING", message, **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """错误日志"""
        if exc_info:
            kwargs["exc_info"] = True
        self._log_structured("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs):
        """严重错误日志"""
        self._log_structured("CRITICAL", message, **kwargs)

    def exception(self, message: str, **kwargs):
        """异常日志（自动包含异常信息）"""
        self.error(message, exc_info=True, **kwargs)


def get_logger(name: Optional[str] = None):
    """获取日志记录器

    Args:
        name: 日志记录器名称，默认为调用模块名

    Returns:
        配置好的日志记录器
    """
    if name is None:
        # 获取调用者的模块名
        import inspect

        frame = inspect.currentframe().f_back
        name = frame.f_globals.get("__name__", "bluev")

    return StructuredLogger(name)


def log_performance(func):
    """性能日志装饰器"""

    def wrapper(*args, **kwargs):
        import time

        start_time = time.time()

        logger_name = f"{func.__module__}.{func.__name__}"
        perf_logger = get_logger(logger_name)

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            perf_logger.info(
                "函数执行完成",
                function=func.__name__,
                execution_time=execution_time,
                success=True,
            )

            return result
        except Exception as e:
            execution_time = time.time() - start_time

            perf_logger.error(
                "函数执行失败",
                function=func.__name__,
                execution_time=execution_time,
                success=False,
                error=str(e),
                exc_info=True,
            )
            raise

    return wrapper


def log_method_calls(cls):
    """类方法调用日志装饰器"""
    get_logger(f"{cls.__module__}.{cls.__name__}")

    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith("_"):
            setattr(cls, attr_name, log_performance(attr))

    return cls
