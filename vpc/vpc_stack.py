from aws_cdk import core
from vpc.utils import SubnetConfigurationConstructor
from vpc.utils import VPCConstructor


class VpcStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        subnet_configurations = SubnetConfigurationConstructor.execute()
        self.vpc = VPCConstructor.execute(scope=self, subnet_configurations=subnet_configurations)
