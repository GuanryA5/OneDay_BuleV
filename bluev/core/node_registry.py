# -*- coding: utf-8 -*-
"""
BlueV 节点注册系统

管理所有可用节点类型的注册、查询和创建。
"""

import threading
from collections import defaultdict
from typing import Dict, List, Optional, Set

from bluev.core.base_node import BaseNode
from bluev.core.node_types import NodeClassType, NodeMetadata
from bluev.utils.logging import get_logger


class NodeRegistry:
    """
    节点注册器

    线程安全的节点类型管理器，支持节点的注册、查询、创建和分类管理。
    """

    def __init__(self) -> None:
        """初始化节点注册器"""
        # 节点类型存储 {node_type: node_class}
        self._node_classes: Dict[str, NodeClassType] = {}

        # 节点分类存储 {category: {node_type, ...}}
        self._categories: Dict[str, Set[str]] = defaultdict(set)

        # 节点元数据缓存 {node_type: metadata}
        self._metadata_cache: Dict[str, NodeMetadata] = {}

        # 线程锁
        self._lock = threading.RLock()

        # 日志记录器
        self.logger = get_logger("NodeRegistry")

        self.logger.debug("节点注册器初始化完成")

    def register_node(
        self, node_type: str, node_class: NodeClassType, category: str = "custom"
    ) -> bool:
        """
        注册节点类型

        Args:
            node_type: 节点类型标识符
            node_class: 节点类
            category: 节点分类

        Returns:
            注册是否成功

        Raises:
            ValueError: 节点类型无效或已存在
            TypeError: 节点类不是BaseNode的子类
        """
        with self._lock:
            # 验证参数
            if not node_type or not isinstance(node_type, str):
                raise ValueError

            if not issubclass(node_class, BaseNode):
                raise TypeError

            # 检查是否已注册
            if node_type in self._node_classes:
                existing_class = self._node_classes[node_type]
                if existing_class != node_class:
                    raise ValueError
                else:
                    self.logger.warning(f"节点类型 '{node_type}' 重复注册，忽略")
                    return False

            # 注册节点
            self._node_classes[node_type] = node_class
            self._categories[category].add(node_type)

            # 缓存元数据
            try:
                metadata = node_class.get_metadata()
                self._metadata_cache[node_type] = metadata
            except Exception as e:
                self.logger.warning(f"获取节点 '{node_type}' 元数据失败: {e}")

            self.logger.info(
                f"注册节点: {node_type} ({node_class.__name__}) -> {category}"
            )
            return True

    def unregister_node(self, node_type: str) -> bool:
        """
        注销节点类型

        Args:
            node_type: 节点类型标识符

        Returns:
            注销是否成功
        """
        with self._lock:
            if node_type not in self._node_classes:
                self.logger.warning(f"尝试注销不存在的节点类型: {node_type}")
                return False

            # 从分类中移除
            for _category, node_types in self._categories.items():
                if node_type in node_types:
                    node_types.remove(node_type)
                    break

            # 移除注册信息
            del self._node_classes[node_type]

            # 清除元数据缓存
            if node_type in self._metadata_cache:
                del self._metadata_cache[node_type]

            self.logger.info(f"注销节点: {node_type}")
            return True

    def get_node_class(self, node_type: str) -> Optional[NodeClassType]:
        """
        获取节点类

        Args:
            node_type: 节点类型标识符

        Returns:
            节点类，如果不存在则返回None
        """
        with self._lock:
            return self._node_classes.get(node_type)

    def create_node(
        self, node_type: str, node_id: Optional[str] = None, label: Optional[str] = None
    ) -> Optional[BaseNode]:
        """
        创建节点实例

        Args:
            node_type: 节点类型标识符
            node_id: 节点ID，如果为None则自动生成
            label: 节点标签

        Returns:
            节点实例，如果节点类型不存在则返回None
        """
        node_class = self.get_node_class(node_type)
        if node_class is None:
            self.logger.error(f"未找到节点类型: {node_type}")
            return None

        try:
            node = node_class(node_id=node_id, label=label)
            self.logger.debug(f"创建节点实例: {node_type} -> {node.node_id}")
            return node
        except Exception as e:
            self.logger.error(f"创建节点实例失败 ({node_type}): {e}")
            return None

    def list_node_types(self, category: Optional[str] = None) -> List[str]:
        """
        列出节点类型

        Args:
            category: 节点分类，如果为None则返回所有类型

        Returns:
            节点类型列表
        """
        with self._lock:
            if category is None:
                return list(self._node_classes.keys())
            else:
                return list(self._categories.get(category, set()))

    def list_categories(self) -> List[str]:
        """
        列出所有分类

        Returns:
            分类列表
        """
        with self._lock:
            return list(self._categories.keys())

    def get_node_metadata(self, node_type: str) -> Optional[NodeMetadata]:
        """
        获取节点元数据

        Args:
            node_type: 节点类型标识符

        Returns:
            节点元数据，如果不存在则返回None
        """
        with self._lock:
            return self._metadata_cache.get(node_type)

    def get_nodes_by_category(self, category: str) -> Dict[str, NodeMetadata]:
        """
        按分类获取节点信息

        Args:
            category: 节点分类

        Returns:
            节点类型到元数据的映射
        """
        with self._lock:
            result = {}
            node_types = self._categories.get(category, set())
            for node_type in node_types:
                metadata = self._metadata_cache.get(node_type)
                if metadata:
                    result[node_type] = metadata
            return result

    def search_nodes(self, keyword: str, category: Optional[str] = None) -> List[str]:
        """
        搜索节点

        Args:
            keyword: 搜索关键词
            category: 限制搜索的分类

        Returns:
            匹配的节点类型列表
        """
        with self._lock:
            keyword_lower = keyword.lower()
            results = []

            # 确定搜索范围
            if category:
                search_types = self._categories.get(category, set())
            else:
                search_types = set(self._node_classes.keys())

            # 搜索匹配
            for node_type in search_types:
                # 检查节点类型名称
                if keyword_lower in node_type.lower():
                    results.append(node_type)
                    continue

                # 检查元数据
                metadata = self._metadata_cache.get(node_type)
                if metadata:
                    # 检查显示名称和描述
                    if (
                        keyword_lower in metadata.display_name.lower()
                        or keyword_lower in metadata.description.lower()
                    ):
                        results.append(node_type)
                        continue

                    # 检查标签
                    for tag in metadata.tags:
                        if keyword_lower in tag.lower():
                            results.append(node_type)
                            break

            return results

    def is_registered(self, node_type: str) -> bool:
        """
        检查节点类型是否已注册

        Args:
            node_type: 节点类型标识符

        Returns:
            是否已注册
        """
        with self._lock:
            return node_type in self._node_classes

    def get_registry_info(self) -> Dict[str, any]:
        """
        获取注册器信息

        Returns:
            注册器统计信息
        """
        with self._lock:
            return {
                "total_nodes": len(self._node_classes),
                "categories": {
                    _category: len(node_types)
                    for _category, node_types in self._categories.items()
                },
                "node_types": list(self._node_classes.keys()),
            }

    def clear(self) -> None:
        """清空所有注册信息"""
        with self._lock:
            self._node_classes.clear()
            self._categories.clear()
            self._metadata_cache.clear()
            self.logger.info("清空节点注册器")


# 全局节点注册器实例
node_registry = NodeRegistry()
