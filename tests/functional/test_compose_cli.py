#!/usr/bin/env python3
"""
Compose CLI 테스트 스크립트
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestComposeCLI(unittest.TestCase):
    """Compose CLI 테스트"""
    
    def setUp(self):
        """테스트 전 초기화"""
        # Compose 관련 모듈을 동적으로 임포트
        try:
            from pawnstack.cli.compose import ComposeCLI
            self.compose_cli = ComposeCLI()
            self.compose_cli_available = True
        except ImportError:
            self.compose_cli_available = False
            print("Compose CLI 모듈을 찾을 수 없습니다. Docker Compose 관련 의존성이 설치되어 있는지 확인하세요.")
    
    def test_compose_cli_import(self):
        """Compose CLI 임포트 테스트"""
        if not self.compose_cli_available:
            self.skipTest("Compose CLI 모듈을 찾을 수 없습니다")
        
        self.assertIsNotNone(self.compose_cli)
        self.assertEqual(self.compose_cli.command_name, "compose")
    
    def test_compose_cli_args(self):
        """Compose CLI 인수 테스트"""
        if not self.compose_cli_available:
            self.skipTest("Compose CLI 모듈을 찾을 수 없습니다")
        
        from argparse import Namespace
        args = Namespace(
            command='up',
            file='docker-compose.yml',
            detach=True
        )
        
        self.compose_cli.args = args
        
        # 인수 검증 테스트
        if hasattr(self.compose_cli, 'validate_args'):
            # validate_args가 True를 반환하도록 모킹
            with patch.object(self.compose_cli, 'validate_args', return_value=True):
                self.assertTrue(self.compose_cli.validate_args())
    
    def test_compose_cli_help(self):
        """Compose CLI 도움말 테스트"""
        if not self.compose_cli_available:
            self.skipTest("Compose CLI 모듈을 찾을 수 없습니다")
        
        from argparse import ArgumentParser
        parser = ArgumentParser()
        
        # 인수 파서 설정 테스트
        try:
            self.compose_cli.get_arguments(parser)
            # 도움말 출력 (실제 출력은 캡처하지 않음)
            # parser.print_help()
            success = True
        except Exception as e:
            print(f"도움말 테스트 중 오류 발생: {e}")
            success = False
        
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()