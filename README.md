# BlueV 游戏自动化蓝图框架

一个基于 PySide6 的可视化游戏自动化工具，让用户通过拖拽节点的方式创建复杂的游戏自动化工作流程。

## 🎯 项目特色

- **零编程门槛**: 完全可视化的节点编辑器，模仿虚幻引擎蓝图系统
- **智能视觉识别**: 基于OpenCV的专业级图像处理和游戏界面识别
- **跨游戏兼容**: 通用的视觉识别框架，适应不同游戏界面
- **开源生态**: 社区驱动的开发模式和模板分享平台

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- Windows 10/11 (主要支持平台)

### 安装步骤

1. **克隆项目**
   ```cmd
   git clone https://github.com/GuanryA5/OneDay_BuleV.git
   cd OneDay_BuleV
   ```

2. **快速设置（推荐）**
   ```cmd
   scripts\windows_setup.bat
   ```

   或者手动设置：

3. **创建虚拟环境**
   ```cmd
   python -m venv venv
   venv\Scripts\activate.bat
   ```

4. **安装依赖**
   ```cmd
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. **安装开发工具**
   ```cmd
   pre-commit install
   ```

5. **运行应用**
   ```bash
   py -m bluev.main
   ```

## 🏗️ 项目结构

```
BlueV/
├── bluev/                  # 主应用包
│   ├── ui/                # 用户界面层
│   ├── core/              # 核心业务逻辑层
│   ├── vision/            # 计算机视觉层
│   ├── actions/           # 操作执行层
│   ├── data/              # 数据管理层
│   └── utils/             # 工具模块
├── tests/                 # 测试代码
├── docs/                  # 项目文档
├── resources/             # 资源文件
├── memory-bank/           # 项目记忆库
└── scripts/               # 项目脚本
```

## 🧪 运行测试

```bash
# 激活虚拟环境
venv\Scripts\activate.bat

# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/unit/test_config.py -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=bluev --cov-report=html
```

## 🛠️ 开发工具

项目配置了完整的开发工具链：

- **代码格式化**: black
- **代码检查**: flake8
- **类型检查**: mypy
- **测试框架**: pytest
- **文档生成**: sphinx

```bash
# 代码格式化
black bluev/

# 代码检查
flake8 bluev/

# 类型检查
mypy bluev/
```

## 📖 技术栈

- **UI框架**: PySide6 (Qt6)
- **图像处理**: OpenCV + NumPy + Pillow
- **自动化操作**: PyAutoGUI + pynput
- **数据存储**: SQLAlchemy + SQLite
- **配置管理**: python-dotenv + pydantic
- **日志系统**: loguru

## 🎮 使用场景

- 游戏日常任务自动化
- 重复性操作的批量处理
- 游戏资源采集自动化
- 副本刷取自动化
- 界面交互自动化

## 📚 项目文档

### 开发文档
- [DevOps 实施计划](docs/devops-implementation-plan.md) - 详细的工具链实施计划
- [DevOps 执行清单](docs/devops-checklist.md) - 快速执行指南和检查点
- [项目状态跟踪](docs/project-status.md) - 实时项目进度和质量指标

### 技术文档
- [项目架构设计](docs/architecture.md) - 系统架构和设计原则
- [开发指南](docs/development.md) - 开发环境和编码规范
- [API 参考文档](docs/api.md) - 接口文档和使用示例

## 📝 开发状态

当前版本: **v0.1.0 (MVP开发中)**

### 已完成 ✅
- 项目基础架构和环境初始化
- 核心配置管理和日志系统
- 异常处理和验证框架
- 代码质量工具链 (85%+ 测试覆盖率)
- DevOps 工具链方案设计

### 进行中 ⏳
- DevOps 工具链实施 (Pre-commit + CI/CD + 文档)
- 节点编辑器设计
- 工作流引擎架构

### 计划中 📋
- 图像识别系统
- 自动化操作引擎
- 用户界面完善

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 讨论交流: [GitHub Discussions]

---

**⚠️ 免责声明**: 本工具仅用于学习和研究目的，请遵守相关游戏的使用条款和法律法规。
