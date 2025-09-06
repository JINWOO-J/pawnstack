"""HTTP 모니터링 예제"""

import asyncio
from typing import List
from pawnstack import PawnStack, Config


async def monitor_multiple_endpoints():
    """여러 엔드포인트 동시 모니터링 예제"""
    
    config = Config(app_name="http_monitor")
    
    # 모니터링할 URL 목록
    urls = [
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/404", 
        "https://httpbin.org/delay/2",
        "https://jsonplaceholder.typicode.com/posts/1",
    ]
    
    async with PawnStack(config) as pstack:
        
        async def check_endpoint(url: str) -> dict:
            """단일 엔드포인트 체크"""
            try:
                response = await pstack.http.get(url)
                return {
                    "url": url,
                    "status_code": response.status_code,
                    "response_time": response.elapsed,
                    "success": response.is_success,
                    "error": None,
                }
            except Exception as e:
                return {
                    "url": url,
                    "status_code": None,
                    "response_time": None,
                    "success": False,
                    "error": str(e),
                }
        
        # 모든 엔드포인트 동시 체크
        pstack.logger.info("HTTP 엔드포인트 모니터링 시작")
        
        tasks = [check_endpoint(url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        # 결과 출력
        for result in results:
            if result["success"]:
                pstack.logger.info(
                    f"✅ {result['url']} - {result['status_code']} "
                    f"({result['response_time']:.3f}s)"
                )
            else:
                pstack.logger.error(
                    f"❌ {result['url']} - {result['error']}"
                )


async def continuous_monitoring():
    """지속적인 모니터링 예제"""
    
    config = Config(app_name="continuous_monitor")
    
    async with PawnStack(config) as pstack:
        
        url = "https://httpbin.org/status/200"
        interval = 5  # 5초 간격
        
        pstack.logger.info(f"지속적인 모니터링 시작: {url}")
        
        try:
            while True:
                try:
                    response = await pstack.http.get(url)
                    
                    if response.is_success:
                        pstack.logger.info(
                            f"✅ {url} - {response.status_code} "
                            f"({response.elapsed:.3f}s)"
                        )
                    else:
                        pstack.logger.warning(
                            f"⚠️ {url} - {response.status_code} "
                            f"({response.elapsed:.3f}s)"
                        )
                        
                except Exception as e:
                    pstack.logger.error(f"❌ {url} - {e}")
                
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            pstack.logger.info("모니터링이 중단되었습니다")


if __name__ == "__main__":
    print("1. 여러 엔드포인트 동시 모니터링")
    print("2. 지속적인 모니터링")
    
    choice = input("선택하세요 (1 또는 2): ")
    
    if choice == "1":
        asyncio.run(monitor_multiple_endpoints())
    elif choice == "2":
        asyncio.run(continuous_monitoring())
    else:
        print("잘못된 선택입니다.")