# -*- coding: utf-8 -*-
"""
异常处理模块单元测试
"""

import pytest

from bluev.utils.exceptions import (
    BlueVConfigurationError,
    BlueVCriticalError,
    BlueVException,
    BlueVValidationError,
    exception_context,
    handle_exception,
    safe_execute,
)


class TestBlueVException:
    """BlueV异常类测试"""

    def test_basic_exception(self) -> None:
        """测试基础异常"""
        exc = BlueVException("测试错误")

        assert str(exc) == "[BlueVException] 测试错误"
        assert exc.message == "测试错误"
        assert exc.error_code == "BlueVException"
        assert exc.details == {}
        assert exc.cause is None

    def test_exception_with_details(self) -> None:
        """测试带详细信息的异常"""
        details = {"key": "value", "number": 42}
        exc = BlueVException("测试错误", error_code="TEST_ERROR", details=details)

        assert exc.error_code == "TEST_ERROR"
        assert exc.details == details

    def test_exception_with_cause(self) -> None:
        """测试带原因的异常"""
        original_error = ValueError("原始错误")
        exc = BlueVException("包装错误", cause=original_error)

        assert exc.cause == original_error

    def test_exception_hierarchy(self) -> None:
        """测试异常层次结构"""
        critical_error = BlueVCriticalError("严重错误")
        config_error = BlueVConfigurationError("配置错误")
        validation_error = BlueVValidationError("验证错误")

        assert isinstance(critical_error, BlueVException)
        assert isinstance(config_error, BlueVException)
        assert isinstance(validation_error, BlueVException)


class TestHandleException:
    """异常处理函数测试"""

    def test_handle_bluev_exception(self) -> None:
        """测试处理BlueV异常"""
        original_exc = BlueVValidationError("验证失败")

        # 不重新抛出
        result = handle_exception(original_exc, reraise=False)
        assert result == original_exc

        # 重新抛出
        with pytest.raises(BlueVValidationError):
            handle_exception(original_exc, reraise=True)

    def test_handle_standard_exception(self) -> None:
        """测试处理标准异常"""
        original_exc = ValueError("值错误")

        # 不重新抛出
        result = handle_exception(original_exc, reraise=False)
        assert isinstance(result, BlueVValidationError)
        assert "值错误" in str(result)

        # 重新抛出
        with pytest.raises(BlueVValidationError):
            handle_exception(original_exc, reraise=True)

    def test_handle_exception_with_context(self) -> None:
        """测试带上下文的异常处理"""
        original_exc = FileNotFoundError("文件未找到")

        result = handle_exception(original_exc, context="读取配置文件", reraise=False)

        assert isinstance(result, BlueVException)  # 应该映射到文件系统错误
        assert "读取配置文件" in str(result)
        assert "文件未找到" in str(result)


class TestSafeExecute:
    """安全执行函数测试"""

    def test_safe_execute_success(self) -> None:
        """测试安全执行成功"""

        def test_func(x, y):
            return x + y

        result = safe_execute(test_func, 1, 2)
        assert result == 3

    def test_safe_execute_failure(self) -> None:
        """测试安全执行失败"""

        def test_func():
            raise ValueError("测试错误")

        with pytest.raises(BlueVValidationError):
            safe_execute(test_func)


class TestExceptionContext:
    """异常上下文管理器测试"""

    def test_exception_context_success(self) -> None:
        """测试异常上下文成功"""
        with exception_context("测试操作"):
            result = 1 + 1

        assert result == 2

    def test_exception_context_failure_reraise(self) -> None:
        """测试异常上下文失败并重新抛出"""
        with pytest.raises(BlueVValidationError):
            with exception_context("测试操作", reraise=True):
                raise ValueError("测试错误")

    def test_exception_context_failure_no_reraise(self) -> None:
        """测试异常上下文失败不重新抛出"""
        with exception_context("测试操作", reraise=False):
            raise ValueError("测试错误")

        # 如果到达这里，说明异常被抑制了
        assert True
