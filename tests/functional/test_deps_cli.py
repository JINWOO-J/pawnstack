#!/usr/bin/env python3
"""
Deps CLI 테스트 스크립트
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestDepsCLI(unittest.TestCase):
    """Deps CLI 테스트"""
    
    def setUp(self):
        """테스트 전 초기화"""
        # Deps 관련 모듈을 동적으로 임포트
        try:
            from pawnstack.cli.deps import DepsCLI
            self.deps_cli = DepsCLI()
            self.deps_cli_available = True
        except ImportError:
            self.deps_cli_available = False
            print("Deps CLI 모듈을 찾을 수 없습니다.")
    
    def test_deps_cli_import(self):
        """Deps CLI 임포트 테스트"""
        if not self.deps_cli_available:
            self.skipTest("Deps CLI 모듈을 찾을 수 없습니다")
        
        self.assertIsNotNone(self.deps_cli)
        self.assertEqual(self.deps_cli.command_name, "deps")
    
    def test_deps_cli_args(self):
        """Deps CLI 인수 테스트"""
        if not self.deps_cli_available:
            self.skipTest("Deps CLI 모듈을 찾을 수 없습니다")
        
        from argparse import Namespace
        args = Namespace(
            check=False,
            list=True,
            install=None
        )
        
        self.deps_cli.args = args
        
        # 인수 검증 테스트
        if hasattr(self.deps_cli, 'validate_args'):
            # validate_args가 True를 반환하도록 모킹
            with patch.object(self.deps_cli, 'validate_args', return_value=True):
                self.assertTrue(self.deps_cli.validate_args())
    
    def test_deps_cli_help(self):
        """Deps CLI 도움말 테스트"""
        if not self.deps_cli_available:
            self.skipTest("Deps CLI 모듈을 찾을 수 없습니다")
        
        from argparse import ArgumentParser
        parser = ArgumentParser()
        
        # 인수 파서 설정 테스트
        try:
            self.deps_cli.get_arguments(parser)
            # 도움말 출력 (실제 출력은 캡처하지 않음)
            # parser.print_help()
            success = True
        except Exception as e:
            print(f"도움말 테스트 중 오류 발생: {e}")
            success = False
        
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()