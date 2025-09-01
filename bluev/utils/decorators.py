# -*- coding: utf-8 -*-
"""
BlueV 装饰器模块

提供各种实用的装饰器函数。
"""

import functools
import time
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from bluev.utils.logging import get_logger

# 定义类型变量
F = TypeVar('F', bound=Callable[..., Any])


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable[[F], F]:
    """重试装饰器

    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟时间倍数
        exceptions: 需要重试的异常类型
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_logger(f"{func.__module__}.{func.__name__}")

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        logger.error(
                            f"函数 {func.__name__} 重试 {max_attempts} 次后仍然失败",
                            error=str(e),
                            attempts=max_attempts,
                        )
                        raise

                    wait_time = delay * (backoff**attempt)
                    logger.warning(
                        f"函数 {func.__name__} 第 {attempt + 1} 次执行失败，{wait_time:.2f}秒后重试",
                        error=str(e),
                        attempt=attempt + 1,
                        wait_time=wait_time,
                    )
                    time.sleep(wait_time)

            return None  # 不应该到达这里

        return wrapper  # type: ignore

    return decorator


def timeout(seconds: float) -> Callable[[F], F]:
    """超时装饰器

    Args:
        seconds: 超时时间（秒）
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            import platform
            import threading
            import time

            if platform.system() == "Windows":
                # Windows 不支持 SIGALRM，使用线程实现超时
                result: list[Any] = [None]
                exception: list[Exception] = [None]  # type: ignore

                def target() -> None:
                    try:
                        result[0] = func(*args, **kwargs)
                    except Exception as e:
                        exception[0] = e

                thread = threading.Thread(target=target)
                thread.daemon = True
                thread.start()
                thread.join(timeout=seconds)

                if thread.is_alive():
                    raise TimeoutError(f"函数 {func.__name__} 执行超时 ({seconds}秒)")

                if exception[0]:
                    raise exception[0]

                return result[0]
            else:
                # Unix 系统使用信号
                import signal

                def timeout_handler(signum: int, frame: Any) -> None:
                    raise TimeoutError(f"函数 {func.__name__} 执行超时 ({seconds}秒)")

                if hasattr(signal, 'SIGALRM') and hasattr(signal, 'alarm'):
                    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(int(seconds))

                    try:
                        result = func(*args, **kwargs)
                        signal.alarm(0)
                        return result
                    finally:
                        signal.signal(signal.SIGALRM, old_handler)
                else:
                    # 如果信号不可用，直接执行函数
                    return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def validate_types(**type_hints: Any) -> Callable[[F], F]:
    """类型验证装饰器

    Args:
        **type_hints: 参数名和对应的类型
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 获取函数签名
            import inspect

            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # 验证类型
            for param_name, expected_type in type_hints.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if value is not None and not isinstance(value, expected_type):
                        raise TypeError(
                            f"参数 {param_name} 期望类型 {expected_type.__name__}，"
                            f"实际类型 {type(value).__name__}"
                        )

            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def cache_result(ttl: Optional[float] = None) -> Callable[[F], F]:
    """结果缓存装饰器

    Args:
        ttl: 缓存生存时间（秒），None 表示永久缓存
    """

    def decorator(func: F) -> F:
        cache: Dict[str, Dict[str, Any]] = {}

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 生成缓存键
            cache_key = str(hash((args, tuple(sorted(kwargs.items())))))

            # 检查缓存
            if cache_key in cache:
                cached_data = cache[cache_key]

                # 检查TTL
                if ttl is None or time.time() - cached_data["timestamp"] < ttl:
                    return cached_data["result"]
                else:
                    # 缓存过期，删除
                    del cache[cache_key]

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache[cache_key] = {"result": result, "timestamp": time.time()}

            return result

        # 添加清除缓存的方法
        setattr(wrapper, 'clear_cache', lambda: cache.clear())
        setattr(wrapper, 'cache_info', lambda: {
            "cache_size": len(cache),
            "cache_keys": list(cache.keys()),
        })

        return wrapper  # type: ignore

    return decorator


def singleton(cls: type) -> type:
    """单例装饰器"""
    instances = {}

    @functools.wraps(cls)
    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance  # type: ignore


def deprecated(reason: str = "") -> Callable[[F], F]:
    """废弃警告装饰器

    Args:
        reason: 废弃原因
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            import warnings

            message = f"函数 {func.__name__} 已废弃"
            if reason:
                message += f": {reason}"

            warnings.warn(message, DeprecationWarning, stacklevel=2)

            logger = get_logger(f"{func.__module__}.{func.__name__}")
            logger.warning("使用了废弃的函数", function=func.__name__, reason=reason)

            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def safe_call(
    default_return: Any = None, log_errors: bool = True
) -> Callable[[F], F]:
    """安全调用装饰器，捕获异常并返回默认值

    Args:
        default_return: 发生异常时的默认返回值
        log_errors: 是否记录错误日志
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger = get_logger(f"{func.__module__}.{func.__name__}")
                    logger.error(
                        f"函数 {func.__name__} 执行失败，返回默认值",
                        error=str(e),
                        default_return=default_return,
                        exc_info=True,
                    )
                return default_return

        return wrapper  # type: ignore

    return decorator
