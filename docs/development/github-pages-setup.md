# GitHub Pages 设置指南

## 🎯 概述

本文档说明如何为 BlueV 项目启用 GitHub Pages 自动部署功能。

## 📋 前置条件

- 项目已推送到 GitHub 仓库
- 拥有仓库的管理员权限
- CI/CD 工作流已正确配置

## 🔧 启用步骤

### 1. 访问仓库设置

1. 打开 GitHub 仓库页面
2. 点击 **Settings** 标签页
3. 在左侧菜单中找到 **Pages** 选项

### 2. 配置 Pages 源

1. 在 **Source** 部分选择 **GitHub Actions**
2. 这将允许通过 Actions 工作流部署页面

### 3. 启用文档自动部署

编辑 `.github/workflows/docs.yml` 文件，取消注释部署相关的步骤：

```yaml
# 取消注释这些行
- name: Setup Pages
  uses: actions/configure-pages@v4

- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: ./site

# 取消注释整个 deploy 作业
deploy:
  environment:
    name: github-pages
    url: ${{ steps.deployment.outputs.page_url }}
  runs-on: ubuntu-latest
  needs: build
  steps:
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v4
```

### 4. 验证部署

1. 推送更改到 `main` 分支
2. 检查 Actions 标签页中的工作流运行状态
3. 部署成功后，文档将在以下地址可用：
   ```
   https://[username].github.io/OneDay_BuleV/
   ```

## 🚨 常见问题

### 问题：部署失败，提示 "Cannot find any run"

**原因**: GitHub Pages 功能未启用

**解决方案**:
1. 确保在仓库设置中启用了 Pages
2. 选择 "GitHub Actions" 作为源
3. 重新运行工作流

### 问题：权限错误

**原因**: Actions 没有足够的权限

**解决方案**:
1. 在仓库设置 → Actions → General 中
2. 确保 "Workflow permissions" 设置为 "Read and write permissions"
3. 勾选 "Allow GitHub Actions to create and approve pull requests"

## 📚 相关资源

- [GitHub Pages 官方文档](https://docs.github.com/en/pages)
- [GitHub Actions 部署到 Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow)
- [MkDocs 部署指南](https://www.mkdocs.org/user-guide/deploying-your-docs/)

## 🔄 自动化流程

启用后，文档将在以下情况自动更新：

1. **推送到 main 分支** 且修改了文档相关文件
2. **CI 工作流成功完成** 后自动触发
3. **手动触发** (workflow_dispatch)

文档构建包含：
- API 文档自动生成
- Markdown 文件处理
- 静态资源优化
- 搜索索引构建
