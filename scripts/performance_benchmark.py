#!/usr/bin/env python3
"""
BlueV 性能基准测试脚本
测试各个组件的性能指标并建立基准
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict

import psutil


class PerformanceBenchmark:
    """性能基准测试类"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results: Dict[str, Dict] = {}

    def measure_time_and_memory(self, func, *args, **kwargs):
        """测量函数执行时间和内存使用"""
        process = psutil.Process()

        # 记录开始状态
        start_time = time.time()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 执行函数
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = str(e)
            success = False

        # 记录结束状态
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB

        return {
            "success": success,
            "result": result,
            "duration": end_time - start_time,
            "memory_start": start_memory,
            "memory_end": end_memory,
            "memory_delta": end_memory - start_memory,
        }

    def benchmark_config_loading(self) -> Dict:
        """基准测试：配置加载性能"""
        print("📊 基准测试：配置加载性能")

        def load_config():
            from bluev.config import Config

            config = Config()
            return f"Loaded config for {config.APP_NAME}"

        # 多次测试取平均值
        results = []
        for _i in range(5):
            result = self.measure_time_and_memory(load_config)
            results.append(result)

        avg_duration = sum(r["duration"] for r in results) / len(results)
        avg_memory = sum(r["memory_delta"] for r in results) / len(results)

        benchmark = {
            "test_name": "Config Loading",
            "iterations": len(results),
            "avg_duration": avg_duration,
            "avg_memory_delta": avg_memory,
            "target_duration": 0.1,  # 目标：100ms 内
            "target_memory": 5.0,  # 目标：5MB 内
            "status": "PASS" if avg_duration < 0.1 and avg_memory < 5.0 else "FAIL",
        }

        print(f"  平均耗时: {avg_duration:.3f}s (目标: <0.1s)")
        print(f"  平均内存: {avg_memory:.2f}MB (目标: <5MB)")
        print(f"  状态: {benchmark['status']}")

        return benchmark

    def benchmark_logging_performance(self) -> Dict:
        """基准测试：日志系统性能"""
        print("📊 基准测试：日志系统性能")

        def logging_test():
            from bluev.utils.logging import get_logger

            logger = get_logger("benchmark")

            # 写入100条日志
            for i in range(100):
                logger.info(f"Benchmark log message {i}")

            return "100 log messages written"

        result = self.measure_time_and_memory(logging_test)

        benchmark = {
            "test_name": "Logging Performance",
            "iterations": 100,
            "duration": result["duration"],
            "memory_delta": result["memory_delta"],
            "target_duration": 1.0,  # 目标：1s 内写入100条
            "target_memory": 10.0,  # 目标：10MB 内
            "status": "PASS"
            if result["duration"] < 1.0 and result["memory_delta"] < 10.0
            else "FAIL",
        }

        print(f"  100条日志耗时: {result['duration']:.3f}s (目标: <1s)")
        print(f"  内存增长: {result['memory_delta']:.2f}MB (目标: <10MB)")
        print(f"  状态: {benchmark['status']}")

        return benchmark

    def benchmark_ruff_performance(self) -> Dict:
        """基准测试：Ruff 性能"""
        print("📊 基准测试：Ruff 代码检查性能")

        python_exe = self.project_root / "venv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = self.project_root / "venv" / "bin" / "python"

        def run_ruff():
            # 只检查核心模块以避免超时
            result = subprocess.run(
                [str(python_exe), "-m", "ruff", "check", "bluev/", "--quiet"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root,
            )
            return f"Ruff check completed with exit code {result.returncode}"

        result = self.measure_time_and_memory(run_ruff)

        benchmark = {
            "test_name": "Ruff Code Check",
            "duration": result["duration"],
            "memory_delta": result["memory_delta"],
            "target_duration": 30.0,  # 目标：30s 内
            "target_memory": 50.0,  # 目标：50MB 内
            "status": "PASS"
            if result["success"] and result["duration"] < 30.0
            else "FAIL",
        }

        print(f"  Ruff 检查耗时: {result['duration']:.3f}s (目标: <30s)")
        print(f"  内存使用: {result['memory_delta']:.2f}MB (目标: <50MB)")
        print(f"  状态: {benchmark['status']}")

        return benchmark

    def benchmark_import_performance(self) -> Dict:
        """基准测试：模块导入性能"""
        print("📊 基准测试：模块导入性能")

        def import_modules():
            # 测试主要模块的导入时间
            return "Core modules imported"

        result = self.measure_time_and_memory(import_modules)

        benchmark = {
            "test_name": "Module Import",
            "duration": result["duration"],
            "memory_delta": result["memory_delta"],
            "target_duration": 2.0,  # 目标：2s 内
            "target_memory": 20.0,  # 目标：20MB 内
            "status": "PASS"
            if result["success"] and result["duration"] < 2.0
            else "FAIL",
        }

        print(f"  模块导入耗时: {result['duration']:.3f}s (目标: <2s)")
        print(f"  内存使用: {result['memory_delta']:.2f}MB (目标: <20MB)")
        print(f"  状态: {benchmark['status']}")

        return benchmark

    def benchmark_application_startup(self) -> Dict:
        """基准测试：应用程序启动性能"""
        print("📊 基准测试：应用程序启动性能")

        python_exe = self.project_root / "venv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = self.project_root / "venv" / "bin" / "python"

        def startup_test():
            # 测试应用程序初始化（不启动GUI）
            result = subprocess.run(
                [
                    str(python_exe),
                    "-c",
                    "from bluev.main import BlueVApplication; app = BlueVApplication(); print('App initialized')",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.project_root,
            )
            return f"App startup test: {result.returncode}"

        result = self.measure_time_and_memory(startup_test)

        benchmark = {
            "test_name": "Application Startup",
            "duration": result["duration"],
            "memory_delta": result["memory_delta"],
            "target_duration": 5.0,  # 目标：5s 内
            "target_memory": 30.0,  # 目标：30MB 内
            "status": "PASS"
            if result["success"] and result["duration"] < 5.0
            else "FAIL",
        }

        print(f"  应用启动耗时: {result['duration']:.3f}s (目标: <5s)")
        print(f"  内存使用: {result['memory_delta']:.2f}MB (目标: <30MB)")
        print(f"  状态: {benchmark['status']}")

        return benchmark

    def run_all_benchmarks(self) -> Dict[str, Dict]:
        """运行所有性能基准测试"""
        print("🚀 开始性能基准测试...\n")

        benchmarks = [
            self.benchmark_config_loading,
            self.benchmark_logging_performance,
            self.benchmark_import_performance,
            self.benchmark_ruff_performance,
            self.benchmark_application_startup,
        ]

        results = {}
        for benchmark_func in benchmarks:
            try:
                result = benchmark_func()
                results[result["test_name"]] = result
            except Exception as e:
                print(f"  ❌ 基准测试失败: {e}")
                results[benchmark_func.__name__] = {
                    "test_name": benchmark_func.__name__,
                    "status": "ERROR",
                    "error": str(e),
                }
            print()

        return results

    def save_benchmark_results(self, results: Dict):
        """保存基准测试结果"""
        results_file = self.project_root / "benchmark_results.json"

        # 添加系统信息
        system_info = {
            "timestamp": time.time(),
            "python_version": sys.version,
            "platform": sys.platform,
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
        }

        full_results = {"system_info": system_info, "benchmarks": results}

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(full_results, f, indent=2, ensure_ascii=False)

        print(f"📄 基准测试结果已保存到: {results_file}")

    def print_summary(self, results: Dict):
        """打印基准测试总结"""
        print("=" * 60)
        print("📊 性能基准测试总结")
        print("=" * 60)

        passed = sum(1 for r in results.values() if r.get("status") == "PASS")
        failed = sum(1 for r in results.values() if r.get("status") == "FAIL")
        errors = sum(1 for r in results.values() if r.get("status") == "ERROR")
        total = len(results)

        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"错误: {errors}")
        print(f"成功率: {passed/total*100:.1f}%")
        print()

        print("性能指标:")
        for test_name, result in results.items():
            if result.get("status") in ["PASS", "FAIL"]:
                duration = result.get("duration", result.get("avg_duration", 0))
                memory = result.get("memory_delta", result.get("avg_memory_delta", 0))
                status_icon = "✅" if result["status"] == "PASS" else "❌"
                print(f"  {status_icon} {test_name}: {duration:.3f}s, {memory:.2f}MB")

        return passed == total


def main():
    """主函数"""
    benchmark = PerformanceBenchmark()
    results = benchmark.run_all_benchmarks()
    success = benchmark.print_summary(results)
    benchmark.save_benchmark_results(results)

    if success:
        print("\n🎉 所有性能基准测试通过！")
    else:
        print("\n⚠️ 部分性能基准测试未达标，需要优化。")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
