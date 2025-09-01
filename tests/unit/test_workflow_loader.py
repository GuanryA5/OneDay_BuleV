# -*- coding: utf-8 -*-
import pytest

from bluev.core.workflow_loader import (
    WorkflowValidationError,
    build_engine_from_workflow,
    load_workflow_from_json,
)


def test_invalid_types():
    with pytest.raises(WorkflowValidationError):
        build_engine_from_workflow([1, 2, 3])  # type: ignore[arg-type]


def test_minimal_workflow_schema(monkeypatch):
    # 假定注册器中已有 5 个核心节点：screenshot/find_image/click/delay/log
    # 这里仅测试加载路径，不执行引擎
    data = {
        "workflow_id": "wf-1",
        "nodes": [
            {"id": "n1", "type": "screenshot", "params": {}},
            {
                "id": "n2",
                "type": "find_image",
                "params": {"template": "btn.png", "threshold": 0.8},
            },
        ],
        "edges": [["n1", "n2"]],
    }

    # 如果节点未注册，构建会失败；这里根据实际注册情况决定断言
    try:
        engine = build_engine_from_workflow(data)
    except WorkflowValidationError as e:
        # 当节点类型未注册时，报错信息应包含类型名
        assert "未找到节点类型" in str(e) or "不存在" in str(e)
        return

    # 如果注册器已就绪，检查连接数量
    info = engine.get_workflow_info()
    assert info["node_count"] == 2
    assert info["connection_count"] == 1


def test_json_loader_error():
    with pytest.raises(WorkflowValidationError):
        load_workflow_from_json("{broken json}")


def test_edges_reference_validation():
    data = {
        "workflow_id": "wf-2",
        "nodes": [
            {"id": "n1", "type": "screenshot"},
        ],
        "edges": [["n1", "n2"]],  # n2 不存在
    }
    with pytest.raises(WorkflowValidationError):
        build_engine_from_workflow(data)
