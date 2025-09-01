#!/usr/bin/env python3
"""
BlueV 依赖版本监控脚本
用途: 监控项目依赖的版本状态，检查更新和安全漏洞

使用方法:
    python scripts/dependency-monitor.py [--check-updates] [--security-scan]
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

class Colors:
    """终端颜色定义"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class DependencyMonitor:
    """依赖监控器"""

    def __init__(self):
        self.current_deps = {}
        self.outdated_deps = {}
        self.security_issues = []

    def log_info(self, message: str) -> None:
        """输出信息日志"""
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

    def log_success(self, message: str) -> None:
        """输出成功日志"""
        print(f"{Colors.GREEN}[✅]{Colors.NC} {message}")

    def log_warning(self, message: str) -> None:
        """输出警告日志"""
        print(f"{Colors.YELLOW}[⚠️]{Colors.NC} {message}")

    def log_error(self, message: str) -> None:
        """输出错误日志"""
        print(f"{Colors.RED}[❌]{Colors.NC} {message}")

    def run_command(self, cmd: List[str]) -> Optional[subprocess.CompletedProcess]:
        """运行命令并返回结果"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return result
        except Exception as e:
            self.log_error(f"命令执行失败 {' '.join(cmd)}: {e}")
            return None

    def get_installed_packages(self) -> Dict[str, str]:
        """获取已安装的包列表"""
        self.log_info("📦 获取已安装包列表...")

        # 使用 conda run 在 bluev-dev 环境中执行
        result = self.run_command([
            "conda", "run", "-n", "bluev-dev", "pip", "list", "--format=json"
        ])

        if result and result.returncode == 0:
            try:
                packages = json.loads(result.stdout)
                package_dict = {pkg['name']: pkg['version'] for pkg in packages}
                self.log_success(f"找到 {len(package_dict)} 个已安装包")
                return package_dict
            except json.JSONDecodeError as e:
                self.log_error(f"解析包列表失败: {e}")
        else:
            self.log_error("获取包列表失败")

        return {}

    def get_requirements_packages(self) -> Dict[str, List[str]]:
        """解析 requirements 文件中的包"""
        self.log_info("📋 解析 requirements 文件...")

        req_files = {
            "core": PROJECT_ROOT / "requirements.txt",
            "dev": PROJECT_ROOT / "requirements-dev.txt"
        }

        all_requirements = {}

        for req_type, req_file in req_files.items():
            if req_file.exists():
                try:
                    with open(req_file, encoding='utf-8') as f:
                        lines = f.readlines()

                    packages = []
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # 解析包名和版本要求
                            match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                            if match:
                                packages.append(line)

                    all_requirements[req_type] = packages
                    self.log_success(f"{req_type} requirements: {len(packages)} 个包")

                except Exception as e:
                    self.log_error(f"解析 {req_file} 失败: {e}")
            else:
                self.log_warning(f"Requirements 文件不存在: {req_file}")

        return all_requirements

    def check_outdated_packages(self) -> Dict[str, Dict]:
        """检查过时的包"""
        self.log_info("🔍 检查过时的包...")

        result = self.run_command([
            "conda", "run", "-n", "bluev-dev", "pip", "list", "--outdated", "--format=json"
        ])

        if result and result.returncode == 0:
            try:
                outdated = json.loads(result.stdout)
                outdated_dict = {}

                for pkg in outdated:
                    outdated_dict[pkg['name']] = {
                        'current': pkg['version'],
                        'latest': pkg['latest_version'],
                        'type': pkg.get('latest_filetype', 'unknown')
                    }

                if outdated_dict:
                    self.log_warning(f"发现 {len(outdated_dict)} 个过时的包")
                    for name, info in outdated_dict.items():
                        print(f"  📦 {name}: {info['current']} → {info['latest']}")
                else:
                    self.log_success("所有包都是最新版本")

                return outdated_dict

            except json.JSONDecodeError as e:
                self.log_error(f"解析过时包列表失败: {e}")
        else:
            self.log_error("检查过时包失败")

        return {}

    def check_security_vulnerabilities(self) -> List[Dict]:
        """检查安全漏洞"""
        self.log_info("🔒 检查安全漏洞...")

        # 尝试使用 pip-audit (如果可用)
        result = self.run_command([
            "conda", "run", "-n", "bluev-dev", "pip-audit", "--format=json"
        ])

        if result and result.returncode == 0:
            try:
                audit_data = json.loads(result.stdout)
                vulnerabilities = audit_data.get('vulnerabilities', [])

                if vulnerabilities:
                    self.log_warning(f"发现 {len(vulnerabilities)} 个安全漏洞")
                    for vuln in vulnerabilities:
                        package = vuln.get('package', 'unknown')
                        version = vuln.get('installed_version', 'unknown')
                        advisory = vuln.get('advisory', {})
                        severity = advisory.get('severity', 'unknown')

                        print(f"  🚨 {package} v{version}: {severity}")
                        print(f"     {advisory.get('summary', 'No description')}")
                else:
                    self.log_success("未发现安全漏洞")

                return vulnerabilities

            except json.JSONDecodeError as e:
                self.log_error(f"解析安全审计结果失败: {e}")
        else:
            # pip-audit 可能未安装，尝试其他方法
            self.log_warning("pip-audit 不可用，跳过安全扫描")
            self.log_info("建议安装 pip-audit: pip install pip-audit")

        return []

    def generate_dependency_report(self) -> Dict:
        """生成依赖报告"""
        self.log_info("📊 生成依赖报告...")

        # 获取数据
        installed = self.get_installed_packages()
        requirements = self.get_requirements_packages()
        outdated = self.check_outdated_packages()

        # 分析核心依赖状态
        core_deps_status = {}
        if 'core' in requirements:
            for req in requirements['core']:
                pkg_name = re.match(r'^([a-zA-Z0-9_-]+)', req).group(1)
                if pkg_name in installed:
                    core_deps_status[pkg_name] = {
                        'installed': True,
                        'version': installed[pkg_name],
                        'outdated': pkg_name in outdated,
                        'requirement': req
                    }
                else:
                    core_deps_status[pkg_name] = {
                        'installed': False,
                        'version': None,
                        'outdated': False,
                        'requirement': req
                    }

        # 生成报告
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_installed': len(installed),
                'core_dependencies': len(core_deps_status),
                'dev_dependencies': len(requirements.get('dev', [])),
                'outdated_packages': len(outdated),
                'security_issues': len(self.security_issues)
            },
            'installed_packages': installed,
            'requirements': requirements,
            'core_dependencies_status': core_deps_status,
            'outdated_packages': outdated,
            'security_issues': self.security_issues
        }

        return report

    def print_summary(self, report: Dict) -> None:
        """打印依赖状态摘要"""
        print(f"\n{Colors.CYAN}📊 依赖状态摘要{Colors.NC}")
        print("=" * 50)

        summary = report['summary']

        print(f"📦 总安装包数: {summary['total_installed']}")
        print(f"🎯 核心依赖: {summary['core_dependencies']}")
        print(f"🛠️ 开发依赖: {summary['dev_dependencies']}")

        if summary['outdated_packages'] > 0:
            print(f"{Colors.YELLOW}📈 过时包数: {summary['outdated_packages']}{Colors.NC}")
        else:
            print(f"{Colors.GREEN}📈 过时包数: {summary['outdated_packages']}{Colors.NC}")

        if summary['security_issues'] > 0:
            print(f"{Colors.RED}🚨 安全问题: {summary['security_issues']}{Colors.NC}")
        else:
            print(f"{Colors.GREEN}🚨 安全问题: {summary['security_issues']}{Colors.NC}")

        # 核心依赖状态
        print(f"\n{Colors.CYAN}🎯 核心依赖状态{Colors.NC}")
        core_status = report['core_dependencies_status']

        installed_count = sum(1 for dep in core_status.values() if dep['installed'])
        outdated_count = sum(1 for dep in core_status.values() if dep['outdated'])

        print(f"✅ 已安装: {installed_count}/{len(core_status)}")
        if outdated_count > 0:
            print(f"{Colors.YELLOW}📈 需更新: {outdated_count}{Colors.NC}")
        else:
            print(f"{Colors.GREEN}📈 需更新: {outdated_count}{Colors.NC}")

        # 健康评分
        health_score = self.calculate_health_score(report)
        if health_score >= 90:
            print(f"\n{Colors.GREEN}🏥 依赖健康度: {health_score}% (优秀){Colors.NC}")
        elif health_score >= 75:
            print(f"\n{Colors.YELLOW}🏥 依赖健康度: {health_score}% (良好){Colors.NC}")
        else:
            print(f"\n{Colors.RED}🏥 依赖健康度: {health_score}% (需要关注){Colors.NC}")

    def calculate_health_score(self, report: Dict) -> int:
        """计算依赖健康评分"""
        summary = report['summary']
        core_status = report['core_dependencies_status']

        # 基础分数
        score = 100

        # 核心依赖缺失扣分
        missing_core = sum(1 for dep in core_status.values() if not dep['installed'])
        score -= missing_core * 20

        # 过时包扣分
        score -= min(summary['outdated_packages'] * 2, 20)

        # 安全问题扣分
        score -= summary['security_issues'] * 10

        return max(0, score)

    def run_monitor(self, check_updates: bool = True, security_scan: bool = False) -> Dict:
        """运行依赖监控"""
        print(f"{Colors.CYAN}📦 BlueV 依赖版本监控{Colors.NC}")
        print("=" * 50)

        # 生成报告
        report = self.generate_dependency_report()

        # 检查安全漏洞 (如果启用)
        if security_scan:
            self.security_issues = self.check_security_vulnerabilities()
            report['security_issues'] = self.security_issues

        # 打印摘要
        self.print_summary(report)

        return report

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="BlueV 依赖版本监控")
    parser.add_argument("--check-updates", action="store_true", default=True, help="检查包更新")
    parser.add_argument("--security-scan", action="store_true", help="执行安全扫描")
    parser.add_argument("--output", help="输出报告到 JSON 文件")

    args = parser.parse_args()

    # 切换到项目根目录
    import os
    os.chdir(PROJECT_ROOT)

    # 运行监控
    monitor = DependencyMonitor()
    report = monitor.run_monitor(
        check_updates=args.check_updates,
        security_scan=args.security_scan
    )

    # 保存报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n📄 报告已保存到: {args.output}")

    # 返回适当的退出码
    if report['summary']['security_issues'] > 0:
        sys.exit(1)
    elif report['summary']['outdated_packages'] > 5:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
