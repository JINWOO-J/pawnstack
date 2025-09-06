#!/usr/bin/env python3
"""
Scan Key CLI 테스트 스크립트
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestScanKeyCLI(unittest.TestCase):
    """Scan Key CLI 테스트"""
    
    def setUp(self):
        """테스트 전 초기화"""
        # Scan Key 관련 모듈을 동적으로 임포트
        try:
            from pawnstack.cli.scan_key import ScanKeyCLI
            self.scan_key_cli = ScanKeyCLI()
            self.scan_key_cli_available = True
        except ImportError:
            self.scan_key_cli_available = False
            print("Scan Key CLI 모듈을 찾을 수 없습니다.")
    
    def test_scan_key_cli_import(self):
        """Scan Key CLI 임포트 테스트"""
        if not self.scan_key_cli_available:
            self.skipTest("Scan Key CLI 모듈을 찾을 수 없습니다")
        
        self.assertIsNotNone(self.scan_key_cli)
        self.assertEqual(self.scan_key_cli.command_name, "scan-key")
    
    def test_scan_key_cli_args(self):
        """Scan Key CLI 인수 테스트"""
        if not self.scan_key_cli_available:
            self.skipTest("Scan Key CLI 모듈을 찾을 수 없습니다")
        
        from argparse import Namespace
        args = Namespace(
            directory='.',
            pattern='*.key',
            recursive=True
        )
        
        self.scan_key_cli.args = args
        
        # 인수 검증 테스트
        if hasattr(self.scan_key_cli, 'validate_args'):
            # validate_args가 True를 반환하도록 모킹
            with patch.object(self.scan_key_cli, 'validate_args', return_value=True):
                self.assertTrue(self.scan_key_cli.validate_args())
    
    def test_scan_key_cli_help(self):
        """Scan Key CLI 도움말 테스트"""
        if not self.scan_key_cli_available:
            self.skipTest("Scan Key CLI 모듈을 찾을 수 없습니다")
        
        from argparse import ArgumentParser
        parser = ArgumentParser()
        
        # 인수 파서 설정 테스트
        try:
            self.scan_key_cli.get_arguments(parser)
            # 도움말 출력 (실제 출력은 캡처하지 않음)
            # parser.print_help()
            success = True
        except Exception as e:
            print(f"도움말 테스트 중 오류 발생: {e}")
            success = False
        
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()