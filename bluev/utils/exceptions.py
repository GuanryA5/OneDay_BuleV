# -*- coding: utf-8 -*-
"""
BlueV 异常处理模块

定义应用程序的异常层次结构和错误处理机制。
"""

from typing import Any, Callable, Dict, Optional


class BlueVException(Exception):
    """BlueV 基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.cause = cause

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', error_code='{self.error_code}')"


class BlueVCriticalError(BlueVException):
    """BlueV 严重错误 - 需要立即终止应用程序"""

    pass


class BlueVConfigurationError(BlueVException):
    """配置相关错误"""

    pass


class BlueVValidationError(BlueVException):
    """数据验证错误"""

    pass


class BlueVFileSystemError(BlueVException):
    """文件系统操作错误"""

    pass


class BlueVNetworkError(BlueVException):
    """网络相关错误"""

    pass


class BlueVUIError(BlueVException):
    """用户界面相关错误"""

    pass


class BlueVWorkflowError(BlueVException):
    """工作流执行错误"""

    pass


class BlueVNodeError(BlueVException):
    """节点相关错误"""

    pass


class BlueVVisionError(BlueVException):
    """计算机视觉相关错误"""

    pass


class BlueVActionError(BlueVException):
    """操作执行相关错误"""

    pass


class BlueVDataError(BlueVException):
    """数据处理相关错误"""

    pass


def handle_exception(
    exception: Exception,
    context: Optional[str] = None,
    reraise: bool = True,
    default_message: str = "发生未知错误",
) -> Optional[BlueVException]:
    """
    统一异常处理函数

    Args:
        exception: 原始异常
        context: 异常发生的上下文
        reraise: 是否重新抛出异常
        default_message: 默认错误消息

    Returns:
        处理后的 BlueV 异常，如果 reraise=False

    Raises:
        BlueVException: 如果 reraise=True
    """
    # 如果已经是 BlueV 异常，直接处理
    if isinstance(exception, BlueVException):
        if reraise:
            raise exception
        return exception

    # 根据异常类型转换为对应的 BlueV 异常
    message = str(exception) or default_message
    if context:
        message = f"{context}: {message}"

    # 异常类型映射
    exception_mapping = {
        FileNotFoundError: BlueVFileSystemError,
        PermissionError: BlueVFileSystemError,
        OSError: BlueVFileSystemError,
        ValueError: BlueVValidationError,
        TypeError: BlueVValidationError,
        KeyError: BlueVValidationError,
        ConnectionError: BlueVNetworkError,
        TimeoutError: BlueVNetworkError,
    }

    # 选择合适的异常类型
    bluev_exception_class = exception_mapping.get(type(exception), BlueVException)

    bluev_exception = bluev_exception_class(message=message, cause=exception)

    if reraise:
        raise bluev_exception

    return bluev_exception


def safe_execute(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """
    安全执行函数，捕获并转换异常

    Args:
        func: 要执行的函数
        *args: 函数参数
        **kwargs: 函数关键字参数

    Returns:
        函数执行结果或 None（如果发生异常）

    Raises:
        BlueVException: 转换后的异常
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_exception(e, context=f"执行函数 {func.__name__}")


class ExceptionContext:
    """异常上下文管理器"""

    def __init__(
        self, context: str, reraise: bool = True, exception_class: type = BlueVException
    ):
        self.context = context
        self.reraise = reraise
        self.exception_class = exception_class

    def __enter__(self) -> "ExceptionContext":
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> bool:
        if exc_type is not None and exc_value is not None:
            # 确保 exc_value 是 Exception 类型
            if isinstance(exc_value, Exception):
                handle_exception(exc_value, context=self.context, reraise=self.reraise)
        return not self.reraise  # 如果不重新抛出，则抑制异常


# 便捷的上下文管理器
def exception_context(context: str, reraise: bool = True) -> ExceptionContext:
    """创建异常上下文管理器的便捷函数"""
    return ExceptionContext(context, reraise)
