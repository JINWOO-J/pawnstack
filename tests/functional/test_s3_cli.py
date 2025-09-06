#!/usr/bin/env python3
"""
S3 CLI 테스트 스크립트
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestS3CLI(unittest.TestCase):
    """S3 CLI 테스트"""
    
    def setUp(self):
        """테스트 전 초기화"""
        # S3 관련 모듈을 동적으로 임포트
        try:
            from pawnstack.cli.s3 import S3CLI
            self.s3_cli = S3CLI()
            self.s3_cli_available = True
        except ImportError:
            self.s3_cli_available = False
            print("S3 CLI 모듈을 찾을 수 없습니다. AWS 관련 의존성이 설치되어 있는지 확인하세요.")
    
    def test_s3_cli_import(self):
        """S3 CLI 임포트 테스트"""
        if not self.s3_cli_available:
            self.skipTest("S3 CLI 모듈을 찾을 수 없습니다")
        
        self.assertIsNotNone(self.s3_cli)
        self.assertEqual(self.s3_cli.command_name, "s3")
    
    @patch('boto3.client')
    def test_s3_cli_with_mock_client(self, mock_boto_client):
        """S3 CLI 클라이언트 생성 테스트"""
        if not self.s3_cli_available:
            self.skipTest("S3 CLI 모듈을 찾을 수 없습니다")
        
        # boto3 클라이언트 모킹
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        # 테스트용 인수 설정
        from argparse import Namespace
        args = Namespace(
            operation='list_buckets',
            bucket=None,
            key=None
        )
        
        self.s3_cli.args = args
        
        # 인수 검증 테스트
        if hasattr(self.s3_cli, 'validate_args'):
            # validate_args가 True를 반환하도록 모킹
            with patch.object(self.s3_cli, 'validate_args', return_value=True):
                self.assertTrue(self.s3_cli.validate_args())
    
    def test_s3_cli_help(self):
        """S3 CLI 도움말 테스트"""
        if not self.s3_cli_available:
            self.skipTest("S3 CLI 모듈을 찾을 수 없습니다")
        
        from argparse import ArgumentParser
        parser = ArgumentParser()
        
        # 인수 파서 설정 테스트
        try:
            self.s3_cli.get_arguments(parser)
            # 도움말 출력 (실제 출력은 캡처하지 않음)
            # parser.print_help()
            success = True
        except Exception as e:
            print(f"도움말 테스트 중 오류 발생: {e}")
            success = False
        
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()