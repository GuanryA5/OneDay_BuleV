# -*- coding: utf-8 -*-
"""
ScreenshotNode - 屏幕截图节点

提供屏幕截图功能，支持全屏截图和区域截图，
可选择保存到文件或仅返回图像数据。
"""

import os
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import numpy as np

if TYPE_CHECKING:
    from bluev.core.execution_context import ExecutionContext
from bluev.core import BaseNode, NodeInput, NodeMetadata, NodeOutput
from bluev.core.decorators import image_processing_node
from bluev.utils.system_adapter import get_system_adapter


@image_processing_node(
    node_type="screenshot",
    display_name="屏幕截图",
    description="捕获屏幕截图，支持全屏和区域截图",
)
class ScreenshotNode(BaseNode):
    """
    屏幕截图节点

    功能：
    - 全屏截图
    - 区域截图 (x, y, width, height)
    - 可选文件保存
    - 返回 numpy 数组格式的图像数据

    适用场景：
    - 工作流开始时捕获当前屏幕状态
    - 为图像识别节点提供源图像
    - 调试时保存屏幕快照
    """

    @classmethod
    def get_input_spec(cls) -> List[NodeInput]:
        """获取输入规范"""
        return [
            NodeInput(
                name="region",
                data_type=Optional[Tuple[int, int, int, int]],
                default_value=None,
                required=False,
                description="截图区域 (x, y, width, height)，None表示全屏",
            ),
            NodeInput(
                name="save_path",
                data_type=Optional[str],
                default_value=None,
                required=False,
                description="保存路径，None表示不保存文件",
            ),
            NodeInput(
                name="format",
                data_type=str,
                default_value="PNG",
                required=False,
                description="图像格式 (PNG, JPEG, BMP)",
            ),
        ]

    @classmethod
    def get_output_spec(cls) -> List[NodeOutput]:
        """获取输出规范"""
        return [
            NodeOutput(
                name="image",
                data_type=np.ndarray,
                description="截图的 numpy 数组数据 (RGB格式)",
            ),
            NodeOutput(
                name="image_path",
                data_type=Optional[str],
                description="保存的图片文件路径，如果未保存则为 None",
            ),
            NodeOutput(
                name="image_size",
                data_type=Tuple[int, int],
                description="图像尺寸 (width, height)",
            ),
            NodeOutput(name="capture_time", data_type=str, description="截图时间戳"),
        ]

    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """获取节点元数据"""
        return NodeMetadata(
            display_name="屏幕截图",
            description="捕获屏幕截图，支持全屏和区域截图",
            category="image_processing",
            tags=["screenshot", "image", "capture"],
            version="1.0.0",
        )

    async def execute(self, context: "ExecutionContext") -> Dict[str, Any]:
        """
        执行屏幕截图

        Args:
            context: 执行上下文

        Returns:
            包含截图数据的字典

        Raises:
            Exception: 截图失败时抛出异常
        """
        self.logger.info("开始执行屏幕截图")

        try:
            # 获取输入参数
            region = self.inputs.get("region")
            save_path = self.inputs.get("save_path")
            image_format = self.inputs.get("format", "PNG").upper()

            # 记录截图时间
            capture_time = datetime.now().isoformat()

            # 执行截图（通过系统适配层）
            adapter = get_system_adapter()
            if region is not None:
                # 区域截图
                x, y, width, height = region
                bbox = (x, y, x + width, y + height)
                self.logger.debug(f"区域截图: {bbox}")
                pil_image = adapter.screenshot(region=(x, y, width, height))
            else:
                # 全屏截图
                self.logger.debug("全屏截图")
                pil_image = adapter.screenshot(region=None)

            # 转换为 numpy 数组 (RGB格式)
            image_array = np.array(pil_image)
            if image_array.ndim == 3 and image_array.shape[2] == 4:
                # 如果是 RGBA，转换为 RGB
                image_array = image_array[:, :, :3]

            # 获取图像尺寸
            height, width = image_array.shape[:2]
            image_size = (width, height)

            # 保存文件（如果指定了路径）
            saved_path = None
            if save_path:
                try:
                    # 确保目录存在
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)

                    # 保存图像
                    pil_image.save(save_path, format=image_format)
                    saved_path = save_path
                    self.logger.info(f"截图已保存: {save_path}")
                except Exception as e:
                    self.logger.warning(f"保存截图失败: {e}")
                    # 不抛出异常，继续返回图像数据

            # 返回结果
            result = {
                "image": image_array,
                "image_path": saved_path,
                "image_size": image_size,
                "capture_time": capture_time,
            }

            self.logger.info(f"截图完成: {image_size[0]}x{image_size[1]}")
            return result

        except Exception as e:
            self.logger.error(f"截图执行失败: {e}")
            raise
