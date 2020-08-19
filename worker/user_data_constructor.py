from aws_cdk.aws_ec2 import UserData
from utils.user_data_construction_utils import LocalAssetCreator
from utils.user_data_construction_utils import AWSCliInstallationAttacher
from deployment_asset.deployment_asset_stack_constructor import DeploymentAssetStack
from aws_cdk.aws_ec2 import Instance
from master.master_stack_constructor import MasterStack


class WorkerUserDataConstructor:
    def __init__(
        self,
        master_stack: MasterStack,
        deployment_asset_stack: DeploymentAssetStack,
        token: str,

        instance: Instance
    ):
        self.__master_private_ip = master_stack.master_instance.instance_private_ip
        self.__token = token

        self.__user_data = UserData.for_linux()
        self.__local_asset_creator = LocalAssetCreator(user_data=self.__user_data, instance=instance)

        self.__deploy_worker_script_asset = deployment_asset_stack.deploy_worker_script_asset
        self.__public_key_asset = deployment_asset_stack.public_key_asset
        self.__create_user_script_asset = deployment_asset_stack.create_user_script_asset
        self.__deploy_kubeadm_script_asset = deployment_asset_stack.deploy_kubeadm_script_asset
        self.__check_master_ready_script_asset = deployment_asset_stack.check_master_ready_script_asset

    def execute(self):
        AWSCliInstallationAttacher(self.__user_data).execute()

        local_deploy_worker_script = self.__local_asset_creator.execute(self.__deploy_worker_script_asset)
        local_public_key = self.__local_asset_creator.execute(self.__public_key_asset)
        local_create_user_script = self.__local_asset_creator.execute(self.__create_user_script_asset)
        local_deploy_kubeadm_script = self.__local_asset_creator.execute(self.__deploy_kubeadm_script_asset)
        local_check_master_ready_script = self.__local_asset_creator.execute(self.__check_master_ready_script_asset)

        self.__user_data.add_execute_file_command(
            file_path=local_deploy_worker_script,
            arguments="{} {} {} {} {} {} &".format(
                local_public_key,
                local_create_user_script,
                local_deploy_kubeadm_script,
                self.__token,
                self.__master_private_ip,
                local_check_master_ready_script
            )
        )

        return self.__user_data
