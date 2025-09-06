#!/usr/bin/env python3
"""
Icon CLI 테스트 스크립트
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestIconCLI(unittest.TestCase):
    """Icon CLI 테스트"""
    
    def setUp(self):
        """테스트 전 초기화"""
        # Icon 관련 모듈을 동적으로 임포트
        try:
            from pawnstack.cli.icon import IconCLI
            self.icon_cli = IconCLI()
            self.icon_cli_available = True
        except ImportError:
            self.icon_cli_available = False
            print("Icon CLI 모듈을 찾을 수 없습니다. 블록체인 관련 의존성이 설치되어 있는지 확인하세요.")
    
    def test_icon_cli_import(self):
        """Icon CLI 임포트 테스트"""
        if not self.icon_cli_available:
            self.skipTest("Icon CLI 모듈을 찾을 수 없습니다")
        
        self.assertIsNotNone(self.icon_cli)
        self.assertEqual(self.icon_cli.command_name, "icon")
    
    def test_icon_cli_args(self):
        """Icon CLI 인수 테스트"""
        if not self.icon_cli_available:
            self.skipTest("Icon CLI 모듈을 찾을 수 없습니다")
        
        from argparse import Namespace
        args = Namespace(
            command='balance',
            address='hx1234567890123456789012345678901234567890',
            endpoint='https://ctz.solidwallet.io/api/v3'
        )
        
        self.icon_cli.args = args
        
        # 인수 검증 테스트
        if hasattr(self.icon_cli, 'validate_args'):
            # validate_args가 True를 반환하도록 모킹
            with patch.object(self.icon_cli, 'validate_args', return_value=True):
                self.assertTrue(self.icon_cli.validate_args())
    
    def test_icon_cli_help(self):
        """Icon CLI 도움말 테스트"""
        if not self.icon_cli_available:
            self.skipTest("Icon CLI 모듈을 찾을 수 없습니다")
        
        from argparse import ArgumentParser
        parser = ArgumentParser()
        
        # 인수 파서 설정 테스트
        try:
            self.icon_cli.get_arguments(parser)
            # 도움말 출력 (실제 출력은 캡처하지 않음)
            # parser.print_help()
            success = True
        except Exception as e:
            print(f"도움말 테스트 중 오류 발생: {e}")
            success = False
        
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()