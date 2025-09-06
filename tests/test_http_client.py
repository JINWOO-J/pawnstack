"""HTTP 클라이언트 테스트"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from pawnstack.config.settings import HttpConfig
from pawnstack.http.client import HttpClient, HttpResponse


@pytest.fixture
def http_config():
    """HTTP 설정 픽스처"""
    config = HttpConfig()
    config.timeout = 10.0
    config.max_retries = 2
    return config


@pytest.fixture
def http_client(http_config):
    """HTTP 클라이언트 픽스처"""
    return HttpClient(http_config)


def test_http_client_initialization(http_client):
    """HTTP 클라이언트 초기화 테스트"""
    assert http_client.config.timeout == 10.0
    assert http_client.config.max_retries == 2


def test_http_response_model():
    """HTTP 응답 모델 테스트"""
    response = HttpResponse(
        status_code=200,
        headers={"content-type": "application/json"},
        content=b'{"test": "data"}',
        text='{"test": "data"}',
        url="https://example.com",
        elapsed=0.5,
    )
    
    assert response.status_code == 200
    assert response.is_success is True
    assert response.is_client_error is False
    assert response.is_server_error is False
    assert response.json() == {"test": "data"}


@pytest.mark.asyncio
async def test_http_client_close(http_client):
    """HTTP 클라이언트 종료 테스트"""
    # 클라이언트 인스턴스 생성
    _ = http_client.client
    
    # 종료 테스트
    await http_client.close()
    assert http_client._client is None