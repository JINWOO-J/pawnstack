"""시스템 모니터링 예제"""

import asyncio
from pawnstack import PawnStack, Config


async def basic_system_info():
    """기본 시스템 정보 조회 예제"""
    
    config = Config(app_name="system_info")
    
    async with PawnStack(config) as pstack:
        
        pstack.logger.info("시스템 정보 조회")
        
        # 현재 시스템 정보 수집
        info = pstack.system.get_current_info()
        
        pstack.logger.info(f"CPU 사용률: {info.cpu_percent:.1f}%")
        pstack.logger.info(f"메모리 사용률: {info.memory_percent:.1f}%")
        pstack.logger.info(f"메모리 사용량: {info.memory_used / (1024**3):.1f} GB")
        pstack.logger.info(f"디스크 사용률: {info.disk_percent:.1f}%")
        pstack.logger.info(f"실행 중인 프로세스: {info.process_count}개")
        
        if info.load_average:
            pstack.logger.info(f"로드 평균: {info.load_average}")


async def continuous_system_monitoring():
    """지속적인 시스템 모니터링 예제"""
    
    config = Config(app_name="system_monitor")
    
    # 임계값 설정
    config.system.cpu_threshold = 70.0
    config.system.memory_threshold = 80.0
    config.system.monitor_interval = 2.0
    
    async with PawnStack(config) as pstack:
        
        def monitoring_callback(info):
            """모니터링 콜백 함수"""
            pstack.logger.info(
                f"CPU: {info.cpu_percent:.1f}%, "
                f"메모리: {info.memory_percent:.1f}%, "
                f"디스크: {info.disk_percent:.1f}%"
            )
        
        pstack.logger.info("지속적인 시스템 모니터링 시작 (Ctrl+C로 중단)")
        
        try:
            # 30초 동안 모니터링
            await pstack.system.start_monitoring(
                duration=30.0,
                callback=monitoring_callback
            )
        except KeyboardInterrupt:
            pstack.logger.info("모니터링이 중단되었습니다")


async def system_statistics():
    """시스템 통계 예제"""
    
    config = Config(app_name="system_stats")
    
    async with PawnStack(config) as pstack:
        
        pstack.logger.info("시스템 통계 수집 시작")
        
        # 10초 동안 데이터 수집
        await pstack.system.start_monitoring(duration=10.0)
        
        # 평균 통계 조회
        stats = pstack.system.get_average_stats(minutes=1)
        
        if stats:
            pstack.logger.info("최근 1분간 평균 통계:")
            pstack.logger.info(f"  CPU: {stats['cpu_percent']:.1f}%")
            pstack.logger.info(f"  메모리: {stats['memory_percent']:.1f}%")
            pstack.logger.info(f"  디스크: {stats['disk_percent']:.1f}%")
            pstack.logger.info(f"  샘플 수: {stats['sample_count']}개")
        
        # 상위 프로세스 조회
        top_processes = pstack.system.get_top_processes(limit=5, sort_by='cpu')
        
        pstack.logger.info("CPU 사용률 상위 5개 프로세스:")
        for i, proc in enumerate(top_processes, 1):
            pstack.logger.info(
                f"  {i}. {proc['name']} (PID: {proc['pid']}) - "
                f"CPU: {proc['cpu_percent']:.1f}%, "
                f"메모리: {proc['memory_percent']:.1f}%"
            )


if __name__ == "__main__":
    print("1. 기본 시스템 정보")
    print("2. 지속적인 모니터링")
    print("3. 시스템 통계")
    
    choice = input("선택하세요 (1, 2, 또는 3): ")
    
    if choice == "1":
        asyncio.run(basic_system_info())
    elif choice == "2":
        asyncio.run(continuous_system_monitoring())
    elif choice == "3":
        asyncio.run(system_statistics())
    else:
        print("잘못된 선택입니다.")