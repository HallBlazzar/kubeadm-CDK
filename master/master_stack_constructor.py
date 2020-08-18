from utils.instance_constructor import PrivateInstanceConstructor
from aws_cdk.core import Construct
from aws_cdk.core import Stack
from aws_cdk.core import Environment
from aws_cdk.aws_ec2 import SecurityGroup
from deployment_asset.deployment_asset_stack_constructor import DeploymentAssetStack
from master.user_data_constructor import MasterUserDataConstructor
from vpc.vpc_stack_constructor import VpcStack
from cluster_security_group.cluster_security_group_stack_constructor import ClusterSecurityGroupStack


class MasterStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        config: dict,
        vpc_stack: VpcStack,
        deployment_asset_stack: DeploymentAssetStack,
        security_group: SecurityGroup,
        **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        self.master_instance = PrivateInstanceConstructor(
            scope=self,
            config=config,
            instance_id="master",
            vpc_stack=vpc_stack,
        ).execute()

        master_user_data = MasterUserDataConstructor(
            deployment_asset_stack=deployment_asset_stack, instance=self.master_instance
        ).execute()
        row_user_data = master_user_data.render()

        self.master_instance.add_user_data(row_user_data)
        self.master_instance.add_security_group(security_group)


class MasterStackConstructor:
    def __init__(
        self,
        scope: Construct,
        env: Environment,
        config: dict,

        vpc_stack: VpcStack,
        deployment_asset_stack: DeploymentAssetStack,
        cluster_security_group_stack: ClusterSecurityGroupStack
    ):
        self.__scope = scope
        self.__env = env
        self.__config = config

        self.__vpc_stack = vpc_stack
        self.__deployment_asset_stack = deployment_asset_stack
        self.__cluster_security_group_stack = cluster_security_group_stack

    def execute(self):
        return MasterStack(
            scope=self.__scope,
            env=self.__env,
            id="{}Master".format(self.__config["ENVIRONMENT_NAME"]),

            config=self.__config,

            vpc_stack=self.__vpc_stack,
            deployment_asset_stack=self.__deployment_asset_stack,
            security_group=self.__cluster_security_group_stack.master_security_group
        )
