from aws_cdk.core import Stack
from aws_cdk.core import Construct
from vpc.vpc_stack_constructor import VpcStack
from aws_cdk.aws_ec2 import SecurityGroup
from deployment_asset.deployment_asset_stack_constructor import DeploymentAssetStack
from manager.user_data_constructor import ManagerUserDataConstructor
from utils.instance_constructor import PublicInstanceConstructor
from master.master_stack_constructor import MasterStack
from aws_cdk.core import Environment
from cluster_security_group.cluster_security_group_stack_constructor import ClusterSecurityGroupStack


class ManagerStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        config: dict,
        vpc_stack: VpcStack,
        deployment_asset_stack: DeploymentAssetStack,
        security_group: SecurityGroup,
        master_stack: MasterStack,
        **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        manager_instance = PublicInstanceConstructor(
            scope=self,
            config=config,
            instance_id="manager",
            vpc_stack=vpc_stack
        ).execute()

        user_data = ManagerUserDataConstructor(
            config=config,
            deployment_asset_stack=deployment_asset_stack,
            instance=manager_instance,
            master_stack=master_stack
        ).execute()
        row_user_data = user_data.render()

        manager_instance.add_user_data(row_user_data)
        manager_instance.add_security_group(security_group)


class ManagerStackConstructor:
    def __init__(
        self,
        scope: Construct,
        env: Environment,
        config: dict,

        vpc_stack: VpcStack,
        deployment_asset_stack: DeploymentAssetStack,
        cluster_security_group_stack: ClusterSecurityGroupStack,
        master_stack: MasterStack
    ):
        self.__scope = scope
        self.__env = env
        self.__config = config

        self.__vpc_stack = vpc_stack
        self.__deployment_asset_stack = deployment_asset_stack
        self.__cluster_security_group_stack = cluster_security_group_stack
        self.__master_stack = master_stack

    def execute(self):
        return ManagerStack(
            scope=self.__scope,
            env=self.__env,
            id="{}Manager".format(self.__config["ENVIRONMENT_NAME"]),

            config=self.__config,

            vpc_stack=self.__vpc_stack,
            deployment_asset_stack=self.__deployment_asset_stack,
            security_group=self.__cluster_security_group_stack.manager_security_group,
            master_stack=self.__master_stack
        )
