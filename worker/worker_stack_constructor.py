from utils.instance_constructor import PublicInstanceConstructor
from aws_cdk.core import Stack
from aws_cdk.core import Construct
from aws_cdk.aws_ec2 import SecurityGroup
from deployment_asset.deployment_asset_stack_constructor import DeploymentAssetStack
from worker.user_data_constructor import WorkerUserDataConstructor
from master.master_stack_constructor import MasterStack
from vpc.vpc_stack_constructor import VpcStack
from aws_cdk.core import Environment
from cluster_security_group.cluster_security_group_stack_constructor import ClusterSecurityGroupStack


class WorkerStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        config: dict,

        deployment_asset_stack: DeploymentAssetStack,
        master_stack: MasterStack,
        vpc_stack: VpcStack,
        security_group: SecurityGroup,

        token: str,
        number_of_worker: int,

        **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        for i in range(number_of_worker):
            worker_instance = PublicInstanceConstructor(
                scope=self,
                config=config,
                instance_id="worker-{}".format(i),
                vpc_stack=vpc_stack
            ).execute()

            user_data = WorkerUserDataConstructor(
                master_stack=master_stack,
                deployment_asset_stack=deployment_asset_stack,
                token=token,
                instance=worker_instance
            ).execute()
            row_user_data = user_data.render()

            worker_instance.add_user_data(row_user_data)
            worker_instance.add_security_group(security_group)


class WorkerStackConstructor:
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
        return WorkerStack(
            scope=self.__scope,
            env=self.__env,
            id="{}Worker".format(self.__config["ENVIRONMENT_NAME"]),

            config=self.__config,
            deployment_asset_stack=self.__deployment_asset_stack,
            vpc_stack=self.__vpc_stack,
            master_stack=self.__master_stack,

            number_of_worker=self.__config["NUMBER_OF_WORKER"],
            security_group=self.__cluster_security_group_stack.worker_security_group,
            token=self.__config["TOKEN"]
        )
