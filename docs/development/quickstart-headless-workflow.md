# Quick Start：无 UI 跑通一个完整工作流

本教程将带你在**无 UI**场景下，使用“工作流加载器 + 工作流引擎”快速跑通一个最小可执行工作流。适用于 Windows 11 + Git Bash + Conda (bluev-dev)。

## 前置条件
- 已完成环境准备（参考“Windows 环境设置”）
- 建议先阅读“无 UI 工作流与加载器”文档，了解最小 JSON 结构

## 示例 A：最小可运行工作流（Delay → Log）
该示例不依赖图像资源，容易在任意环境直接运行。

```python
import asyncio
from bluev.core.workflow_loader import build_engine_from_workflow
from bluev.core.execution_context import ExecutionContext

# 1) 定义最小工作流（无边或简单顺序均可）
workflow_dict = {
    "workflow_id": "wf-quick-start",
    "nodes": [
        {"id": "n1", "type": "delay", "params": {"ms": 200}},
        {"id": "n2", "type": "log", "params": {"message": "Hello, BlueV!"}},
    ],
    "edges": [["n1", "n2"]]
}

# 2) 构建引擎
engine = build_engine_from_workflow(workflow_dict)

# 3) 执行工作流
async def main():
    ctx = ExecutionContext(workflow_id="wf-quick-start", timeout_seconds=10)
    # 可选：订阅回调，观察执行过程
    async def on_event(**kwargs):
        print("[EVENT]", kwargs)
    for evt in ("workflow_start","node_start","node_complete","node_end","workflow_complete","workflow_end","workflow_error","node_error"):
        ctx.on(evt, on_event)  # 如果 ExecutionContext 暴露了 on() 辅助方法

    results = await engine.execute_workflow(ctx)
    print("Results:", results)

asyncio.run(main())
```

说明：
- Delay 节点提供基本等待；Log 节点输出一条消息
- 当前版本端口推断规则为“单入/单出自动连线”，如出现“端口不唯一”提示，请改为无边运行单节点或等待后续版本支持显式端口

## 示例 B：视觉链路工作流（Screenshot → FindImage → Click → Delay → Log）
该示例需要准备模板图（例如 `btn.png`），并确保点击操作在当前系统允许的前台窗口中执行。

```python
import asyncio, json
from bluev.core.workflow_loader import load_workflow_from_json
from bluev.core.execution_context import ExecutionContext

json_text = json.dumps({
    "workflow_id": "wf-vision",
    "nodes": [
        {"id": "n1", "type": "screenshot", "params": {}},
        {"id": "n2", "type": "find_image", "params": {"template": "btn.png", "threshold": 0.85}},
        {"id": "n3", "type": "click", "params": {"offset": [0, 0]}},
        {"id": "n4", "type": "delay", "params": {"ms": 300}},
        {"id": "n5", "type": "log", "params": {"message": "clicked"}},
    ],
    "edges": [["n1","n2"],["n2","n3"],["n3","n4"],["n4","n5"]]
})

engine = load_workflow_from_json(json_text)

async def main():
    ctx = ExecutionContext(workflow_id="wf-vision", timeout_seconds=30)
    results = await engine.execute_workflow(ctx)
    print("Results:", results)

asyncio.run(main())
```

注意：
- 需要在工作目录放置 `btn.png` 模板图
- 在某些显示缩放（DPI 125%）或多显示器环境下，坐标可能需要换算；后续版本将提供统一的 DPI 处理策略

## 运行方式（Windows + Git Bash）
```bash
conda activate bluev-dev
python quickstart_headless.py   # 将上述示例保存为该文件名
```

或直接交互测试：
```bash
python -c "import asyncio; from bluev.core.workflow_loader import build_engine_from_workflow; from bluev.core.execution_context import ExecutionContext; wf={'workflow_id':'wf','nodes':[{'id':'n1','type':'delay','params':{'ms':200}},{'id':'n2','type':'log','params':{'message':'hi'}}],'edges':[['n1','n2']]}; import sys; async def main():\n ctx=ExecutionContext(workflow_id='wf');\n eng=build_engine_from_workflow(wf);\n print(await eng.execute_workflow(ctx));\n asyncio.run(main())"  # 行内演示（可读性较差）
```

## 常见问题
- 报错“未找到节点类型”：说明节点尚未注册或命名不一致；请确认你正在使用内置 5 节点（delay/log/screenshot/find_image/click）
- 报错“端口不唯一”：当前版本只在“单入/单出”时推断端口，暂不支持多端口自动推断
- Windows 下点击无效：请确认有前台焦点与必要权限，尝试以管理员启动终端

## 进阶与下一步
- 阅读“无 UI 工作流与加载器”，理解 `WorkflowValidationError` 的触发条件与修复方式
- 将本 Quick Start 的工作流保存为 JSON，后续 UI 节点编辑器将直接输出类似结构
- 扩展工作流：添加更多节点（如循环/变量/更多 CV 节点）并增加测试
