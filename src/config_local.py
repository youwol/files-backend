from pathlib import Path
from config_common import get_py_youwol_env
from youwol_files_backend import Constants, Configuration as ServiceConfiguration
from youwol_utils.clients.file_system import LocalFileSystem
from youwol_utils.context import PyYouwolContextLogger
from youwol_utils.servers.fast_api import AppConfiguration, ServerOptions


async def get_configuration() -> AppConfiguration[ServiceConfiguration[LocalFileSystem]]:
    env = await get_py_youwol_env()
    databases_path = Path(env['pathsBook']['databases'])

    service_config: ServiceConfiguration[LocalFileSystem] = ServiceConfiguration[LocalFileSystem](
        file_system=LocalFileSystem(
            root_path=databases_path / 'storage' / Constants.namespace / 'youwol-users'
        )
    )

    server_options = ServerOptions(
        root_path="",
        http_port=env['portsBook']['files-backend'],
        base_path="",
        middlewares=[],
        ctx_logger=PyYouwolContextLogger(py_youwol_port=env["httpPort"])
    )
    return AppConfiguration[ServiceConfiguration](
        server=server_options,
        service=service_config
    )
