from minio import Minio

from config_common import get_py_youwol_env
from youwol_files_backend import Constants, Configuration as ServiceConfiguration
from youwol_utils.clients.file_system.minio_file_system import MinioFileSystem
from youwol_utils.context import PyYouwolContextReporter
from youwol_utils.servers.fast_api import AppConfiguration, ServerOptions


async def get_configuration() -> AppConfiguration[ServiceConfiguration[MinioFileSystem]]:
    env = await get_py_youwol_env()
    # await py_youwol_exec_command('POST', 'start-minio', {port:'9000', access_key:'guillaume', secret_key:'guillaume'})
    service_config: ServiceConfiguration[MinioFileSystem] = ServiceConfiguration(
        file_system=MinioFileSystem(
            bucket_name=Constants.namespace,
            client=Minio(
                endpoint="127.0.0.1:9000",
                access_key="minioadmin",
                secret_key="minioadmin",
                secure=False
            )
        )
    )

    await service_config.file_system.ensure_bucket()
    server_options = ServerOptions(
        root_path="",
        http_port=env['portsBook']['files-backend'],
        base_path="",
        middlewares=[],
        ctx_logger=PyYouwolContextReporter(py_youwol_port=env["httpPort"])
    )

    return AppConfiguration[ServiceConfiguration](
        server=server_options,
        service=service_config
    )
