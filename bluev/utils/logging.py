# -*- coding: utf-8 -*-
"""
BlueV 日志系统配置

提供统一的日志配置和管理功能，支持文件日志、控制台日志、
日志轮转等功能。
"""

import io
import sys
from datetime import datetime
from typing import Any, Callable, Optional

from loguru import logger

from bluev.config import Config

_CONFIGURED = False
_UTF8_CONSOLE_INITIALIZED = False


def _ensure_utf8_console_sink() -> None:
    """确保控制台使用 UTF-8 输出，避免中文乱码。

    仅在未通过 setup_logging 正式配置时启用，避免覆盖文件日志等配置。
    """
    global _UTF8_CONSOLE_INITIALIZED
    if _CONFIGURED or _UTF8_CONSOLE_INITIALIZED:
        return

    try:
        logger.remove()
    except Exception as e:
        # 忽略移除默认处理器时的异常，这是正常的
        # 记录调试信息以便排查问题
        import sys

        print(f"Debug: 移除默认日志处理器时的预期异常: {e}", file=sys.stderr)

    # 包装 stdout，强制使用 UTF-8 编码
    stream = sys.stdout
    if hasattr(sys.stdout, "buffer"):
        try:
            stream = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
        except Exception:
            stream = sys.stdout

    console_format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
    logger.add(
        stream,
        format=console_format,
        level="DEBUG",
        colorize=False,
        backtrace=False,
        diagnose=False,
    )
    _UTF8_CONSOLE_INITIALIZED = True


def setup_logging(config: Config) -> None:
    """设置日志系统

    Args:
        config: 应用程序配置对象
    """
    global _CONFIGURED
    # 移除默认的日志处理器
    logger.remove()

    # 确保日志目录存在
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # 控制台日志配置（UTF-8）
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

    # 控制台 sink 使用 UTF-8 包装
    stream = sys.stdout
    if hasattr(sys.stdout, "buffer"):
        try:
            stream = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
        except Exception:
            stream = sys.stdout

    # 添加控制台日志处理器
    logger.add(
        stream,
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
        encoding="utf-8",
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
        encoding="utf-8",
    )

    # 记录启动信息
    logger.info(f"BlueV {getattr(config, 'APP_VERSION', 'Unknown')} 启动")
    logger.info(f"调试模式: {getattr(config, 'DEBUG', 'Unknown')}")
    logger.info(f"日志级别: {getattr(config, 'LOG_LEVEL', 'Unknown')}")
    logger.info(f"项目根目录: {getattr(config, 'PROJECT_ROOT', 'Unknown')}")
    logger.info(f"数据目录: {getattr(config, 'DATA_DIR', 'Unknown')}")

    _CONFIGURED = True


class StructuredLogger:
    """结构化日志记录器"""

    def __init__(self, name: str) -> None:
        # 名称保留；logger 属性保持可用（兼容测试中对 .logger 非空的断言）
        self.name = name
        self.logger = logger  # 基础 loguru logger（不在此处预绑定）

    def _log_structured(self, level: str, message: str, **kwargs: Any) -> None:
        """记录结构化日志（按调用时绑定，满足单测期望）"""
        extra_data = {
            "timestamp": datetime.now().isoformat(),
            "logger_name": getattr(self, "name", "Unknown"),
            **kwargs,
        }

        # 在调用处绑定（包含 name 与结构化字段），确保 mock_logger.bind(...) 返回的对象直接接收 debug/info 等调用
        bound_logger = self.logger.bind(name=self.name, **extra_data)
        getattr(bound_logger, level.lower())(message)

    def debug(self, message: str, **kwargs: Any) -> None:
        """调试日志"""
        self._log_structured("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """信息日志"""
        self._log_structured("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """警告日志"""
        self._log_structured("WARNING", message, **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        """错误日志"""
        if exc_info:
            kwargs["exc_info"] = True
        self._log_structured("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """严重错误日志"""
        self._log_structured("CRITICAL", message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """异常日志（自动包含异常信息）"""
        self.error(message, exc_info=True, **kwargs)


def get_logger(name: Optional[str] = None) -> StructuredLogger:
    """获取日志记录器，确保控制台 UTF-8 输出避免中文乱码"""
    _ensure_utf8_console_sink()

    if name is None:
        # 获取调用者的模块名
        import inspect

        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get("__name__", "bluev")
        else:
            name = "bluev"

    return StructuredLogger(name)


def log_performance(func: Callable[..., Any]) -> Callable[..., Any]:
    """性能日志装饰器"""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
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


def log_method_calls(cls: type) -> type:
    """类方法调用日志装饰器"""
    get_logger(f"{cls.__module__}.{cls.__name__}")

    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith("_"):
            setattr(cls, attr_name, log_performance(attr))

    return cls
