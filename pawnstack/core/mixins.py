"""믹스인 클래스들"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pawnstack.logging.logger import Logger


class LoggerMixin:
    """로깅 기능을 제공하는 믹스인 클래스"""
    
    def __init__(self) -> None:
        self._logger_instance: logging.Logger | None = None
    
    @property
    def logger(self) -> logging.Logger:
        """로거 인스턴스 반환"""
        if self._logger_instance is None:
            self._logger_instance = logging.getLogger(
                f"{self.__class__.__module__}.{self.__class__.__name__}"
            )
        return self._logger_instance


class ConfigMixin:
    """설정 관리 기능을 제공하는 믹스인 클래스"""
    
    def __init__(self, config: dict | None = None) -> None:
        self._config = config or {}
    
    def get_config(self, key: str, default: any = None) -> any:
        """설정 값 조회"""
        return self._config.get(key, default)
    
    def set_config(self, key: str, value: any) -> None:
        """설정 값 설정"""
        self._config[key] = value
    
    def update_config(self, config: dict) -> None:
        """설정 업데이트"""
        self._config.update(config)