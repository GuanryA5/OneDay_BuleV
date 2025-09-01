#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BlueV 主应用程序入口

这是 BlueV 应用程序的主入口点，负责初始化应用程序、
配置日志系统、创建主窗口并启动事件循环。
"""

import signal
import sys
import traceback
from pathlib import Path
from typing import Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from bluev.config import Config
from bluev.ui.main_window import MainWindow
from bluev.utils.exceptions import BlueVCriticalError, BlueVException
from bluev.utils.logging import get_logger, setup_logging


class BlueVApplication:
    """BlueV 应用程序主类"""

    def __init__(self) -> None:
        self.app: Optional[QApplication] = None
        self.main_window: Optional[MainWindow] = None
        self.config = Config()
        self.logger = None
        self._shutdown_requested = False

    def setup_application(self) -> QApplication:
        """设置 Qt 应用程序"""
        # 设置应用程序属性 (PySide6 中这些属性可能不需要或已自动启用)
        # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # PySide6 中已默认启用
        # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)     # PySide6 中已默认启用

        # 创建应用程序实例
        app = QApplication(sys.argv)

        # 设置应用程序信息
        app.setApplicationName(self.config.APP_NAME)
        app.setApplicationVersion(self.config.APP_VERSION)
        app.setOrganizationName("BlueV Team")
        app.setOrganizationDomain("bluev.dev")

        # 设置应用程序图标
        icon_path = self.config.RESOURCES_DIR / "icons" / "app_icon.png"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))

        return app

    def setup_directories(self) -> None:
        """创建必要的目录"""
        directories = [
            self.config.DATA_DIR,
            self.config.TEMP_DIR,
            self.config.LOGS_DIR,
            self.config.WORKFLOWS_DIR,
            self.config.SCREENSHOTS_DIR,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def setup_signal_handlers(self) -> None:
        """设置信号处理器"""

        def signal_handler(signum: int, frame: Optional[object]) -> None:
            if self.logger:
                self.logger.info(f"接收到信号 {signum}，准备关闭应用程序")
            self._shutdown_requested = True
            if self.app:
                self.app.quit()

        # 设置信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def setup_exception_handler(self) -> None:
        """设置全局异常处理器"""

        def handle_exception(
            exc_type: type, exc_value: Exception, exc_traceback: Optional[object]
        ) -> None:
            if issubclass(exc_type, KeyboardInterrupt):
                # 允许 KeyboardInterrupt 正常处理
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            # 记录异常
            if self.logger:
                self.logger.error(
                    "未处理的异常", exc_info=(exc_type, exc_value, exc_traceback)
                )

            # 显示错误对话框
            if self.app and not self._shutdown_requested:
                error_msg = f"发生未处理的错误:\n{exc_type.__name__}: {exc_value}"
                QMessageBox.critical(None, "BlueV 错误", error_msg)

        sys.excepthook = handle_exception

    def run(self) -> int:
        """运行应用程序"""
        try:
            # 设置日志系统
            setup_logging(self.config)
            self.logger = get_logger(__name__)
            self.logger.info("BlueV 应用程序启动")

            # 设置异常处理和信号处理
            self.setup_exception_handler()
            self.setup_signal_handlers()

            # 创建必要目录
            self.setup_directories()

            # 设置 Qt 应用程序
            self.app = self.setup_application()

            # 创建主窗口
            self.main_window = MainWindow(self.config)
            self.main_window.show()

            self.logger.info("BlueV 应用程序启动完成")

            # 启动事件循环
            return self.app.exec()

        except BlueVCriticalError as e:
            error_msg = f"严重错误: {e}"
            print(f"❌ {error_msg}")
            if self.logger:
                self.logger.critical(error_msg)
            return 2
        except BlueVException as e:
            error_msg = f"应用程序错误: {e}"
            print(f"❌ {error_msg}")
            if self.logger:
                self.logger.error(error_msg)
            return 1
        except Exception as e:
            error_msg = f"未知错误: {e}"
            print(f"❌ {error_msg}")
            if self.logger:
                self.logger.error(error_msg, exc_info=True)
            else:
                traceback.print_exc()
            return 1

    def cleanup(self) -> None:
        """清理资源"""
        if getattr(self, "logger", "Unknown"):
            getattr(self, "logger", "Unknown").info("开始清理应用程序资源")

        try:
            if getattr(self, "main_window", "Unknown"):
                getattr(self, "main_window", "Unknown").close()
                self.main_window = None

            if getattr(self, "app", "Unknown"):
                getattr(self, "app", "Unknown").quit()
                self.app = None

            if getattr(self, "logger", "Unknown"):
                getattr(self, "logger", "Unknown").info("应用程序资源清理完成")
        except Exception as e:
            print(f"清理资源时发生错误: {e}")
            if getattr(self, "logger", "Unknown"):
                getattr(self, "logger", "Unknown").error(f"清理资源时发生错误: {e}")


def main() -> int:
    """主函数"""
    app = BlueVApplication()

    try:
        return app.run()
    except KeyboardInterrupt:
        print("\n🛑 用户中断，正在退出...")
        return 0
    except Exception as e:
        print(f"❌ 未处理的异常: {e}")
        return 1
    finally:
        app.cleanup()


if __name__ == "__main__":
    sys.exit(main())
