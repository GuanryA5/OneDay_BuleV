# GitHub Pages 配置指南

## 🎯 目标

为 BlueV 项目启用 GitHub Pages 自动文档部署，实现文档的自动构建和发布。

## 📋 配置步骤

### 1. 启用 GitHub Pages

1. **访问仓库设置**
   - 打开 https://github.com/GuanryA5/OneDay_BuleV
   - 点击 "Settings" 标签页

2. **配置 Pages 设置**
   - 在左侧菜单中找到 "Pages"
   - 在 "Source" 部分选择 **"GitHub Actions"**
   - 点击 "Save" 保存设置

### 2. 验证 Actions 权限

1. **检查 Actions 权限**
   - 在 Settings 中点击 "Actions" → "General"
   - 确保 "Actions permissions" 设置为：
     - ✅ "Allow all actions and reusable workflows"
     - 或 ✅ "Allow select actions and reusable workflows"

2. **检查 Workflow 权限**
   - 在 "Workflow permissions" 部分选择：
     - ✅ "Read and write permissions"
   - 勾选 ✅ "Allow GitHub Actions to create and approve pull requests"

### 3. 手动触发文档部署

如果自动部署没有触发，可以手动触发：

1. **访问 Actions 页面**
   - 打开 https://github.com/GuanryA5/OneDay_BuleV/actions

2. **手动触发工作流**
   - 找到 "Deploy Documentation" 工作流
   - 点击 "Run workflow" 按钮
   - 选择 "main" 分支
   - 点击绿色的 "Run workflow" 按钮

### 4. 验证部署状态

1. **检查工作流状态**
   - 在 Actions 页面查看工作流运行状态
   - 确保 "Deploy Documentation" 工作流成功完成

2. **访问文档网站**
   - 部署成功后，访问：https://guanrya5.github.io/OneDay_BuleV
   - 应该能看到 BlueV 项目文档

## 🔧 故障排除

### 问题 1: Actions 没有运行

**可能原因**:
- Actions 权限未正确配置
- 工作流文件语法错误
- 仓库设置问题

**解决方案**:
```bash
# 1. 检查工作流文件语法
cd .github/workflows
cat ci.yml | head -20
cat docs.yml | head -20

# 2. 手动触发 CI
git commit --allow-empty -m "ci: trigger GitHub Actions"
git push origin main
```

### 问题 2: 文档构建失败

**可能原因**:
- MkDocs 配置错误
- 依赖安装失败
- 文档文件路径问题

**解决方案**:
```bash
# 本地测试文档构建
pip install mkdocs mkdocs-material mkdocstrings[python]
mkdocs build --clean --strict

# 如果本地构建成功，检查 CI 日志
```

### 问题 3: Pages 部署失败

**可能原因**:
- Pages 权限未配置
- 部署工作流权限不足
- 构建产物路径错误

**解决方案**:
1. 确认 Pages 设置为 "GitHub Actions"
2. 检查 Workflow 权限设置
3. 查看部署工作流的详细日志

## 📊 预期结果

配置完成后，您应该看到：

### GitHub Actions 页面
- ✅ "CI" 工作流：代码质量检查和测试
- ✅ "Deploy Documentation" 工作流：文档构建和部署

### 文档网站
- 🌐 **URL**: https://guanrya5.github.io/OneDay_BuleV
- 📚 **内容**: BlueV 项目完整文档
- 🎨 **主题**: Material Design 现代化界面

### 自动化流程
- 📝 **代码推送** → 自动触发 CI 检查
- 📚 **文档更新** → 自动重新部署文档
- 🔄 **持续集成** → 多 Python 版本测试

## 🎉 成功标志

当看到以下内容时，说明配置成功：

1. **GitHub Actions 页面**显示绿色的 ✅ 状态
2. **文档网站**可以正常访问并显示内容
3. **自动化流程**在代码推送后自动运行

## 📞 需要帮助？

如果遇到问题：

1. **检查 Actions 日志**：查看详细的错误信息
2. **本地测试**：运行 `mkdocs serve` 测试文档
3. **验证配置**：确保所有设置步骤都已完成

---

**配置完成后，您的 BlueV 项目将拥有完全自动化的文档部署系统！** 🚀
