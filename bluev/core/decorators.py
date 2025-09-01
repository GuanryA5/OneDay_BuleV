# -*- coding: utf-8 -*-
"""
BlueV 节点装饰器

提供便于使用的装饰器来简化节点注册和定义。
"""

from functools import wraps
from typing import List, Optional, Type

from bluev.core.base_node import BaseNode
from bluev.core.node_registry import node_registry
from bluev.core.node_types import NodeMetadata
from bluev.utils.logging import get_logger

logger = get_logger("NodeDecorators")


def bluev_node(
    node_type: str,
    category: str = "custom",
    display_name: Optional[str] = None,
    description: str = "",
    version: str = "1.0.0",
    author: str = "BlueV User",
    tags: Optional[List[str]] = None,
    icon: Optional[str] = None,
) -> Callable[[type], type]:
    """
    BlueV 节点装饰器

    自动注册节点类型并设置元数据。

    Args:
        node_type: 节点类型标识符
        category: 节点分类
        display_name: 显示名称，如果为None则使用类名
        description: 节点描述
        version: 版本号
        author: 作者
        tags: 标签列表
        icon: 图标路径

    Returns:
        装饰后的节点类

    Example:
        @bluev_node("my_custom_node", "utility", "我的自定义节点")
        class MyCustomNode(BaseNode):
            # 节点实现
            pass
    """

    def decorator(cls: Type[BaseNode]) -> Type[BaseNode]:
        # 验证节点类
        if not issubclass(cls, BaseNode):
            raise TypeError

        # 设置显示名称
        actual_display_name = display_name or cls.__name__

        # 创建元数据
        metadata = NodeMetadata(
            node_type=node_type,
            category=category,
            display_name=actual_display_name,
            description=description,
            version=version,
            author=author,
            tags=tags or [],
            icon=icon,
        )

        # 为类添加get_metadata方法
        def get_metadata_func(cls: type) -> NodeMetadata:
            return metadata

        setattr(cls, 'get_metadata', classmethod(get_metadata_func))

        # 注册节点
        try:
            success = node_registry.register_node(node_type, cls, category)
            if success:
                logger.info(f"通过装饰器注册节点: {node_type} ({cls.__name__})")
            else:
                logger.warning(f"节点 {node_type} 可能已经注册")
        except Exception as e:
            logger.error(f"注册节点失败 ({node_type}): {e}")
            raise

        return cls

    return decorator


def input_node(
    node_type: str, display_name: Optional[str] = None, description: str = "", **kwargs: Any
) -> Callable[[type], type]:
    """
    输入节点装饰器

    专门用于输入类型节点的装饰器。

    Args:
        node_type: 节点类型标识符
        display_name: 显示名称
        description: 节点描述
        **kwargs: 其他参数传递给bluev_node

    Returns:
        装饰后的节点类
    """
    return bluev_node(
        node_type=node_type,
        category="input",
        display_name=display_name,
        description=description,
        tags=["input", "data"],
        **kwargs,
    )


def output_node(
    node_type: str, display_name: Optional[str] = None, description: str = "", **kwargs: Any
) -> Callable[[type], type]:
    """
    输出节点装饰器

    专门用于输出类型节点的装饰器。

    Args:
        node_type: 节点类型标识符
        display_name: 显示名称
        description: 节点描述
        **kwargs: 其他参数传递给bluev_node

    Returns:
        装饰后的节点类
    """
    return bluev_node(
        node_type=node_type,
        category="output",
        display_name=display_name,
        description=description,
        tags=["output", "result"],
        **kwargs,
    )


def image_processing_node(
    node_type: str, display_name: Optional[str] = None, description: str = "", **kwargs: Any
) -> Callable[[type], type]:
    """
    图像处理节点装饰器

    专门用于图像处理类型节点的装饰器。

    Args:
        node_type: 节点类型标识符
        display_name: 显示名称
        description: 节点描述
        **kwargs: 其他参数传递给bluev_node

    Returns:
        装饰后的节点类
    """
    return bluev_node(
        node_type=node_type,
        category="image_processing",
        display_name=display_name,
        description=description,
        tags=["image_processing", "opencv", "vision"],
        **kwargs,
    )


def control_flow_node(
    node_type: str, display_name: Optional[str] = None, description: str = "", **kwargs: Any
) -> Callable[[type], type]:
    """
    控制流节点装饰器

    专门用于控制流类型节点的装饰器。

    Args:
        node_type: 节点类型标识符
        display_name: 显示名称
        description: 节点描述
        **kwargs: 其他参数传递给bluev_node

    Returns:
        装饰后的节点类
    """
    return bluev_node(
        node_type=node_type,
        category="control_flow",
        display_name=display_name,
        description=description,
        tags=["control_flow", "timing", "logic"],
        **kwargs,
    )


def user_interaction_node(
    node_type: str, display_name: Optional[str] = None, description: str = "", **kwargs: Any
) -> Callable[[type], type]:
    """
    用户交互节点装饰器

    专门用于用户交互类型节点的装饰器。

    Args:
        node_type: 节点类型标识符
        display_name: 显示名称
        description: 节点描述
        **kwargs: 其他参数传递给bluev_node

    Returns:
        装饰后的节点类
    """
    return bluev_node(
        node_type=node_type,
        category="user_interaction",
        display_name=display_name,
        description=description,
        tags=["user_interaction", "automation", "input"],
        **kwargs,
    )


def utility_node(
    node_type: str, display_name: Optional[str] = None, description: str = "", **kwargs: Any
) -> Callable[[type], type]:
    """
    工具节点装饰器

    专门用于工具类型节点的装饰器。

    Args:
        node_type: 节点类型标识符
        display_name: 显示名称
        description: 节点描述
        **kwargs: 其他参数传递给bluev_node

    Returns:
        装饰后的节点类
    """
    return bluev_node(
        node_type=node_type,
        category="utility",
        display_name=display_name,
        description=description,
        tags=["utility", "logging", "debugging"],
        **kwargs,
    )


def deprecated_node(reason: str = "") -> Callable[[type], type]:
    """
    废弃节点装饰器

    标记节点为废弃状态。

    Args:
        reason: 废弃原因

    Returns:
        装饰后的节点类
    """

    def decorator(cls: Type[BaseNode]) -> Type[BaseNode]:
        # 保存原始的get_metadata方法
        original_get_metadata = cls.get_metadata

        @classmethod
        def get_metadata(cls) -> NodeMetadata:
            metadata = original_get_metadata()
            # 添加废弃标记
            metadata.tags.append("deprecated")
            if reason:
                metadata.description += f" [已废弃: {reason}]"
            return metadata

        cls.get_metadata = get_metadata

        # 添加废弃警告
        original_init = cls.__init__

        @wraps(original_init)
        def _deprecated_init_wrapper(self: Any, *args: Any, **kwargs: Any) -> None:
            logger.warning(f"使用了废弃的节点类型: {cls.__name__}. {reason}")
            original_init(self, *args, **kwargs)

        cls.__init__ = _deprecated_init_wrapper

        return cls

    return decorator
