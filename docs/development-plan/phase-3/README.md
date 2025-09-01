# Phase 3: 基础UI实现开发计划

**阶段**: Phase 3 of 3
**工期**: 2周 (Week 5-6)
**开始日期**: 2025-02-28
**结束日期**: 2025-03-14
**负责人**: 全栈开发者
**前置条件**: Phase 1 & 2 已完成，核心功能可用

---

## 🎯 **阶段目标**

### **主要目标**
实现用户友好的桌面界面，让用户能够通过图形界面创建和管理工作流。

### **具体目标**
- 🎨 实现基础的节点编辑器界面
- 🔧 开发工作流运行和监控界面
- 📋 实现节点属性配置面板
- 💾 实现工作流保存和加载功能
- 🖥️ 完善主窗口和用户体验

---

## 📋 **详细任务分解**

### **Week 5: 核心UI组件开发**

#### **Day 29-30: 节点编辑器基础框架**

**任务 3.1: 节点编辑器画布**
```python
# 目标文件: bluev/ui/node_editor/canvas.py
class NodeCanvas(QGraphicsView):
    """节点编辑器画布"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.nodes = {}
        self.connections = []

    def add_node(self, node_type: str, position: QPointF) -> str
    def remove_node(self, node_id: str)
    def connect_nodes(self, from_node: str, from_output: str,
                     to_node: str, to_input: str)
    def get_workflow_data(self) -> Dict[str, Any]
    def load_workflow_data(self, data: Dict[str, Any])
```

**任务 3.2: 节点图形组件**
```python
# 目标文件: bluev/ui/node_editor/node_widget.py
class NodeWidget(QGraphicsItem):
    """节点图形组件"""

    def __init__(self, node_id: str, node_type: str, position: QPointF):
        super().__init__()
        self.node_id = node_id
        self.node_type = node_type
        self.inputs = []
        self.outputs = []
        self.setPos(position)

    def paint(self, painter: QPainter, option, widget)
    def boundingRect(self) -> QRectF
    def add_input_port(self, name: str, data_type: type)
    def add_output_port(self, name: str, data_type: type)
    def mousePressEvent(self, event)
    def mouseMoveEvent(self, event)
```

**验收标准**:
- [ ] 节点可以在画布上创建和移动
- [ ] 节点显示输入输出端口
- [ ] 画布支持缩放和平移
- [ ] 节点选择和多选功能

#### **Day 31-32: 连接线和交互**

**任务 3.3: 连接线组件**
```python
# 目标文件: bluev/ui/node_editor/connection.py
class ConnectionLine(QGraphicsItem):
    """节点连接线"""

    def __init__(self, from_port: QPointF, to_port: QPointF):
        super().__init__()
        self.from_port = from_port
        self.to_port = to_port
        self.path = QPainterPath()

    def paint(self, painter: QPainter, option, widget)
    def boundingRect(self) -> QRectF
    def update_path(self)
    def set_color(self, color: QColor)
```

**任务 3.4: 拖拽连接功能**
```python
# 目标文件: bluev/ui/node_editor/connection_manager.py
class ConnectionManager:
    """连接管理器"""

    def __init__(self, canvas: NodeCanvas):
        self.canvas = canvas
        self.temp_connection = None
        self.is_connecting = False

    def start_connection(self, from_port: QPointF, port_info: Dict)
    def update_temp_connection(self, to_point: QPointF)
    def finish_connection(self, to_port: QPointF, port_info: Dict)
    def cancel_connection()
    def validate_connection(self, from_info: Dict, to_info: Dict) -> bool
```

**验收标准**:
- [ ] 支持拖拽创建连接线
- [ ] 连接线样式美观
- [ ] 连接验证机制正确
- [ ] 支持连接删除

#### **Day 33-35: 节点库和属性面板**

**任务 3.5: 节点库面板**
```python
# 目标文件: bluev/ui/panels/node_library.py
class NodeLibraryPanel(QWidget):
    """节点库面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_node_categories()

    def setup_ui(self)
    def load_node_categories(self)
    def create_node_item(self, node_type: str, category: str) -> QListWidgetItem
    def on_node_double_clicked(self, item: QListWidgetItem)
    def filter_nodes(self, search_text: str)
```

**任务 3.6: 属性配置面板**
```python
# 目标文件: bluev/ui/panels/property_panel.py
class PropertyPanel(QWidget):
    """节点属性配置面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_node = None
        self.property_widgets = {}
        self.setup_ui()

    def setup_ui(self)
    def set_current_node(self, node_id: str)
    def create_property_widget(self, prop_name: str, prop_type: type,
                              default_value: Any) -> QWidget
    def get_property_values(self) -> Dict[str, Any]
    def update_node_properties(self)
```

**验收标准**:
- [ ] 节点库分类显示清晰
- [ ] 支持节点搜索和过滤
- [ ] 属性面板动态生成
- [ ] 属性修改实时生效

### **Week 6: 工作流管理和完善**

#### **Day 36-37: 工作流运行器**

**任务 3.7: 工作流运行界面**
```python
# 目标文件: bluev/ui/workflow/runner.py
class WorkflowRunner(QWidget):
    """工作流运行器界面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.workflow_engine = None
        self.execution_thread = None
        self.setup_ui()

    def setup_ui(self)
    def load_workflow(self, workflow_data: Dict[str, Any])
    def start_execution(self)
    def pause_execution(self)
    def stop_execution(self)
    def on_node_executed(self, node_id: str, result: Dict[str, Any])
    def on_execution_finished(self, results: Dict[str, Any])
```

**任务 3.8: 执行状态监控**
```python
# 目标文件: bluev/ui/workflow/monitor.py
class ExecutionMonitor(QWidget):
    """执行状态监控器"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.execution_log = []
        self.setup_ui()

    def setup_ui(self)
    def add_log_entry(self, level: str, message: str, node_id: str = None)
    def update_node_status(self, node_id: str, status: str)
    def show_execution_progress(self, progress: float)
    def clear_log(self)
```

**验收标准**:
- [ ] 工作流可以正常启动和停止
- [ ] 执行状态实时显示
- [ ] 日志信息完整准确
- [ ] 进度显示直观

#### **Day 38-39: 文件管理功能**

**任务 3.9: 工作流保存和加载**
```python
# 目标文件: bluev/ui/file/workflow_manager.py
class WorkflowFileManager:
    """工作流文件管理器"""

    def __init__(self):
        self.current_file_path = None
        self.is_modified = False

    def new_workflow(self) -> Dict[str, Any]
    def save_workflow(self, workflow_data: Dict[str, Any],
                     file_path: str = None) -> bool
    def load_workflow(self, file_path: str) -> Optional[Dict[str, Any]]
    def export_workflow(self, workflow_data: Dict[str, Any],
                       format: str = "json") -> bool
    def get_recent_files(self) -> List[str]
```

**任务 3.10: 文件对话框集成**
```python
# 目标文件: bluev/ui/dialogs/file_dialogs.py
class WorkflowFileDialogs:
    """工作流文件对话框"""

    @staticmethod
    def save_workflow_dialog(parent=None) -> Optional[str]
    @staticmethod
    def open_workflow_dialog(parent=None) -> Optional[str]
    @staticmethod
    def export_workflow_dialog(parent=None) -> Optional[str]
    @staticmethod
    def show_unsaved_changes_dialog(parent=None) -> int
```

**验收标准**:
- [ ] 工作流可以保存为 JSON 格式
- [ ] 支持工作流加载和验证
- [ ] 文件对话框用户体验良好
- [ ] 支持最近文件列表

#### **Day 40-42: 主窗口集成和完善**

**任务 3.11: 主窗口布局完善**
```python
# 目标文件: bluev/ui/main_window.py (更新)
class MainWindow(QMainWindow):
    """主窗口 (完整版)"""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.workflow_manager = WorkflowFileManager()
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.connect_signals()

    def create_node_editor_tab(self) -> QWidget
    def create_workflow_runner_tab(self) -> QWidget
    def on_workflow_modified(self)
    def on_execution_started(self)
    def on_execution_finished(self)
```

**任务 3.12: 用户体验优化**
```python
# 目标文件: bluev/ui/utils/ui_helpers.py
class UIHelpers:
    """UI 辅助工具"""

    @staticmethod
    def show_info_message(parent, title: str, message: str)
    @staticmethod
    def show_error_message(parent, title: str, message: str)
    @staticmethod
    def show_progress_dialog(parent, title: str, maximum: int) -> QProgressDialog
    @staticmethod
    def apply_dark_theme(app: QApplication)
    @staticmethod
    def set_window_icon(window: QWidget, icon_path: str)
```

**验收标准**:
- [ ] 主窗口布局合理美观
- [ ] 标签页切换流畅
- [ ] 状态栏信息准确
- [ ] 用户交互体验良好

---

## 📊 **完成定义 (Definition of Done)**

### **功能标准**
- [ ] 用户可以通过界面创建包含 5个节点的工作流
- [ ] 工作流可以保存和加载
- [ ] 执行状态可以实时显示
- [ ] 界面操作流畅 (响应时间 < 100ms)

### **用户体验标准**
- [ ] 新用户可以在 30分钟内创建第一个工作流
- [ ] 界面布局合理，操作直观
- [ ] 错误提示友好易懂
- [ ] 支持键盘快捷键

### **技术标准**
- [ ] 所有 UI 组件正常工作
- [ ] 内存使用稳定 (< 512MB)
- [ ] 界面响应流畅无卡顿
- [ ] 代码质量达标

---

## 🚨 **风险和缓解措施**

### **技术风险**
- **风险**: PySide6 复杂组件开发难度
- **缓解**: 使用成熟的 UI 设计模式，参考优秀开源项目

### **用户体验风险**
- **风险**: 界面复杂度过高，用户学习成本大
- **缓解**: 简化界面设计，提供操作引导

### **性能风险**
- **风险**: 大型工作流界面渲染性能问题
- **缓解**: 虚拟化渲染，延迟加载

---

## 📈 **里程碑检查点**

- **Day 32**: 节点编辑器基础功能完成
- **Day 37**: 工作流运行器完成
- **Day 42**: Phase 3 完整交付，UI 功能完整

---

## 🎉 **项目完成标准**

### **最终验收**
- [ ] 完整的桌面应用程序可以正常运行
- [ ] 用户可以创建、编辑、保存、运行工作流
- [ ] 图像处理功能准确可靠
- [ ] 界面美观易用，用户体验良好
- [ ] 所有自动化测试通过
- [ ] 文档完整，包含用户手册

### **发布准备**
- [ ] 创建安装包和分发版本
- [ ] 编写用户使用指南
- [ ] 准备项目演示材料
- [ ] 收集用户反馈和改进建议

---

**文档状态**: ✅ 已完成
**上一阶段**: [Phase 2: 图像处理集成](../phase-2/README.md)
**项目完成**: 🎉 BlueV MVP 版本交付！
