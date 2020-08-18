from aws_cdk.aws_ec2 import UserData
from utils.user_data_construction_utils import LocalAssetCreator
from utils.user_data_construction_utils import AWSCliInstallationAttacher
from deployment_asset.deployment_asset_stack_constructor import DeploymentAssetStack
from aws_cdk.aws_ec2 import Instance
from master.master_stack_constructor import MasterStack


class ManagerUserDataConstructor:
    def __init__(
        self,
        config: dict,
        master_stack: MasterStack,
        deployment_asset_stack: DeploymentAssetStack,

        instance: Instance
    ):
        self.__number_of_worker = config["NUMBER_OF_WORKER"]
        self.__master_private_ip = master_stack.master_instance.instance_private_ip

        self.__user_data = UserData.for_linux()
        self.__local_asset_creator = LocalAssetCreator(user_data=self.__user_data, instance=instance)

        self.__deploy_manager_script_asset = deployment_asset_stack.deploy_manager_script_asset
        self.__public_key_asset = deployment_asset_stack.public_key_asset
        self.__create_user_script_asset = deployment_asset_stack.create_user_script_asset
        self.__check_master_ready_script_asset = deployment_asset_stack.check_master_ready_script_asset
        self.__private_key_asset = deployment_asset_stack.private_key_asset

        self.__rook_pod_security_policy_asset = deployment_asset_stack.rook_pod_security_policy_asset
        self.__ceph_file_system_asset = deployment_asset_stack.ceph_file_system_asset
        self.__storage_class_asset = deployment_asset_stack.storage_class_asset

    def execute(self):
        AWSCliInstallationAttacher(self.__user_data).execute()

        local_deploy_manager_script = self.__local_asset_creator.execute(self.__deploy_manager_script_asset)

        local_public_key = self.__local_asset_creator.execute(self.__public_key_asset)
        local_create_user_script = self.__local_asset_creator.execute(self.__create_user_script_asset)
        local_check_master_ready_script = self.__local_asset_creator.execute(self.__check_master_ready_script_asset)
        local_private_key = self.__local_asset_creator.execute(self.__private_key_asset)
        local_rook_pod_security_policy = self.__local_asset_creator.execute(self.__rook_pod_security_policy_asset)
        local_ceph_file_system = self.__local_asset_creator.execute(self.__ceph_file_system_asset)
        local_storage_class = self.__local_asset_creator.execute(self.__storage_class_asset)

        self.__user_data.add_execute_file_command(
            file_path=local_deploy_manager_script,
            arguments="{} {} {} {} {} {} {} {} {}".format(
                local_public_key,
                local_create_user_script,
                local_check_master_ready_script,
                self.__master_private_ip,
                local_private_key,
                local_rook_pod_security_policy,
                local_ceph_file_system,
                local_storage_class,
                self.__number_of_worker
            )
        )

        return self.__user_data
