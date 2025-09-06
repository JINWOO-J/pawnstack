"""
HTTP 모니터링 데모

새로운 모니터링 모듈을 사용한 HTTP 엔드포인트 모니터링 예제
"""

import asyncio
from pawnstack.monitoring import HTTPMonitor, HTTPMonitorConfig


async def basic_monitoring_demo():
    """기본 HTTP 모니터링 데모"""
    print("=== 기본 HTTP 모니터링 데모 ===")

    # 모니터링 설정
    config = HTTPMonitorConfig(
        url="https://httpbin.org/status/200",
        method="GET",
        interval=2.0,
        success_criteria=["status_code==200", "response_time<2.0"],
        name="HTTPBin 상태 체크"
    )

    # 모니터 생성 및 엔드포인트 추가
    monitor = HTTPMonitor()
    monitor.add_endpoint(config)

    # 10초간 모니터링 실행
    try:
        monitoring_task = asyncio.create_task(monitor.start_monitoring(dashboard=True))
        await asyncio.sleep(10)
        await monitor.stop_monitoring()
    except KeyboardInterrupt:
        await monitor.stop_monitoring()


async def multiple_endpoints_demo():
    """여러 엔드포인트 동시 모니터링 데모"""
    print("=== 여러 엔드포인트 모니터링 데모 ===")

    # 여러 엔드포인트 설정
    configs = [
        HTTPMonitorConfig(
            url="https://httpbin.org/status/200",
            name="HTTPBin 200",
            interval=1.0
        ),
        HTTPMonitorConfig(
            url="https://httpbin.org/status/404",
            name="HTTPBin 404",
            interval=1.5,
            success_criteria=["status_code==404"]  # 404를 성공으로 간주
        ),
        HTTPMonitorConfig(
            url="https://httpbin.org/delay/1",
            name="HTTPBin Delay",
            interval=2.0,
            success_criteria=["status_code==200", "response_time<3.0"]
        ),
        HTTPMonitorConfig(
            url="https://jsonplaceholder.typicode.com/posts/1",
            name="JSONPlaceholder",
            interval=1.0
        )
    ]

    # 모니터 생성 및 엔드포인트들 추가
    monitor = HTTPMonitor()
    for config in configs:
        monitor.add_endpoint(config)

    # 15초간 모니터링 실행
    try:
        monitoring_task = asyncio.create_task(monitor.start_monitoring(dashboard=True))
        await asyncio.sleep(15)
        await monitor.stop_monitoring()

        # 결과 내보내기
        monitor.export_results("monitoring_results.json")
        print("모니터링 결과가 monitoring_results.json에 저장되었습니다.")

    except KeyboardInterrupt:
        await monitor.stop_monitoring()


async def api_monitoring_demo():
    """API 모니터링 데모 (POST 요청 포함)"""
    print("=== API 모니터링 데모 ===")

    # POST API 모니터링 설정
    post_config = HTTPMonitorConfig(
        url="https://httpbin.org/post",
        method="POST",
        headers={"Content-Type": "application/json"},
        data={"test": "data", "timestamp": "2024-01-01"},
        interval=3.0,
        success_criteria=["status_code==200"],
        name="HTTPBin POST API"
    )

    # GET API 모니터링 설정
    get_config = HTTPMonitorConfig(
        url="https://httpbin.org/json",
        method="GET",
        interval=2.0,
        success_criteria=["status_code==200", "response_time<1.0"],
        name="HTTPBin JSON API"
    )

    monitor = HTTPMonitor()
    monitor.add_endpoint(post_config)
    monitor.add_endpoint(get_config)

    # 모니터링 실행
    try:
        monitoring_task = asyncio.create_task(monitor.start_monitoring(dashboard=True))
        await asyncio.sleep(12)
        await monitor.stop_monitoring()

        # 통계 출력
        stats = monitor.get_statistics()
        print("\n=== 최종 통계 ===")
        for name, stat in stats.items():
            print(f"{name}:")
            print(f"  총 요청: {stat['total_requests']}")
            print(f"  성공률: {stat['uptime_percentage']:.1f}%")
            print(f"  평균 응답시간: {stat['avg_response_time']:.3f}초")

    except KeyboardInterrupt:
        await monitor.stop_monitoring()


async def custom_success_criteria_demo():
    """커스텀 성공 기준 데모"""
    print("=== 커스텀 성공 기준 데모 ===")

    # 복잡한 성공 기준 설정
    config = HTTPMonitorConfig(
        url="https://httpbin.org/json",
        method="GET",
        interval=2.0,
        success_criteria=[
            "status_code==200",
            "response_time<2.0"
        ],
        logical_operator="and",  # 모든 조건을 만족해야 성공
        name="복합 조건 체크"
    )

    monitor = HTTPMonitor()
    monitor.add_endpoint(config)

    try:
        monitoring_task = asyncio.create_task(monitor.start_monitoring(dashboard=True))
        await asyncio.sleep(10)
        await monitor.stop_monitoring()

    except KeyboardInterrupt:
        await monitor.stop_monitoring()


def main():
    """메인 함수"""
    print("HTTP 모니터링 데모를 선택하세요:")
    print("1. 기본 모니터링")
    print("2. 여러 엔드포인트 모니터링")
    print("3. API 모니터링 (POST/GET)")
    print("4. 커스텀 성공 기준")

    choice = input("선택 (1-4): ").strip()

    if choice == "1":
        asyncio.run(basic_monitoring_demo())
    elif choice == "2":
        asyncio.run(multiple_endpoints_demo())
    elif choice == "3":
        asyncio.run(api_monitoring_demo())
    elif choice == "4":
        asyncio.run(custom_success_criteria_demo())
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()
