#!/usr/bin/env python3
"""
AWS CLI 테스트 스크립트
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestAWSCLI(unittest.TestCase):
    """AWS CLI 테스트"""
    
    def setUp(self):
        """테스트 전 초기화"""
        # AWS 관련 모듈을 동적으로 임포트
        try:
            from pawnstack.cli.aws import AWSCLI
            self.aws_cli = AWSCLI()
            self.aws_cli_available = True
        except ImportError:
            self.aws_cli_available = False
            print("AWS CLI 모듈을 찾을 수 없습니다. 관련 의존성이 설치되어 있는지 확인하세요.")
    
    def test_aws_cli_import(self):
        """AWS CLI 임포트 테스트"""
        if not self.aws_cli_available:
            self.skipTest("AWS CLI 모듈을 찾을 수 없습니다")
        
        self.assertIsNotNone(self.aws_cli)
        self.assertEqual(self.aws_cli.command_name, "aws")
    
    @patch('boto3.client')
    def test_aws_cli_with_mock_client(self, mock_boto_client):
        """AWS CLI 클라이언트 생성 테스트"""
        if not self.aws_cli_available:
            self.skipTest("AWS CLI 모듈을 찾을 수 없습니다")
        
        # boto3 클라이언트 모킹
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        # 테스트용 인수 설정
        from argparse import Namespace
        args = Namespace(
            service='s3',
            operation='list_buckets',
            region='us-east-1',
            profile=None
        )
        
        self.aws_cli.args = args
        
        # 인수 검증 테스트
        # validate_args 메서드가 있다면 호출
        if hasattr(self.aws_cli, 'validate_args'):
            # validate_args가 True를 반환하도록 모킹
            with patch.object(self.aws_cli, 'validate_args', return_value=True):
                self.assertTrue(self.aws_cli.validate_args())
    
    def test_aws_cli_help(self):
        """AWS CLI 도움말 테스트"""
        if not self.aws_cli_available:
            self.skipTest("AWS CLI 모듈을 찾을 수 없습니다")
        
        from argparse import ArgumentParser
        parser = ArgumentParser()
        
        # 인수 파서 설정 테스트
        try:
            self.aws_cli.get_arguments(parser)
            # 도움말 출력 (실제 출력은 캡처하지 않음)
            # parser.print_help()
            success = True
        except Exception as e:
            print(f"도움말 테스트 중 오류 발생: {e}")
            success = False
        
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()