"""
PawnStack CLI 테스트
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from argparse import Namespace

from pawnstack.cli.main import (
    get_submodule_names,
    get_module_name,
    parse_args,
    load_cli_module
)
from pawnstack.cli.base import BaseCLI, AsyncBaseCLI
from pawnstack.cli.parser import CustomArgumentParser, OrderedNamespace
from pawnstack.cli.formatter import ColoredHelpFormatter
from pawnstack.cli.banner import generate_banner, generate_simple_banner
from pawnstack.cli.info import InfoCLI
from pawnstack.cli.banner import BannerCLI


class TestCLIMain:
    """CLI 메인 기능 테스트"""
    
    def test_get_module_name(self):
        """모듈명 추출 테스트"""
        assert get_module_name("/path/to/test.py") == "test"
        assert get_module_name("example.py") == "example"
    
    def test_get_submodule_names(self):
        """하위 모듈 이름 목록 테스트"""
        modules = get_submodule_names()
        assert isinstance(modules, list)
        # 기본 모듈들이 제외되었는지 확인
        assert "main" not in modules
        assert "base" not in modules
        assert "parser" not in modules
        assert "formatter" not in modules


class TestBaseCLI:
    """BaseCLI 클래스 테스트"""
    
    def test_base_cli_creation(self):
        """BaseCLI 생성 테스트"""
        
        class TestCLI(BaseCLI):
            def get_arguments(self, parser):
                parser.add_argument('--test', help='Test argument')
            
            def run(self):
                return 0
        
        cli = TestCLI()
        assert cli.command_name == "test"
        assert hasattr(cli, 'start_time')
    
    def test_base_cli_with_args(self):
        """인수가 있는 BaseCLI 테스트"""
        
        class TestCLI(BaseCLI):
            def get_arguments(self, parser):
                parser.add_argument('--test', help='Test argument')
            
            def run(self):
                return 0
        
        args = Namespace(test="value")
        cli = TestCLI(args)
        assert cli.args.test == "value"
    
    def test_logging_methods(self):
        """로깅 메서드 테스트"""
        
        class TestCLI(BaseCLI):
            def get_arguments(self, parser):
                pass
            
            def run(self):
                self.log_info("Info message")
                self.log_success("Success message")
                self.log_warning("Warning message")
                self.log_error("Error message")
                self.log_debug("Debug message")
                return 0
        
        cli = TestCLI()
        # 로깅 메서드들이 오류 없이 실행되는지 확인
        result = cli.run()
        assert result == 0


class TestAsyncBaseCLI:
    """AsyncBaseCLI 클래스 테스트"""
    
    @pytest.mark.asyncio
    async def test_async_base_cli(self):
        """AsyncBaseCLI 테스트"""
        
        class TestAsyncCLI(AsyncBaseCLI):
            def get_arguments(self, parser):
                parser.add_argument('--test', help='Test argument')
            
            async def run_async(self):
                return 0
        
        cli = TestAsyncCLI()
        result = await cli.run_async()
        assert result == 0


class TestCustomArgumentParser:
    """CustomArgumentParser 테스트"""
    
    def test_parser_creation(self):
        """파서 생성 테스트"""
        parser = CustomArgumentParser(description="Test parser")
        assert parser.description == "Test parser"
    
    def test_global_arguments(self):
        """전역 인수 테스트"""
        parser = CustomArgumentParser()
        
        # 전역 인수들이 추가되었는지 확인
        help_text = parser.format_help()
        assert "--debug" in help_text
        assert "--verbose" in help_text
        assert "--config" in help_text
        assert "--no-color" in help_text


class TestOrderedNamespace:
    """OrderedNamespace 테스트"""
    
    def test_command_order_tracking(self):
        """명령어 순서 추적 테스트"""
        ns = OrderedNamespace()
        ns.first = "value1"
        ns.second = "value2"
        ns.third = "value3"
        
        assert ns.command_order == ["first", "second", "third"]
    
    def test_dash_replacement(self):
        """대시 치환 테스트"""
        ns = OrderedNamespace()
        setattr(ns, "test-key", "value")
        
        assert hasattr(ns, "test_key")
        assert ns.test_key == "value"


class TestBannerGeneration:
    """배너 생성 테스트"""
    
    def test_generate_banner(self):
        """배너 생성 테스트"""
        banner = generate_banner("TEST", "1.0.0", "Author")
        assert isinstance(banner, str)
        assert len(banner) > 0
    
    def test_generate_simple_banner(self):
        """간단한 배너 생성 테스트"""
        banner = generate_simple_banner("TEST", "1.0.0")
        assert isinstance(banner, str)
        assert "TEST" in banner
        assert "1.0.0" in banner
    
    def test_banner_with_different_fonts(self):
        """다양한 폰트로 배너 생성 테스트"""
        fonts = ["graffiti", "block", "simple"]
        
        for font in fonts:
            banner = generate_banner("TEST", "1.0.0", font=font)
            assert isinstance(banner, str)
            assert len(banner) > 0


class TestInfoCLI:
    """InfoCLI 테스트"""
    
    def test_info_cli_creation(self):
        """InfoCLI 생성 테스트"""
        cli = InfoCLI()
        assert cli.command_name == "info"
    
    def test_collect_info(self):
        """정보 수집 테스트"""
        cli = InfoCLI()
        info = cli.collect_info()
        
        assert isinstance(info, dict)
        assert "system" in info
        assert "network" in info
        assert "disk" in info
        
        # 시스템 정보 확인
        system_info = info["system"]
        assert "hostname" in system_info
        assert "machine" in system_info
    
    def test_info_with_system_only(self):
        """시스템 정보만 수집 테스트"""
        args = Namespace()
        cli = InfoCLI(args)
        info = cli.collect_info()
        
        # 시스템 정보가 포함되어야 함
        assert isinstance(info, dict)
        assert "system" in info


class TestBannerCLI:
    """BannerCLI 테스트"""
    
    def test_banner_cli_creation(self):
        """BannerCLI 생성 테스트"""
        cli = BannerCLI()
        assert cli.command_name == "banner"
    
    def test_banner_cli_run(self):
        """BannerCLI 실행 테스트"""
        args = Namespace(
            text="TEST",
            font="graffiti",
            style="cyan",
            version="1.0.0",
            author="Test",
            simple=False
        )
        cli = BannerCLI(args)
        
        # 출력을 캡처하기 위해 stdout을 모킹
        with patch('builtins.print') as mock_print:
            result = cli.run()
            assert result == 0
            mock_print.assert_called_once()
    
    def test_banner_cli_simple_mode(self):
        """BannerCLI 간단 모드 테스트"""
        args = Namespace(
            text="TEST",
            font="graffiti",
            style="cyan",
            version="1.0.0",
            author="Test",
            simple=True
        )
        cli = BannerCLI(args)
        
        with patch('builtins.print') as mock_print:
            result = cli.run()
            assert result == 0
            mock_print.assert_called_once()


class TestCLIIntegration:
    """CLI 통합 테스트"""
    
    @patch('sys.argv', ['test', 'info'])
    def test_info_command_integration(self):
        """info 명령어 통합 테스트"""
        from pawnstack.cli.info import main
        
        # main 함수가 오류 없이 실행되는지 확인
        try:
            result = main()
            # 정상 실행되면 0을 반환해야 함
            assert result == 0
        except SystemExit as e:
            # 도움말 출력 등으로 인한 정상 종료
            assert e.code in [0, None]
    
    @patch('sys.argv', ['test', 'banner'])
    def test_banner_command_integration(self):
        """banner 명령어 통합 테스트"""
        from pawnstack.cli.banner import main
        
        try:
            result = main()
            assert result == 0
        except SystemExit as e:
            assert e.code in [0, None]


if __name__ == "__main__":
    pytest.main([__file__])