# Phase 1: 核心节点系统开发计划

**阶段**: Phase 1 of 3
**工期**: 2周 (Week 1-2)
**开始日期**: 2025-01-31
**结束日期**: 2025-02-14
**负责人**: 全栈开发者

---

## 🎯 **阶段目标**

### **主要目标**
实现 BlueV 的核心节点系统架构，为后续功能开发奠定坚实基础。

### **具体目标**
- 🏗️ 建立完整的节点抽象架构
- 🔧 实现节点注册和管理系统
- ⚡ 开发简单的工作流执行引擎
- 📦 实现 5个核心节点类型
- 🧪 建立完整的测试框架

---

## 📋 **详细任务分解**

### **Week 1: 基础架构搭建**

#### **Day 1-2: 节点系统核心架构**

**任务 1.1: BaseNode 抽象类设计**
```python
# 目标文件: bluev/core/base_node.py
class BaseNode(ABC):
    """节点基类，定义所有节点的通用接口"""

    # 核心属性
    - node_id: str
    - node_type: str
    - state: NodeState
    - inputs: Dict[str, Any]
    - outputs: Dict[str, Any]

    # 抽象方法
    - execute() -> Dict[str, Any]
    - validate_inputs() -> bool
    - get_input_spec() -> List[NodeInput]
    - get_output_spec() -> List[NodeOutput]
```

**验收标准**:
- [ ] BaseNode 类可以正常继承
- [ ] 节点状态管理正确
- [ ] 输入输出验证机制完善
- [ ] 完整的类型注解

**任务 1.2: 节点状态和数据结构**
```python
# 目标文件: bluev/core/node_types.py
from enum import Enum
from dataclasses import dataclass

class NodeState(Enum):
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class NodeInput:
    name: str
    data_type: type
    default_value: Any = None
    required: bool = True
    description: str = ""

@dataclass
class NodeOutput:
    name: str
    data_type: type
    description: str = ""
```

**验收标准**:
- [ ] 状态枚举定义完整
- [ ] 数据结构类型安全
- [ ] 支持序列化和反序列化

#### **Day 3-4: 节点注册系统**

**任务 1.3: NodeRegistry 实现**
```python
# 目标文件: bluev/core/node_registry.py
class NodeRegistry:
    """节点注册器，管理所有可用节点类型"""

    def register_node(self, node_type: str, node_class: Type[BaseNode], category: str)
    def get_node_class(self, node_type: str) -> Type[BaseNode]
    def list_nodes(self, category: str = None) -> List[str]
    def create_node(self, node_type: str, node_id: str) -> BaseNode
```

**验收标准**:
- [ ] 支持动态节点注册
- [ ] 节点分类管理
- [ ] 线程安全的注册器
- [ ] 完整的错误处理

**任务 1.4: 节点装饰器**
```python
# 目标文件: bluev/core/decorators.py
def bluev_node(node_type: str, category: str = "custom"):
    """节点装饰器，简化节点注册"""
    def decorator(cls):
        # 自动注册节点
        node_registry.register_node(node_type, cls, category)
        return cls
    return decorator
```

**验收标准**:
- [ ] 装饰器语法简洁易用
- [ ] 自动注册功能正常
- [ ] 支持节点分类

#### **Day 5-7: 工作流执行引擎**

**任务 1.5: WorkflowEngine 核心实现**
```python
# 目标文件: bluev/core/workflow_engine.py
class WorkflowEngine:
    """简化的工作流执行引擎"""

    def __init__(self):
        self.nodes: Dict[str, BaseNode] = {}
        self.connections: List[Connection] = []
        self.thread_pool = ThreadPoolExecutor(max_workers=4)

    def add_node(self, node: BaseNode)
    def connect_nodes(self, from_node: str, from_output: str,
                     to_node: str, to_input: str)
    def execute_workflow(self) -> Dict[str, Any]
    def topological_sort(self) -> List[str]
```

**验收标准**:
- [ ] 支持节点添加和连接
- [ ] 拓扑排序算法正确
- [ ] 线程池执行机制
- [ ] 错误处理和状态追踪

### **Week 2: 核心节点实现**

#### **Day 8-10: 基础节点实现**

**任务 2.1: ScreenshotNode - 屏幕截图节点**
```python
# 目标文件: bluev/nodes/image/screenshot_node.py
@bluev_node("screenshot", "image_processing")
class ScreenshotNode(BaseNode):
    """屏幕截图节点"""

    输入参数:
    - region: Optional[Tuple[int, int, int, int]] = None  # 截图区域
    - save_path: Optional[str] = None  # 保存路径

    输出结果:
    - image: np.ndarray  # 截图数据
    - image_path: str    # 图片路径
```

**任务 2.2: DelayNode - 延迟等待节点**
```python
# 目标文件: bluev/nodes/control/delay_node.py
@bluev_node("delay", "control_flow")
class DelayNode(BaseNode):
    """延迟等待节点"""

    输入参数:
    - duration: float  # 延迟时间(秒)
    - random_range: Optional[float] = None  # 随机范围

    输出结果:
    - actual_delay: float  # 实际延迟时间
```

**任务 2.3: LogNode - 日志输出节点**
```python
# 目标文件: bluev/nodes/utility/log_node.py
@bluev_node("log", "utility")
class LogNode(BaseNode):
    """日志输出节点"""

    输入参数:
    - message: str     # 日志消息
    - level: str = "info"  # 日志级别

    输出结果:
    - logged: bool     # 是否成功记录
```

**验收标准**:
- [ ] 所有节点正常执行
- [ ] 输入输出规范正确
- [ ] 错误处理完善
- [ ] 单元测试覆盖

#### **Day 11-12: 图像处理基础节点**

**任务 2.4: FindImageNode - 图像查找节点 (基础版)**
```python
# 目标文件: bluev/nodes/image/find_image_node.py
@bluev_node("find_image", "image_processing")
class FindImageNode(BaseNode):
    """图像查找节点 (基础实现)"""

    输入参数:
    - template_image: np.ndarray  # 模板图像
    - source_image: np.ndarray    # 源图像
    - threshold: float = 0.8      # 匹配阈值

    输出结果:
    - found: bool                 # 是否找到
    - location: Optional[Tuple[int, int]]  # 位置坐标
    - confidence: float           # 匹配置信度
```

**任务 2.5: ClickNode - 鼠标点击节点**
```python
# 目标文件: bluev/nodes/interaction/click_node.py
@bluev_node("click", "user_interaction")
class ClickNode(BaseNode):
    """鼠标点击节点"""

    输入参数:
    - location: Tuple[int, int]   # 点击位置
    - button: str = "left"        # 鼠标按键
    - clicks: int = 1             # 点击次数
    - interval: float = 0.1       # 点击间隔

    输出结果:
    - success: bool               # 是否成功
    - actual_clicks: int          # 实际点击次数
```

**验收标准**:
- [ ] 基础图像匹配功能正常
- [ ] 鼠标操作准确可靠
- [ ] 参数验证完善
- [ ] 异常处理健壮

#### **Day 13-14: 测试和集成**

**任务 2.6: 单元测试实现**
```python
# 目标文件: tests/unit/test_nodes.py
class TestBaseNode:
    def test_node_creation()
    def test_state_management()
    def test_input_validation()
    def test_output_generation()

class TestWorkflowEngine:
    def test_node_addition()
    def test_node_connection()
    def test_workflow_execution()
    def test_error_handling()
```

**任务 2.7: 集成测试**
```python
# 目标文件: tests/integration/test_workflow.py
def test_simple_workflow():
    """测试简单工作流: 截图 -> 延迟 -> 日志"""

def test_image_workflow():
    """测试图像工作流: 截图 -> 找图 -> 点击"""
```

**验收标准**:
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试通过
- [ ] 所有 CI 检查通过
- [ ] 代码质量达标

---

## 📊 **完成定义 (Definition of Done)**

### **技术标准**
- [ ] 所有代码通过 Ruff 检查
- [ ] 类型注解覆盖率 100%
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 所有 CI/CD 检查通过

### **功能标准**
- [ ] 5个核心节点正常工作
- [ ] 工作流可以通过代码创建和执行
- [ ] 节点注册系统功能完整
- [ ] 错误处理机制健壮

### **质量标准**
- [ ] 代码结构清晰，易于理解
- [ ] 文档完整，包含使用示例
- [ ] 性能满足要求 (执行时间 < 2秒)
- [ ] 内存使用稳定 (< 128MB)

---

## 🚨 **风险和缓解措施**

### **技术风险**
- **风险**: OpenCV 集成复杂度
- **缓解**: 先实现基础功能，复杂算法放到 Phase 2

### **进度风险**
- **风险**: 节点系统设计过于复杂
- **缓解**: 采用简化设计，专注核心功能

### **质量风险**
- **风险**: 测试时间不足
- **缓解**: 并行开发和测试，持续集成

---

## 📈 **里程碑检查点**

- **Day 7**: 核心架构完成，可以创建和注册节点
- **Day 10**: 基础节点实现完成
- **Day 14**: Phase 1 完整交付，准备进入 Phase 2

---

**文档状态**: ✅ 已完成
**下一阶段**: [Phase 2: 图像处理集成](../phase-2/README.md)
