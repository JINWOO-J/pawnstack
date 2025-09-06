"""
PawnStack 로거 테스트
"""

import asyncio
import logging
import tempfile
from pathlib import Path

from pawnstack.config.settings import Config, LoggingConfig
from pawnstack.core.base import PawnStack


async def test_logger_functionality():
    """로거 기능 테스트"""
    print("=== PawnStack 로거 기능 테스트 ===")
    
    # 임시 로그 파일 생성
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"
        
        # 로깅 설정
        logging_config = LoggingConfig()
        logging_config.level = "DEBUG"
        logging_config.file_path = log_file
        logging_config.max_file_size = 1024*1024  # 1MB
        logging_config.backup_count = 3
        
        # 설정 객체 생성
        config = Config()
        config.logging = logging_config
        
        # PawnStack 인스턴스 생성 (로거 자동 초기화)
        async with PawnStack(config=config) as ps:
            # 기본 로거 테스트
            ps.logger.debug("디버그 메시지 테스트")
            ps.logger.info("정보 메시지 테스트")
            ps.logger.warning("경고 메시지 테스트")
            ps.logger.error("에러 메시지 테스트")
            
            # HTTP 클라이언트를 통한 로깅 테스트
            try:
                # 존재하지 않는 URL로 요청하여 에러 발생
                await ps.http.get("http://localhost:12345/nonexistent")
            except Exception as e:
                ps.logger.exception(f"HTTP 요청 실패: {e}")
            
            print(f"\n--- 로그 파일 내용 ({log_file}) ---")
            if log_file.exists():
                print(log_file.read_text())
            else:
                print("로그 파일이 생성되지 않았습니다.")
            
            # 파일 로테이션 테스트
            print("\n--- 파일 로테이션 테스트 ---")
            for i in range(100):
                ps.logger.info(f"로테이션 테스트 메시지 {i}")
            
            print(f"로그 파일 크기: {log_file.stat().st_size if log_file.exists() else 0} bytes")
            
            # 백업 파일 확인
            backup_files = list(log_file.parent.glob(f"{log_file.name}.*"))
            print(f"생성된 백업 파일 수: {len(backup_files)}")


if __name__ == "__main__":
    asyncio.run(test_logger_functionality())