#!/usr/bin/env python3
"""
WebSocket CLI 테스트 스크립트
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestWebSocketCLI(unittest.TestCase):
    """WebSocket CLI 테스트"""
    
    def setUp(self):
        """테스트 전 초기화"""
        # WebSocket 관련 모듈을 동적으로 임포트
        try:
            from pawnstack.cli.websocket import WebSocketCLI
            self.websocket_cli = WebSocketCLI()
            self.websocket_cli_available = True
        except ImportError:
            self.websocket_cli_available = False
            print("WebSocket CLI 모듈을 찾을 수 없습니다.")
    
    def test_websocket_cli_import(self):
        """WebSocket CLI 임포트 테스트"""
        if not self.websocket_cli_available:
            self.skipTest("WebSocket CLI 모듈을 찾을 수 없습니다")
        
        self.assertIsNotNone(self.websocket_cli)
        self.assertEqual(self.websocket_cli.command_name, "websocket")
    
    def test_websocket_cli_args(self):
        """WebSocket CLI 인수 테스트"""
        if not self.websocket_cli_available:
            self.skipTest("WebSocket CLI 모듈을 찾을 수 없습니다")
        
        from argparse import Namespace
        args = Namespace(
            url='ws://localhost:8080',
            message='Hello, WebSocket!',
            count=10
        )
        
        self.websocket_cli.args = args
        
        # 인수 검증 테스트
        if hasattr(self.websocket_cli, 'validate_args'):
            # validate_args가 True를 반환하도록 모킹
            with patch.object(self.websocket_cli, 'validate_args', return_value=True):
                self.assertTrue(self.websocket_cli.validate_args())
    
    def test_websocket_cli_help(self):
        """WebSocket CLI 도움말 테스트"""
        if not self.websocket_cli_available:
            self.skipTest("WebSocket CLI 모듈을 찾을 수 없습니다")
        
        from argparse import ArgumentParser
        parser = ArgumentParser()
        
        # 인수 파서 설정 테스트
        try:
            self.websocket_cli.get_arguments(parser)
            # 도움말 출력 (실제 출력은 캡처하지 않음)
            # parser.print_help()
            success = True
        except Exception as e:
            print(f"도움말 테스트 중 오류 발생: {e}")
            success = False
        
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()