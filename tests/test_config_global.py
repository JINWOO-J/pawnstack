"""
PawnStack 전역 설정 테스트
"""

import os
import pytest
from unittest.mock import patch

from pawnstack.config.global_config import (
    PawnStackConfig,
    ConfigHandler,
    NestedNamespace,
    pawnstack_config,
    pawn
)


class TestNestedNamespace:
    """NestedNamespace 클래스 테스트"""
    
    def test_basic_creation(self):
        """기본 생성 테스트"""
        ns = NestedNamespace(hello="world", count=42)
        assert ns.hello == "world"
        assert ns.count == 42
    
    def test_nested_dict(self):
        """중첩 딕셔너리 테스트"""
        data = {
            "level1": {
                "level2": {
                    "value": "nested"
                }
            }
        }
        ns = NestedNamespace(**data)
        assert ns.level1.level2.value == "nested"
    
    def test_list_handling(self):
        """리스트 처리 테스트"""
        data = {
            "items": [
                {"name": "item1"},
                {"name": "item2"}
            ]
        }
        ns = NestedNamespace(**data)
        assert ns.items[0].name == "item1"
        assert ns.items[1].name == "item2"
    
    def test_keys_values(self):
        """키와 값 메서드 테스트"""
        ns = NestedNamespace(a=1, b=2, c=3)
        assert set(ns.keys()) == {"a", "b", "c"}
        assert set(ns.values()) == {1, 2, 3}
    
    def test_as_dict(self):
        """딕셔너리 변환 테스트"""
        data = {
            "level1": {
                "level2": "value"
            },
            "simple": "test"
        }
        ns = NestedNamespace(**data)
        result = ns.as_dict()
        assert result == data
    
    def test_get_nested(self):
        """중첩 값 검색 테스트"""
        ns = NestedNamespace(level1={'level2': {'level3': 'value'}})
        assert ns.get_nested(['level1', 'level2', 'level3']) == 'value'
        assert ns.get_nested(['level1', 'nonexistent', 'level3']) is None


class TestConfigHandler:
    """ConfigHandler 클래스 테스트"""
    
    def test_basic_creation(self):
        """기본 생성 테스트"""
        handler = ConfigHandler()
        assert handler.config_file == 'config.ini'
        assert handler.args == {}
        assert handler.env_prefix is None
    
    def test_env_prefix_filtering(self):
        """환경변수 접두사 필터링 테스트"""
        with patch.dict(os.environ, {
            'PAWN_DEBUG': 'true',
            'PAWN_TIMEOUT': '5000',
            'OTHER_VAR': 'ignored'
        }):
            handler = ConfigHandler(env_prefix='pawn_')
            assert 'debug' in handler.env
            assert 'timeout' in handler.env
            assert 'other_var' not in handler.env
    
    def test_value_conversion(self):
        """값 타입 변환 테스트"""
        assert ConfigHandler._convert_value('true') is True
        assert ConfigHandler._convert_value('false') is False
        assert ConfigHandler._convert_value('123') == 123
        assert ConfigHandler._convert_value('12.34') == 12.34
        assert ConfigHandler._convert_value('hello') == 'hello'
    
    def test_get_with_defaults(self):
        """기본값과 함께 값 가져오기 테스트"""
        defaults = {'test_key': 'default_value'}
        handler = ConfigHandler(defaults=defaults)
        
        assert handler.get('test_key') == 'default_value'
        assert handler.get('nonexistent', 'fallback') == 'fallback'
    
    def test_update_and_set(self):
        """설정 업데이트 테스트"""
        handler = ConfigHandler()
        
        handler.set('new_key', 'new_value')
        assert handler.get('new_key') == 'new_value'
        
        handler.update({'key1': 'value1', 'key2': 'value2'})
        assert handler.get('key1') == 'value1'
        assert handler.get('key2') == 'value2'
    
    def test_as_namespace(self):
        """네임스페이스 변환 테스트"""
        handler = ConfigHandler(defaults={'test': 'value'})
        ns = handler.as_namespace()
        assert isinstance(ns, NestedNamespace)
        assert ns.test == 'value'


class TestPawnStackConfig:
    """PawnStackConfig 클래스 테스트"""
    
    def test_singleton_pattern(self):
        """싱글톤 패턴 테스트"""
        config1 = PawnStackConfig()
        config2 = PawnStackConfig()
        assert config1 is config2
    
    def test_basic_get_set(self):
        """기본 get/set 테스트"""
        config = PawnStackConfig()
        config.set(test_key="test_value")
        assert config.get("test_key") == "test_value"
    
    def test_str2bool(self):
        """문자열 불린 변환 테스트"""
        assert PawnStackConfig.str2bool("true") is True
        assert PawnStackConfig.str2bool("false") is False
        assert PawnStackConfig.str2bool("yes") is True
        assert PawnStackConfig.str2bool("no") is False
        assert PawnStackConfig.str2bool(True) is True
        assert PawnStackConfig.str2bool(False) is False
    
    def test_increase_decrease(self):
        """증가/감소 테스트"""
        config = PawnStackConfig()
        
        # 증가 테스트
        config.set(counter=10)
        result = config.increase(counter=5)
        assert result == 15
        assert config.get("counter") == 15
        
        # 감소 테스트
        result = config.decrease(counter=3)
        assert result == 12
        assert config.get("counter") == 12
    
    def test_list_operations(self):
        """리스트 연산 테스트"""
        config = PawnStackConfig()
        
        # 리스트에 추가
        config.set(items=[])
        config.append_list(items="item1")
        config.append_list(items="item2")
        assert config.get("items") == ["item1", "item2"]
        
        # 리스트에서 제거
        config.remove_list(items="item1")
        assert config.get("items") == ["item2"]
    
    def test_data_namespace(self):
        """데이터 네임스페이스 테스트"""
        config = PawnStackConfig()
        test_data = {"nested": {"value": "test"}}
        config.set(data=test_data)
        
        assert isinstance(config.data, NestedNamespace)
        assert config.data.nested.value == "test"
    
    def test_conf_method(self):
        """conf 메서드 테스트"""
        config = PawnStackConfig()
        config.set(test="value")
        
        conf = config.conf()
        assert isinstance(conf, NestedNamespace)
        assert conf.test == "value"
    
    def test_to_dict_method(self):
        """to_dict 메서드 테스트"""
        config = PawnStackConfig()
        config.set(test="value", number=42)
        
        result = config.to_dict()
        assert isinstance(result, dict)
        assert result["test"] == "value"
        assert result["number"] == 42
    
    @patch.dict(os.environ, {
        'PAWN_DEBUG': 'true',
        'PAWN_TIMEOUT': '5000'
    })
    def test_environment_variables(self):
        """환경변수 처리 테스트"""
        config = PawnStackConfig()
        config.fill_config_from_environment()
        
        assert config.get('PAWN_DEBUG') is True
        assert config.get('PAWN_TIMEOUT') == 5000


class TestGlobalInstances:
    """전역 인스턴스 테스트"""
    
    def test_global_config_instance(self):
        """전역 설정 인스턴스 테스트"""
        assert isinstance(pawnstack_config, PawnStackConfig)
        assert pawn is pawnstack_config
    
    def test_global_config_functionality(self):
        """전역 설정 기능 테스트"""
        pawn.set(global_test="global_value")
        assert pawn.get("global_test") == "global_value"
        
        # 다른 참조로도 접근 가능한지 확인
        assert pawnstack_config.get("global_test") == "global_value"


class TestLegacyCompatibility:
    """레거시 호환성 테스트"""
    
    def test_time_format_compatibility(self):
        """시간 포맷 레거시 호환성 테스트"""
        config = PawnStackConfig()
        
        # 기본 시간 포맷 테스트
        assert config.log_time_format is None
        
        # 커스텀 시간 포맷 설정
        config.set(PAWN_CONSOLE={'log_time_format': '%H:%M:%S.%f'})
        assert config.log_time_format == '%H:%M:%S.%f'
    
    def test_legacy_aliases(self):
        """레거시 별칭 테스트"""
        from pawnstack.config.global_config import pconf, global_verbose
        
        # pconf 함수 테스트
        conf_result = pconf()
        assert isinstance(conf_result, NestedNamespace)
        
        # global_verbose 변수 테스트
        assert isinstance(global_verbose, int)
    
    def test_verbose_functionality(self):
        """Verbose 기능 테스트"""
        config = PawnStackConfig()
        
        # 기본 verbose 레벨
        assert config.verbose == 0
        
        # verbose 레벨 설정
        config.set(PAWN_VERBOSE=3)
        assert config.get('PAWN_VERBOSE') == 3
        assert config.verbose == 3
    
    def test_logger_configuration(self):
        """로거 설정 테스트 (레거시 호환)"""
        config = PawnStackConfig()
        
        # 로거 설정 (시뮬레이션)
        logger_config = {
            'app_name': 'Test Logger',
            'log_level': 'DEBUG',
            'stdout': True
        }
        
        config.set(PAWN_LOGGER=logger_config)
        assert config.get('PAWN_LOGGER') == logger_config
    
    def test_console_configuration(self):
        """콘솔 설정 테스트 (레거시 호환)"""
        config = PawnStackConfig()
        
        # 콘솔 설정
        console_config = {
            'log_time_format': '%Y-%m-%d %H:%M:%S.%f',
            'record': True,
            'soft_wrap': False
        }
        
        config.set(PAWN_CONSOLE=console_config)
        assert config.console_options == console_config
        assert config._loaded['console'] is True
    
    def test_priority_keys_ordering(self):
        """우선순위 키 순서 테스트"""
        config = PawnStackConfig()
        
        # 우선순위 키들이 먼저 처리되는지 테스트
        config.set(
            normal_key="normal",
            PAWN_DEBUG=True,
            PAWN_PATH="/test/path",
            another_key="another"
        )
        
        assert config.get('PAWN_DEBUG') is True
        assert config.get('PAWN_PATH') == "/test/path"
        assert config.get('normal_key') == "normal"
        assert config.get('another_key') == "another"


if __name__ == "__main__":
    pytest.main([__file__])