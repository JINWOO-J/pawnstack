"""PawnStack 기본 사용 예제"""

import asyncio
import logging
import os
# 환경 변수를 설정하여 전역 설정의 로그 출력 비활성화
os.environ['PAWN_CONSOLE'] = '{"redirect": false}'

from pawnstack import PawnStack, Config


async def main():
    """기본 사용 예제"""
    
    # 외부 라이브러리의 로그 레벨을 WARNING으로 올려 DEBUG/INFO 메시지 숨기기
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # 설정 생성
    config = Config(
        app_name="example_app",
        debug=False,
    )
    
    # HTTP 설정 조정
    config.http.timeout = 15.0
    config.http.max_retries = 2
    
    # 로깅 설정 조정
    config.logging.level = "INFO"
    config.logging.enable_rich = True
    config.logging.enable_console = True
    
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
    # 루트 로거 설정
    logging.basicConfig(
        format="%(message)s",
        level=logging.WARNING  # 전역 로거 레벨을 WARNING으로 설정하여 INFO 메시지 숨기기
    )
    
    asyncio.run(main())