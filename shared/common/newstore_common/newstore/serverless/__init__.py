from typing import Dict

from newstore_common.newstore.serverless.environment import NewStoreServerlessEnvironment, Stage


def from_aws_dict(params: Dict, context) -> NewStoreServerlessEnvironment:
    return NewStoreServerlessEnvironment(
        tenant=params["tenant"],
        stage=Stage[params["stage"]],
        api_user=params["ns_user"],
        api_credentials=params["ns_password"],
        function_version=context.function_version,
        function_name=context.function_name,
        request_id=context.aws_request_id,
    )
