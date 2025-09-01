# 无 UI 工作流与加载器（最小闭环）

本页介绍如何使用内置“工作流加载器”在无 UI 场景下构建并运行最小工作流，为后续 UI 节点编辑器打下基础。

适用环境：Windows 11 + Git Bash + Conda (bluev-dev)

## 功能概览
- 校验最小工作流定义（workflow_id/nodes/edges）
- 通过 NodeRegistry 创建节点并注入 params（按节点输入规范过滤）
- 在“单入/单出”规则下自动推断连接端口并连线（多端口暂不自动推断）
- 构建 WorkflowEngine 实例，准备执行

对应实现：`bluev/core/workflow_loader.py`

## 最小工作流 JSON 结构（示例）
```json
{
  "workflow_id": "wf-hello",
  "nodes": [
    {"id": "n1", "type": "screenshot", "params": {}},
    {"id": "n2", "type": "find_image", "params": {"template": "btn.png", "threshold": 0.85}},
    {"id": "n3", "type": "click", "params": {"offset": [0, 0]}},
    {"id": "n4", "type": "delay", "params": {"ms": 500}},
    {"id": "n5", "type": "log", "params": {"message": "done"}}
  ],
  "edges": [["n1","n2"], ["n2","n3"], ["n3","n4"], ["n4","n5"]]
}
```

说明：
- `nodes[].type` 必须是已注册的节点类型（如 screenshot/find_image/click/delay/log）
- `params` 中的键会按节点输入规范过滤并写入，最终由 `validate_inputs()` 统一校验
- `edges` 使用最小格式 `[from_id, to_id]`，当前版本在“单入/单出”情况下自动推断端口名

## Python 使用示例
```python
from bluev.core.workflow_loader import load_workflow_from_json, build_engine_from_workflow
from bluev.core.workflow_engine import WorkflowEngine
from bluev.core.execution_context import ExecutionContext

# 1) 从 JSON 字符串加载
engine: WorkflowEngine = load_workflow_from_json(json_text)

# 2) 或使用 Python dict 定义并构建
engine: WorkflowEngine = build_engine_from_workflow(workflow_dict)

# 3) 准备执行（示意）
ctx = ExecutionContext(workflow_id="wf-hello", timeout_seconds=60)
# 注册回调（可选）
# await engine.execute_workflow(ctx)
```

注意：示例仅展示构建流程；执行需要实际的节点实现与资源（如模板图 btn.png）。

## 常见错误与修复建议
加载器会抛出 `WorkflowValidationError`，常见信息与处理：

- “工作流数据必须为对象/数组”：传入的顶层或字段类型不符合要求；请传入 dict/JSON 对象
- “字段 'workflow_id' 必须为非空字符串”：请提供字符串 ID
- “重复的节点ID: …”：确保 `nodes[].id` 全局唯一
- “edges[i]: 源/目标节点不存在 …”：确保边引用的节点在 `nodes[]` 内已定义
- “未找到节点类型: …”：该 `nodes[].type` 尚未注册（请确认节点注册或更换已有类型）
- “节点 X 输入/输出端口不唯一，需显式指定端口名”：
  - 当前版本仅在“单入/单出”时自动推断端口
  - 若出现该错误，说明目标/源节点存在多个输入/输出端口，需在未来的工作流定义中提供端口名（后续版本将支持扩展格式）

## 验证与自测
- 仅运行加载器相关用例：
```bash
conda activate bluev-dev
pytest tests/unit/test_workflow_loader.py -q
```
- 常见通过标准：
  - JSON 解析错误用例抛出 `WorkflowValidationError`
  - 边引用不存在节点时抛出 `WorkflowValidationError`
  - 注册器已具备必要节点时，可成功构建引擎且 `connection_count` 正确

## 与后续 UI 的关系
- UI 节点编辑器完成后，前端将生成 JSON/或通过 API 传入 dict
- 加载器负责把定义“落地”为可执行的引擎 + 节点实例
- 多端口/复杂依赖将在下一版本扩展（如显式 `from_output/to_input`）

## 下一步
- 提供“Quick Start：无 UI 跑通一个工作流”的完整示例
- 扩展加载器以支持显式端口名与更复杂的依赖关系
