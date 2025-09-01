# -*- coding: utf-8 -*-
"""
BlueV 主窗口

应用程序的主窗口，包含菜单栏、工具栏、状态栏和主要的工作区域。
负责整个应用程序的布局和基本交互。
"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from bluev.config import Config
from bluev.utils.logging import get_logger


class MainWindow(QMainWindow):
    """BlueV 主窗口类"""

    def __init__(self, config: Config, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config = config
        self.logger = get_logger(__name__)

        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()

        self.logger.info("主窗口初始化完成")

    def setup_ui(self) -> None:
        """设置用户界面"""
        # 设置窗口属性
        self.setWindowTitle(f"{self.config.APP_NAME} v{self.config.APP_VERSION}")
        self.setMinimumSize(self.config.WINDOW_MIN_WIDTH, self.config.WINDOW_MIN_HEIGHT)
        self.resize(self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # 左侧面板（节点库和属性面板）
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # 中央工作区（节点编辑器）
        center_panel = self.create_center_panel()
        splitter.addWidget(center_panel)

        # 右侧面板（日志和输出）
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # 设置分割器比例
        splitter.setSizes([250, 700, 250])

    def create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 临时标签，后续替换为实际组件
        label = QLabel("节点库\n(待实现)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("border: 1px solid gray; padding: 20px;")
        layout.addWidget(label)

        return panel

    def create_center_panel(self) -> QWidget:
        """创建中央面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 临时标签，后续替换为节点编辑器
        label = QLabel("节点编辑器\n(待实现)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("border: 1px solid gray; padding: 50px;")
        layout.addWidget(label)

        return panel

    def create_right_panel(self) -> QWidget:
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 临时标签，后续替换为实际组件
        label = QLabel("属性面板\n和\n日志输出\n(待实现)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("border: 1px solid gray; padding: 20px;")
        layout.addWidget(label)

        return panel

    def setup_menu(self) -> None:
        """设置菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        new_action = QAction("新建工作流(&N)", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_workflow)
        file_menu.addAction(new_action)

        open_action = QAction("打开工作流(&O)", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_workflow)
        file_menu.addAction(open_action)

        save_action = QAction("保存工作流(&S)", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_workflow)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")

        undo_action = QAction("撤销(&U)", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("重做(&R)", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)

        # 运行菜单
        run_menu = menubar.addMenu("运行(&R)")

        start_action = QAction("开始执行(&S)", self)
        start_action.setShortcut("F5")
        start_action.triggered.connect(self.start_workflow)
        run_menu.addAction(start_action)

        stop_action = QAction("停止执行(&T)", self)
        stop_action.setShortcut("Shift+F5")
        stop_action.triggered.connect(self.stop_workflow)
        run_menu.addAction(stop_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于 BlueV(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_toolbar(self) -> None:
        """设置工具栏"""
        toolbar = self.addToolBar("主工具栏")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # 新建按钮
        new_action = QAction("新建", self)
        new_action.triggered.connect(self.new_workflow)
        toolbar.addAction(new_action)

        # 打开按钮
        open_action = QAction("打开", self)
        open_action.triggered.connect(self.open_workflow)
        toolbar.addAction(open_action)

        # 保存按钮
        save_action = QAction("保存", self)
        save_action.triggered.connect(self.save_workflow)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # 运行按钮
        start_action = QAction("运行", self)
        start_action.triggered.connect(self.start_workflow)
        toolbar.addAction(start_action)

        # 停止按钮
        stop_action = QAction("停止", self)
        stop_action.triggered.connect(self.stop_workflow)
        toolbar.addAction(stop_action)

    def setup_statusbar(self) -> None:
        """设置状态栏"""
        statusbar = self.statusBar()

        # 状态标签
        self.status_label = QLabel("就绪")
        statusbar.addWidget(self.status_label)

        # 版本信息
        version_label = QLabel(f"v{self.config.APP_VERSION}")
        statusbar.addPermanentWidget(version_label)

    # 菜单和工具栏事件处理方法
    def new_workflow(self) -> None:
        """新建工作流"""
        self.logger.info("新建工作流")
        self.status_label.setText("新建工作流")

    def open_workflow(self) -> None:
        """打开工作流"""
        self.logger.info("打开工作流")
        self.status_label.setText("打开工作流")

    def save_workflow(self) -> None:
        """保存工作流"""
        self.logger.info("保存工作流")
        self.status_label.setText("保存工作流")

    def undo(self) -> None:
        """撤销操作"""
        self.logger.info("撤销操作")
        self.status_label.setText("撤销操作")

    def redo(self) -> None:
        """重做操作"""
        self.logger.info("重做操作")
        self.status_label.setText("重做操作")

    def start_workflow(self) -> None:
        """开始执行工作流"""
        self.logger.info("开始执行工作流")
        self.status_label.setText("正在执行工作流...")

    def stop_workflow(self) -> None:
        """停止执行工作流"""
        self.logger.info("停止执行工作流")
        self.status_label.setText("工作流已停止")

    def show_about(self) -> None:
        """显示关于对话框"""
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.about(
            self,
            "关于 BlueV",
            f"""
            <h3>BlueV v{self.config.APP_VERSION}</h3>
            <p>游戏自动化蓝图框架</p>
            <p>一个基于 PySide6 的可视化游戏自动化工具</p>
            <p>Copyright © 2025 BlueV Team</p>
            """,
        )

    def closeEvent(self, event: QCloseEvent) -> None:
        """窗口关闭事件"""
        self.logger.info("主窗口关闭")
        event.accept()
