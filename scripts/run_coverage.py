# -*- coding: utf-8 -*-
import sys
from pathlib import Path


def main():
    # 延迟导入，避免覆盖率提前启动
    import coverage
    import pytest

    repo_root = Path(__file__).resolve().parents[1]
    # 仅在仓库根目录运行
    print(f"[run_coverage] repo_root={repo_root}")

    cov = coverage.Coverage(config_file=str(repo_root / ".coveragerc"))
    cov.erase()
    cov.start()

    # 分组执行，降低一次性运行的不稳定性；不使用 pytest-cov 插件
    code = 0
    for group in [
        ["tests/unit"],
        ["tests/integration"],
    ]:
        print(f"[run_coverage] pytest {' '.join(group)}")
        rc = pytest.main(["-q", "-p", "no:qt", *group])
        if rc != 0:
            code = rc
            print(f"[run_coverage] group failed: {group}, rc={rc}")
            break

    cov.stop()
    cov.save()

    print("\n[run_coverage] Coverage Report (target: 85%):")
    total_coverage = cov.report(show_missing=True, skip_covered=True)

    # 手动检查覆盖率阈值
    if total_coverage < 85.0:
        print(f"❌ 覆盖率 {total_coverage:.1f}% 低于目标 85%")
        code = max(code, 1)
    else:
        print(f"✅ 覆盖率 {total_coverage:.1f}% 达到目标 85%")

    # 生成 HTML 报告（可选）
    html_dir = repo_root / "htmlcov"
    cov.html_report(directory=str(html_dir))
    print(f"[run_coverage] HTML report at: {html_dir}")

    sys.exit(code)


if __name__ == "__main__":
    main()
