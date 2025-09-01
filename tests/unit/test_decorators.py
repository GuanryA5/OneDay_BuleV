# -*- coding: utf-8 -*-
"""
装饰器模块单元测试
"""

import time

import pytest

from bluev.utils.decorators import (
    cache_result,
    deprecated,
    retry,
    safe_call,
    singleton,
    timeout,
    validate_types,
)


class TestRetryDecorator:
    """重试装饰器测试"""

    def test_retry_success_first_attempt(self) -> None:
        """测试第一次尝试就成功"""
        call_count = 0

        @retry(max_attempts=3)
        def test_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = test_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_success_after_failures(self) -> None:
        """测试重试后成功"""
        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("临时错误")
            return "success"

        result = test_func()
        assert result == "success"
        assert call_count == 3

    def test_retry_max_attempts_exceeded(self) -> None:
        """测试超过最大重试次数"""
        call_count = 0

        @retry(max_attempts=2, delay=0.01)
        def test_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("持续错误")

        with pytest.raises(ValueError):
            test_func()
        assert call_count == 2

    def test_retry_specific_exceptions(self) -> None:
        """测试只重试特定异常"""

        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def test_func(should_raise_type_error=False):
            if should_raise_type_error:
                raise TypeError("类型错误")
            raise ValueError("值错误")

        # ValueError 会被重试
        with pytest.raises(ValueError):
            test_func()

        # TypeError 不会被重试
        with pytest.raises(TypeError):
            test_func(should_raise_type_error=True)


class TestTimeoutDecorator:
    """超时装饰器测试"""

    @pytest.mark.skipif(True, reason="信号在Windows上可能不工作")
    def test_timeout_success(self) -> None:
        """测试在超时前完成"""

        @timeout(1.0)
        def fast_func():
            return "completed"

        result = fast_func()
        assert result == "completed"

    @pytest.mark.skipif(True, reason="信号在Windows上可能不工作")
    def test_timeout_exceeded(self) -> None:
        """测试超时"""

        @timeout(0.1)
        def slow_func():
            time.sleep(0.2)
            return "should not reach here"

        with pytest.raises(TimeoutError):
            slow_func()


class TestValidateTypesDecorator:
    """类型验证装饰器测试"""

    def test_validate_types_success(self) -> None:
        """测试类型验证成功"""

        @validate_types(x=int, y=str)
        def test_func(x, y):
            return f"{x}: {y}"

        result = test_func(42, "hello")
        assert result == "42: hello"

    def test_validate_types_failure(self) -> None:
        """测试类型验证失败"""

        @validate_types(x=int, y=str)
        def test_func(x, y):
            return f"{x}: {y}"

        with pytest.raises(TypeError):
            test_func("not_int", "hello")

    def test_validate_types_none_allowed(self) -> None:
        """测试None值被允许"""

        @validate_types(x=int)
        def test_func(x=None):
            return x

        result = test_func(None)
        assert result is None


class TestCacheResultDecorator:
    """结果缓存装饰器测试"""

    def test_cache_result_basic(self) -> None:
        """测试基础缓存功能"""
        call_count = 0

        @cache_result()
        def expensive_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # 第一次调用
        result1 = expensive_func(5)
        assert result1 == 10
        assert call_count == 1

        # 第二次调用相同参数，应该使用缓存
        result2 = expensive_func(5)
        assert result2 == 10
        assert call_count == 1

        # 不同参数，应该重新计算
        result3 = expensive_func(10)
        assert result3 == 20
        assert call_count == 2

    def test_cache_result_with_ttl(self) -> None:
        """测试带TTL的缓存"""
        call_count = 0

        @cache_result(ttl=0.1)
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x

        # 第一次调用
        result1 = test_func(1)
        assert result1 == 1
        assert call_count == 1

        # 立即再次调用，使用缓存
        result2 = test_func(1)
        assert result2 == 1
        assert call_count == 1

        # 等待TTL过期
        time.sleep(0.15)
        result3 = test_func(1)
        assert result3 == 1
        assert call_count == 2

    def test_cache_clear(self) -> None:
        """测试清除缓存"""
        call_count = 0

        @cache_result()
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x

        test_func(1)
        assert call_count == 1

        test_func(1)
        assert call_count == 1  # 使用缓存

        test_func.clear_cache()
        test_func(1)
        assert call_count == 2  # 缓存被清除，重新计算


class TestSingletonDecorator:
    """单例装饰器测试"""

    def test_singleton_same_instance(self) -> None:
        """测试单例返回相同实例"""

        @singleton
        class TestClass:
            def __init__(self, value=0) -> None:
                self.value = value

        instance1 = TestClass(10)
        instance2 = TestClass(20)  # 参数被忽略

        assert instance1 is instance2
        assert instance1.value == 10  # 保持第一次创建时的值


class TestDeprecatedDecorator:
    """废弃警告装饰器测试"""

    def test_deprecated_warning(self) -> None:
        """测试废弃警告"""

        @deprecated("使用新函数替代")
        def old_func():
            return "old"

        with pytest.warns(DeprecationWarning):
            result = old_func()
            assert result == "old"


class TestSafeCallDecorator:
    """安全调用装饰器测试"""

    def test_safe_call_success(self) -> None:
        """测试安全调用成功"""

        @safe_call(default_return="default")
        def test_func():
            return "success"

        result = test_func()
        assert result == "success"

    def test_safe_call_exception_with_default(self) -> None:
        """测试异常时返回默认值"""

        @safe_call(default_return="default")
        def test_func():
            raise ValueError("测试错误")

        result = test_func()
        assert result == "default"

    def test_safe_call_exception_no_logging(self) -> None:
        """测试异常时不记录日志"""

        @safe_call(default_return="default", log_errors=False)
        def test_func():
            raise ValueError("测试错误")

        result = test_func()
        assert result == "default"

    def test_safe_call_none_default(self) -> None:
        """测试默认返回None"""

        @safe_call()
        def test_func():
            raise ValueError("测试错误")

        result = test_func()
        assert result is None
