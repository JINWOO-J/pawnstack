"""PawnStack 기본 사용 예제"""

import asyncio
from pawnstack import PawnStack, Config


async def main():
    """기본 사용 예제"""
    
    # 설정 생성
    config = Config(
        app_name="example_app",
        debug=True,
    )
    
    # HTTP 설정 조정
    config.http.timeout = 15.0
    config.http.max_retries = 2
    
    # 로깅 설정 조정
    config.logging.level = "DEBUG"
    config.logging.enable_rich = True
    
    # PawnStack 인스턴스 생성 및 사용
    async with PawnStack(config) as pstack:
        
        # 로깅 예제
        pstack.logger.info("PawnStack 예제 시작")
        
        # HTTP 요청 예제
        try:
            response = await pstack.http.get("https://httpbin.org/json")
            pstack.logger.info(f"HTTP 응답: {response.status_code}")
            
            if response.is_success:
                data = response.json()
                pstack.logger.info(f"응답 데이터: {data}")
            
        except Exception as e:
            pstack.logger.error(f"HTTP 요청 실패: {e}")
        
        # 시스템 정보 예제
        system_info = pstack.system.get_current_info()
        pstack.logger.info(f"CPU 사용률: {system_info.cpu_percent}%")
        pstack.logger.info(f"메모리 사용률: {system_info.memory_percent}%")
        
        pstack.logger.info("PawnStack 예제 완료")


if __name__ == "__main__":
    asyncio.run(main())