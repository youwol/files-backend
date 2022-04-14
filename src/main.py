from youwol_files_backend import get_router
from youwol_utils.servers.fast_api import serve, FastApiApp, FastApiRouter, \
    select_configuration_from_command_line


app_config = select_configuration_from_command_line(
    {}
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
