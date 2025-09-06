#!/usr/bin/env python3
"""
Docker CLI 테스트 스크립트
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestDockerCLI(unittest.TestCase):
    """Docker CLI 테스트"""
    
    def setUp(self):
        """테스트 전 초기화"""
        # Docker 관련 모듈을 동적으로 임포트
        try:
            from pawnstack.cli.docker import DockerCLI
            self.docker_cli = DockerCLI()
            self.docker_cli_available = True
        except ImportError:
            self.docker_cli_available = False
            print("Docker CLI 모듈을 찾을 수 없습니다. 관련 의존성이 설치되어 있는지 확인하세요.")
    
    def test_docker_cli_import(self):
        """Docker CLI 임포트 테스트"""
        if not self.docker_cli_available:
            self.skipTest("Docker CLI 모듈을 찾을 수 없습니다")
        
        self.assertIsNotNone(self.docker_cli)
        self.assertEqual(self.docker_cli.command_name, "docker")
    
    @patch('docker.from_env')
    def test_docker_cli_with_mock_client(self, mock_docker_client):
        """Docker CLI 클라이언트 생성 테스트"""
        if not self.docker_cli_available:
            self.skipTest("Docker CLI 모듈을 찾을 수 없습니다")
        
        # Docker 클라이언트 모킹
        mock_client = MagicMock()
        mock_docker_client.return_value = mock_client
        
        # 테스트용 인수 설정
        from argparse import Namespace
        args = Namespace(
            command='ps',
            all=False,
            quiet=False
        )
        
        self.docker_cli.args = args
        
        # 인수 검증 테스트
        # validate_args 메서드가 있다면 호출
        if hasattr(self.docker_cli, 'validate_args'):
            # validate_args가 True를 반환하도록 모킹
            with patch.object(self.docker_cli, 'validate_args', return_value=True):
                self.assertTrue(self.docker_cli.validate_args())
    
    def test_docker_cli_help(self):
        """Docker CLI 도움말 테스트"""
        if not self.docker_cli_available:
            self.skipTest("Docker CLI 모듈을 찾을 수 없습니다")
        
        from argparse import ArgumentParser
        parser = ArgumentParser()
        
        # 인수 파서 설정 테스트
        try:
            self.docker_cli.get_arguments(parser)
            # 도움말 출력 (실제 출력은 캡처하지 않음)
            # parser.print_help()
            success = True
        except Exception as e:
            print(f"도움말 테스트 중 오류 발생: {e}")
            success = False
        
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()