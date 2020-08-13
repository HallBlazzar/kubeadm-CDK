from utils.instance_constructor import InstanceConstructor, InstanceConstructionProperties
from aws_cdk import core
from aws_cdk.aws_ec2 import SecurityGroup
from deployment_asset.deployment_asset_stack import DeploymentAssetStack
from aws_cdk.aws_ec2 import UserData
from utils.user_data_helper import LocalAssetCreator, AttachAWSCliInstallation, AccessGranter


class WorkerStack(core.Stack):
    def __init__(
        self, scope: core.Construct, id: str,
        instance_construction_properties: InstanceConstructionProperties,
        deployment_asset_stack: DeploymentAssetStack,
        token: str, master_instance_private_ip: str, security_group: SecurityGroup, number_of_worker: int,
        **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        self.__deployment_asset_stack = deployment_asset_stack
        self.__token = token
        self.__master_instance_private_ip = master_instance_private_ip

        user_data = self.__get_user_data()

        for i in range(number_of_worker):
            worker_instance = InstanceConstructor(
                scope=self, instance_construction_properties=instance_construction_properties, user_data=user_data
            ).construct_public_node("worker-{}".format(i))
            worker_instance.add_security_group(security_group)
            self.__grant_access_to_asset(worker_instance)

    def __get_user_data(self) -> UserData:
        user_data = UserData.for_linux()

        AttachAWSCliInstallation.execute(user_data)

        local_deploy_worker_script = LocalAssetCreator.execute(target_asset=self.__deployment_asset_stack.deploy_worker_script_asset, user_data=user_data)

        local_public_key = LocalAssetCreator.execute(target_asset=self.__deployment_asset_stack.public_key_asset, user_data=user_data)
        local_create_user_script = LocalAssetCreator.execute(target_asset=self.__deployment_asset_stack.create_user_script_asset, user_data=user_data)
        local_deploy_kubeadm_script = LocalAssetCreator.execute(target_asset=self.__deployment_asset_stack.deploy_kubeadm_script_asset, user_data=user_data)
        local_check_master_ready_script = LocalAssetCreator.execute(target_asset=self.__deployment_asset_stack.check_master_ready_script_asset, user_data=user_data)

        user_data.add_execute_file_command(
            file_path=local_deploy_worker_script,
            arguments="{} {} {} {} {} {}".format(
                local_public_key, local_create_user_script, local_deploy_kubeadm_script,
                self.__token, self.__master_instance_private_ip, local_check_master_ready_script
            )
        )

        return user_data

    def __grant_access_to_asset(self, instance):
        AccessGranter.execute(
            instance,
            self.__deployment_asset_stack.deploy_worker_script_asset,
            self.__deployment_asset_stack.public_key_asset,
            self.__deployment_asset_stack.create_user_script_asset,
            self.__deployment_asset_stack.deploy_kubeadm_script_asset,
            self.__deployment_asset_stack.check_master_ready_script_asset
        )
