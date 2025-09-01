# -*- coding: utf-8 -*-
"""
FindImageNode - 图像查找节点 (基础版)

提供基础的图像模板匹配功能，使用 OpenCV 进行图像识别，
支持在源图像中查找模板图像的位置。
"""

import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import cv2  # type: ignore
import numpy as np

if TYPE_CHECKING:
    from bluev.core.execution_context import ExecutionContext
from bluev.core import BaseNode, NodeInput, NodeMetadata, NodeOutput
from bluev.core.decorators import image_processing_node


@image_processing_node(
    node_type="find_image",
    display_name="图像查找",
    description="在源图像中查找模板图像，返回匹配位置和置信度",
)
class FindImageNode(BaseNode):
    """
    图像查找节点 (基础版)

    功能：
    - 基础模板匹配 (使用 OpenCV)
    - 可配置匹配阈值
    - 返回最佳匹配位置和置信度
    - 支持多种图像格式输入

    适用场景：
    - 在屏幕截图中查找UI元素
    - 游戏自动化中的图标识别
    - 简单的图像定位任务

    注意：这是基础版实现，复杂的多尺度匹配等功能将在 Phase 2 实现
    """

    # 支持的 OpenCV 匹配方法
    MATCH_METHODS = {
        "TM_CCOEFF": cv2.TM_CCOEFF,
        "TM_CCOEFF_NORMED": cv2.TM_CCOEFF_NORMED,
        "TM_CCORR": cv2.TM_CCORR,
        "TM_CCORR_NORMED": cv2.TM_CCORR_NORMED,
        "TM_SQDIFF": cv2.TM_SQDIFF,
        "TM_SQDIFF_NORMED": cv2.TM_SQDIFF_NORMED,
    }

    @classmethod
    def get_input_spec(cls) -> List[NodeInput]:
        """获取输入规范"""
        return [
            NodeInput(
                name="template_image",
                data_type=np.ndarray,
                required=True,
                description="模板图像 (numpy 数组格式)",
            ),
            NodeInput(
                name="source_image",
                data_type=np.ndarray,
                required=True,
                description="源图像 (numpy 数组格式)",
            ),
            NodeInput(
                name="threshold",
                data_type=float,
                default_value=0.8,
                required=False,
                description="匹配阈值 (0.0-1.0)，越高越严格",
            ),
            NodeInput(
                name="method",
                data_type=str,
                default_value="TM_CCOEFF_NORMED",
                required=False,
                description=f"匹配方法，支持: {', '.join(cls.MATCH_METHODS.keys())}",
            ),
        ]

    @classmethod
    def get_output_spec(cls) -> List[NodeOutput]:
        """获取输出规范"""
        return [
            NodeOutput(name="found", data_type=bool, description="是否找到匹配"),
            NodeOutput(
                name="location",
                data_type=Optional[Tuple[int, int]],  # type: ignore
                description="匹配位置 (x, y)，如果未找到则为 None",
            ),
            NodeOutput(
                name="confidence", data_type=float, description="匹配置信度 (0.0-1.0)"
            ),
            NodeOutput(
                name="match_rect",
                data_type=Optional[Tuple[int, int, int, int]],  # type: ignore
                description="匹配矩形区域 (x, y, width, height)",
            ),
            NodeOutput(
                name="processing_time", data_type=float, description="处理时间 (秒)"
            ),
        ]

    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """获取节点元数据"""
        return NodeMetadata(
            node_type="find_image_node",
            display_name="图像查找",
            description="在源图像中查找模板图像，返回匹配位置和置信度",
            category="image_processing",
            tags=["find_image", "template", "matching", "opencv"],
            version="1.0.0",
        )

    def _prepare_image(self, image: np.ndarray) -> np.ndarray:
        """
        准备图像用于匹配

        Args:
            image: 输入图像

        Returns:
            处理后的图像 (灰度)
        """
        # 如果是彩色图像，转换为灰度
        if len(image.shape) == 3:
            if image.shape[2] == 3:  # RGB
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            elif image.shape[2] == 4:  # RGBA
                gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
            else:
                gray = image[:, :, 0]  # 取第一个通道
        else:
            gray = image

        return gray  # type: ignore

    async def execute(self, context: "ExecutionContext") -> Dict[str, Any]:
        """
        执行图像查找

        Args:
            context: 执行上下文

        Returns:
            包含匹配结果的字典

        Raises:
            ValueError: 输入参数无效时抛出异常
            Exception: 图像处理失败时抛出异常
        """
        self.logger.info("开始执行图像查找")
        start_time = time.time()

        try:
            # 获取输入参数
            template_image = self.inputs.get("template_image")
            source_image = self.inputs.get("source_image")
            threshold = self.inputs.get("threshold", 0.8)
            method_name = self.inputs.get("method", "TM_CCOEFF_NORMED")

            # 参数验证
            if template_image is None or source_image is None:
                raise ValueError

            if not (0.0 <= threshold <= 1.0):
                raise ValueError

            if method_name not in self.MATCH_METHODS:
                self.logger.warning(
                    f"未知的匹配方法 '{method_name}'，使用默认方法 'TM_CCOEFF_NORMED'"
                )
                method_name = "TM_CCOEFF_NORMED"

            method = self.MATCH_METHODS[method_name]

            # 准备图像
            template_gray = self._prepare_image(template_image)
            source_gray = self._prepare_image(source_image)

            # 检查图像尺寸
            if (
                template_gray.shape[0] > source_gray.shape[0]
                or template_gray.shape[1] > source_gray.shape[1]
            ):
                self.logger.warning("模板图像大于源图像，无法进行匹配")
                processing_time = time.time() - start_time
                return {
                    "found": False,
                    "location": None,
                    "confidence": 0.0,
                    "match_rect": None,
                    "processing_time": processing_time,
                }

            self.logger.debug(f"开始模板匹配: 方法={method_name}, 阈值={threshold}")
            self.logger.debug(
                f"模板尺寸: {template_gray.shape}, 源图像尺寸: {source_gray.shape}"
            )

            # 执行模板匹配
            result = cv2.matchTemplate(source_gray, template_gray, method)

            # 获取最佳匹配位置
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # 根据匹配方法确定最佳匹配值和位置
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                # 对于 SQDIFF 方法，值越小越好
                best_match_val = min_val
                best_match_loc = min_loc
                # 转换为相似度 (0-1)
                if method == cv2.TM_SQDIFF_NORMED:
                    confidence = 1.0 - best_match_val
                else:
                    # 对于非归一化的 SQDIFF，需要特殊处理
                    confidence = 1.0 / (1.0 + best_match_val)
            else:
                # 对于其他方法，值越大越好
                best_match_val = max_val
                best_match_loc = max_loc
                # 归一化置信度
                if method in [cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED]:
                    confidence = max(0.0, best_match_val)
                else:
                    # 对于非归一化方法，简单归一化
                    confidence = min(1.0, max(0.0, best_match_val / 1000000.0))

            # 判断是否找到匹配
            found = confidence >= threshold

            # 计算匹配矩形
            if found:
                x, y = best_match_loc
                h, w = template_gray.shape
                location = (x, y)
                match_rect = (x, y, w, h)
                self.logger.info(f"找到匹配: 位置=({x}, {y}), 置信度={confidence:.3f}")
            else:
                location = None
                match_rect = None
                self.logger.info(
                    f"未找到匹配: 最高置信度={confidence:.3f} < 阈值={threshold}"
                )

            # 计算处理时间
            processing_time = time.time() - start_time

            # 返回结果
            result = {
                "found": found,
                "location": location,
                "confidence": confidence,
                "match_rect": match_rect,
                "processing_time": processing_time,
            }

            self.logger.info(f"图像查找完成: 耗时 {processing_time:.3f}秒")
            return result  # type: ignore

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"图像查找失败: {e}")

            # 返回失败结果
            return {
                "found": False,
                "location": None,
                "confidence": 0.0,
                "match_rect": None,
                "processing_time": processing_time,
            }
