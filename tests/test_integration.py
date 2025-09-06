"""통합 테스트"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from pawnstack import PawnStack, Config


def test_pawnstack_import():
    """PawnStack 기본 import 테스트"""
    # 이미 import가 성공했으므로 패스
    assert True


def test_config_creation():
    """설정 생성 테스트"""
    config = Config(app_name="test_app", debug=True)
    
    assert config.app_name == "test_app"
    assert config.debug is True
    assert config.logging is not None
    assert config.http is not None
    assert config.system is not None


def test_pawnstack_creation():
    """PawnStack 인스턴스 생성 테스트"""
    config = Config(app_name="test_app")
    pstack = PawnStack(config)
    
    assert pstack.config.app_name == "test_app"
    assert pstack.logger is not None


def test_system_monitor_access():
    """시스템 모니터 접근 테스트"""
    config = Config()
    pstack = PawnStack(config)
    
    # 시스템 모니터 접근
    system_monitor = pstack.system
    assert system_monitor is not None
    
    # 현재 시스템 정보 수집
    info = system_monitor.get_current_info()
    assert info is not None
    assert info.cpu_percent >= 0
    assert info.memory_total > 0


def test_http_client_access():
    """HTTP 클라이언트 접근 테스트"""
    config = Config()
    pstack = PawnStack(config)
    
    # HTTP 클라이언트 접근
    http_client = pstack.http
    assert http_client is not None
    assert http_client.timeout == 30.0


@pytest.mark.asyncio
async def test_pawnstack_context_manager():
    """PawnStack 컨텍스트 매니저 테스트"""
    config = Config(app_name="async_test")
    
    async with PawnStack(config) as pstack:
        assert pstack.config.app_name == "async_test"
        assert pstack.logger is not None


@pytest.mark.asyncio
@patch('pawnstack.http.client.httpx.AsyncClient')
async def test_http_client_mock(mock_client):
    """HTTP 클라이언트 모킹 테스트"""
    # Mock 응답 설정
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "application/json"}
    mock_response.content = b'{"test": "data"}'
    mock_response.text = '{"test": "data"}'
    mock_response.url = "https://example.com"
    
    mock_client_instance = MagicMock()
    mock_client_instance.request.return_value = mock_response
    mock_client.return_value = mock_client_instance
    
    config = Config()
    async with PawnStack(config) as pstack:
        # HTTP 클라이언트가 생성되는지 확인
        http_client = pstack.http
        assert http_client is not None