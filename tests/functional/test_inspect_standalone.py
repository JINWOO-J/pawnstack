#!/usr/bin/env python3
"""
Inspect CLI 독립 실행 테스트
"""

import sys
import os
import json
from argparse import ArgumentParser
from urllib.parse import urlparse

# 간단한 Mock 클래스들
class MockConsole:
    @staticmethod
    def log(msg):
        print(msg)

    @staticmethod
    def print(obj):
        print(obj)

class MockPawn:
    console = MockConsole()

class HTTPBaseCLI:
    def __init__(self, args=None):
        self.args = args or type('Args', (), {})()
        self.command_name = "inspect"
        self.description = "URL 검사를 위한 포괄적인 도구 (DNS, HTTP, SSL)"

        # 검사 명령어 정의
        self.commands = {"dns", "http", "ssl", "all"}
        self.root_commands = {"inspect"}

        # 종료 코드 정의
        self.EXIT_OK = 0
        self.EXIT_DNS_FAIL = 10
        self.EXIT_HTTP_FAIL = 11
        self.EXIT_SSL_FAIL = 12

    def log_info(self, msg): print(f"ℹ️  {msg}")
    def log_success(self, msg): print(f"✅ {msg}")
    def log_warning(self, msg): print(f"⚠️  {msg}")
    def log_error(self, msg): print(f"❌ {msg}")
    def log_debug(self, msg): print(f"🐛 {msg}")

    def main(self):
        return self.run()

class DependencyChecker:
    @staticmethod
    def check_dependencies(extras):
        return True

# Mock pawn 객체
pawn = MockPawn()

class InspectCLI(HTTPBaseCLI):
    """URL 검사 CLI 명령어"""

    def get_arguments(self, parser: ArgumentParser):
        """명령어별 인수 정의"""

        # 서브커맨드 파서 생성
        subparsers = parser.add_subparsers(
            dest='command',
            help='검사 유형 선택',
            metavar='COMMAND'
        )

        # 공통 인수 파서
        common_parser = ArgumentParser(add_help=False)
        self._add_common_arguments(common_parser)

        # 각 서브커맨드 추가
        subparsers.add_parser(
            'dns',
            parents=[common_parser],
            help='DNS 레코드 검사',
            description='도메인의 DNS 레코드를 조회하고 분석합니다'
        )

        subparsers.add_parser(
            'http',
            parents=[common_parser],
            help='HTTP 요청 검사',
            description='HTTP 요청을 수행하고 응답을 분석합니다'
        )

        subparsers.add_parser(
            'ssl',
            parents=[common_parser],
            help='SSL 인증서 검사',
            description='SSL/TLS 인증서를 검사하고 유효성을 확인합니다'
        )

        subparsers.add_parser(
            'all',
            parents=[common_parser],
            help='모든 검사 수행',
            description='DNS, HTTP, SSL 검사를 모두 수행합니다'
        )

        return parser

    def _add_common_arguments(self, parser: ArgumentParser):
        """공통 인수 추가"""

        # 필수 인수
        parser.add_argument(
            'url',
            help='검사할 URL',
            nargs='?',
            default=""
        )

        # HTTP 관련 옵션
        parser.add_argument(
            '-m', '--method',
            type=str,
            default='GET',
            help='HTTP 메서드 (default: GET)'
        )

        parser.add_argument(
            '-t', '--timeout',
            type=float,
            default=10.0,
            help='요청 타임아웃 (초, default: 10)'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제 HTTP 요청 없이 드라이 런 수행'
        )

        parser.add_argument(
            '-v', '--verbose',
            action='count',
            default=1,
            help='상세 출력 모드 (반복 사용 시 더 상세)'
        )

    def validate_args(self) -> bool:
        """인수 검증"""
        if not self.args.url:
            self.log_error("URL이 필요합니다")
            return False

        # URL 형식 검증
        parsed_url = urlparse(self.args.url)
        if not parsed_url.scheme and not parsed_url.netloc:
            # 스키마가 없는 경우 http:// 추가
            self.args.url = f"http://{self.args.url}"
            parsed_url = urlparse(self.args.url)

        if not parsed_url.netloc:
            self.log_error(f"유효하지 않은 URL 형식: {self.args.url}")
            return False

        return True

    def run(self) -> int:
        """명령어 실행"""
        if not self.validate_args():
            return 1

        # 명령어 결정
        command = getattr(self.args, 'command', 'all')
        if command in ("dns", "http", "ssl"):
            needs = {command}
        else:
            needs = {"dns", "http", "ssl"}

        self.log_info(f"검사 유형: {', '.join(sorted(needs))}")

        # URL 파싱
        parsed_url = urlparse(self.args.url)
        domain = parsed_url.netloc or parsed_url.path

        # 검사 실행
        return self._handle_inspect(needs, domain, parsed_url)

    def _handle_inspect(self, needs, domain, parsed_url):
        """검사 처리"""

        # DNS 검사
        if "dns" in needs:
            if not self._check_dns(domain):
                return self.EXIT_DNS_FAIL

        # SSL 검사
        if "ssl" in needs:
            if not self._check_ssl(domain, parsed_url):
                return self.EXIT_SSL_FAIL

        # HTTP 검사
        if "http" in needs:
            if not self._check_http(parsed_url):
                return self.EXIT_HTTP_FAIL

        return self.EXIT_OK

    def _check_dns(self, domain: str) -> bool:
        """DNS 검사"""
        try:
            import socket

            pawn.console.log("🔍 DNS 레코드 검사 중...")

            # 기본 IP 주소 조회
            try:
                ip_address = socket.gethostbyname(domain)
                self.log_success(f"IP 주소: {ip_address}")
                return True
            except socket.gaierror as e:
                self.log_error(f"DNS 조회 실패: {e}")
                return False

        except Exception as e:
            self.log_error(f"DNS 검사 중 오류 발생: {e}")
            return False

    def _check_ssl(self, domain: str, parsed_url) -> bool:
        """SSL 검사"""
        if not parsed_url.scheme.startswith('https'):
            self.log_warning("SSL 검사는 HTTPS URL에서만 지원됩니다")
            return True

        try:
            import ssl
            import socket
            from datetime import datetime

            pawn.console.log("🔒 SSL 인증서 검사 중...")

            # SSL 컨텍스트 생성
            context = ssl.create_default_context()

            # SSL 연결 및 인증서 정보 조회
            port = parsed_url.port or 443

            with socket.create_connection((domain, port), timeout=self.args.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()

                    if cert:
                        # 인증서 정보 표시
                        self.log_success("SSL 인증서 정보:")

                        # 주체 정보
                        subject = dict(x[0] for x in cert['subject'])
                        pawn.console.log(f"  • 주체: {subject.get('commonName', 'N/A')}")

                        # 발급자 정보
                        issuer = dict(x[0] for x in cert['issuer'])
                        pawn.console.log(f"  • 발급자: {issuer.get('commonName', 'N/A')}")

                        # 유효 기간
                        not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')

                        pawn.console.log(f"  • 유효 시작: {not_before}")
                        pawn.console.log(f"  • 유효 만료: {not_after}")

                        # 만료일 확인
                        now = datetime.now()
                        if now > not_after:
                            self.log_error("인증서가 만료되었습니다")
                            return False
                        elif (not_after - now).days < 30:
                            self.log_warning(f"인증서가 {(not_after - now).days}일 후 만료됩니다")

                    return True

        except ssl.SSLError as e:
            self.log_error(f"SSL 오류: {e}")
            return False
        except socket.timeout:
            self.log_error("SSL 연결 타임아웃")
            return False
        except Exception as e:
            self.log_error(f"SSL 검사 중 오류 발생: {e}")
            return False

    def _check_http(self, parsed_url) -> bool:
        """HTTP 검사"""
        if self.args.dry_run:
            self.log_warning("드라이 런 모드: HTTP 요청을 수행하지 않습니다")
            return True

        try:
            import urllib.request
            import urllib.error
            import time
            import socket

            pawn.console.log("🌐 HTTP 요청 수행 중...")

            # 요청 설정
            url = parsed_url.geturl()

            # 요청 수행
            start_time = time.time()

            try:
                with urllib.request.urlopen(url, timeout=self.args.timeout) as response:
                    content = response.read()

                    # 응답 정보 표시
                    status_code = response.getcode()
                    status_color = "✅" if 200 <= status_code < 300 else "❌"
                    pawn.console.log(f"{status_color} 응답 코드: {status_code}")

                    # 응답 시간
                    elapsed = time.time() - start_time
                    pawn.console.log(f"응답 시간: {elapsed:.3f}초")

                    # 응답 크기
                    content_length = len(content)
                    pawn.console.log(f"응답 크기: {content_length:,} 바이트")

                    # 헤더 정보 (상세 모드)
                    if self.args.verbose > 1:
                        pawn.console.log("응답 헤더:")
                        for header, value in response.headers.items():
                            pawn.console.log(f"  • {header}: {value}")

                    return True

            except urllib.error.HTTPError as e:
                status_color = "❌" if e.code >= 400 else "⚠️"
                pawn.console.log(f"{status_color} HTTP 오류: {e.code} {e.reason}")
                return e.code < 500  # 4xx는 성공으로 간주 (클라이언트 오류)

        except urllib.error.URLError as e:
            self.log_error(f"URL 오류: {e.reason}")
            return False
        except socket.timeout:
            self.log_error("HTTP 요청 타임아웃")
            return False
        except Exception as e:
            self.log_error(f"HTTP 검사 중 오류 발생: {e}")
            return False


def main():
    """메인 함수"""
    from argparse import RawDescriptionHelpFormatter

    parser = ArgumentParser(
        description="URL 검사를 위한 포괄적인 도구 (DNS, HTTP, SSL)",
        formatter_class=RawDescriptionHelpFormatter
    )

    cli = InspectCLI()
    cli.get_arguments(parser)

    # 인수 파싱
    args = parser.parse_args()
    cli.args = args

    # 실행
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())
