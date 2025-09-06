"""
성능 벤치마킹 데모

새로운 성능 모니터링 및 벤치마킹 모듈을 사용한 예제
"""

import asyncio
import json
from pawnstack.monitoring import (
    PerformanceMonitor,
    BenchmarkManager,
    RegressionTestConfig,
    quick_benchmark,
    compare_endpoints
)


async def basic_benchmark_demo():
    """기본 벤치마크 데모"""
    print("=== 기본 벤치마크 데모 ===")

    # 간단한 벤치마크 실행
    result = await quick_benchmark(
        url="https://httpbin.org/status/200",
        name="HTTPBin 기본 벤치마크",
        requests=50,
        concurrency=5
    )

    print(f"벤치마크 완료: {result.name}")
    print(f"RPS: {result.requests_per_second:.2f}")
    print(f"평균 응답시간: {result.avg_response_time:.3f}초")
    print(f"에러율: {result.error_rate:.2f}%")


async def detailed_benchmark_demo():
    """상세 벤치마크 데모"""
    print("=== 상세 벤치마크 데모 ===")

    monitor = PerformanceMonitor()

    # 상세 벤치마크 실행
    result = await monitor.run_benchmark(
        name="HTTPBin 상세 벤치마크",
        url="https://httpbin.org/json",
        method="GET",
        concurrent_requests=10,
        total_requests=100,
        warmup_requests=10
    )

    print("\n=== 벤치마크 결과 ===")
    print(f"총 요청: {result.total_requests}")
    print(f"성공 요청: {result.successful_requests}")
    print(f"실패 요청: {result.failed_requests}")
    print(f"RPS: {result.requests_per_second:.2f}")
    print(f"평균 응답시간: {result.avg_response_time:.3f}초")
    print(f"95th 백분위수: {result.percentiles.get(95, 0):.3f}초")
    print(f"99th 백분위수: {result.percentiles.get(99, 0):.3f}초")

    # 결과 내보내기
    monitor.export_benchmark_results("benchmark_results.json")
    print("벤치마크 결과가 benchmark_results.json에 저장되었습니다.")


async def endpoint_comparison_demo():
    """엔드포인트 성능 비교 데모"""
    print("=== 엔드포인트 성능 비교 데모 ===")

    # 비교할 엔드포인트들
    endpoints = [
        {
            "name": "HTTPBin Status 200",
            "url": "https://httpbin.org/status/200",
            "method": "GET"
        },
        {
            "name": "HTTPBin JSON",
            "url": "https://httpbin.org/json",
            "method": "GET"
        },
        {
            "name": "HTTPBin Delay 0.5s",
            "url": "https://httpbin.org/delay/0.5",
            "method": "GET"
        },
        {
            "name": "JSONPlaceholder Posts",
            "url": "https://jsonplaceholder.typicode.com/posts/1",
            "method": "GET"
        }
    ]

    # 성능 비교 실행
    results = await compare_endpoints(
        endpoints=endpoints,
        requests_per_endpoint=30,
        concurrency=3
    )

    print(f"\n{len(results)}개 엔드포인트 성능 비교 완료")


async def baseline_creation_demo():
    """성능 기준선 생성 데모"""
    print("=== 성능 기준선 생성 데모 ===")

    manager = BenchmarkManager(baseline_dir="demo_benchmarks")

    # 성능 기준선 생성
    baseline = manager.create_baseline(
        name="httpbin_api",
        version="1.0.0",
        url="https://httpbin.org/json",
        method="GET",
        requests=100,
        concurrency=5,
        description="HTTPBin JSON API 기준선"
    )

    print(f"기준선 생성 완료: {baseline.name} v{baseline.version}")

    # 기준선 목록 출력
    baselines = manager.list_baselines()
    print(f"저장된 기준선 수: {len(baselines)}")


async def regression_test_demo():
    """회귀 테스트 데모"""
    print("=== 회귀 테스트 데모 ===")

    manager = BenchmarkManager(baseline_dir="demo_benchmarks")

    # 먼저 기준선이 있는지 확인하고 없으면 생성
    if not manager.get_baseline("httpbin_api"):
        print("기준선을 먼저 생성합니다...")
        manager.create_baseline(
            name="httpbin_api",
            version="1.0.0",
            url="https://httpbin.org/json",
            requests=50,
            concurrency=3
        )

    # 회귀 테스트 설정
    regression_config = RegressionTestConfig(
        name="httpbin_api",
        url="https://httpbin.org/json",
        method="GET",
        requests=50,
        concurrency=3,
        acceptable_regression_percent=15.0,
        critical_regression_percent=30.0
    )

    manager.add_regression_test(regression_config)

    # 회귀 테스트 실행
    try:
        result = await manager.run_regression_test("httpbin_api")

        print(f"\n회귀 테스트 결과: {result.config_name}")
        print(f"회귀 감지: {'예' if result.regression_detected else '아니오'}")
        print(f"심각도: {result.regression_severity}")

        # 결과 내보내기
        manager.export_regression_results([result], "regression_test_results.json")

    except Exception as e:
        print(f"회귀 테스트 실행 중 오류: {e}")


async def memory_monitoring_demo():
    """메모리 사용량 모니터링 데모"""
    print("=== 메모리 사용량 모니터링 데모 ===")

    monitor = PerformanceMonitor()

    # 단일 요청 성능 측정
    print("단일 요청 성능 측정 중...")
    for i in range(5):
        metrics = await monitor.measure_single_request(
            url="https://httpbin.org/json",
            method="GET"
        )

        print(f"요청 {i+1}: "
              f"응답시간={metrics.response_time:.3f}초, "
              f"메모리={metrics.memory_usage_mb:.2f}MB, "
              f"CPU={metrics.cpu_percent:.1f}%")

    # 성능 요약 출력
    summary = monitor.get_performance_summary(last_n_minutes=5)
    if summary:
        print(f"\n=== 최근 5분 성능 요약 ===")
        print(f"총 요청: {summary['total_requests']}")
        print(f"성공률: {summary['success_rate']:.1f}%")
        print(f"평균 응답시간: {summary['avg_response_time']:.3f}초")
        print(f"평균 메모리 사용량: {summary['avg_memory_usage']:.2f}MB")
        print(f"평균 CPU 사용률: {summary['avg_cpu_usage']:.1f}%")


async def stress_test_demo():
    """스트레스 테스트 데모"""
    print("=== 스트레스 테스트 데모 ===")

    monitor = PerformanceMonitor()

    # 점진적으로 부하 증가
    concurrency_levels = [1, 5, 10, 20]

    for concurrency in concurrency_levels:
        print(f"\n동시 요청 수: {concurrency}")

        result = await monitor.run_benchmark(
            name=f"스트레스 테스트 (동시요청: {concurrency})",
            url="https://httpbin.org/json",
            concurrent_requests=concurrency,
            total_requests=concurrency * 10,  # 각 레벨당 적절한 요청 수
            warmup_requests=5
        )

        print(f"RPS: {result.requests_per_second:.2f}")
        print(f"평균 응답시간: {result.avg_response_time:.3f}초")
        print(f"에러율: {result.error_rate:.2f}%")
        print(f"최대 메모리: {result.memory_usage.get('peak', 0):.2f}MB")


def create_sample_regression_config():
    """샘플 회귀 테스트 설정 파일 생성"""
    config = {
        "regression_tests": [
            {
                "name": "api_health_check",
                "url": "https://httpbin.org/status/200",
                "method": "GET",
                "requests": 50,
                "concurrency": 5,
                "acceptable_regression_percent": 10.0,
                "critical_regression_percent": 25.0
            },
            {
                "name": "api_json_endpoint",
                "url": "https://httpbin.org/json",
                "method": "GET",
                "requests": 100,
                "concurrency": 10,
                "acceptable_regression_percent": 15.0,
                "critical_regression_percent": 30.0
            }
        ]
    }

    with open("sample_regression_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print("샘플 회귀 테스트 설정이 sample_regression_config.json에 저장되었습니다.")


def main():
    """메인 함수"""
    print("성능 벤치마킹 데모를 선택하세요:")
    print("1. 기본 벤치마크")
    print("2. 상세 벤치마크")
    print("3. 엔드포인트 성능 비교")
    print("4. 성능 기준선 생성")
    print("5. 회귀 테스트")
    print("6. 메모리 사용량 모니터링")
    print("7. 스트레스 테스트")
    print("8. 샘플 설정 파일 생성")

    choice = input("선택 (1-8): ").strip()

    if choice == "1":
        asyncio.run(basic_benchmark_demo())
    elif choice == "2":
        asyncio.run(detailed_benchmark_demo())
    elif choice == "3":
        asyncio.run(endpoint_comparison_demo())
    elif choice == "4":
        asyncio.run(baseline_creation_demo())
    elif choice == "5":
        asyncio.run(regression_test_demo())
    elif choice == "6":
        asyncio.run(memory_monitoring_demo())
    elif choice == "7":
        asyncio.run(stress_test_demo())
    elif choice == "8":
        create_sample_regression_config()
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()
