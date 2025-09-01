# 2周执行计划：Engine-first 最小闭环（/p）
- 版本/日期: v1.0 / 2025-09-01
- 范围: BaseNode/Registry/Engine 稳定化；工作流加载器；5核心节点；无UI集成演示；测试与文档
- 环境: Windows 11 + Git Bash + Conda (bluev-dev)

## 1) Mission（任务定义）
在 2 周内交付“可运行、可测试、可演示”的无 UI 最小闭环：
- 能加载 JSON/代码定义的工作流
- 执行 5 个核心节点（截图/找图/点击/延迟/日志）
- CI 全绿（ruff/mypy/pytest/mkdocs）
- 提供 Quick Start 文档与示例

## 2) Chunking（任务分解，10–20 分钟粒度）
说明: 每个任务都给出 DoD 与测试映射（与 docs/05-review/engine-first-QA-checklist.md 一致）

A. 接口与契约收敛
- T1: 审阅 BaseNode/Registry/Engine 现有接口（10m）
  - DoD: 差异点清单/备注；对齐接口规范文档
  - Test: 无（文档走查）
- T2: 为 BaseNode 填充/校正 docstring/类型注解（15m）
  - DoD: mypy 通过；ruff 通过；docstring 完整
  - Test: mypy/ruff
- T3: 为 NodeRegistry 增补契约注释与边界检查（15m）
  - DoD: 非法注册/重复注册/非子类注册均抛出明确异常
  - Test: 单测覆盖三类异常
- T4: 为 WorkflowEngine 明确错误模型与日志（20m）
  - DoD: CircularDependencyError/WorkflowExecutionError 统一；日志含 node_id
  - Test: 单测验证异常路径

B. 工作流定义与加载器
- T5: 设计最小 JSON Schema 与 params→inputs 映射（15m）
  - DoD: JSON 样例 + 校验规则说明落文档
  - Test: 单测用样例 JSON
- T6: 实现加载器（校验节点/边/必填与默认值）（20m）
  - DoD: 无 UI 下可加载并构建 engine
  - Test: 单测（合法/缺节点/错边/缺参数）
- T7: 代码版工作流（Python dict）加载入口（10m）
  - DoD: 与 JSON 同等校验
  - Test: 单测覆盖

C. 5 节点验收（最小实现/完善）
- T8: ScreenshotNode 校对 inputs/outputs，支持 region（15m）
  - DoD: region=None/区域两种均可；错误信息清晰
  - Test: 单测（mock 截图/返回尺寸）
- T9: FindImageNode 阈值与返回结构（20m）
  - DoD: found/bbox/score 三要素；image 为空时内部截图
  - Test: 单测（模板命中/不命中/异常模板路径）
- T10: ClickNode 点中心与偏移（15m）
  - DoD: bbox 优先；point 备选；offset 生效；左/右键可选
  - Test: 单测（用后端mock，不触发真实点击）
- T11: DelayNode 简化实现（10m）
  - DoD: 精准等待；返回 delayed=True
  - Test: 单测（时间断言容忍度）
- T12: LogNode 结构化日志（10m）
  - DoD: level/message 生效；输出记录到 logger
  - Test: 单测（捕获日志）

D. 集成执行闭环
- T13: 构建示例工作流（顺序 5 节点）（15m）
  - DoD: 本地可运行；日志完整
  - Test: 手动 + 集成测试样例
- T14: Engine 执行路径异常处理检查（15m）
  - DoD: 任一节点失败能抛 WorkflowExecutionError 并记录 node_id
  - Test: 集成测试（故意让 FindImage 失败）
- T15: 执行上下文回调与指标（20m）
  - DoD: workflow_start/node_start/node_end/node_error/workflow_end 均可触发；metrics 记录节点耗时
  - Test: 集成测试（回调被调用断言）

E. 单元测试（core+nodes）
- T16: BaseNode/Registry/Engine 单测基础（20m）
  - DoD: 关键分支覆盖；异常路径覆盖
  - Test: pytest
- T17: 5 节点单测（20m）
  - DoD: 正常/异常/边界；mock 外部依赖
  - Test: pytest
- T18: 覆盖率门槛配置（10m）
  - DoD: 覆盖率≥80%（核心模块）
  - Test: --cov 报告 ≥80%

F. 集成测试与 CI
- T19: 无 UI 集成测试（20m）
  - DoD: 最小工作流在 CI Windows 通过
  - Test: GitHub Actions 成功
- T20: CI Gate：ruff/mypy/pytest/mkdocs（15m）
  - DoD: 工作流加入 gates；失败阻断
  - Test: 触发一次 CI

G. 文档与示例
- T21: Quick Start：无 UI 运行一个工作流（15m）
  - DoD: 新人10分钟可跑通
  - Test: 走查 + 本地验证
- T22: 节点规范文档（5 节点一页速查）（20m）
  - DoD: 输入/输出/示例齐全
  - Test: MkDocs 构建通过
- T23: 故障排查附录（10m）
  - DoD: 常见错误与修复（模板路径/DPI/权限）
  - Test: MkDocs 构建通过

H. 收尾
- T24: QA 清单逐项标记与结项（15m）
  - DoD: docs/05-review/engine-first-QA-checklist.md 更新为 PASSED（如满足）
  - Test: 文档更新

## 3) Pathfinding（严格线性执行序列）
顺序（→ 表示依赖）：
1) T1 → T2 → T3 → T4
2) T5 → T6 → T7
3) T8 → T9 → T10 → T11 → T12
4) (1)&(2)&(3) → T13 → T14 → T15
5) T16 → T17 → T18
6) (4)&(5) → T19 → T20
7) T21 → T22 → T23 → T24

## 4) 工期与配速（2周）
- Week 1: A/B/C（接口/加载器/节点），力争到 T13
- Week 2: D/E/F/G/H（集成/测试/CI/文档/收尾）

## 5) DoD 总表（与 QA 清单对齐）
- 接口与契约：mypy/ruff 通过，注释齐全
- 加载器：合法/非法路径单测齐全
- 5 节点：参数校验、失败可诊断
- 集成闭环：最小工作流跑通
- 覆盖率：≥80%（core/nodes）
- CI：全绿（含文档构建）
- 文档：Quick Start + 节点规范 + 故障排查

## 6) 运行命令速查（Windows + Git Bash）
```bash
# 激活环境
conda activate bluev-dev

# 质量门槛
ruff check . && ruff format --check .
mypy bluev/

# 测试
pytest -q --maxfail=1 --disable-warnings
pytest --cov=bluev --cov-report=term-missing

# 文档
mkdocs build
```
