from newstore_adapter import Context
from newstore_adapter.connector import NewStoreConnector

from newstore_common.newstore.serverless.environment import NewStoreServerlessEnvironment


def new_connector(env: NewStoreServerlessEnvironment) -> NewStoreConnector:
    ctx = Context(
        tenant=env.tenant,
        stage=env.stage.name,
        function_name=env.function_name or "undefined",
        function_version=env.function_version or "undefined",
        aws_request_id=env.request_id or "undefined")
    connector = NewStoreConnector(ctx.tenant, ctx, env.api_user, env.api_credentials, ctx.api_host())
    return connector
