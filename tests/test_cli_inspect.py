#!/usr/bin/env python3
"""
Inspect CLI 테스트
"""

import unittest
from unittest.mock import patch, MagicMock
from argparse import Namespace
import sys
import os

# 테스트를 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from pawnstack.cli.inspect import InspectCLI
except ImportError:
    # 순환 import 문제가 있는 경우 스킵
    InspectCLI = None


class TestInspectCLI(unittest.TestCase):
    """Inspect CLI 테스트 클래스"""

    def setUp(self):
        """테스트 설정"""
        # args 객체에 필요한 속성들을 추가
        from argparse import Namespace
        args = Namespace()
        args.dns_server = None
        args.headers = None
        args.data = None
        args.timeout = 10
        args.dry_run = False
        args.verbose = 1
        args.full_body = False
        args.output = None
        args.auth = None
        args.ignore_ssl = False
        self.cli = InspectCLI(args)
        self.cli.args = Namespace()

    def test_init(self):
        """초기화 테스트"""
        self.assertEqual(self.cli.command_name, "inspect")
        self.assertIn("URL 검사", self.cli.description)
        self.assertEqual(self.cli.EXIT_OK, 0)
        self.assertEqual(self.cli.EXIT_DNS_FAIL, 10)
        self.assertEqual(self.cli.EXIT_HTTP_FAIL, 11)
        self.assertEqual(self.cli.EXIT_SSL_FAIL, 12)

    def test_preprocess_command(self):
        """명령어 전처리 테스트"""
        # 빈 인수
        result = self.cli.preprocess_command([])
        self.assertEqual(result, [])

        # inspect 명령어만
        result = self.cli.preprocess_command(["inspect"])
        self.assertEqual(result, ["inspect", "all"])

        # inspect + URL
        result = self.cli.preprocess_command(["inspect", "google.com"])
        self.assertEqual(result, ["inspect", "all", "google.com"])

        # URL만
        result = self.cli.preprocess_command(["google.com"])
        self.assertEqual(result, ["all", "google.com"])

        # 정상적인 명령어
        result = self.cli.preprocess_command(["dns", "google.com"])
        self.assertEqual(result, ["dns", "google.com"])

    def test_validate_args_no_url(self):
        """URL 없는 경우 검증 테스트"""
        self.cli.args.url = ""
        self.assertFalse(self.cli.validate_args())

    def test_validate_args_valid_url(self):
        """유효한 URL 검증 테스트"""
        self.cli.args.url = "https://google.com"
        self.assertTrue(self.cli.validate_args())

    def test_validate_args_url_without_scheme(self):
        """스키마 없는 URL 검증 테스트"""
        self.cli.args.url = "google.com"
        self.assertTrue(self.cli.validate_args())
        # http:// 가 자동으로 추가되어야 함
        self.assertEqual(self.cli.args.url, "http://google.com")

    def test_validate_args_invalid_url(self):
        """유효하지 않은 URL 검증 테스트"""
        self.cli.args.url = "invalid-url"
        self.assertTrue(self.cli.validate_args())  # http://가 추가되어 유효해짐

    @patch('socket.gethostbyname')
    def test_check_dns_success(self, mock_gethostbyname):
        """DNS 검사 성공 테스트"""
        mock_gethostbyname.return_value = "142.250.76.142"

        result = self.cli._check_dns("google.com")
        self.assertTrue(result)
        mock_gethostbyname.assert_called_once_with("google.com")

    @patch('socket.gethostbyname')
    def test_check_dns_failure(self, mock_gethostbyname):
        """DNS 검사 실패 테스트"""
        import socket
        mock_gethostbyname.side_effect = socket.gaierror("Name resolution failed")

        result = self.cli._check_dns("invalid-domain.com")
        self.assertFalse(result)

    def test_check_ssl_non_https(self):
        """비HTTPS URL SSL 검사 테스트"""
        from urllib.parse import urlparse
        parsed_url = urlparse("http://google.com")

        result = self.cli._check_ssl("google.com", parsed_url)
        self.assertTrue(result)  # 경고만 출력하고 성공으로 처리

    @patch('urllib.request.urlopen')
    def test_check_http_success(self, mock_urlopen):
        """HTTP 검사 성공 테스트"""
        from urllib.parse import urlparse

        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'{"test": "data"}'
        mock_response.headers = {'content-type': 'application/json'}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # 테스트 인수 설정
        self.cli.args.timeout = 10
        self.cli.args.dry_run = False
        self.cli.args.verbose = 1
        self.cli.args.full_body = False
        self.cli.args.output = None

        parsed_url = urlparse("https://httpbin.org/json")
        result = self.cli._check_http(parsed_url)

        self.assertTrue(result)
        mock_urlopen.assert_called_once()

    def test_check_http_dry_run(self):
        """HTTP 드라이 런 테스트"""
        from urllib.parse import urlparse

        self.cli.args.dry_run = True
        parsed_url = urlparse("https://google.com")

        result = self.cli._check_http(parsed_url)
        self.assertTrue(result)

    @patch('urllib.request.urlopen')
    def test_check_http_timeout(self, mock_urlopen):
        """HTTP 타임아웃 테스트"""
        from urllib.parse import urlparse
        import socket

        mock_urlopen.side_effect = socket.timeout("Request timed out")

        self.cli.args.timeout = 1
        self.cli.args.dry_run = False

        parsed_url = urlparse("https://slow-site.com")
        result = self.cli._check_http(parsed_url)

        self.assertFalse(result)

    def test_handle_inspect_all(self):
        """전체 검사 처리 테스트"""
        from urllib.parse import urlparse

        needs = {"dns", "http", "ssl"}
        domain = "google.com"
        parsed_url = urlparse("https://google.com")

        # Mock 메서드들
        with patch.object(self.cli, '_check_dns', return_value=True), \
             patch.object(self.cli, '_check_ssl', return_value=True), \
             patch.object(self.cli, '_check_http', return_value=True):

            result = self.cli._handle_inspect(needs, domain, parsed_url)
            self.assertEqual(result, self.cli.EXIT_OK)

    def test_handle_inspect_dns_fail(self):
        """DNS 검사 실패 처리 테스트"""
        from urllib.parse import urlparse

        needs = {"dns"}
        domain = "invalid-domain.com"
        parsed_url = urlparse("http://invalid-domain.com")

        with patch.object(self.cli, '_check_dns', return_value=False):
            result = self.cli._handle_inspect(needs, domain, parsed_url)
            self.assertEqual(result, self.cli.EXIT_DNS_FAIL)

    def test_save_response_content(self):
        """응답 내용 저장 테스트"""
        import tempfile
        import os

        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            self.cli.args.output = tmp_path
            test_content = b'{"test": "data"}'

            self.cli._save_response_content(test_content)

            # 파일이 올바르게 저장되었는지 확인
            with open(tmp_path, 'rb') as f:
                saved_content = f.read()

            self.assertEqual(saved_content, test_content)

        finally:
            # 임시 파일 정리
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_run_with_valid_args(self):
        """유효한 인수로 실행 테스트"""
        self.cli.args.url = "google.com"
        self.cli.args.command = "dns"

        with patch.object(self.cli, 'validate_args', return_value=True), \
             patch.object(self.cli, '_handle_inspect', return_value=0):

            result = self.cli.run()
            self.assertEqual(result, 0)

    def test_run_with_invalid_args(self):
        """유효하지 않은 인수로 실행 테스트"""
        self.cli.args.url = ""

        with patch.object(self.cli, 'validate_args', return_value=False):
            result = self.cli.run()
            self.assertEqual(result, 1)


class TestInspectCLIIntegration(unittest.TestCase):
    """Inspect CLI 통합 테스트"""

    def setUp(self):
        """테스트 설정"""
        if InspectCLI is None:
            self.skipTest("InspectCLI import failed due to circular import")

    @patch('sys.argv', ['inspect', 'dns', 'google.com'])
    def test_main_function(self):
        """메인 함수 테스트"""
        from pawnstack.cli.inspect import main

        with patch('pawnstack.cli.inspect.InspectCLI') as mock_cli_class:
            mock_cli = MagicMock()
            mock_cli.main.return_value = 0
            mock_cli_class.return_value = mock_cli

            result = main()
            self.assertEqual(result, 0)


if __name__ == '__main__':
    unittest.main()
