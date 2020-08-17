from aws_cdk.core import Construct
from aws_cdk.core import Environment
from aws_cdk.core import Stack
from vpc.utils import SubnetConfigurationConstructor
from vpc.utils import VPCConstructor


class VpcStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        subnet_configurations = SubnetConfigurationConstructor.execute()
        self.vpc = VPCConstructor.execute(scope=self, subnet_configurations=subnet_configurations)


class VpcStackConstructor:
    def __init__(self,  scope: Construct, env: Environment, config: dict):
        self.__scope = scope
        self.__env = env
        self.__config = config

    def execute(self):
        return VpcStack(
            scope=self.__scope,
            id="{}Vpc".format(self.__config["ENVIRONMENT_NAME"]),
            env=self.__env
        )
