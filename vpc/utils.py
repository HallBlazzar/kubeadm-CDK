from aws_cdk.core import Construct
from aws_cdk.aws_ec2 import Vpc
from aws_cdk.aws_ec2 import SubnetConfiguration
from aws_cdk.aws_ec2 import SubnetType


class SubnetConfigurationConstructor:
    @staticmethod
    def execute() -> list:
        subnet_configurations = [
            SubnetConfiguration(
                cidr_mask=20,
                name="Public",
                subnet_type=SubnetType.PUBLIC
            ),
            SubnetConfiguration(
                cidr_mask=20,
                name="Private",
                subnet_type=SubnetType.PRIVATE
            )
        ]

        return subnet_configurations


class VPCConstructor:
    @staticmethod
    def execute(scope: Construct, subnet_configurations: list) -> Vpc:
        vpc = Vpc(
            scope=scope,
            id="vpc",
            subnet_configuration=subnet_configurations
        )

        return vpc
