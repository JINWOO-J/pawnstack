#!/usr/bin/env python3
"""
간단한 top 테스트
"""

import os
import time
import psutil
from dataclasses import dataclass


@dataclass
class SystemStats:
    """시스템 통계 저장"""
    timestamp: float = 0
    net_bytes_sent: int = 0
    net_bytes_recv: int = 0
    net_packets_sent: int = 0
    net_packets_recv: int = 0
    disk_read_bytes: int = 0
    disk_write_bytes: int = 0


class SimpleTop:
    def __init__(self):
        self.prev_stats = None

    def get_current_stats(self) -> SystemStats:
        """현재 시스템 통계 수집"""
        current_time = time.time()
        net_io = psutil.net_io_counters()
        disk_io = psutil.disk_io_counters()

        return SystemStats(
            timestamp=current_time,
            net_bytes_sent=net_io.bytes_sent if net_io else 0,
            net_bytes_recv=net_io.bytes_recv if net_io else 0,
            net_packets_sent=net_io.packets_sent if net_io else 0,
            net_packets_recv=net_io.packets_recv if net_io else 0,
            disk_read_bytes=disk_io.read_bytes if disk_io else 0,
            disk_write_bytes=disk_io.write_bytes if disk_io else 0
        )

    def calculate_rates(self, current: SystemStats, previous: SystemStats) -> dict:
        """초당 전송률 계산"""
        if not previous or current.timestamp <= previous.timestamp:
            return {
                "net_in_rate": 0.0,
                "net_out_rate": 0.0,
                "pk_in_rate": 0.0,
                "pk_out_rate": 0.0,
                "disk_rd_rate": 0.0,
                "disk_wr_rate": 0.0
            }

        time_diff = current.timestamp - previous.timestamp

        # 네트워크 전송률 (MB/s)
        net_in_rate = (current.net_bytes_recv - previous.net_bytes_recv) / time_diff / (1024 * 1024)
        net_out_rate = (current.net_bytes_sent - previous.net_bytes_sent) / time_diff / (1024 * 1024)

        # 패킷 전송률 (packets/s)
        pk_in_rate = (current.net_packets_recv - previous.net_packets_recv) / time_diff
        pk_out_rate = (current.net_packets_sent - previous.net_packets_sent) / time_diff

        # 디스크 I/O 전송률 (MB/s)
        disk_rd_rate = (current.disk_read_bytes - previous.disk_read_bytes) / time_diff / (1024 * 1024)
        disk_wr_rate = (current.disk_write_bytes - previous.disk_write_bytes) / time_diff / (1024 * 1024)

        return {
            "net_in_rate": max(0, net_in_rate),
            "net_out_rate": max(0, net_out_rate),
            "pk_in_rate": max(0, pk_in_rate),
            "pk_out_rate": max(0, pk_out_rate),
            "disk_rd_rate": max(0, disk_rd_rate),
            "disk_wr_rate": max(0, disk_wr_rate)
        }

    def get_resource_status(self) -> dict:
        """리소스 상태 수집"""
        # 현재 통계 수집
        current_stats = self.get_current_stats()

        # CPU 정보
        cpu_times = psutil.cpu_times_percent(interval=0.1)
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)

        # 메모리 정보
        memory = psutil.virtual_memory()

        # 전송률 계산
        rates = self.calculate_rates(current_stats, self.prev_stats)

        # 이전 통계 업데이트
        self.prev_stats = current_stats

        return {
            "time": time.strftime("%H:%M:%S"),
            "net_in": f"{rates['net_in_rate']:.2f}M",
            "net_out": f"{rates['net_out_rate']:.2f}M",
            "pk_in": f"{int(rates['pk_in_rate'])}",
            "pk_out": f"{int(rates['pk_out_rate'])}",
            "load": f"{load_avg[0]:.2f}",
            "usr": f"{cpu_times.user:.1f}%" if hasattr(cpu_times, 'user') else "0.0%",
            "sys": f"{cpu_times.system:.1f}%" if hasattr(cpu_times, 'system') else "0.0%",
            "i/o": f"{cpu_times.iowait:.2f}" if hasattr(cpu_times, 'iowait') else "0.00",
            "disk_rd": f"{rates['disk_rd_rate']:.2f}M",
            "disk_wr": f"{rates['disk_wr_rate']:.2f}M",
            "mem_%": f"{memory.percent:.1f}%",
        }

    def run(self, interval=1.0, duration=10):
        """모니터링 실행"""
        print("🚀 Starting resource monitoring")
        print("│    time│   net_in│  net_out│     pk_in│    pk_out│ load│   usr│   sys│   i/o│   disk_rd│   disk_wr│ mem_%│")

        # 첫 번째 측정 (기준점 설정)
        self.prev_stats = self.get_current_stats()
        time.sleep(interval)

        count = 0
        start_time = time.time()

        try:
            while time.time() - start_time < duration:
                data = self.get_resource_status()

                # 값 출력 (레거시 형식과 유사하게)
                line = f"│{data['time']:>8}│{data['net_in']:>9}│{data['net_out']:>9}│{data['pk_in']:>10}│{data['pk_out']:>10}│{data['load']:>5}│{data['usr']:>6}│{data['sys']:>6}│{data['i/o']:>6}│{data['disk_rd']:>10}│{data['disk_wr']:>10}│{data['mem_%']:>6}│"
                print(line)

                count += 1
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n모니터링이 중단되었습니다")


if __name__ == "__main__":
    import sys

    interval = 1.0
    duration = 30

    if len(sys.argv) > 1:
        try:
            interval = float(sys.argv[1])
        except ValueError:
            pass

    if len(sys.argv) > 2:
        try:
            duration = float(sys.argv[2])
        except ValueError:
            pass

    top = SimpleTop()
    top.run(interval=interval, duration=duration)
