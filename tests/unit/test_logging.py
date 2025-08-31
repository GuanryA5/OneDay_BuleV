# -*- coding: utf-8 -*-
"""
日志系统模块单元测试
"""

from unittest.mock import Mock, patch

import pytest

from bluev.utils.logging import (
    StructuredLogger,
    get_logger,
    log_method_calls,
    log_performance,
    setup_logging,
)


class TestSetupLogging:
    """日志设置测试"""

    def test_setup_logging_basic(self, config):
        """测试基础日志设置"""
        with patch("bluev.utils.logging.logger") as mock_logger:
            setup_logging(config)

            # 验证日志处理器被添加
            assert mock_logger.remove.called
            assert mock_logger.add.call_count >= 3  # 控制台 + 普通文件 + 错误文件

    def test_setup_logging_creates_directories(self, config, tmp_path):
        """测试日志设置创建目录"""
        config.LOGS_DIR = tmp_path / "logs"

        with patch("bluev.utils.logging.logger"):
            setup_logging(config)

            # 验证日志目录被创建
            assert config.LOGS_DIR.exists()

    def test_setup_logging_debug_mode(self, config):
        """测试调试模式的日志设置"""
        config.DEBUG = True
        config.LOG_LEVEL = "DEBUG"

        with patch("bluev.utils.logging.logger") as mock_logger:
            setup_logging(config)

            # 在调试模式下应该启用backtrace和diagnose
            mock_logger.add.assert_called()


class TestStructuredLogger:
    """结构化日志记录器测试"""

    def test_structured_logger_init(self):
        """测试结构化日志记录器初始化"""
        logger = StructuredLogger("test_logger")

        assert logger.name == "test_logger"
        assert logger.logger is not None

    @patch("bluev.utils.logging.logger")
    def test_structured_logger_debug(self, mock_logger):
        """测试调试日志"""
        mock_bound_logger = Mock()
        mock_logger.bind.return_value = mock_bound_logger

        logger = StructuredLogger("test")
        logger.debug("测试消息", key="value")

        mock_logger.bind.assert_called()
        mock_bound_logger.debug.assert_called_with("测试消息")

    @patch("bluev.utils.logging.logger")
    def test_structured_logger_info(self, mock_logger):
        """测试信息日志"""
        mock_bound_logger = Mock()
        mock_logger.bind.return_value = mock_bound_logger

        logger = StructuredLogger("test")
        logger.info("测试消息", key="value")

        mock_bound_logger.info.assert_called_with("测试消息")

    @patch("bluev.utils.logging.logger")
    def test_structured_logger_error_with_exc_info(self, mock_logger):
        """测试带异常信息的错误日志"""
        mock_bound_logger = Mock()
        mock_logger.bind.return_value = mock_bound_logger

        logger = StructuredLogger("test")
        logger.error("错误消息", exc_info=True, key="value")

        mock_bound_logger.error.assert_called_with("错误消息")

    @patch("bluev.utils.logging.logger")
    def test_structured_logger_exception(self, mock_logger):
        """测试异常日志"""
        mock_bound_logger = Mock()
        mock_logger.bind.return_value = mock_bound_logger

        logger = StructuredLogger("test")
        logger.exception("异常消息", key="value")

        mock_bound_logger.error.assert_called_with("异常消息")


class TestGetLogger:
    """获取日志记录器测试"""

    def test_get_logger_with_name(self):
        """测试指定名称获取日志记录器"""
        logger = get_logger("test_logger")

        assert isinstance(logger, StructuredLogger)
        assert logger.name == "test_logger"

    def test_get_logger_without_name(self):
        """测试不指定名称获取日志记录器"""
        logger = get_logger()

        assert isinstance(logger, StructuredLogger)
        # 应该使用调用模块的名称
        assert logger.name is not None


class TestLogPerformanceDecorator:
    """性能日志装饰器测试"""

    @patch("bluev.utils.logging.get_logger")
    def test_log_performance_success(self, mock_get_logger):
        """测试性能日志装饰器成功情况"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @log_performance
        def test_func(x, y):
            return x + y

        result = test_func(1, 2)

        assert result == 3
        mock_logger.info.assert_called()

        # 检查日志调用参数
        call_args = mock_logger.info.call_args
        assert "函数执行完成" in call_args[0][0]
        assert call_args[1]["function"] == "test_func"
        assert call_args[1]["success"] is True
        assert "execution_time" in call_args[1]

    @patch("bluev.utils.logging.get_logger")
    def test_log_performance_exception(self, mock_get_logger):
        """测试性能日志装饰器异常情况"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @log_performance
        def test_func():
            raise ValueError("测试错误")

        with pytest.raises(ValueError):
            test_func()

        mock_logger.error.assert_called()

        # 检查错误日志调用参数
        call_args = mock_logger.error.call_args
        assert "函数执行失败" in call_args[0][0]
        assert call_args[1]["function"] == "test_func"
        assert call_args[1]["success"] is False
        assert "execution_time" in call_args[1]
        assert call_args[1]["exc_info"] is True


class TestLogMethodCallsDecorator:
    """类方法调用日志装饰器测试"""

    @patch("bluev.utils.logging.get_logger")
    def test_log_method_calls(self, mock_get_logger):
        """测试类方法调用日志装饰器"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @log_method_calls
        class TestClass:
            def public_method(self):
                return "result"

            def _private_method(self):
                return "private"

        obj = TestClass()
        result = obj.public_method()

        assert result == "result"
        # 公共方法应该被装饰
        mock_logger.info.assert_called()

        # 私有方法不应该被装饰（因为以_开头）
        obj._private_method()


class TestLoggingIntegration:
    """日志系统集成测试"""

    def test_logging_integration_with_config(self, config, tmp_path):
        """测试日志系统与配置的集成"""
        config.LOGS_DIR = tmp_path / "logs"
        config.LOG_LEVEL = "INFO"
        config.DEBUG = False

        # 设置日志系统
        setup_logging(config)

        # 获取日志记录器并记录消息
        logger = get_logger("integration_test")
        logger.info("集成测试消息", test_key="test_value")

        # 验证日志目录被创建
        assert config.LOGS_DIR.exists()

    def test_multiple_loggers(self):
        """测试多个日志记录器"""
        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")

        assert logger1.name == "logger1"
        assert logger2.name == "logger2"
        assert logger1 is not logger2
