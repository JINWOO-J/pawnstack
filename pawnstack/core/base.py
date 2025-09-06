"""PawnStack 메인 클래스"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Optional

from pawnstack.config.settings import Config
from pawnstack.core.mixins import LoggerMixin
from pawnstack.http.client import HTTPClient
from pawnstack.logging.logger import Logger

if TYPE_CHECKING:
    from pawnstack.system.monitor import SystemMonitor


class PawnStack(LoggerMixin):
    """
    PawnStack 메인 클래스
    
    모든 PawnStack 기능에 대한 중앙 집중식 접근점을 제공합니다.
    """
    
    def __init__(self, config: Optional[Config] = None) -> None:
        """
        PawnStack 인스턴스 초기화
        
        Args:
            config: 설정 객체. None인 경우 기본 설정 사용
        """
        self.config = config or Config()
        super().__init__()
        
        # 핵심 컴포넌트 초기화
        self._logger = Logger(self.config.logging)
        self._http: Optional[HTTPClient] = None
        self._system_monitor: Optional[SystemMonitor] = None
        
        self.logger.info(f"PawnStack 초기화 완료 - 버전: {self.config.version}")
    
    @property
    def http(self) -> HTTPClient:
        """HTTP 클라이언트 인스턴스"""
        if self._http is None:
            self._http = HTTPClient()
        return self._http
    
    @property
    def system(self) -> SystemMonitor:
        """시스템 모니터 인스턴스"""
        if self._system_monitor is None:
            from pawnstack.system.monitor import SystemMonitor
            self._system_monitor = SystemMonitor(config=self.config.system)
        return self._system_monitor
    
    async def __aenter__(self) -> PawnStack:
        """비동기 컨텍스트 매니저 진입"""
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """비동기 컨텍스트 매니저 종료"""
        await self.close()
    
    async def close(self) -> None:
        """리소스 정리"""
        # HTTPClient는 각 요청마다 새로운 클라이언트를 생성하므로 별도 정리 불필요
        self.logger.info("PawnStack 리소스 정리 완료")
    
    def __repr__(self) -> str:
        return f"PawnStack(config={self.config})"