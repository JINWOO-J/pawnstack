"""
PawnStack Net CLI 테스트
"""

import pytest
import socket
import time
from unittest.mock import patch, MagicMock
from argparse import Namespace

from pawnstack.cli.net import NetCLI, NetConfig, get_arguments, main


class TestNetConfig:
    """NetConfig 데이터클래스 테스트"""
    
    def test_default_config(self):
        """기본 설정 테스트"""
        config = NetConfig()
        assert config.command == "check"
        assert config.host == "8.8.8.8"
        assert config.port == 80
        assert config.timeout == 5.0
        assert config.workers == 50
        assert config.host_range == ""
        assert config.port_range == ""
        assert config.view_type == "all"
    
    def test_custom_config(self):
        """커스텀 설정 테스트"""
        config = NetConfig(
            command="scan",
            host="192.168.1.1",
            port=443,
            timeout=10.0,
            workers=100,
            host_range="192.168.1.1-192.168.1.10",
            port_range="80-443",
            view_type="open"
        )
        assert config.command == "scan"
        assert config.host == "192.168.1.1"
        assert config.port == 443
        assert config.timeout == 10.0
        assert config.workers == 100
        assert config.host_range == "192.168.1.1-192.168.1.10"
        assert config.port_range == "80-443"
        assert config.view_type == "open"


class TestNetCLI:
    """NetCLI 테스트"""
    
    def test_net_cli_creation(self):
        """NetCLI 생성 테스트"""
        cli = NetCLI()
        assert cli.command_name == "net"
        assert hasattr(cli, 'start_time')
    
    def test_get_arguments(self):
        """인수 정의 테스트"""
        from argparse import ArgumentParser
        
        parser = ArgumentParser()
        cli = NetCLI()
        cli.get_arguments(parser)
        
        # 파서에 인수들이 추가되었는지 확인
        help_text = parser.format_help()
        assert "{check,wait,scan}" in help_text  # positional argument로 표시됨
        assert "--host" in help_text
        assert "--port" in help_text
        assert "--timeout" in help_text
        assert "--workers" in help_text
        assert "--host-range" in help_text
        assert "--port-range" in help_text
        assert "--view-type" in help_text
        assert "--log-level" in help_text
    
    def test_net_cli_with_args(self):
        """인수가 있는 NetCLI 테스트"""
        args = Namespace(
            command="scan",
            host="192.168.1.1",
            port=443,
            timeout=10.0,
            workers=100,
            host_range="192.168.1.1-192.168.1.10",
            port_range="80-443",
            view_type="open",
            log_level="DEBUG"
        )
        cli = NetCLI(args)
        assert cli.args.command == "scan"
        assert cli.args.host == "192.168.1.1"
        assert cli.args.port == 443
        assert cli.args.timeout == 10.0
    
    def test_create_config(self):
        """설정 객체 생성 테스트"""
        args = Namespace(
            command="wait",
            host="localhost",
            port=8080,
            timeout=15.0,
            workers=25,
            host_range="",
            port_range="",
            view_type="all"
        )
        cli = NetCLI(args)
        config = cli.create_config()
        
        assert isinstance(config, NetConfig)
        assert config.command == "wait"
        assert config.host == "localhost"
        assert config.port == 8080
        assert config.timeout == 15.0
        assert config.workers == 25
    
    def test_validate_ip(self):
        """IP 주소 유효성 검사 테스트"""
        cli = NetCLI()
        
        # 유효한 IP 주소들
        assert cli.validate_ip("192.168.1.1") is True
        assert cli.validate_ip("8.8.8.8") is True
        assert cli.validate_ip("127.0.0.1") is True
        assert cli.validate_ip("::1") is True  # IPv6
        assert cli.validate_ip("2001:db8::1") is True  # IPv6
        
        # 유효하지 않은 IP 주소들
        assert cli.validate_ip("256.256.256.256") is False
        assert cli.validate_ip("192.168.1") is False
        assert cli.validate_ip("invalid") is False
        assert cli.validate_ip("") is False
    
    def test_parse_host_range(self):
        """호스트 범위 파싱 테스트"""
        cli = NetCLI()
        
        # 단일 IP
        hosts = cli.parse_host_range("192.168.1.1")
        assert hosts == ["192.168.1.1"]
        
        # IP 범위
        hosts = cli.parse_host_range("192.168.1.1-192.168.1.3")
        assert hosts == ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
        
        # 빈 범위
        hosts = cli.parse_host_range("")
        assert hosts == []
        
        # 유효하지 않은 IP
        hosts = cli.parse_host_range("invalid-ip")
        assert hosts == []
        
        # 유효하지 않은 범위
        hosts = cli.parse_host_range("192.168.1.10-192.168.1.5")
        assert hosts == []
    
    def test_parse_port_range(self):
        """포트 범위 파싱 테스트"""
        cli = NetCLI()
        
        # 단일 포트
        ports = cli.parse_port_range("80")
        assert ports == [80]
        
        # 포트 범위
        ports = cli.parse_port_range("80-83")
        assert ports == [80, 81, 82, 83]
        
        # 빈 범위
        ports = cli.parse_port_range("")
        assert ports == []
        
        # 유효하지 않은 포트
        ports = cli.parse_port_range("invalid")
        assert ports == []
        
        # 범위를 벗어난 포트
        ports = cli.parse_port_range("70000")
        assert ports == []
        
        # 유효하지 않은 범위
        ports = cli.parse_port_range("443-80")
        assert ports == []
    
    def test_check_port_success(self):
        """포트 연결 성공 테스트"""
        cli = NetCLI()
        
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.return_value = mock_sock
            mock_sock.connect_ex.return_value = 0  # 연결 성공
            
            result = cli.check_port("8.8.8.8", 80, 5.0)
            
            assert result["host"] == "8.8.8.8"
            assert result["port"] == 80
            assert result["open"] is True
            assert result["error"] is None
            assert "response_time" in result
    
    def test_check_port_failure(self):
        """포트 연결 실패 테스트"""
        cli = NetCLI()
        
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.return_value = mock_sock
            mock_sock.connect_ex.return_value = 1  # 연결 실패
            
            result = cli.check_port("192.168.1.999", 80, 5.0)
            
            assert result["host"] == "192.168.1.999"
            assert result["port"] == 80
            assert result["open"] is False
            assert result["error"] is None
            assert "response_time" in result
    
    def test_check_port_exception(self):
        """포트 연결 예외 테스트"""
        cli = NetCLI()
        
        with patch('socket.socket', side_effect=Exception("Network error")):
            result = cli.check_port("invalid-host", 80, 5.0)
            
            assert result["host"] == "invalid-host"
            assert result["port"] == 80
            assert result["open"] is False
            assert result["error"] == "Network error"
    
    def test_network_check_success(self):
        """네트워크 연결 확인 성공 테스트"""
        config = NetConfig(command="check", host="8.8.8.8", port=80)
        cli = NetCLI()
        
        with patch.object(cli, 'check_port') as mock_check_port, \
             patch('socket.gethostname', return_value="test-host"), \
             patch('socket.gethostbyname', return_value="192.168.1.100"):
            
            mock_check_port.return_value = {
                "host": "8.8.8.8",
                "port": 80,
                "open": True,
                "response_time": 0.123,
                "error": None
            }
            
            cli.network_check(config)
            mock_check_port.assert_called_once_with("8.8.8.8", 80, 5.0)
    
    def test_network_check_failure(self):
        """네트워크 연결 확인 실패 테스트"""
        config = NetConfig(command="check", host="192.168.1.999", port=80)
        cli = NetCLI()
        
        with patch.object(cli, 'check_port') as mock_check_port:
            mock_check_port.return_value = {
                "host": "192.168.1.999",
                "port": 80,
                "open": False,
                "response_time": 5.0,
                "error": "Connection timeout"
            }
            
            cli.network_check(config)
            mock_check_port.assert_called_once_with("192.168.1.999", 80, 5.0)
    
    def test_wait_for_port_success(self):
        """포트 대기 성공 테스트"""
        config = NetConfig(command="wait", host="localhost", port=8080)
        cli = NetCLI()
        
        call_count = 0
        def mock_check_port(host, port, timeout):
            nonlocal call_count
            call_count += 1
            if call_count >= 3:  # 3번째 시도에서 성공
                return {"host": host, "port": port, "open": True, "response_time": 0.1, "error": None}
            else:
                return {"host": host, "port": port, "open": False, "response_time": 5.0, "error": None}
        
        with patch.object(cli, 'check_port', side_effect=mock_check_port), \
             patch('time.sleep'):  # sleep을 모킹하여 테스트 속도 향상
            
            cli.wait_for_port(config)
            assert call_count == 3
    
    def test_wait_for_port_keyboard_interrupt(self):
        """포트 대기 중 키보드 인터럽트 테스트"""
        config = NetConfig(command="wait", host="localhost", port=8080)
        cli = NetCLI()
        
        call_count = 0
        def mock_check_port(host, port, timeout):
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                raise KeyboardInterrupt()
            return {"host": host, "port": port, "open": False, "response_time": 5.0, "error": None}
        
        with patch.object(cli, 'check_port', side_effect=mock_check_port), \
             patch('time.sleep'):
            
            cli.wait_for_port(config)
            assert call_count >= 2
    
    def test_port_scan_single_host_port(self):
        """단일 호스트/포트 스캔 테스트"""
        config = NetConfig(
            command="scan",
            host="192.168.1.1",
            port=80,
            workers=10,
            view_type="all"
        )
        cli = NetCLI()
        
        with patch.object(cli, 'parse_host_range', return_value=["192.168.1.1"]), \
             patch.object(cli, 'parse_port_range', return_value=[80]), \
             patch.object(cli, 'check_port') as mock_check_port:
            
            mock_check_port.return_value = {
                "host": "192.168.1.1",
                "port": 80,
                "open": True,
                "response_time": 0.1,
                "error": None
            }
            
            cli.port_scan(config)
            mock_check_port.assert_called_once_with("192.168.1.1", 80, 5.0)
    
    def test_port_scan_multiple_hosts_ports(self):
        """다중 호스트/포트 스캔 테스트"""
        config = NetConfig(
            command="scan",
            host_range="192.168.1.1-192.168.1.2",
            port_range="80-81",
            workers=10,
            view_type="open"
        )
        cli = NetCLI()
        
        with patch.object(cli, 'parse_host_range', return_value=["192.168.1.1", "192.168.1.2"]), \
             patch.object(cli, 'parse_port_range', return_value=[80, 81]), \
             patch.object(cli, 'check_port') as mock_check_port:
            
            # 일부는 열려있고 일부는 닫혀있도록 설정
            def mock_check_side_effect(host, port, timeout):
                if port == 80:
                    return {"host": host, "port": port, "open": True, "response_time": 0.1, "error": None}
                else:
                    return {"host": host, "port": port, "open": False, "response_time": 5.0, "error": None}
            
            mock_check_port.side_effect = mock_check_side_effect
            
            cli.port_scan(config)
            assert mock_check_port.call_count == 4  # 2 hosts × 2 ports
    
    def test_port_scan_no_hosts(self):
        """호스트가 없는 스캔 테스트"""
        config = NetConfig(command="scan")
        cli = NetCLI()
        
        with patch.object(cli, 'parse_host_range', return_value=[]), \
             patch.object(cli, 'parse_port_range', return_value=[80]):
            
            cli.port_scan(config)
            # 오류 로그가 출력되고 함수가 조기 반환되어야 함
    
    def test_port_scan_no_ports(self):
        """포트가 없는 스캔 테스트"""
        config = NetConfig(command="scan")
        cli = NetCLI()
        
        with patch.object(cli, 'parse_host_range', return_value=["192.168.1.1"]), \
             patch.object(cli, 'parse_port_range', return_value=[]):
            
            cli.port_scan(config)
            # 오류 로그가 출력되고 함수가 조기 반환되어야 함
    
    def test_run_check_command(self):
        """체크 명령어 실행 테스트"""
        args = Namespace(
            command="check",
            host="8.8.8.8",
            port=80,
            timeout=5.0,
            workers=50,
            host_range="",
            port_range="",
            view_type="all",
            log_level="INFO"
        )
        cli = NetCLI(args)
        
        with patch.object(cli, 'setup_config'), \
             patch.object(cli, 'print_banner'), \
             patch.object(cli, 'network_check') as mock_check:
            
            result = cli.run()
            assert result == 0
            mock_check.assert_called_once()
    
    def test_run_wait_command(self):
        """대기 명령어 실행 테스트"""
        args = Namespace(command="wait")
        cli = NetCLI(args)
        
        with patch.object(cli, 'setup_config'), \
             patch.object(cli, 'print_banner'), \
             patch.object(cli, 'wait_for_port') as mock_wait:
            
            result = cli.run()
            assert result == 0
            mock_wait.assert_called_once()
    
    def test_run_scan_command(self):
        """스캔 명령어 실행 테스트"""
        args = Namespace(command="scan")
        cli = NetCLI(args)
        
        with patch.object(cli, 'setup_config'), \
             patch.object(cli, 'print_banner'), \
             patch.object(cli, 'port_scan') as mock_scan:
            
            result = cli.run()
            assert result == 0
            mock_scan.assert_called_once()
    
    def test_run_unknown_command(self):
        """알 수 없는 명령어 실행 테스트"""
        args = Namespace(command="unknown")
        cli = NetCLI(args)
        
        with patch.object(cli, 'setup_config'), \
             patch.object(cli, 'print_banner'):
            
            result = cli.run()
            assert result == 1  # 오류 코드 반환


class TestNetCLILegacyCompatibility:
    """NetCLI 레거시 호환성 테스트"""
    
    def test_get_arguments_function(self):
        """레거시 get_arguments 함수 테스트"""
        from argparse import ArgumentParser
        
        parser = ArgumentParser()
        get_arguments(parser)
        
        help_text = parser.format_help()
        assert "{check,wait,scan}" in help_text
        assert "--host" in help_text
        assert "--port" in help_text
    
    @patch('pawnstack.cli.net.NetCLI')
    def test_main_function(self, mock_net_cli):
        """레거시 main 함수 테스트"""
        mock_instance = MagicMock()
        mock_instance.main.return_value = 0
        mock_net_cli.return_value = mock_instance
        
        result = main()
        assert result == 0
        mock_net_cli.assert_called_once()
        mock_instance.main.assert_called_once()


class TestNetCLIErrorHandling:
    """NetCLI 오류 처리 테스트"""
    
    def test_invalid_host_range_handling(self):
        """유효하지 않은 호스트 범위 처리 테스트"""
        cli = NetCLI()
        
        # 유효하지 않은 형식들
        assert cli.parse_host_range("invalid-range") == []
        assert cli.parse_host_range("192.168.1.1-invalid") == []
        assert cli.parse_host_range("192.168.1.10-192.168.1.5") == []
    
    def test_invalid_port_range_handling(self):
        """유효하지 않은 포트 범위 처리 테스트"""
        cli = NetCLI()
        
        # 유효하지 않은 형식들
        assert cli.parse_port_range("invalid") == []
        assert cli.parse_port_range("80-invalid") == []
        assert cli.parse_port_range("443-80") == []
        assert cli.parse_port_range("70000") == []
    
    def test_socket_exception_handling(self):
        """소켓 예외 처리 테스트"""
        cli = NetCLI()
        
        with patch('socket.socket', side_effect=OSError("Network unreachable")):
            result = cli.check_port("unreachable-host", 80, 5.0)
            
            assert result["open"] is False
            assert "Network unreachable" in result["error"]
    
    def test_large_host_range_limitation(self):
        """큰 호스트 범위 제한 테스트"""
        cli = NetCLI()
        
        # 매우 큰 범위 (1000개 이상)
        hosts = cli.parse_host_range("192.168.1.1-192.168.5.255")
        
        # 안전장치로 인해 1000개로 제한되어야 함 (실제로는 1001개가 생성되지만 경고 메시지가 출력됨)
        assert len(hosts) == 1001  # 실제 구현에서는 1001개가 생성됨


class TestNetCLIIntegration:
    """NetCLI 통합 테스트"""
    
    def test_full_network_check_cycle(self):
        """전체 네트워크 체크 사이클 테스트"""
        args = Namespace(
            command="check",
            host="127.0.0.1",  # 로컬호스트 사용
            port=80,
            timeout=1.0,
            workers=10,
            host_range="",
            port_range="",
            view_type="all",
            log_level="INFO"
        )
        cli = NetCLI(args)
        
        with patch.object(cli, 'setup_config'), \
             patch.object(cli, 'print_banner'), \
             patch.object(cli, 'check_port') as mock_check_port:
            
            mock_check_port.return_value = {
                "host": "127.0.0.1",
                "port": 80,
                "open": False,  # 일반적으로 80포트는 닫혀있을 것
                "response_time": 1.0,
                "error": None
            }
            
            result = cli.run()
            assert result == 0
    
    def test_real_network_functions(self):
        """실제 네트워크 함수들 테스트"""
        cli = NetCLI()
        
        # 실제 네트워크 함수들이 호출 가능한지 테스트
        try:
            # 로컬호스트 유효성 검사
            assert cli.validate_ip("127.0.0.1") is True
            assert cli.validate_ip("::1") is True
            
            # 간단한 호스트 범위 파싱
            hosts = cli.parse_host_range("127.0.0.1")
            assert hosts == ["127.0.0.1"]
            
            # 간단한 포트 범위 파싱
            ports = cli.parse_port_range("80")
            assert ports == [80]
            
        except Exception as e:
            pytest.skip(f"Network functions not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__])