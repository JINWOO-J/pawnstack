"""설정 관련 테스트"""

import pytest
from pathlib import Path

from pawnstack.config.settings import Config, LoggingConfig, HttpConfig


def test_default_config():
    """기본 설정 테스트"""
    config = Config()
    
    assert config.app_name == "pawnstack"
    assert config.debug is False
    assert isinstance(config.logging, LoggingConfig)
    assert isinstance(config.http, HttpConfig)


def test_config_update():
    """설정 업데이트 테스트"""
    config = Config()
    
    config.update(debug=True, app_name="test_app")
    
    assert config.debug is True
    assert config.app_name == "test_app"


def test_config_get():
    """설정 조회 테스트"""
    config = Config()
    
    # 기본값 테스트
    assert config.get("debug") is False
    assert config.get("nonexistent", "default") == "default"
    
    # 추가 설정 테스트
    config.update(custom_key="custom_value")
    assert config.get("custom_key") == "custom_value"


def test_logging_config():
    """로깅 설정 테스트"""
    logging_config = LoggingConfig()
    
    assert logging_config.level == "INFO"
    assert logging_config.enable_console is True
    assert logging_config.enable_rich is True


def test_http_config():
    """HTTP 설정 테스트"""
    http_config = HttpConfig()
    
    assert http_config.timeout == 30.0
    assert http_config.max_retries == 3
    assert http_config.verify_ssl is True