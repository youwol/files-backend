from youwol_files_backend import get_router, Configuration as ServiceConfiguration
from youwol_utils.servers.fast_api import serve, FastApiApp, FastApiRouter, \
    select_configuration_from_command_line, AppConfiguration


async def local() -> AppConfiguration[ServiceConfiguration]:
    from config_local import get_configuration as config
    return await config()


async def local_minio() -> AppConfiguration[ServiceConfiguration]:
    from config_local_minio import get_configuration as config
    return await config()


async def prod() -> AppConfiguration[ServiceConfiguration]:
    from config_prod import get_configuration as config
    return await config()


app_config = select_configuration_from_command_line(
    {
        "local": local,
        "local-minio": local_minio,
        "prod": prod
    }
)

serve(
    FastApiApp(
        title="files-backend",
        description="Service used to expose a file-system like API to YouWol",
        server_options=app_config.server,
        root_router=FastApiRouter(
            router=get_router(app_config.service)
        )
    )
)
