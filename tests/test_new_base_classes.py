"""
새로운 CLI 기본 클래스 단위 테스트
"""

import unittest
import os
from unittest.mock import patch, MagicMock
from argparse import Namespace, ArgumentParser

from pawnstack.cli.base import (
    BlockchainBaseCLI,
    CloudBaseCLI,
    ContainerBaseCLI,
    DependencyChecker
)


class TestDependencyChecker(unittest.TestCase):
    """의존성 검사 시스템 테스트"""

    def test_check_existing_dependencies(self):
        """존재하는 의존성 검사"""
        # 기본 Python 모듈로 테스트 (항상 존재)
        from pawnstack.cli.dependencies import DependencyInfo
        with patch.dict(DependencyChecker.EXTRAS_DEPENDENCIES, {
            'test': [
                DependencyInfo(module_name='os', package_name='os'),
                DependencyInfo(module_name='sys', package_name='sys')
            ]
        }):
            result = DependencyChecker.check_dependencies(['test'])
            self.assertTrue(result)

    def test_check_missing_dependencies(self):
        """누락된 의존성 검사"""
        from pawnstack.cli.dependencies import DependencyInfo
        with patch.dict(DependencyChecker.EXTRAS_DEPENDENCIES, {
            'test': [
                DependencyInfo(
                    module_name='nonexistent_module',
                    package_name='nonexistent-package'
                )
            ]
        }):
            with patch('pawnstack.cli.dependencies.pawn') as mock_pawn:
                mock_console = MagicMock()
                mock_pawn.console = mock_console

                result = DependencyChecker.check_dependencies(['test'])
                self.assertFalse(result)

                # 안내 메시지가 출력되었는지 확인
                mock_console.log.assert_called()


class MockBlockchainCLI(BlockchainBaseCLI):
    """테스트용 블록체인 CLI 구현"""
    def get_arguments(self, parser):
        self.get_common_blockchain_arguments(parser)

    async def run_async(self):
        return 0


class TestBlockchainBaseCLI(unittest.TestCase):
    """블록체인 CLI 기본 클래스 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.args = Namespace(
            network='testnet',
            rpc_url=None,
            keystore=None,
            password=None,
            timeout=30,
            retry=3
        )
        self.cli = MockBlockchainCLI(self.args)

    def test_network_configuration(self):
        """네트워크 설정 테스트"""
        # 기본 네트워크 설정
        self.assertEqual(self.cli.get_network_id(), '0x2')  # testnet
        self.assertEqual(self.cli.get_rpc_url(), 'https://test-ctz.solidwallet.io/api/v3')

        # 커스텀 RPC URL
        self.args.rpc_url = 'https://custom-rpc.example.com'
        self.assertEqual(self.cli.get_rpc_url(), 'https://custom-rpc.example.com')

    def test_get_common_blockchain_arguments(self):
        """블록체인 공통 인수 테스트"""
        parser = ArgumentParser()
        self.cli.get_common_blockchain_arguments(parser)

        # 인수가 제대로 추가되었는지 확인
        args = parser.parse_args(['--network', 'mainnet', '--timeout', '60'])
        self.assertEqual(args.network, 'mainnet')
        self.assertEqual(args.timeout, 60)

    def test_validate_keystore_no_keystore(self):
        """키스토어 없는 경우 검증"""
        result = self.cli.validate_keystore()
        self.assertTrue(result)  # 키스토어가 없어도 통과

    @patch('pathlib.Path.exists')
    def test_validate_keystore_missing_file(self, mock_exists):
        """키스토어 파일이 없는 경우"""
        mock_exists.return_value = False
        self.args.keystore = 'missing_keystore.json'

        with patch.object(self.cli, 'log_error'):
            result = self.cli.validate_keystore()
            self.assertFalse(result)

    @patch('pathlib.Path.exists')
    @patch('builtins.open')
    def test_validate_keystore_valid_file(self, mock_open, mock_exists):
        """유효한 키스토어 파일"""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = '''
        {
            "version": 3,
            "id": "test-id",
            "crypto": {}
        }
        '''

        self.args.keystore = 'valid_keystore.json'
        result = self.cli.validate_keystore()
        self.assertTrue(result)


class MockCloudCLI(CloudBaseCLI):
    """테스트용 클라우드 CLI 구현"""
    def get_arguments(self, parser):
        self.get_common_cloud_arguments(parser)

    async def run_async(self):
        return 0


class TestCloudBaseCLI(unittest.TestCase):
    """클라우드 CLI 기본 클래스 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.args = Namespace(
            profile='test-profile',
            region='ap-northeast-2',
            access_key_id=None,
            secret_access_key=None,
            session_token=None,
            endpoint_url=None
        )

    @patch('os.getenv')
    def test_get_aws_config(self, mock_getenv):
        """AWS 설정 반환 테스트"""
        mock_getenv.side_effect = lambda key, default=None: {
            "AWS_ACCESS_KEY_ID": "FAKEACCESSKEY1234567890",
            "AWS_SECRET_ACCESS_KEY": "fakeSecretKeyDontUseInProd1234567890"
        }.get(key, default)

        self.cli = MockCloudCLI(self.args)
        config = self.cli.get_aws_config()

        expected = {
            'profile_name': 'test-profile',
            'region_name': 'ap-northeast-2',
            'aws_access_key_id': 'FAKEACCESSKEY1234567890',
            'aws_secret_access_key': 'fakeSecretKeyDontUseInProd1234567890'
        }
        self.assertEqual(config, expected)

    def test_get_common_cloud_arguments(self):
        """클라우드 공통 인수 테스트"""
        self.cli = MockCloudCLI(self.args)
        parser = ArgumentParser()
        self.cli.get_common_cloud_arguments(parser)

        # 인수가 제대로 추가되었는지 확인
        args = parser.parse_args(['--profile', 'test', '--region', 'us-east-1'])
        self.assertEqual(args.profile, 'test')
        self.assertEqual(args.region, 'us-east-1')

    def test_aws_regions_list(self):
        """AWS 리전 목록 테스트"""
        self.cli = MockCloudCLI(self.args)
        self.assertIn('ap-northeast-2', self.cli.aws_regions)
        self.assertIn('us-east-1', self.cli.aws_regions)


class MockContainerCLI(ContainerBaseCLI):
    """테스트용 컨테이너 CLI 구현"""
    def get_arguments(self, parser):
        self.get_common_container_arguments(parser)

    async def run_async(self):
        return 0


class TestContainerBaseCLI(unittest.TestCase):
    """컨테이너 CLI 기본 클래스 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.args = Namespace(
            docker_host=None,
            compose_file='docker-compose.yml',
            project_name='test-project',
            env_file=None,
            timeout=60
        )
        self.cli = MockContainerCLI(self.args)

    def test_get_docker_config(self):
        """Docker 설정 반환 테스트"""
        config = self.cli.get_docker_config()
        expected = {
            'base_url': 'unix:///var/run/docker.sock',
            'timeout': 60
        }
        self.assertEqual(config, expected)

        # Docker 호스트 설정
        self.args.docker_host = 'tcp://localhost:2376'
        config = self.cli.get_docker_config()
        expected = {
            'base_url': 'tcp://localhost:2376',
            'timeout': 60
        }
        self.assertEqual(config, expected)

    def test_get_common_container_arguments(self):
        """컨테이너 공통 인수 테스트"""
        parser = ArgumentParser()
        self.cli.get_common_container_arguments(parser)

        # 인수가 제대로 추가되었는지 확인
        args = parser.parse_args(['--project-name', 'test', '--timeout', '120'])
        self.assertEqual(args.project_name, 'test')
        self.assertEqual(args.timeout, 120)

    def test_validate_compose_file_no_file(self):
        """Compose 파일 없는 경우 검증"""
        self.args.compose_file = None
        result = self.cli.validate_compose_file()
        self.assertTrue(result)  # Compose 파일이 없어도 통과

    @patch('pathlib.Path.exists')
    def test_validate_compose_file_missing(self, mock_exists):
        """Compose 파일이 없는 경우"""
        mock_exists.return_value = False

        with patch.object(self.cli, 'log_error'):
            result = self.cli.validate_compose_file()
            self.assertFalse(result)

    @patch('pathlib.Path.exists')
    @patch('builtins.open')
    @patch('yaml.safe_load')
    def test_validate_compose_file_valid(self, mock_yaml_load, mock_open, mock_exists):
        """유효한 Compose 파일"""
        mock_exists.return_value = True
        mock_yaml_load.return_value = {
            'version': '3.8',
            'services': {
                'web': {
                    'image': 'nginx'
                }
            }
        }

        result = self.cli.validate_compose_file()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
