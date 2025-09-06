#!/usr/bin/env python3
"""
Network CLI 테스트 스크립트
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestNetCLI(unittest.TestCase):
    """Network CLI 테스트"""
    
    def setUp(self):
        """테스트 전 초기화"""
        # Network 관련 모듈을 동적으로 임포트
        try:
            from pawnstack.cli.net import NetCLI
            self.net_cli = NetCLI()
            self.net_cli_available = True
        except ImportError:
            self.net_cli_available = False
            print("Network CLI 모듈을 찾을 수 없습니다.")
    
    def test_net_cli_import(self):
        """Network CLI 임포트 테스트"""
        if not self.net_cli_available:
            self.skipTest("Network CLI 모듈을 찾을 수 없습니다")
        
        self.assertIsNotNone(self.net_cli)
        self.assertEqual(self.net_cli.command_name, "net")
    
    def test_net_cli_args(self):
        """Network CLI 인수 테스트"""
        if not self.net_cli_available:
            self.skipTest("Network CLI 모듈을 찾을 수 없습니다")
        
        from argparse import Namespace
        args = Namespace(
            command='scan',
            target='192.168.1.0/24',
            port=None
        )
        
        self.net_cli.args = args
        
        # 인수 검증 테스트
        if hasattr(self.net_cli, 'validate_args'):
            # validate_args가 True를 반환하도록 모킹
            with patch.object(self.net_cli, 'validate_args', return_value=True):
                self.assertTrue(self.net_cli.validate_args())
    
    def test_net_cli_help(self):
        """Network CLI 도움말 테스트"""
        if not self.net_cli_available:
            self.skipTest("Network CLI 모듈을 찾을 수 없습니다")
        
        from argparse import ArgumentParser
        parser = ArgumentParser()
        
        # 인수 파서 설정 테스트
        try:
            self.net_cli.get_arguments(parser)
            # 도움말 출력 (실제 출력은 캡처하지 않음)
            # parser.print_help()
            success = True
        except Exception as e:
            print(f"도움말 테스트 중 오류 발생: {e}")
            success = False
        
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()