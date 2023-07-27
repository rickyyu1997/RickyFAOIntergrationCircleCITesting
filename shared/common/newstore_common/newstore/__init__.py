from newstore_adapter.connector import NewStoreConnector
from newstore_adapter import Context


def create_ns_connector(context, lambda_parameters):
    ctx = Context(
        tenant=lambda_parameters["ns_tenant"],
        stage=lambda_parameters["stage"],
        function_name=context.function_name,
        function_version=context.function_version,
        aws_request_id=context.aws_request_id)

    connector = NewStoreConnector(
        ctx.tenant, ctx, lambda_parameters["ns_user"],
        lambda_parameters["ns_password"], ctx.api_host())
    return connector


def create_ns_connector_from_context(context) -> NewStoreConnector:
    ctx = Context(
        tenant=context["tenant"],
        stage=context["stage"],
        function_name=context.get("function_name", "undefined"),
        function_version=context.get("function_version", "undefined"),
        aws_request_id=context.get("aws_request_id", "undefined"))

    connector = NewStoreConnector(
        ctx.tenant, ctx, context["ns_user"],
        context["ns_password"], ctx.api_host())
    return connector


def compare_ordinal(value_1: str, value_2: str) -> bool:
    return value_1.lower().strip() == value_2.lower().strip()
