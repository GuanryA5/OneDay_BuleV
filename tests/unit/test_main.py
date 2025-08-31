# -*- coding: utf-8 -*-
"""
主程序模块单元测试
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

from bluev.config import Config
from bluev.main import BlueVApplication, main
from bluev.utils.exceptions import BlueVCriticalError, BlueVException


class TestBlueVApplication:
    """BlueV应用程序类测试"""

    def test_application_init(self):
        """测试应用程序初始化"""
        app = BlueVApplication()

        assert app.app is None
        assert app.main_window is None
        assert isinstance(app.config, Config)
        assert app.logger is None
        assert app._shutdown_requested is False

    def test_setup_directories(self):
        """测试目录创建"""
        app = BlueVApplication()
        app.logger = Mock()

        # 模拟配置
        app.config.DATA_DIR = Path("test_data")
        app.config.TEMP_DIR = Path("test_temp")
        app.config.LOGS_DIR = Path("test_logs")
        app.config.WORKFLOWS_DIR = Path("test_workflows")
        app.config.SCREENSHOTS_DIR = Path("test_screenshots")

        with patch("pathlib.Path.mkdir") as mock_mkdir:
            app.setup_directories()
            # 验证所有目录都被创建
            assert mock_mkdir.call_count == 5

    @patch("PySide6.QtWidgets.QApplication")
    def test_setup_application(self, mock_qapp_class):
        """测试Qt应用程序设置"""
        mock_qapp = Mock()
        mock_qapp_class.return_value = mock_qapp

        app = BlueVApplication()
        result = app.setup_application()

        assert result == mock_qapp
        mock_qapp.setApplicationName.assert_called_with(app.config.APP_NAME)
        mock_qapp.setApplicationVersion.assert_called_with(app.config.APP_VERSION)

    def test_setup_signal_handlers(self):
        """测试信号处理器设置"""
        app = BlueVApplication()
        app.logger = Mock()

        with patch("signal.signal") as mock_signal:
            app.setup_signal_handlers()
            # 验证信号处理器被设置
            assert mock_signal.call_count == 2

    def test_setup_exception_handler(self):
        """测试异常处理器设置"""
        app = BlueVApplication()
        app.logger = Mock()

        original_excepthook = sys.excepthook
        app.setup_exception_handler()

        # 验证异常处理器被替换
        assert sys.excepthook != original_excepthook

        # 恢复原始异常处理器
        sys.excepthook = original_excepthook

    @patch("bluev.main.QApplication")
    @patch("bluev.main.MainWindow")
    @patch("bluev.main.setup_logging")
    @patch("bluev.main.get_logger")
    def test_run_success(
        self,
        mock_get_logger,
        mock_setup_logging,
        mock_main_window_class,
        mock_qapp_class,
    ):
        """测试应用程序成功运行"""
        # 设置模拟对象
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_qapp = Mock()
        mock_qapp.exec.return_value = 0
        mock_qapp_class.return_value = mock_qapp

        mock_main_window = Mock()
        mock_main_window_class.return_value = mock_main_window

        app = BlueVApplication()

        with patch.object(app, "setup_directories") as mock_setup_dirs:
            result = app.run()

            assert result == 0
            mock_setup_logging.assert_called_once()
            mock_setup_dirs.assert_called_once()
            mock_main_window.show.assert_called_once()
            mock_qapp.exec.assert_called_once()

    @patch("bluev.main.setup_logging")
    @patch("bluev.main.get_logger")
    def test_run_bluev_critical_error(self, mock_get_logger, mock_setup_logging):
        """测试应用程序运行时的严重错误"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_setup_logging.side_effect = BlueVCriticalError("严重错误")

        app = BlueVApplication()
        result = app.run()

        assert result == 2
        mock_logger.critical.assert_called()

    @patch("bluev.main.setup_logging")
    @patch("bluev.main.get_logger")
    def test_run_bluev_exception(self, mock_get_logger, mock_setup_logging):
        """测试应用程序运行时的一般错误"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_setup_logging.side_effect = BlueVException("一般错误")

        app = BlueVApplication()
        result = app.run()

        assert result == 1
        mock_logger.error.assert_called()

    @patch("bluev.main.setup_logging")
    def test_run_unknown_exception(self, mock_setup_logging):
        """测试应用程序运行时的未知错误"""
        mock_setup_logging.side_effect = RuntimeError("未知错误")

        app = BlueVApplication()
        result = app.run()

        assert result == 1

    def test_cleanup(self):
        """测试资源清理"""
        app = BlueVApplication()
        app.logger = Mock()
        app.main_window = Mock()
        app.app = Mock()

        app.cleanup()

        app.main_window.close.assert_called_once()
        app.app.quit.assert_called_once()
        assert app.main_window is None
        assert app.app is None

    def test_cleanup_with_exception(self):
        """测试清理时发生异常"""
        app = BlueVApplication()
        app.logger = Mock()
        app.main_window = Mock()
        app.main_window.close.side_effect = Exception("清理错误")

        # 不应该抛出异常
        app.cleanup()
        app.logger.error.assert_called()


class TestMainFunction:
    """主函数测试"""

    @patch("bluev.main.BlueVApplication")
    def test_main_success(self, mock_app_class):
        """测试主函数成功执行"""
        mock_app = Mock()
        mock_app.run.return_value = 0
        mock_app_class.return_value = mock_app

        result = main()

        assert result == 0
        mock_app.run.assert_called_once()
        mock_app.cleanup.assert_called_once()

    @patch("bluev.main.BlueVApplication")
    def test_main_keyboard_interrupt(self, mock_app_class):
        """测试主函数键盘中断"""
        mock_app = Mock()
        mock_app.run.side_effect = KeyboardInterrupt()
        mock_app_class.return_value = mock_app

        result = main()

        assert result == 0
        mock_app.cleanup.assert_called_once()

    @patch("bluev.main.BlueVApplication")
    def test_main_exception(self, mock_app_class):
        """测试主函数异常处理"""
        mock_app = Mock()
        mock_app.run.side_effect = Exception("测试异常")
        mock_app_class.return_value = mock_app

        result = main()

        assert result == 1
        mock_app.cleanup.assert_called_once()

    @patch("bluev.main.BlueVApplication")
    def test_main_cleanup_exception(self, mock_app_class):
        """测试主函数清理时异常"""
        mock_app = Mock()
        mock_app.run.return_value = 0
        mock_app.cleanup.side_effect = Exception("清理异常")
        mock_app_class.return_value = mock_app

        # 不应该影响返回值
        result = main()
        assert result == 0
