# -*- coding: utf-8 -*-
"""
BlueV 工作流加载器（最小实现）

职责：
- 校验最小工作流定义（dict/JSON）
- 使用 NodeRegistry 创建节点并设置参数
- 依据简单边（仅节点ID对）推断端口并连接（单入/单出规则）
- 构建 WorkflowEngine 返回

注意：此实现为最小可用版本，端口推断规则：
- 若源节点只有一个输出，则采用该输出；否则报错要求在未来提供端口名
- 若目标节点只有一个输入，则采用该输入；否则报错要求在未来提供端口名
"""

from __future__ import annotations

import json
from typing import Any

from bluev.core.base_node import BaseNode
from bluev.core.node_registry import NodeRegistry, node_registry
from bluev.core.node_types import NodeInput, NodeOutput
from bluev.core.workflow_engine import WorkflowEngine


class WorkflowValidationError(ValueError):
    """工作流定义校验错误"""


def _require_str(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise WorkflowValidationError
    return value


def _require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise WorkflowValidationError
    return value


def validate_workflow_dict(
    data: dict[str, Any],
) -> tuple[str, list[dict[str, Any]], list[list[str]]]:
    """校验最小工作流定义并返回三元组 (workflow_id, nodes, edges)

    期望字段:
    - workflow_id: str
    - nodes: List[{id:str, type:str, params:dict(optional)}]
    - edges: List[[from_id, to_id]]
    """
    if not isinstance(data, dict):
        raise WorkflowValidationError

    workflow_id = _require_str(data.get("workflow_id"), "workflow_id")
    nodes = _require_list(data.get("nodes"), "nodes")
    edges = _require_list(data.get("edges"), "edges")

    seen_ids = set()
    for i, n in enumerate(nodes):
        if not isinstance(n, dict):
            raise WorkflowValidationError
        node_id = _require_str(n.get("id"), f"nodes[{i}].id")
        _require_str(n.get("type"), f"nodes[{i}].type")
        if node_id in seen_ids:
            raise WorkflowValidationError
        seen_ids.add(node_id)
        # params 可选
        params = n.get("params", {})
        if params is not None and not isinstance(params, dict):
            raise WorkflowValidationError

    for _j, e in enumerate(edges):
        if not isinstance(e, list) or len(e) != 2:
            raise WorkflowValidationError
        frm, to = e
        if frm not in seen_ids:
            raise WorkflowValidationError
        if to not in seen_ids:
            raise WorkflowValidationError

    return workflow_id, nodes, edges


def _set_params_to_node(node: BaseNode, params: dict[str, Any]) -> None:
    # 仅将匹配输入规范的键写入，并使用 validate_inputs 后总体校验
    allowed_inputs = {spec.name for spec in node.get_input_spec()}
    for k, v in (params or {}).items():
        if k in allowed_inputs:
            node.set_input(k, v)


def _resolve_single_port(node: BaseNode, kind: str) -> str:
    if kind == "input":
        specs: list[NodeInput] | list[NodeOutput] = node.get_input_spec()
        preferred = ["image", "source_image", "input", "bbox", "location"]
    else:
        specs = node.get_output_spec()
        preferred = ["image", "result", "output", "bbox", "location"]

    if not specs:
        raise WorkflowValidationError(
            f"节点 {node.node_id} 未定义{('输入' if kind == 'input' else '输出')}端口"
        )

    # 优先命名匹配
    names = [s.name for s in specs]
    for p in preferred:
        if p in names:
            return p

    # 回退：选择第一个端口名（最小实现）
    return str(specs[0].name)


def build_engine_from_workflow(
    data: dict[str, Any], registry: NodeRegistry | None = None
) -> WorkflowEngine:
    """从最小工作流定义构建 WorkflowEngine。

    会执行：
    - 基本结构校验
    - 创建节点并写入 params
    - 连接节点（单入/单出推断）
    - 返回可用于执行的引擎
    """
    registry = registry or node_registry

    workflow_id, nodes_def, edges_def = validate_workflow_dict(data)

    engine = WorkflowEngine()

    # 创建节点
    id_to_node: dict[str, BaseNode] = {}
    for n in nodes_def:
        node_id = n["id"]
        node_type = n["type"]
        params = n.get("params", {})

        node = registry.create_node(node_type, node_id=node_id, label=node_id)
        if node is None:
            raise WorkflowValidationError

        _set_params_to_node(node, params)
        engine.add_node(node)
        id_to_node[node_id] = node

    # 连接（推断端口）
    for frm, to in edges_def:
        src = id_to_node[frm]
        dst = id_to_node[to]
        out_port = _resolve_single_port(src, "output")
        in_port = _resolve_single_port(dst, "input")
        engine.connect_nodes(frm, out_port, to, in_port)

    return engine


def load_workflow_from_json(
    json_str: str, registry: NodeRegistry | None = None
) -> WorkflowEngine:
    """从 JSON 字符串加载工作流并构建引擎"""
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise WorkflowValidationError(f"JSON 解析失败: {e}") from e
    return build_engine_from_workflow(data, registry=registry)
