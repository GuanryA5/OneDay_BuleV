# 接口规范：Engine-first 最小闭环
- **日期:** 2025-09-01
- **适用范围:** BaseNode/NodeRegistry/WorkflowEngine/ExecutionContext/Workflow JSON/5 核心节点

## 1. 基础类型
- NodeState: READY | RUNNING | SUCCESS | FAILED | SKIPPED | CANCELLED
- 结构化类型：NodeInput / NodeOutput / NodeMetadata

## 2. BaseNode 契约
- 方法：get_input_spec(), get_output_spec(), get_metadata(), async execute(context)
- 行为：输入校验、默认值填充、状态迁移、错误记录、输出返回

## 3. NodeRegistry 与装饰器
- 注册器能力：register_node/get_node_class/create_node/list_node_types/list_by_category
- 装饰器：@bluev_node(node_type, label, category, description, version, tags)

## 4. ExecutionContext 契约
- 控制：start_execution/finish_execution/pause/resume/cancel/check_timeout
- 回调：workflow_start/node_start/node_end/node_error/workflow_end（协程）
- 指标：record_node_execution(node_id, success, **metrics)

## 5. WorkflowEngine 契约
- 关键方法：add_node/add_edge/topological_sort/execute_workflow
- 错误模型：CircularDependencyError/WorkflowExecutionError
- 返回：以 node_id 为 key 的输出汇总（或记录在 Context 内）

## 6. 工作流 JSON（最小）
```json
{
  "workflow_id": "string",
  "timeout": 60.0,
  "nodes": [
    {"id": "n1", "type": "screenshot", "params": {"region": null}},
    {"id": "n2", "type": "find_image", "params": {"template": "btn.png", "threshold": 0.85}},
    {"id": "n3", "type": "click", "params": {"offset": [0, 0]}},
    {"id": "n4", "type": "delay", "params": {"ms": 500}},
    {"id": "n5", "type": "log", "params": {"message": "done"}}
  ],
  "edges": [["n1","n2"], ["n2","n3"], ["n3","n4"], ["n4","n5"]]
}
```

## 7. 核心节点 I/O 规范
- ScreenshotNode
  - in: region?: [x,y,w,h]; out: image(ndarray)
- FindImageNode
  - in: image?(ndarray), template(str path), threshold(float=0.85), method(str)
  - out: found(bool), bbox?[x,y,w,h], score(float)
- ClickNode
  - in: bbox?[x,y,w,h], point?[x,y], offset=[0,0], button="left"; out: clicked(bool)
- DelayNode
  - in: ms(int); out: delayed(True)
- LogNode
  - in: message(str), level(str="INFO"); out: logged(True)

## 8. 测试点映射（对齐 QA 清单）
- mypy/ruff 通过；错误路径与异常信息明确
- 工作流加载器：节点/边引用校验、参数默认值与必填校验
- 核心节点：正常/异常/边界值
- 集成执行：最小工作流在 CI Windows 通过
