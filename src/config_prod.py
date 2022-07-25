import os

from minio import Minio

from youwol_files_backend import Constants, Configuration as ServiceConfiguration
from youwol_utils.clients.file_system.minio_file_system import MinioFileSystem
from youwol_utils.clients.oidc.oidc_config import OidcInfos, PrivateClient
from youwol_utils.context import DeployedContextReporter
from youwol_utils.middlewares import AuthMiddleware
from youwol_utils.servers.fast_api import AppConfiguration, ServerOptions, FastApiMiddleware


async def get_configuration() -> AppConfiguration[ServiceConfiguration[MinioFileSystem]]:
    required_env_vars = [
        "OPENID_BASE_URL",
        "OPENID_CLIENT_ID",
        "OPENID_CLIENT_SECRET",
        "MINIO_HOST_PORT",
        "MINIO_ACCESS_KEY",
        "MINIO_ACCESS_SECRET",
    ]

    not_founds = [v for v in required_env_vars if not os.getenv(v)]
    if not_founds:
        raise RuntimeError(f"Missing environments variable: {not_founds}")

    openid_infos = OidcInfos(
        base_uri=os.getenv("OPENID_BASE_URL"),
        client=PrivateClient(
            client_id=os.getenv("OPENID_CLIENT_ID"),
            client_secret=os.getenv("OPENID_CLIENT_SECRET")
        )
    )

    service_config: ServiceConfiguration[MinioFileSystem] = ServiceConfiguration(
        file_system=MinioFileSystem(
            bucket_name=Constants.namespace,
            client=Minio(
                endpoint=os.getenv("MINIO_HOST_PORT"),
                access_key=os.getenv("MINIO_ACCESS_KEY"),
                secret_key=os.getenv("MINIO_ACCESS_SECRET"),
                secure=False
            )
        )
    )

    await service_config.file_system.ensure_bucket()
    server_options = ServerOptions(
        root_path='/api/files-backend',
        http_port=8080,
        base_path="",
        middlewares=[
            FastApiMiddleware(
                AuthMiddleware, {
                    'openid_infos': openid_infos,
                    'predicate_public_path': lambda url:
                    url.path.endswith("/healthz")
                }
            )
        ],
        ctx_logger=DeployedContextReporter()
    )

    return AppConfiguration[ServiceConfiguration](
        server=server_options,
        service=service_config
    )
