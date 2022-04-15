import os

from minio import Minio

from config_common import cache_prefix
from youwol_files_backend import Constants, Configuration as ServiceConfiguration
from youwol_utils import AuthClient, CacheClient
from youwol_utils.clients.file_system.minio_file_system import MinioFileSystem
from youwol_utils.context import DeployedContextLogger
from youwol_utils.servers.fast_api import AppConfiguration, ServerOptions, FastApiMiddleware
from youwol_utils.middlewares import Middleware


async def get_configuration() -> AppConfiguration[ServiceConfiguration[MinioFileSystem]]:
    required_env_vars = ["MINIO_HOST_PORT", "MINIO_ACCESS_KEY", "MINIO_ACCESS_SECRET", "AUTH_HOST", "AUTH_CLIENT_ID",
                         "AUTH_CLIENT_SECRET", "AUTH_CLIENT_SCOPE"]

    not_founds = [v for v in required_env_vars if not os.getenv(v)]
    if not_founds:
        raise RuntimeError(f"Missing environments variable: {not_founds}")

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
    openid_host = os.getenv("AUTH_HOST")
    auth_client = AuthClient(url_base=f"https://{openid_host}/auth")
    cache_client = CacheClient(host="redis-master.infra.svc.cluster.local", prefix=cache_prefix)

    await service_config.file_system.ensure_bucket()
    server_options = ServerOptions(
        root_path='/api/files-backend',
        http_port=8080,
        base_path="",
        middlewares=[
            FastApiMiddleware(
                Middleware, {
                    "auth_client": auth_client,
                    "cache_client": cache_client,
                    # healthz need to not be protected as it is used for liveness prob
                    "unprotected_paths": lambda url: url.path.split("/")[-1] == "healthz"
                }
            )
        ],
        ctx_logger=DeployedContextLogger()
    )

    return AppConfiguration[ServiceConfiguration](
        server=server_options,
        service=service_config
    )
