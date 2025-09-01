# -*- coding: utf-8 -*-
"""
ClickNode - 鼠标点击节点

提供鼠标点击功能，支持多种点击模式和参数配置，
用于自动化用户界面交互。
"""

import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from bluev.core.execution_context import ExecutionContext
from bluev.core import BaseNode, NodeInput, NodeMetadata, NodeOutput
from bluev.core.decorators import user_interaction_node
from bluev.utils.system_adapter import get_system_adapter


@user_interaction_node(
    node_type="click",
    display_name="鼠标点击",
    description="执行鼠标点击操作，支持多种点击模式",
)
class ClickNode(BaseNode):
    """
    鼠标点击节点

    功能：
    - 支持左键、右键、中键点击
    - 可配置点击次数和间隔
    - 支持双击和多次点击
    - 自动安全检查和错误处理

    适用场景：
    - 点击UI按钮和控件
    - 游戏自动化操作
    - 自动化测试脚本
    - 重复性点击任务

    安全特性：
    - 屏幕边界检查
    - 点击前延迟
    - 失败安全机制
    """

    # 支持的鼠标按键
    MOUSE_BUTTONS = {
        "left": "left",
        "right": "right",
        "middle": "middle",
        "primary": "left",  # 别名
        "secondary": "right",  # 别名
    }

    def __init__(
        self, node_id: Optional[str] = None, label: Optional[str] = None
    ) -> None:
        """初始化点击节点"""
        super().__init__(node_id, label)

        # 通过系统适配层获取屏幕尺寸（Windows 可用，WSL 会抛异常）
        try:
            adapter = get_system_adapter()
            self.screen_width, self.screen_height = adapter.get_screen_size()
            self.logger.debug(f"屏幕尺寸: {self.screen_width}x{self.screen_height}")
        except Exception as e:
            self.logger.warning(f"无法获取屏幕尺寸: {e}")
            self.screen_width, self.screen_height = 1920, 1080  # 默认值

    @classmethod
    def get_input_spec(cls) -> List[NodeInput]:
        """获取输入规范"""
        return [
            NodeInput(
                name="location",
                data_type=tuple,  # 运行时校验采用基础类型，避免 typing 检查问题
                required=True,
                description="点击位置坐标 (x, y)",
            ),
            NodeInput(
                name="button",
                data_type=str,
                default_value="left",
                required=False,
                description=f"鼠标按键，支持: {', '.join(cls.MOUSE_BUTTONS.keys())}",
            ),
            NodeInput(
                name="clicks",
                data_type=int,
                default_value=1,
                required=False,
                description="点击次数，必须大于0",
            ),
            NodeInput(
                name="interval",
                data_type=float,
                default_value=0.1,
                required=False,
                description="多次点击间的间隔时间 (秒)",
            ),
            NodeInput(
                name="duration",
                data_type=float,
                default_value=0.0,
                required=False,
                description="按住时间 (秒)，0表示普通点击",
            ),
            NodeInput(
                name="before_delay",
                data_type=float,
                default_value=0.0,
                required=False,
                description="点击前延迟时间 (秒)",
            ),
        ]

    @classmethod
    def get_output_spec(cls) -> List[NodeOutput]:
        """获取输出规范"""
        return [
            NodeOutput(name="success", data_type=bool, description="是否成功执行点击"),
            NodeOutput(
                name="actual_clicks", data_type=int, description="实际执行的点击次数"
            ),
            NodeOutput(
                name="click_location",
                data_type=Tuple[int, int],  # type: ignore
                description="实际点击的位置坐标",
            ),
            NodeOutput(
                name="execution_time", data_type=float, description="执行时间 (秒)"
            ),
            NodeOutput(
                name="error_message",
                data_type=Optional[str],  # type: ignore
                description="错误信息，成功时为 None",
            ),
        ]

    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """获取节点元数据"""
        return NodeMetadata(
            node_type="click_node",
            display_name="鼠标点击",
            description="执行鼠标点击操作，支持多种点击模式",
            category="user_interaction",
            tags=["click", "mouse", "interaction", "automation"],
            version="1.0.0",
        )

    def _validate_location(self, x: int, y: int) -> bool:
        """
        验证点击位置是否在屏幕范围内

        Args:
            x: X坐标
            y: Y坐标

        Returns:
            是否有效
        """
        return 0 <= x < self.screen_width and 0 <= y < self.screen_height

    async def execute(self, context: "ExecutionContext") -> Dict[str, Any]:
        """
        执行鼠标点击

        Args:
            context: 执行上下文

        Returns:
            包含点击结果的字典
        """
        self.logger.info("开始执行鼠标点击")
        start_time = time.time()

        try:
            # 获取并验证输入参数
            params = self._get_and_validate_params()

            # 执行点击前延迟
            self._execute_before_delay(params["before_delay"])

            # 执行点击操作
            actual_clicks = self._perform_clicks(params)

            # 生成并返回结果
            return self._generate_result(params, actual_clicks, start_time)

        except Exception as e:
            return self._generate_error_result(e, start_time)

    def _get_and_validate_params(self) -> Dict[str, Any]:
        """获取并验证输入参数"""
        # 获取输入参数
        location = self.inputs.get("location")
        button = self.inputs.get("button", "left").lower()
        clicks = self.inputs.get("clicks", 1)
        interval = self.inputs.get("interval", 0.1)
        duration = self.inputs.get("duration", 0.0)
        before_delay = self.inputs.get("before_delay", 0.0)

        # 参数验证
        if location is None or len(location) != 2:
            raise ValueError("位置参数必须是包含两个数字的坐标元组")

        x, y = int(location[0]), int(location[1])

        if not self._validate_location(x, y):
            raise ValueError(
                f"点击位置 ({x}, {y}) 超出屏幕范围 ({self.screen_width}x{self.screen_height})"
            )

        if button not in self.MOUSE_BUTTONS:
            self.logger.warning(f"未知的鼠标按键 '{button}'，使用默认按键 'left'")
            button = "left"

        # 转换按键名称
        button = self.MOUSE_BUTTONS[button]

        if clicks <= 0:
            raise ValueError("点击次数必须大于0")

        if interval < 0:
            raise ValueError("点击间隔不能为负数")

        if duration < 0:
            raise ValueError("点击持续时间不能为负数")

        return {
            "x": x,
            "y": y,
            "button": button,
            "clicks": clicks,
            "interval": interval,
            "duration": duration,
            "before_delay": before_delay,
        }

    def _execute_before_delay(self, before_delay: float) -> None:
        """执行点击前延迟"""
        if before_delay > 0:
            self.logger.debug(f"点击前延迟 {before_delay} 秒")
            time.sleep(before_delay)

    def _perform_clicks(self, params: Dict[str, Any]) -> int:
        """执行点击操作"""
        x, y = params["x"], params["y"]
        button = params["button"]
        clicks = params["clicks"]
        interval = params["interval"]
        duration = params["duration"]

        self.logger.info(f"执行点击: 位置=({x}, {y}), 按键={button}, 次数={clicks}")

        actual_clicks = 0
        for i in range(clicks):
            try:
                self._perform_single_click(x, y, button, duration)
                actual_clicks += 1
                self.logger.debug(f"完成第 {i + 1} 次点击")

                # 多次点击间的间隔
                if i < clicks - 1 and interval > 0:
                    time.sleep(interval)

            except Exception as e:
                if "FailSafe" in str(e):
                    self.logger.warning("触发 PyAutoGUI 安全机制，停止点击")
                else:
                    self.logger.error(f"第 {i + 1} 次点击失败: {e}")
                break

        return actual_clicks

    def _perform_single_click(
        self, x: int, y: int, button: str, duration: float
    ) -> None:
        """执行单次点击"""
        adapter = get_system_adapter()
        if duration > 0:
            # 按住点击
            adapter.click(x, y, button=button)
            time.sleep(duration)
            adapter.click(x, y, button=button)
        else:
            # 普通点击
            adapter.click(x, y, button=button)

    def _generate_result(
        self, params: Dict[str, Any], actual_clicks: int, start_time: float
    ) -> Dict[str, Any]:
        """生成执行结果"""
        execution_time = time.time() - start_time
        success = actual_clicks > 0
        error_message = None if success else "所有点击都失败了"

        result = {
            "success": success,
            "actual_clicks": actual_clicks,
            "click_location": (params["x"], params["y"]),
            "execution_time": execution_time,
            "error_message": error_message,
        }

        if success:
            self.logger.info(
                f"点击完成: {actual_clicks}/{params['clicks']} 次成功, 耗时 {execution_time:.3f}秒"
            )
        else:
            self.logger.error(f"点击失败: 耗时 {execution_time:.3f}秒")

        return result

    def _generate_error_result(
        self, error: Exception, start_time: float
    ) -> Dict[str, Any]:
        """生成错误结果"""
        execution_time = time.time() - start_time
        self.logger.error(f"点击执行失败: {error}")

        return {
            "success": False,
            "actual_clicks": 0,
            "click_location": (0, 0),
            "execution_time": execution_time,
            "error_message": str(error),
        }
