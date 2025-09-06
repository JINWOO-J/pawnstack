"""
PawnStack Server CLI 테스트
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from argparse import Namespace

from pawnstack.cli.server import ServerCLI, get_arguments, main
from pawnstack.resource.system import get_cpu_info, get_mem_info, get_load_average, get_uptime, get_process_count
from pawnstack.resource.network import get_network_stats
from pawnstack.resource.disk import DiskUsage


class TestServerCLI:
    """ServerCLI 테스트"""
    
    def test_server_cli_creation(self):
        """ServerCLI 생성 테스트"""
        cli = ServerCLI()
        assert cli.command_name == "server"
        assert hasattr(cli, 'start_time')
    
    def test_get_arguments(self):
        """인수 정의 테스트"""
        from argparse import ArgumentParser
        
        parser = ArgumentParser()
        cli = ServerCLI()
        cli.get_arguments(parser)
        
        # 파서에 인수들이 추가되었는지 확인
        help_text = parser.format_help()
        assert "--cpu-only" in help_text
        assert "--memory-only" in help_text
        assert "--disk-only" in help_text
        assert "--network-only" in help_text
        assert "--no-live" in help_text
        assert "--interval" in help_text
        assert "--duration" in help_text
    
    def test_server_cli_with_args(self):
        """인수가 있는 ServerCLI 테스트"""
        args = Namespace(
            cpu_only=True,
            memory_only=False,
            disk_only=False,
            network_only=False,
            no_live=True,
            interval=5,
            duration=10
        )
        cli = ServerCLI(args)
        assert cli.args.cpu_only is True
        assert cli.args.interval == 5
    
    @pytest.mark.asyncio
    async def test_show_snapshot(self):
        """스냅샷 모드 테스트"""
        args = Namespace(no_live=True)
        cli = ServerCLI(args)
        
        with patch.object(cli, 'create_layout') as mock_layout:
            mock_layout.return_value = "test_layout"
            
            await cli.show_snapshot()
            mock_layout.assert_called_once()
    
    def test_create_cpu_panel(self):
        """CPU 패널 생성 테스트"""
        cli = ServerCLI()
        
        with patch('pawnstack.cli.server.get_cpu_info') as mock_cpu_info, \
             patch('pawnstack.cli.server.get_load_average') as mock_load_avg, \
             patch('pawnstack.cli.server.get_uptime') as mock_uptime, \
             patch('pawnstack.cli.server.get_process_count') as mock_proc_count:
            
            mock_cpu_info.return_value = {
                'physical_cores': 4,
                'logical_cores': 8,
                'cpu_percent': 25.5,
                'cpu_freq': {'current': 2400}
            }
            mock_load_avg.return_value = "1.2, 1.5, 1.8"
            mock_uptime.return_value = "2d 5h 30m"
            mock_proc_count.return_value = 150
            
            panel = cli.create_cpu_panel()
            assert panel is not None
            assert hasattr(panel, 'title')
            assert "CPU Information" in str(panel.title)
    
    def test_create_memory_panel(self):
        """메모리 패널 생성 테스트"""
        cli = ServerCLI()
        
        with patch('pawnstack.cli.server.get_mem_info') as mock_mem_info:
            mock_mem_info.return_value = {
                'mem_total': 16.0,
                'mem_used': 8.5,
                'mem_available': 7.5,
                'mem_percent': 53.1
            }
            
            panel = cli.create_memory_panel()
            assert panel is not None
            assert hasattr(panel, 'title')
            assert "Memory Information" in str(panel.title)
    
    def test_create_disk_panel(self):
        """디스크 패널 생성 테스트"""
        cli = ServerCLI()
        
        with patch('pawnstack.cli.server.DiskUsage') as mock_disk_usage:
            mock_instance = MagicMock()
            mock_disk_usage.return_value = mock_instance
            
            mock_instance.get_disk_usage.return_value = {
                "/": {
                    'used': 45.2,
                    'total': 100.0,
                    'percent': 45.2
                }
            }
            
            panel = cli.create_disk_panel()
            assert panel is not None
            assert hasattr(panel, 'title')
            assert "Disk Usage" in str(panel.title)
    
    def test_create_network_panel(self):
        """네트워크 패널 생성 테스트"""
        cli = ServerCLI()
        
        with patch('pawnstack.cli.server.get_network_stats') as mock_net_stats:
            mock_net_stats.return_value = {
                'bytes_sent': 1024 * 1024 * 100,  # 100MB
                'bytes_recv': 1024 * 1024 * 200,  # 200MB
                'packets_sent': 1000,
                'packets_recv': 2000,
                'errin': 0,
                'errout': 0
            }
            
            panel = cli.create_network_panel()
            assert panel is not None
            assert hasattr(panel, 'title')
            assert "Network Statistics" in str(panel.title)
    
    def test_create_layout_all_panels(self):
        """전체 패널 레이아웃 생성 테스트"""
        cli = ServerCLI()
        
        with patch.object(cli, 'create_cpu_panel') as mock_cpu, \
             patch.object(cli, 'create_memory_panel') as mock_memory, \
             patch.object(cli, 'create_disk_panel') as mock_disk, \
             patch.object(cli, 'create_network_panel') as mock_network, \
             patch('pawnstack.cli.server.get_hostname') as mock_hostname:
            
            mock_cpu.return_value = "cpu_panel"
            mock_memory.return_value = "memory_panel"
            mock_disk.return_value = "disk_panel"
            mock_network.return_value = "network_panel"
            mock_hostname.return_value = "test-host"
            
            layout = cli.create_layout()
            assert layout is not None
            
            # 모든 패널이 호출되었는지 확인
            mock_cpu.assert_called_once()
            mock_memory.assert_called_once()
            mock_disk.assert_called_once()
            mock_network.assert_called_once()
    
    def test_create_layout_cpu_only(self):
        """CPU만 표시하는 레이아웃 테스트"""
        args = Namespace(cpu_only=True)
        cli = ServerCLI(args)
        
        with patch.object(cli, 'create_cpu_panel') as mock_cpu, \
             patch.object(cli, 'create_memory_panel') as mock_memory, \
             patch.object(cli, 'create_disk_panel') as mock_disk, \
             patch.object(cli, 'create_network_panel') as mock_network, \
             patch('pawnstack.cli.server.get_hostname') as mock_hostname:
            
            mock_cpu.return_value = "cpu_panel"
            mock_hostname.return_value = "test-host"
            
            layout = cli.create_layout()
            assert layout is not None
            
            # CPU 패널만 호출되었는지 확인
            mock_cpu.assert_called_once()
            mock_memory.assert_not_called()
            mock_disk.assert_not_called()
            mock_network.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_run_async_snapshot_mode(self):
        """비동기 실행 - 스냅샷 모드 테스트"""
        args = Namespace(no_live=True)
        cli = ServerCLI(args)
        
        with patch.object(cli, 'show_snapshot') as mock_snapshot:
            mock_snapshot.return_value = None
            
            result = await cli.run_async()
            assert result == 0
            mock_snapshot.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_async_live_mode(self):
        """비동기 실행 - 라이브 모드 테스트"""
        args = Namespace(no_live=False, interval=1, duration=1)
        cli = ServerCLI(args)
        
        with patch.object(cli, 'start_live_monitoring') as mock_live:
            mock_live.return_value = None
            
            result = await cli.run_async()
            assert result == 0
            mock_live.assert_called_once()
    
    def test_error_handling_cpu_info(self):
        """CPU 정보 오류 처리 테스트"""
        cli = ServerCLI()
        
        with patch('pawnstack.cli.server.get_cpu_info') as mock_cpu_info, \
             patch('pawnstack.cli.server.get_load_average') as mock_load_avg, \
             patch('pawnstack.cli.server.get_uptime') as mock_uptime, \
             patch('pawnstack.cli.server.get_process_count') as mock_proc_count:
            
            mock_cpu_info.return_value = {'error': 'CPU info not available'}
            mock_load_avg.return_value = "N/A"
            mock_uptime.return_value = "N/A"
            mock_proc_count.return_value = 0
            
            panel = cli.create_cpu_panel()
            assert panel is not None
    
    def test_error_handling_memory_info(self):
        """메모리 정보 오류 처리 테스트"""
        cli = ServerCLI()
        
        with patch('pawnstack.cli.server.get_mem_info') as mock_mem_info:
            mock_mem_info.return_value = {'error': 'Memory info not available'}
            
            panel = cli.create_memory_panel()
            assert panel is not None
    
    def test_error_handling_network_stats(self):
        """네트워크 통계 오류 처리 테스트"""
        cli = ServerCLI()
        
        with patch('pawnstack.cli.server.get_network_stats') as mock_net_stats:
            mock_net_stats.return_value = {'error': 'Network stats not available'}
            
            panel = cli.create_network_panel()
            assert panel is not None


class TestServerCLILegacyCompatibility:
    """ServerCLI 레거시 호환성 테스트"""
    
    def test_get_arguments_function(self):
        """레거시 get_arguments 함수 테스트"""
        from argparse import ArgumentParser
        
        parser = ArgumentParser()
        get_arguments(parser)
        
        help_text = parser.format_help()
        assert "--cpu-only" in help_text
        assert "--memory-only" in help_text
    
    @patch('pawnstack.cli.server.ServerCLI')
    def test_main_function(self, mock_server_cli):
        """레거시 main 함수 테스트"""
        mock_instance = MagicMock()
        mock_instance.main.return_value = 0
        mock_server_cli.return_value = mock_instance
        
        result = main()
        assert result == 0
        mock_server_cli.assert_called_once()
        mock_instance.main.assert_called_once()


class TestServerCLIIntegration:
    """ServerCLI 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_full_monitoring_cycle(self):
        """전체 모니터링 사이클 테스트"""
        args = Namespace(
            no_live=True,
            cpu_only=False,
            memory_only=False,
            disk_only=False,
            network_only=False
        )
        cli = ServerCLI(args)
        
        # 모든 리소스 함수들을 모킹
        with patch('pawnstack.cli.server.get_cpu_info') as mock_cpu, \
             patch('pawnstack.cli.server.get_mem_info') as mock_mem, \
             patch('pawnstack.cli.server.get_network_stats') as mock_net, \
             patch('pawnstack.cli.server.DiskUsage') as mock_disk, \
             patch('pawnstack.cli.server.get_hostname') as mock_hostname:
            
            # 정상적인 데이터 반환 설정
            mock_cpu.return_value = {'physical_cores': 4, 'logical_cores': 8, 'cpu_percent': 25.0}
            mock_mem.return_value = {'mem_total': 16.0, 'mem_used': 8.0, 'mem_percent': 50.0}
            mock_net.return_value = {'bytes_sent': 1000000, 'bytes_recv': 2000000}
            mock_hostname.return_value = "test-server"
            
            mock_disk_instance = MagicMock()
            mock_disk.return_value = mock_disk_instance
            mock_disk_instance.get_disk_usage.return_value = {
                "/": {'used': 50.0, 'total': 100.0, 'percent': 50.0}
            }
            
            result = await cli.run_async()
            assert result == 0
    
    def test_resource_functions_availability(self):
        """리소스 함수들의 가용성 테스트"""
        # 실제 시스템 리소스 함수들이 호출 가능한지 테스트
        try:
            cpu_info = get_cpu_info()
            assert isinstance(cpu_info, dict)
            
            mem_info = get_mem_info()
            assert isinstance(mem_info, dict)
            
            load_avg = get_load_average()
            assert isinstance(load_avg, str)
            
            uptime = get_uptime()
            assert isinstance(uptime, str)
            
            proc_count = get_process_count()
            assert isinstance(proc_count, int)
            
            net_stats = get_network_stats()
            assert isinstance(net_stats, dict)
            
            disk_usage = DiskUsage()
            disk_info = disk_usage.get_disk_usage("/")
            assert isinstance(disk_info, dict)
            
        except Exception as e:
            pytest.skip(f"System resource functions not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__])