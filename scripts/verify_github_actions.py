#!/usr/bin/env python3
"""
GitHub Actions 验证脚本
检查 CI/CD 和文档部署状态
"""

import sys
from typing import Dict, List

import requests


class GitHubActionsVerifier:
    """GitHub Actions 验证器"""

    def __init__(self, repo_owner: str = "GuanryA5", repo_name: str = "OneDay_BuleV"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_base = f"https://api.github.com/repos/{repo_owner}/{repo_name}"

    def check_actions_status(self) -> Dict:
        """检查 GitHub Actions 状态"""
        print("🔍 检查 GitHub Actions 状态...")

        try:
            # 获取最近的工作流运行
            url = f"{self.api_base}/actions/runs"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                runs = data.get("workflow_runs", [])

                if runs:
                    latest_run = runs[0]
                    print(f"  ✅ 找到 {len(runs)} 个工作流运行")
                    print(f"  📊 最新运行: {latest_run['name']}")
                    print(f"  📅 运行时间: {latest_run['created_at']}")
                    print(
                        f"  🎯 状态: {latest_run['status']} - {latest_run['conclusion']}"
                    )

                    return {
                        "success": True,
                        "runs_count": len(runs),
                        "latest_status": latest_run["status"],
                        "latest_conclusion": latest_run["conclusion"],
                    }
                else:
                    print("  ⚠️  没有找到工作流运行")
                    return {"success": False, "reason": "no_runs"}
            else:
                print(f"  ❌ API 请求失败: {response.status_code}")
                return {"success": False, "reason": "api_error"}

        except Exception as e:
            print(f"  ❌ 检查失败: {e}")
            return {"success": False, "reason": str(e)}

    def check_pages_status(self) -> Dict:
        """检查 GitHub Pages 状态"""
        print("🔍 检查 GitHub Pages 状态...")

        try:
            # 检查 Pages 配置
            url = f"{self.api_base}/pages"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print("  ✅ Pages 已配置")
                print(f"  🌐 URL: {data.get('html_url', 'N/A')}")
                print(f"  📦 源: {data.get('source', {}).get('branch', 'N/A')}")

                # 尝试访问文档网站
                docs_url = (
                    f"https://{self.repo_owner.lower()}.github.io/{self.repo_name}"
                )
                try:
                    docs_response = requests.get(docs_url, timeout=10)
                    if docs_response.status_code == 200:
                        print(f"  ✅ 文档网站可访问: {docs_url}")
                        return {"success": True, "url": docs_url, "accessible": True}
                    else:
                        print(
                            f"  ⚠️  文档网站返回 {docs_response.status_code}: {docs_url}"
                        )
                        return {"success": True, "url": docs_url, "accessible": False}
                except requests.RequestException:
                    print(f"  ⚠️  文档网站暂时无法访问: {docs_url}")
                    return {"success": True, "url": docs_url, "accessible": False}

            elif response.status_code == 404:
                print("  ❌ GitHub Pages 未配置")
                return {"success": False, "reason": "not_configured"}
            else:
                print(f"  ❌ Pages API 请求失败: {response.status_code}")
                return {"success": False, "reason": "api_error"}

        except Exception as e:
            print(f"  ❌ 检查失败: {e}")
            return {"success": False, "reason": str(e)}

    def get_workflow_recommendations(
        self, actions_status: Dict, pages_status: Dict
    ) -> List[str]:
        """获取修复建议"""
        recommendations = []

        if not actions_status["success"]:
            if actions_status.get("reason") == "no_runs":
                recommendations.extend(
                    [
                        "🔧 GitHub Actions 没有运行，建议:",
                        "   1. 检查 .github/workflows/ 目录下的工作流文件",
                        "   2. 确保仓库设置中启用了 Actions",
                        "   3. 创建一个提交来触发工作流",
                        "   4. 手动触发工作流: Actions → Run workflow",
                    ]
                )
            else:
                recommendations.extend(
                    [
                        "🔧 GitHub Actions 访问失败，建议:",
                        "   1. 检查网络连接",
                        "   2. 确认仓库是公开的或有适当权限",
                        "   3. 稍后重试",
                    ]
                )

        if not pages_status["success"]:
            if pages_status.get("reason") == "not_configured":
                recommendations.extend(
                    [
                        "🔧 GitHub Pages 未配置，建议:",
                        "   1. 进入仓库 Settings → Pages",
                        "   2. 在 Source 中选择 'GitHub Actions'",
                        "   3. 保存设置并等待部署",
                    ]
                )
            else:
                recommendations.extend(
                    [
                        "🔧 GitHub Pages 检查失败，建议:",
                        "   1. 检查仓库设置中的 Pages 配置",
                        "   2. 确认工作流权限设置正确",
                        "   3. 查看 Actions 中的部署日志",
                    ]
                )

        if pages_status.get("success") and not pages_status.get("accessible"):
            recommendations.extend(
                [
                    "🔧 文档网站无法访问，建议:",
                    "   1. 等待几分钟让部署完成",
                    "   2. 检查 Actions 中的 'Deploy Documentation' 工作流",
                    "   3. 确认 mkdocs.yml 配置正确",
                ]
            )

        return recommendations

    def run_verification(self) -> bool:
        """运行完整验证"""
        print("🚀 开始验证 GitHub Actions 和 Pages 状态...\n")

        # 检查 Actions 状态
        actions_status = self.check_actions_status()
        print()

        # 检查 Pages 状态
        pages_status = self.check_pages_status()
        print()

        # 生成建议
        recommendations = self.get_workflow_recommendations(
            actions_status, pages_status
        )

        # 打印总结
        print("=" * 60)
        print("📊 验证总结")
        print("=" * 60)

        print(
            f"GitHub Actions: {'✅ 正常' if actions_status['success'] else '❌ 异常'}"
        )
        if actions_status["success"]:
            print(f"  • 工作流运行数: {actions_status.get('runs_count', 0)}")
            print(f"  • 最新状态: {actions_status.get('latest_status', 'N/A')}")

        print(f"GitHub Pages: {'✅ 正常' if pages_status['success'] else '❌ 异常'}")
        if pages_status["success"]:
            print(f"  • 文档网站: {pages_status.get('url', 'N/A')}")
            print(
                f"  • 可访问性: {'✅ 可访问' if pages_status.get('accessible') else '⚠️ 暂时无法访问'}"
            )

        if recommendations:
            print("\n📋 建议操作:")
            for rec in recommendations:
                print(f"  {rec}")

        # 提供快速链接
        print("\n🔗 快速链接:")
        print(
            f"  • Actions: https://github.com/{self.repo_owner}/{self.repo_name}/actions"
        )
        print(
            f"  • Settings: https://github.com/{self.repo_owner}/{self.repo_name}/settings"
        )
        print(
            f"  • Pages: https://github.com/{self.repo_owner}/{self.repo_name}/settings/pages"
        )
        if pages_status.get("url"):
            print(f"  • 文档: {pages_status['url']}")

        # 返回整体状态
        overall_success = actions_status["success"] and pages_status["success"]

        if overall_success:
            print("\n🎉 验证完成！CI/CD 和文档部署系统运行正常。")
        else:
            print("\n⚠️  发现问题，请按照上述建议进行修复。")

        return overall_success


def main():
    """主函数"""
    verifier = GitHubActionsVerifier()
    success = verifier.run_verification()

    if not success:
        print("\n💡 提示: 如果是首次配置，请等待几分钟让系统完成初始化。")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
