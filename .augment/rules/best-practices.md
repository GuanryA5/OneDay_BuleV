---
type: "always_apply"
---

# DevOps 最佳实践指南

## 🎯 核心原则

### 1. 自动化优先 (Automation First)
- **原则**: 能自动化的绝不手动
- **实践**: 使用 pre-commit hooks、CI/CD 流程
- **收益**: 减少人为错误，提高一致性

### 2. 快速反馈 (Fast Feedback)
- **原则**: 尽早发现问题，快速修复
- **实践**: 本地检查 + CI 验证
- **收益**: 降低修复成本，提高开发效率

### 3. 质量内建 (Quality Built-in)
- **原则**: 质量是开发过程的一部分，不是事后检查
- **实践**: 代码规范、测试驱动、持续集成
- **收益**: 减少技术债务，提高代码可维护性

## 📝 代码质量最佳实践

### 代码风格和格式化

#### ✅ 推荐做法

```python
# 使用 Ruff 自动格式化
# 配置在 pyproject.toml 中统一管理

# 好的函数命名和文档
def calculate_user_score(user_data: Dict[str, Any]) -> float:
    """
    计算用户评分

    Args:
        user_data: 用户数据字典

    Returns:
        用户评分 (0.0-100.0)

    Raises:
        ValueError: 当用户数据无效时
    """
    if not user_data:
        raise ValueError("用户数据不能为空")

    return min(100.0, user_data.get("score", 0.0))
```

#### ❌ 避免的做法

```python
# 不一致的代码风格
def calc_score(data):
    if data==None:return 0
    score=data['score'] if 'score' in data else 0
    return score if score<=100 else 100
```

### 错误处理

#### ✅ 推荐做法

```python
from bluev.utils.exceptions import BlueVException, BlueVValidationError

def process_user_input(input_data: str) -> Dict[str, Any]:
    """处理用户输入，使用项目标准异常"""
    try:
        if not input_data.strip():
            raise BlueVValidationError("输入数据不能为空")

        result = json.loads(input_data)
        return result

    except json.JSONDecodeError as e:
        raise BlueVValidationError(f"JSON 格式错误: {e}") from e
    except Exception as e:
        raise BlueVException(f"处理输入数据时发生错误: {e}") from e
```

#### ❌ 避免的做法

```python
def process_input(data):
    try:
        return json.loads(data)
    except:
        return {}  # 静默忽略错误
```

### 日志记录

#### ✅ 推荐做法

```python
from bluev.utils.logging import get_logger

logger = get_logger(__name__)

def important_operation(user_id: str) -> bool:
    """执行重要操作，记录详细日志"""
    logger.info("开始执行重要操作", user_id=user_id)

    try:
        # 执行操作
        result = perform_operation(user_id)

        logger.info(
            "操作执行成功",
            user_id=user_id,
            result=result,
            execution_time=0.123
        )
        return True

    except Exception as e:
        logger.error(
            "操作执行失败",
            user_id=user_id,
            error=str(e),
            exc_info=True
        )
        raise
```

## 🧪 测试最佳实践

### 测试结构

```
tests/
├── unit/           # 单元测试
│   ├── test_config.py
│   └── test_utils.py
├── integration/    # 集成测试
│   └── test_workflow.py
├── fixtures/       # 测试数据
│   └── sample_data.py
└── conftest.py     # pytest 配置
```

### 测试命名规范

#### ✅ 推荐做法

```python
class TestUserValidator:
    """用户验证器测试"""

    def test_validate_email_with_valid_format_should_return_true(self):
        """测试：有效邮箱格式应该返回 True"""
        validator = EmailValidator()
        result = validator.validate("user@example.com")
        assert result is True

    def test_validate_email_with_invalid_format_should_raise_error(self):
        """测试：无效邮箱格式应该抛出异常"""
        validator = EmailValidator()
        with pytest.raises(BlueVValidationError):
            validator.validate("invalid-email")
```

### 测试数据管理

#### ✅ 推荐做法

```python
# tests/fixtures/config_data.py
@pytest.fixture
def valid_config_data():
    """有效的配置数据"""
    return {
        "app_name": "BlueV",
        "debug": False,
        "log_level": "INFO"
    }

@pytest.fixture
def temp_config_file(tmp_path, valid_config_data):
    """临时配置文件"""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(valid_config_data))
    return config_file
```

## 🔄 Git 工作流最佳实践

### 分支策略

```
main                 # 生产环境，只接受 PR
├── develop          # 开发环境，集成分支
├── feature/xxx      # 功能开发分支
├── bugfix/xxx       # 问题修复分支
└── hotfix/xxx       # 紧急修复分支
```

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

#### ✅ 推荐格式

```bash
# 功能添加
feat: add user authentication system
feat(ui): implement node editor drag and drop

# 问题修复
fix: resolve memory leak in workflow engine
fix(config): handle missing configuration file

# 文档更新
docs: update API documentation
docs(readme): add installation instructions

# 重构
refactor: optimize database query performance
refactor(utils): simplify validation logic

# 测试
test: add unit tests for config module
test(integration): add workflow execution tests

# 构建和工具
build: update dependencies to latest versions
ci: add automated security scanning
```

#### ❌ 避免的格式

```bash
# 不清晰的提交信息
git commit -m "fix bug"
git commit -m "update code"
git commit -m "changes"
```

### Pull Request 最佳实践

#### PR 描述模板

```markdown
## 变更描述
简要描述本次变更的内容和目的

## 变更类型
- [ ] 功能添加 (feat)
- [ ] 问题修复 (fix)
- [ ] 文档更新 (docs)
- [ ] 代码重构 (refactor)
- [ ] 性能优化 (perf)
- [ ] 测试添加 (test)

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试完成

## 检查清单
- [ ] 代码符合项目规范
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 通过了所有 CI 检查

## 相关 Issue
Closes #123
```

## 🚀 CI/CD 最佳实践

### 流水线设计原则

1. **快速失败**: 最容易失败的检查放在前面
2. **并行执行**: 独立的检查并行运行
3. **缓存优化**: 合理使用缓存减少执行时间
4. **环境一致**: CI 环境尽量接近生产环境

### 流水线阶段

```yaml
# 推荐的流水线阶段顺序
stages:
  1. 代码检查 (Linting)     # 最快，最容易失败
  2. 单元测试 (Unit Tests)  # 快速反馈
  3. 集成测试 (Integration) # 较慢但重要
  4. 安全扫描 (Security)    # 并行执行
  5. 构建打包 (Build)       # 准备部署
  6. 部署 (Deploy)          # 最后阶段
```

### 环境管理

#### ✅ 推荐做法

```yaml
# 使用环境变量管理配置
env:
  PYTHON_VERSION: "3.8"
  NODE_VERSION: "18"
  CACHE_VERSION: "v1"

# 使用矩阵测试多个环境
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: [3.8, 3.9, "3.10"]
```

## 📊 监控和度量

### 关键指标 (KPIs)

| 指标类别 | 具体指标 | 目标值 | 监控方式 |
|----------|----------|--------|----------|
| **代码质量** | 测试覆盖率 | > 80% | Codecov |
| **代码质量** | 代码重复率 | < 5% | SonarQube |
| **性能** | CI 执行时间 | < 5分钟 | GitHub Actions |
| **性能** | Pre-commit 时间 | < 30秒 | 本地监控 |
| **可靠性** | 构建成功率 | > 95% | CI 统计 |
| **安全** | 安全漏洞数 | 0 | Trufflehog |

### 性能基准

定期运行性能基准测试：

```bash
# 每周运行性能基准测试
python scripts/performance_benchmark.py

# 记录关键指标
echo "$(date): $(python -c 'import time; print(time.time())')" >> performance.log
```

## 🔒 安全最佳实践

### 密钥管理

#### ✅ 推荐做法

```python
# 使用环境变量
import os
from bluev.config import Config

config = Config()
api_key = config.get_env("API_KEY")  # 从环境变量获取

# 使用 GitHub Secrets
# 在 GitHub Actions 中配置敏感信息
```

#### ❌ 避免的做法

```python
# 硬编码密钥
API_KEY = "sk-1234567890abcdef"  # 绝对不要这样做

# 提交包含密钥的文件
config.json  # 包含真实密钥的配置文件
```

### 依赖安全

```bash
# 定期检查依赖漏洞
pip audit

# 使用 Dependabot 自动更新依赖
# 在 .github/dependabot.yml 中配置

# 锁定依赖版本
pip freeze > requirements.txt
```

## 📚 文档最佳实践

### 文档结构

```
docs/
├── index.md              # 项目首页
├── getting-started/      # 快速开始
├── user-guide/          # 用户指南
├── development/         # 开发文档
├── api/                 # API 参考
└── examples/            # 示例代码
```

### 文档写作原则

1. **用户导向**: 从用户角度组织内容
2. **循序渐进**: 从简单到复杂
3. **实例丰富**: 提供充足的代码示例
4. **及时更新**: 代码变更时同步更新文档

### 代码文档

#### ✅ 推荐做法

```python
def process_workflow(
    workflow_data: Dict[str, Any],
    execution_context: Optional[Dict] = None
) -> WorkflowResult:
    """
    处理工作流执行

    这个函数是工作流引擎的核心，负责解析工作流定义并执行相应的节点。

    Args:
        workflow_data: 工作流定义数据，包含节点和连接信息
        execution_context: 可选的执行上下文，用于传递运行时参数

    Returns:
        WorkflowResult: 包含执行结果和状态信息的对象

    Raises:
        WorkflowValidationError: 当工作流定义无效时
        WorkflowExecutionError: 当执行过程中发生错误时

    Example:
        >>> workflow_data = {"nodes": [...], "connections": [...]}
        >>> result = process_workflow(workflow_data)
        >>> print(result.status)  # "completed"

    Note:
        执行过程中会自动保存检查点，支持断点续传
    """
```

## 🎓 团队协作最佳实践

### 代码审查

#### 审查清单

- [ ] **功能正确性**: 代码是否实现了预期功能
- [ ] **代码质量**: 是否符合项目规范和最佳实践
- [ ] **测试覆盖**: 是否有足够的测试覆盖
- [ ] **性能影响**: 是否会影响系统性能
- [ ] **安全考虑**: 是否存在安全风险
- [ ] **文档更新**: 是否更新了相关文档

#### 审查态度

- **建设性**: 提供具体的改进建议
- **尊重**: 尊重作者的努力和想法
- **学习**: 从他人代码中学习新的技巧
- **及时**: 尽快完成审查，不阻塞开发进度

### 知识分享

1. **技术分享会**: 定期分享新技术和最佳实践
2. **代码走读**: 对复杂模块进行集体代码走读
3. **文档维护**: 共同维护项目文档和知识库
4. **问题讨论**: 在 GitHub Discussions 中讨论技术问题

---

## 📈 持续改进

### 定期回顾

- **每周**: 检查 CI/CD 性能指标
- **每月**: 回顾代码质量趋势
- **每季度**: 评估工具链效果，考虑优化

### 工具升级

- **关注新版本**: 定期检查工具的新版本
- **评估收益**: 评估升级带来的收益和风险
- **渐进升级**: 采用渐进式升级策略

记住：**最佳实践不是一成不变的，要根据项目实际情况灵活调整！**
