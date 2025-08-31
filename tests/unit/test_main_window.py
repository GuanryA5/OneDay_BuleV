# -*- coding: utf-8 -*-
"""
主窗口模块单元测试
"""

from unittest.mock import Mock, patch

from bluev.ui.main_window import MainWindow


class TestMainWindow:
    """主窗口类测试"""

    def test_main_window_init(self, mock_qt_app, config):
        """测试主窗口初始化"""
        with patch("bluev.ui.main_window.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            window = MainWindow(config)

            assert window.config == config
            assert window.logger == mock_logger
            mock_logger.info.assert_called_with("主窗口初始化完成")

    def test_main_window_window_properties(self, mock_qt_app, config):
        """测试主窗口属性设置"""
        with patch("bluev.ui.main_window.get_logger"):
            window = MainWindow(config)

            # 验证窗口标题
            expected_title = f"{config.APP_NAME} v{config.APP_VERSION}"
            assert window.windowTitle() == expected_title

            # 验证窗口尺寸
            assert window.minimumWidth() == config.WINDOW_MIN_WIDTH
            assert window.minimumHeight() == config.WINDOW_MIN_HEIGHT
            assert window.width() == config.WINDOW_WIDTH
            assert window.height() == config.WINDOW_HEIGHT

    def test_main_window_central_widget(self, mock_qt_app, config):
        """测试中央部件创建"""
        with patch("bluev.ui.main_window.get_logger"):
            window = MainWindow(config)

            central_widget = window.centralWidget()
            assert central_widget is not None

    def test_main_window_menu_creation(self, mock_qt_app, config):
        """测试菜单创建"""
        with patch("bluev.ui.main_window.get_logger"):
            window = MainWindow(config)

            menubar = window.menuBar()
            assert menubar is not None

            # 检查菜单项
            menus = menubar.findChildren(type(menubar.addMenu("test")))
            menu_texts = [menu.title() for menu in menus if menu.title()]

            expected_menus = ["文件(&F)", "编辑(&E)", "运行(&R)", "帮助(&H)"]
            for expected_menu in expected_menus:
                assert expected_menu in menu_texts

    def test_main_window_toolbar_creation(self, mock_qt_app, config):
        """测试工具栏创建"""
        with patch("bluev.ui.main_window.get_logger"):
            window = MainWindow(config)

            toolbars = window.findChildren(window.addToolBar("test").__class__)
            assert len(toolbars) >= 1

    def test_main_window_statusbar_creation(self, mock_qt_app, config):
        """测试状态栏创建"""
        with patch("bluev.ui.main_window.get_logger"):
            window = MainWindow(config)

            statusbar = window.statusBar()
            assert statusbar is not None
            assert window.status_label is not None

    def test_main_window_menu_actions(self, mock_qt_app, config):
        """测试菜单动作"""
        with patch("bluev.ui.main_window.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            window = MainWindow(config)

            # 测试新建工作流
            window.new_workflow()
            mock_logger.info.assert_called_with("新建工作流")
            assert "新建工作流" in window.status_label.text()

            # 测试打开工作流
            window.open_workflow()
            mock_logger.info.assert_called_with("打开工作流")
            assert "打开工作流" in window.status_label.text()

            # 测试保存工作流
            window.save_workflow()
            mock_logger.info.assert_called_with("保存工作流")
            assert "保存工作流" in window.status_label.text()

    def test_main_window_edit_actions(self, mock_qt_app, config):
        """测试编辑动作"""
        with patch("bluev.ui.main_window.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            window = MainWindow(config)

            # 测试撤销
            window.undo()
            mock_logger.info.assert_called_with("撤销操作")
            assert "撤销操作" in window.status_label.text()

            # 测试重做
            window.redo()
            mock_logger.info.assert_called_with("重做操作")
            assert "重做操作" in window.status_label.text()

    def test_main_window_run_actions(self, mock_qt_app, config):
        """测试运行动作"""
        with patch("bluev.ui.main_window.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            window = MainWindow(config)

            # 测试开始执行
            window.start_workflow()
            mock_logger.info.assert_called_with("开始执行工作流")
            assert "正在执行工作流" in window.status_label.text()

            # 测试停止执行
            window.stop_workflow()
            mock_logger.info.assert_called_with("停止执行工作流")
            assert "工作流已停止" in window.status_label.text()

    @patch("bluev.ui.main_window.QMessageBox")
    def test_main_window_about_dialog(self, mock_message_box, mock_qt_app, config):
        """测试关于对话框"""
        with patch("bluev.ui.main_window.get_logger"):
            window = MainWindow(config)

            window.show_about()

            mock_message_box.about.assert_called_once()
            call_args = mock_message_box.about.call_args

            # 验证对话框内容包含版本信息
            dialog_content = call_args[0][2]
            assert config.APP_VERSION in dialog_content
            assert "BlueV" in dialog_content

    def test_main_window_close_event(self, mock_qt_app, config):
        """测试窗口关闭事件"""
        with patch("bluev.ui.main_window.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            window = MainWindow(config)

            # 模拟关闭事件
            mock_event = Mock()
            window.closeEvent(mock_event)

            mock_logger.info.assert_called_with("主窗口关闭")
            mock_event.accept.assert_called_once()

    def test_main_window_panels_creation(self, mock_qt_app, config):
        """测试面板创建"""
        with patch("bluev.ui.main_window.get_logger"):
            window = MainWindow(config)

            # 验证面板创建方法存在且可调用
            left_panel = window.create_left_panel()
            center_panel = window.create_center_panel()
            right_panel = window.create_right_panel()

            assert left_panel is not None
            assert center_panel is not None
            assert right_panel is not None

    def test_main_window_layout_structure(self, mock_qt_app, config):
        """测试布局结构"""
        with patch("bluev.ui.main_window.get_logger"):
            window = MainWindow(config)

            central_widget = window.centralWidget()
            assert central_widget is not None

            # 验证布局存在
            layout = central_widget.layout()
            assert layout is not None
