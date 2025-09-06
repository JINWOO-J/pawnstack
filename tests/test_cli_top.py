"""
PawnStack Top CLI 테스트
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from argparse import Namespace

from pawnstack.cli.top import TopCLI, TopConfig, get_arguments, main


class TestTopConfig:
    """TopConfig 데이터클래스 테스트"""
    
    def test_default_config(self):
        """기본 설정 테스트"""
        config = TopConfig()
        assert config.command == "resource"
        assert config.interval == 1.0
        assert config.print_type == "line"
        assert config.top_n == 10
        assert config.group_by == "pid"
        assert config.unit == "Mbps"
        assert config.protocols == ["tcp", "udp"]
        assert config.pid_filter is None
        assert config.proc_filter is None
        assert config.min_bytes_threshold == 0
    
    def test_custom_config(self):
        """커스텀 설정 테스트"""
        config = TopConfig(
            command="net",
            interval=2.0,
            print_type="live",
            top_n=20,
            group_by="name",
            unit="Gbps",
            protocols=["tcp"],
            pid_filter=[1234, 5678],
            proc_filter=["python", "node"],
            min_bytes_threshold=1024
        )
        assert config.command == "net"
        assert config.interval == 2.0
        assert config.print_type == "live"
        assert config.top_n == 20
        assert config.group_by == "name"
        assert config.unit == "Gbps"
        assert config.protocols == ["tcp"]
        assert config.pid_filter == [1234, 5678]
        assert config.proc_filter == ["python", "node"]
        assert config.min_bytes_threshold == 1024


class TestTopCLI:
    """TopCLI 테스트"""
    
    def test_top_cli_creation(self):
        """TopCLI 생성 테스트"""
        cli = TopCLI()
        assert cli.command_name == "top"
        assert hasattr(cli, 'start_time')
    
    def test_get_arguments(self):
        """인수 정의 테스트"""
        from argparse import ArgumentParser
        
        parser = ArgumentParser()
        cli = TopCLI()
        cli.get_arguments(parser)
        
        # 파서에 인수들이 추가되었는지 확인
        help_text = parser.format_help()
        assert "command" in help_text
        assert "--interval" in help_text
        assert "--print-type" in help_text
        assert "--top-n" in help_text
        assert "--group-by" in help_text
        assert "--unit" in help_text
        assert "--protocols" in help_text
        assert "--pid-filter" in help_text
        assert "--proc-filter" in help_text
        assert "--min-bytes-threshold" in help_text
        assert "--log-level" in help_text
    
    def test_top_cli_with_args(self):
        """인수가 있는 TopCLI 테스트"""
        args = Namespace(
            command="net",
            interval=2.0,
            print_type="live",
            top_n=20,
            group_by="name",
            unit="Gbps",
            protocols=["tcp"],
            pid_filter=[1234],
            proc_filter=["python"],
            min_bytes_threshold=1024,
            log_level="DEBUG"
        )
        cli = TopCLI(args)
        assert cli.args.command == "net"
        assert cli.args.interval == 2.0
        assert cli.args.top_n == 20
    
    def test_create_config(self):
        """설정 객체 생성 테스트"""
        args = Namespace(
            command="proc",
            interval=3.0,
            print_type="layout",
            top_n=15,
            group_by="name",
            unit="Kbps",
            protocols=["udp"],
            pid_filter=None,
            proc_filter=["nginx"],
            min_bytes_threshold=512
        )
        cli = TopCLI(args)
        config = cli.create_config()
        
        assert isinstance(config, TopConfig)
        assert config.command == "proc"
        assert config.interval == 3.0
        assert config.print_type == "layout"
        assert config.top_n == 15
        assert config.group_by == "name"
        assert config.unit == "Kbps"
        assert config.protocols == ["udp"]
        assert config.proc_filter == ["nginx"]
        assert config.min_bytes_threshold == 512
    
    def test_get_system_info(self):
        """시스템 정보 수집 테스트"""
        cli = TopCLI()
        
        # psutil이 없는 경우를 시뮬레이션 (ImportError 발생)
        with patch.dict('sys.modules', {'psutil': None}):
            info = cli.get_system_info()
            
            assert isinstance(info, dict)
            # ImportError가 발생하면 기본값들이 반환되어야 함
            assert info["hostname"] == "unknown"
            assert info["system"] == "unknown"
            assert info["cores"] == 1
            assert info["logical_cores"] == 1
            assert info["memory"] == 0
            assert info["model"] == "unknown"
    
    def test_get_system_info_with_psutil(self):
        """psutil이 있는 경우 시스템 정보 수집 테스트"""
        cli = TopCLI()
        
        mock_psutil = MagicMock()
        mock_psutil.cpu_count.side_effect = [4, 8]  # physical, logical
        mock_psutil.virtual_memory.return_value.total = 16 * 1024**3  # 16GB
        
        with patch.dict('sys.modules', {'psutil': mock_psutil}), \
             patch('platform.node', return_value="test-host"), \
             patch('platform.system', return_value="Linux"), \
             patch('platform.machine', return_value="x86_64"):
            
            info = cli.get_system_info()
            
            assert info["hostname"] == "test-host"
            assert info["system"] == "Linux"
            assert info["cores"] == 4
            assert info["logical_cores"] == 8
            assert info["memory"] == 16.0
    
    def test_get_resource_status(self):
        """리소스 상태 수집 테스트"""
        cli = TopCLI()
        
        # psutil이 없는 경우를 시뮬레이션
        with patch.dict('sys.modules', {'psutil': None}):
            status = cli.get_resource_status()
            
            assert isinstance(status, dict)
            assert "time" in status
            assert status["cpu_%"] == "N/A"
            assert status["mem_%"] == "N/A"
    
    def test_get_resource_status_with_psutil(self):
        """psutil이 있는 경우 리소스 상태 수집 테스트"""
        cli = TopCLI()
        
        mock_psutil = MagicMock()
        mock_psutil.cpu_percent.return_value = 25.5
        mock_psutil.virtual_memory.return_value.percent = 60.2
        mock_psutil.virtual_memory.return_value.used = 8 * 1024**3  # 8GB
        mock_psutil.net_io_counters.return_value.bytes_recv = 100 * 1024**2  # 100MB
        mock_psutil.net_io_counters.return_value.bytes_sent = 50 * 1024**2   # 50MB
        mock_psutil.disk_io_counters.return_value.read_bytes = 200 * 1024**2  # 200MB
        mock_psutil.disk_io_counters.return_value.write_bytes = 150 * 1024**2 # 150MB
        
        with patch.dict('sys.modules', {'psutil': mock_psutil}), \
             patch('os.getloadavg', return_value=(1.2, 1.5, 1.8)):
            
            status = cli.get_resource_status()
            
            assert status["cpu_%"] == "25.5"
            assert status["load"] == "1.20"
            assert status["mem_%"] == "60.2"
            assert status["mem_used"] == "8.0G"
            assert status["net_in"] == "100.0M"
            assert status["net_out"] == "50.0M"
            assert status["disk_r"] == "200.0M"
            assert status["disk_w"] == "150.0M"
    
    def test_print_line_status(self):
        """라인 상태 출력 테스트"""
        cli = TopCLI()
        
        data = {
            "time": "12:34:56",
            "cpu_%": "25.5",
            "load": "1.20",
            "mem_%": "60.2",
            "mem_used": "8.0G",
            "net_in": "100.0M",
            "net_out": "50.0M",
            "disk_r": "200.0M",
            "disk_w": "150.0M"
        }
        
        system_info = {
            "hostname": "test-host",
            "cores": 4,
            "memory": 16.0
        }
        
        with patch('os.get_terminal_size', return_value=(80, 24)):
            # 출력 함수가 오류 없이 실행되는지 확인
            cli.print_line_status(data, system_info)
    
    def test_monitor_resources(self):
        """리소스 모니터링 테스트"""
        config = TopConfig(interval=0.1)  # 빠른 테스트를 위해 짧은 간격
        cli = TopCLI()
        
        call_count = 0
        def mock_get_resource_status():
            nonlocal call_count
            call_count += 1
            if call_count >= 3:  # 3번 호출 후 KeyboardInterrupt 발생
                raise KeyboardInterrupt()
            return {
                "time": "12:34:56",
                "cpu_%": "25.0",
                "load": "1.20",
                "mem_%": "50.0",
                "mem_used": "8.0G",
                "net_in": "100.0M",
                "net_out": "50.0M",
                "disk_r": "200.0M",
                "disk_w": "150.0M"
            }
        
        with patch.object(cli, 'get_system_info') as mock_system_info, \
             patch.object(cli, 'get_resource_status', side_effect=mock_get_resource_status), \
             patch.object(cli, 'print_line_status') as mock_print_line, \
             patch('time.sleep'):  # sleep을 모킹하여 테스트 속도 향상
            
            mock_system_info.return_value = {"hostname": "test", "cores": 4, "memory": 16}
            
            # KeyboardInterrupt가 정상적으로 처리되는지 확인
            cli.monitor_resources(config)
            
            assert call_count >= 3
            assert mock_print_line.call_count >= 1
    
    def test_monitor_network(self):
        """네트워크 모니터링 테스트"""
        config = TopConfig(command="net")
        cli = TopCLI()
        
        mock_psutil = MagicMock()
        mock_psutil.net_io_counters.return_value.bytes_sent = 1000000
        mock_psutil.net_io_counters.return_value.bytes_recv = 2000000
        mock_psutil.net_io_counters.return_value.packets_sent = 1000
        mock_psutil.net_io_counters.return_value.packets_recv = 2000
        
        with patch.dict('sys.modules', {'psutil': mock_psutil}):
            # 네트워크 모니터링이 오류 없이 실행되는지 확인
            cli.monitor_network(config)
    
    def test_monitor_processes(self):
        """프로세스 모니터링 테스트"""
        config = TopConfig(command="proc", top_n=5)
        cli = TopCLI()
        
        mock_psutil = MagicMock()
        mock_processes = [
            {'pid': 1234, 'name': 'python', 'cpu_percent': 25.5, 'memory_percent': 10.2},
            {'pid': 5678, 'name': 'node', 'cpu_percent': 15.3, 'memory_percent': 8.1},
            {'pid': 9012, 'name': 'nginx', 'cpu_percent': 5.2, 'memory_percent': 3.5}
        ]
        
        mock_process_iter = MagicMock()
        mock_process_iter.__iter__ = lambda self: iter([
            MagicMock(info=proc) for proc in mock_processes
        ])
        mock_psutil.process_iter.return_value = mock_process_iter
        
        with patch.dict('sys.modules', {'psutil': mock_psutil}):
            # 프로세스 모니터링이 오류 없이 실행되는지 확인
            cli.monitor_processes(config)
    
    def test_run_resource_command(self):
        """리소스 명령어 실행 테스트"""
        args = Namespace(
            command="resource",
            config_file="config.ini",
            base_dir="/tmp",
            log_level="INFO",
            interval=1.0,
            print_type="line",
            top_n=10,
            group_by="pid",
            unit="Mbps",
            protocols=["tcp", "udp"],
            pid_filter=None,
            proc_filter=None,
            min_bytes_threshold=0
        )
        cli = TopCLI(args)
        
        with patch.object(cli, 'setup_config'), \
             patch.object(cli, 'print_banner'), \
             patch.object(cli, 'monitor_resources') as mock_monitor:
            
            result = cli.run()
            assert result == 0
            mock_monitor.assert_called_once()
    
    def test_run_network_command(self):
        """네트워크 명령어 실행 테스트"""
        args = Namespace(command="net")
        cli = TopCLI(args)
        
        with patch.object(cli, 'setup_config'), \
             patch.object(cli, 'print_banner'), \
             patch.object(cli, 'monitor_network') as mock_monitor:
            
            result = cli.run()
            assert result == 0
            mock_monitor.assert_called_once()
    
    def test_run_process_command(self):
        """프로세스 명령어 실행 테스트"""
        args = Namespace(command="proc")
        cli = TopCLI(args)
        
        with patch.object(cli, 'setup_config'), \
             patch.object(cli, 'print_banner'), \
             patch.object(cli, 'monitor_processes') as mock_monitor:
            
            result = cli.run()
            assert result == 0
            mock_monitor.assert_called_once()


class TestTopCLILegacyCompatibility:
    """TopCLI 레거시 호환성 테스트"""
    
    def test_get_arguments_function(self):
        """레거시 get_arguments 함수 테스트"""
        from argparse import ArgumentParser
        
        parser = ArgumentParser()
        get_arguments(parser)
        
        help_text = parser.format_help()
        assert "command" in help_text
        assert "--interval" in help_text
        assert "--print-type" in help_text
    
    @patch('pawnstack.cli.top.TopCLI')
    def test_main_function(self, mock_top_cli):
        """레거시 main 함수 테스트"""
        mock_instance = MagicMock()
        mock_instance.main.return_value = 0
        mock_top_cli.return_value = mock_instance
        
        result = main()
        assert result == 0
        mock_top_cli.assert_called_once()
        mock_instance.main.assert_called_once()


class TestTopCLIErrorHandling:
    """TopCLI 오류 처리 테스트"""
    
    def test_missing_psutil_graceful_degradation(self):
        """psutil 없을 때 우아한 성능 저하 테스트"""
        cli = TopCLI()
        
        # psutil을 사용할 수 없는 상황 시뮬레이션
        with patch.dict('sys.modules', {'psutil': None}):
            system_info = cli.get_system_info()
            resource_status = cli.get_resource_status()
            
            # 기본값들이 설정되어 있는지 확인
            assert system_info["cores"] == 1
            assert system_info["memory"] == 0
            assert resource_status["cpu_%"] == "N/A"
            assert resource_status["mem_%"] == "N/A"
    
    def test_terminal_size_fallback(self):
        """터미널 크기 가져오기 실패 시 폴백 테스트"""
        cli = TopCLI()
        
        data = {"time": "12:34:56", "cpu_%": "25.0"}
        system_info = {"hostname": "test", "cores": 4, "memory": 16}
        
        with patch('os.get_terminal_size', side_effect=OSError("No terminal")):
            # OSError가 발생해도 정상적으로 처리되는지 확인
            cli.print_line_status(data, system_info)


class TestTopCLIIntegration:
    """TopCLI 통합 테스트"""
    
    def test_full_resource_monitoring_cycle(self):
        """전체 리소스 모니터링 사이클 테스트"""
        args = Namespace(
            command="resource",
            config_file="config.ini",
            base_dir="/tmp",
            log_level="INFO",
            interval=0.1,  # 빠른 테스트
            print_type="line",
            top_n=10,
            group_by="pid",
            unit="Mbps",
            protocols=["tcp", "udp"],
            pid_filter=None,
            proc_filter=None,
            min_bytes_threshold=0
        )
        cli = TopCLI(args)
        
        # 짧은 모니터링 사이클 실행
        call_count = 0
        def mock_get_resource_status():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                raise KeyboardInterrupt()
            return {
                "time": time.strftime("%H:%M:%S"),
                "cpu_%": "25.0",
                "load": "1.20",
                "mem_%": "50.0",
                "mem_used": "8.0G",
                "net_in": "100.0M",
                "net_out": "50.0M",
                "disk_r": "200.0M",
                "disk_w": "150.0M"
            }
        
        with patch.object(cli, 'setup_config'), \
             patch.object(cli, 'print_banner'), \
             patch.object(cli, 'get_system_info') as mock_system_info, \
             patch.object(cli, 'get_resource_status', side_effect=mock_get_resource_status), \
             patch('time.sleep'):
            
            mock_system_info.return_value = {
                "hostname": "test-host",
                "cores": 4,
                "memory": 16.0
            }
            
            result = cli.run()
            assert result == 0
            assert call_count >= 2


if __name__ == "__main__":
    pytest.main([__file__])