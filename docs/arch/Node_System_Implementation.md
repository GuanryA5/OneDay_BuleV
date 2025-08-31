# BlueV节点系统实现方案

**文档版本**: v1.0
**创建日期**: 2025-01-27
**关联文档**: BlueV_Architecture_Design.md

---

## 🎯 **节点系统设计目标**

### **核心特性**
- 🔧 **类型安全**: 完整的类型注解和运行时验证
- 🔌 **插件化**: 支持动态节点扩展和热插拔
- 📊 **状态管理**: 完善的执行状态追踪和错误处理
- 🚀 **高性能**: 异步执行和并行处理支持
- 🔄 **可序列化**: 支持工作流的保存和恢复

---

## 🏗️ **图像处理节点实现**

### **FindImageNode - 图像查找节点**
```python
import cv2
import numpy as np
from typing import Tuple, Optional

class FindImageNode(BaseNode):
    """在屏幕上查找图片节点"""

    @classmethod
    def get_input_spec(cls) -> List[NodeInput]:
        return [
            NodeInput("screenshot", np.ndarray, description="屏幕截图"),
            NodeInput("template", np.ndarray, description="模板图像"),
            NodeInput("threshold", float, 0.8, description="相似度阈值"),
            NodeInput("method", str, "TM_CCOEFF_NORMED", description="匹配方法")
        ]

    @classmethod
    def get_output_spec(cls) -> List[NodeOutput]:
        return [
            NodeOutput("found", bool, "是否找到"),
            NodeOutput("location", Tuple[int, int], "找到的坐标"),
            NodeOutput("confidence", float, "匹配置信度")
        ]

    async def execute(self, context: 'ExecutionContext') -> Dict[str, Any]:
        """执行图像查找"""
        try:
            self.state = NodeState.RUNNING

            screenshot = self.inputs["screenshot"]
            template = self.inputs["template"]
            threshold = self.inputs["threshold"]
            method = getattr(cv2, self.inputs["method"])

            # 执行模板匹配
            result = cv2.matchTemplate(screenshot, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # 根据匹配方法确定最佳匹配位置
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                best_match = min_loc
                confidence = 1 - min_val
            else:
                best_match = max_loc
                confidence = max_val

            found = confidence >= threshold

            self.state = NodeState.COMPLETED
            return {
                "found": found,
                "location": best_match if found else None,
                "confidence": confidence
            }

        except Exception as e:
            self.state = NodeState.FAILED
            self.error_message = str(e)
            raise
```

### **ClickNode - 点击操作节点**
```python
import pyautogui
import asyncio

class ClickNode(BaseNode):
    """点击节点"""

    @classmethod
    def get_input_spec(cls) -> List[NodeInput]:
        return [
            NodeInput("location", Tuple[int, int], description="点击坐标"),
            NodeInput("button", str, "left", description="鼠标按钮"),
            NodeInput("clicks", int, 1, description="点击次数"),
            NodeInput("interval", float, 0.1, description="点击间隔")
        ]

    @classmethod
    def get_output_spec(cls) -> List[NodeOutput]:
        return [
            NodeOutput("success", bool, "执行是否成功")
        ]

    async def execute(self, context: 'ExecutionContext') -> Dict[str, Any]:
        """执行点击操作"""
        try:
            self.state = NodeState.RUNNING

            location = self.inputs["location"]
            button = self.inputs["button"]
            clicks = self.inputs["clicks"]
            interval = self.inputs["interval"]

            # 执行点击操作
            for i in range(clicks):
                pyautogui.click(location[0], location[1], button=button)
                if i < clicks - 1:  # 最后一次点击不需要等待
                    await asyncio.sleep(interval)

            self.state = NodeState.COMPLETED
            return {"success": True}

        except Exception as e:
            self.state = NodeState.FAILED
            self.error_message = str(e)
            raise
```

### **ScreenshotNode - 屏幕截图节点**
```python
import pyautogui
import numpy as np
from PIL import Image

class ScreenshotNode(BaseNode):
    """屏幕截图节点"""

    @classmethod
    def get_input_spec(cls) -> List[NodeInput]:
        return [
            NodeInput("region", Tuple[int, int, int, int], None, False, "截图区域(x,y,width,height)"),
            NodeInput("grayscale", bool, False, False, "是否转为灰度图")
        ]

    @classmethod
    def get_output_spec(cls) -> List[NodeOutput]:
        return [
            NodeOutput("screenshot", np.ndarray, "截图数据"),
            NodeOutput("timestamp", float, "截图时间戳")
        ]

    async def execute(self, context: 'ExecutionContext') -> Dict[str, Any]:
        """执行屏幕截图"""
        try:
            self.state = NodeState.RUNNING

            region = self.inputs.get("region")
            grayscale = self.inputs.get("grayscale", False)

            # 截图
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()

            # 转换为numpy数组
            screenshot_array = np.array(screenshot)

            # 转换为灰度图
            if grayscale:
                screenshot_array = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2GRAY)

            import time
            timestamp = time.time()

            self.state = NodeState.COMPLETED
            return {
                "screenshot": screenshot_array,
                "timestamp": timestamp
            }

        except Exception as e:
            self.state = NodeState.FAILED
            self.error_message = str(e)
            raise
```

---

## 🔄 **控制流节点实现**

### **DelayNode - 延迟节点**
```python
class DelayNode(BaseNode):
    """延迟节点"""

    @classmethod
    def get_input_spec(cls) -> List[NodeInput]:
        return [
            NodeInput("duration", float, 1.0, description="延迟时间(秒)"),
            NodeInput("pass_through", Any, None, False, "透传数据")
        ]

    @classmethod
    def get_output_spec(cls) -> List[NodeOutput]:
        return [
            NodeOutput("result", Any, "延迟后的结果"),
            NodeOutput("actual_duration", float, "实际延迟时间")
        ]

    async def execute(self, context: 'ExecutionContext') -> Dict[str, Any]:
        """执行延迟"""
        try:
            self.state = NodeState.RUNNING

            duration = self.inputs["duration"]
            pass_through = self.inputs.get("pass_through")

            import time
            start_time = time.time()
            await asyncio.sleep(duration)
            actual_duration = time.time() - start_time

            self.state = NodeState.COMPLETED
            return {
                "result": pass_through,
                "actual_duration": actual_duration
            }

        except Exception as e:
            self.state = NodeState.FAILED
            self.error_message = str(e)
            raise
```

### **ConditionalNode - 条件判断节点**
```python
class ConditionalNode(BaseNode):
    """条件判断节点"""

    @classmethod
    def get_input_spec(cls) -> List[NodeInput]:
        return [
            NodeInput("condition", bool, description="判断条件"),
            NodeInput("true_value", Any, None, False, "条件为真时的值"),
            NodeInput("false_value", Any, None, False, "条件为假时的值")
        ]

    @classmethod
    def get_output_spec(cls) -> List[NodeOutput]:
        return [
            NodeOutput("result", Any, "条件判断结果"),
            NodeOutput("condition_met", bool, "条件是否满足")
        ]

    async def execute(self, context: 'ExecutionContext') -> Dict[str, Any]:
        """执行条件判断"""
        try:
            self.state = NodeState.RUNNING

            condition = self.inputs["condition"]
            true_value = self.inputs.get("true_value")
            false_value = self.inputs.get("false_value")

            result = true_value if condition else false_value

            self.state = NodeState.COMPLETED
            return {
                "result": result,
                "condition_met": condition
            }

        except Exception as e:
            self.state = NodeState.FAILED
            self.error_message = str(e)
            raise
```

---

## 🔌 **节点注册和工厂系统**

### **节点注册器**
```python
class NodeRegistry:
    """节点注册器"""

    def __init__(self):
        self._node_classes: Dict[str, type] = {}
        self._node_categories: Dict[str, List[str]] = {}

    def register_node(self, node_type: str, node_class: type, category: str = "general"):
        """注册节点类"""
        if not issubclass(node_class, BaseNode):
            raise ValueError(f"Node class must inherit from BaseNode")

        self._node_classes[node_type] = node_class

        if category not in self._node_categories:
            self._node_categories[category] = []
        self._node_categories[category].append(node_type)

    def get_node_class(self, node_type: str) -> type:
        """获取节点类"""
        if node_type not in self._node_classes:
            raise ValueError(f"Unknown node type: {node_type}")
        return self._node_classes[node_type]

    def create_node(self, node_type: str, node_id: str, **kwargs) -> BaseNode:
        """创建节点实例"""
        node_class = self.get_node_class(node_type)
        return node_class(node_id, **kwargs)

    def get_available_nodes(self) -> Dict[str, List[str]]:
        """获取可用节点列表"""
        return self._node_categories.copy()

    def get_node_info(self, node_type: str) -> Dict[str, Any]:
        """获取节点信息"""
        node_class = self.get_node_class(node_type)
        return {
            "type": node_type,
            "name": node_class.__name__,
            "description": node_class.__doc__ or "",
            "inputs": [
                {
                    "name": inp.name,
                    "type": inp.type_hint.__name__,
                    "required": inp.required,
                    "default": inp.default_value,
                    "description": inp.description
                }
                for inp in node_class.get_input_spec()
            ],
            "outputs": [
                {
                    "name": out.name,
                    "type": out.type_hint.__name__,
                    "description": out.description
                }
                for out in node_class.get_output_spec()
            ]
        }

# 全局节点注册器
node_registry = NodeRegistry()

# 注册内置节点
node_registry.register_node("find_image", FindImageNode, "image_processing")
node_registry.register_node("click", ClickNode, "user_interaction")
node_registry.register_node("screenshot", ScreenshotNode, "image_processing")
node_registry.register_node("delay", DelayNode, "control_flow")
node_registry.register_node("conditional", ConditionalNode, "control_flow")
```

### **节点装饰器**
```python
def bluev_node(node_type: str, category: str = "custom"):
    """BlueV节点装饰器"""
    def decorator(cls):
        if not issubclass(cls, BaseNode):
            raise ValueError("Decorated class must inherit from BaseNode")

        node_registry.register_node(node_type, cls, category)
        return cls

    return decorator

# 使用示例
@bluev_node("custom_processor", "image_processing")
class CustomImageProcessor(BaseNode):
    """自定义图像处理节点"""

    @classmethod
    def get_input_spec(cls) -> List[NodeInput]:
        return [
            NodeInput("image", np.ndarray, description="输入图像"),
            NodeInput("operation", str, "blur", description="处理操作")
        ]

    @classmethod
    def get_output_spec(cls) -> List[NodeOutput]:
        return [
            NodeOutput("processed_image", np.ndarray, "处理后的图像")
        ]

    async def execute(self, context: 'ExecutionContext') -> Dict[str, Any]:
        # 实现自定义处理逻辑
        pass
```

---

**文档状态**: ✅ 节点系统实现方案已完成
**核心特性**: 类型安全、插件化、状态管理、高性能、可序列化
**内置节点**: 图像处理、用户交互、控制流等核心节点
**扩展机制**: 节点注册器 + 装饰器支持动态扩展
**下一步**: 实现工作流执行引擎和实时通信系统
