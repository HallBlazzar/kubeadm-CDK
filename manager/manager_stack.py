from utils.instance_constructor import InstanceConstructor, InstanceConstructionProperties
from aws_cdk import core
from aws_cdk.aws_ec2 import SecurityGroup
from aws_cdk.aws_ec2 import UserData
from deployment_asset.deployment_asset_stack import DeploymentAssetStack
from utils.user_data_helper import LocalAssetCreator, AttachAWSCliInstallation, AccessGranter


class ManagerStack(core.Stack):
    def __init__(
        self, scope: core.Construct, id: str,
        instance_construction_properties: InstanceConstructionProperties,
        deployment_asset_stack: DeploymentAssetStack, security_group: SecurityGroup,
        master_instance_private_ip: str, number_of_worker_node: int,
        **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        self.__deployment_asset_stack = deployment_asset_stack
        self.__master_instance_private_ip = master_instance_private_ip
        self.__number_of_worker_node = number_of_worker_node

        user_data = self.__get_user_data()

        manager_instance = InstanceConstructor(
            scope=self, instance_construction_properties=instance_construction_properties, user_data=user_data
        ).construct_public_node("manager")

        manager_instance.add_security_group(security_group)
        self.__grant_access_to_asset(manager_instance)

    def __get_user_data(self) -> UserData:
        user_data = UserData.for_linux()

        AttachAWSCliInstallation.execute(user_data)

        local_deploy_manager_script = LocalAssetCreator.execute(target_asset=self.__deployment_asset_stack.deploy_manager_script_asset, user_data=user_data)

        local_public_key = LocalAssetCreator.execute(target_asset=self.__deployment_asset_stack.public_key_asset, user_data=user_data)
        local_create_user_script = LocalAssetCreator.execute(target_asset=self.__deployment_asset_stack.create_user_script_asset, user_data=user_data)
        local_check_master_ready_script = LocalAssetCreator.execute(target_asset=self.__deployment_asset_stack.check_master_ready_script_asset, user_data=user_data)
        local_private_key = LocalAssetCreator.execute(target_asset=self.__deployment_asset_stack.private_key_asset, user_data=user_data)

        local_rook_pod_security_policy = LocalAssetCreator.execute(target_asset=self.__deployment_asset_stack.rook_pod_security_policy_asset, user_data=user_data)
        local_ceph_file_system = LocalAssetCreator.execute(target_asset=self.__deployment_asset_stack.ceph_file_system_asset, user_data=user_data)
        local_storage_class = LocalAssetCreator.execute(target_asset=self.__deployment_asset_stack.storage_class_asset, user_data=user_data)

        user_data.add_execute_file_command(
            file_path=local_deploy_manager_script,
            arguments="{} {} {} {} {} {} {} {} {}".format(
                local_public_key,
                local_create_user_script,
                local_check_master_ready_script,
                self.__master_instance_private_ip,
                local_private_key,
                local_rook_pod_security_policy,
                local_ceph_file_system,
                local_storage_class,
                self.__number_of_worker_node
            )
        )

        return user_data

    def __grant_access_to_asset(self, manager_instance):
        AccessGranter.execute(
            manager_instance,
            self.__deployment_asset_stack.public_key_asset,
            self.__deployment_asset_stack.create_user_script_asset,
            self.__deployment_asset_stack.deploy_manager_script_asset,
            self.__deployment_asset_stack.check_master_ready_script_asset,
            self.__deployment_asset_stack.private_key_asset,
            self.__deployment_asset_stack.rook_pod_security_policy_asset,
            self.__deployment_asset_stack.ceph_file_system_asset,
            self.__deployment_asset_stack.storage_class_asset
        )
