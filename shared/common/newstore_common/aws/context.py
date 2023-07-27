from dataclasses import dataclass


@dataclass
class FakeAwsContext:
    invoked_function_arn: str = ''
    function_name: str = ''
