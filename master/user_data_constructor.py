from aws_cdk.aws_ec2 import UserData
from utils.user_data_construction_utils import LocalAssetCreator
from utils.user_data_construction_utils import AWSCliInstallationAttacher
from deployment_asset.deployment_asset_stack_constructor import DeploymentAssetStack
from aws_cdk.aws_ec2 import Instance


class MasterUserDataConstructor:
    def __init__(self, deployment_asset_stack: DeploymentAssetStack, instance: Instance):
        self.__user_data = UserData.for_linux()
        self.__local_asset_creator = LocalAssetCreator(user_data=self.__user_data, instance=instance)

        self.__deploy_master_script_asset = deployment_asset_stack.deploy_master_script_asset
        self.__public_key_asset = deployment_asset_stack.public_key_asset
        self.__create_user_script_asset = deployment_asset_stack.create_user_script_asset
        self.__deploy_kubeadm_script_asset = deployment_asset_stack.deploy_kubeadm_script_asset
        self.__kubeadm_config_asset = deployment_asset_stack.kubeadm_config_asset

    def execute(self) -> UserData:
        AWSCliInstallationAttacher(self.__user_data).execute()

        local_deploy_master_script = self.__local_asset_creator.execute(self.__deploy_master_script_asset)
        local_public_key = self.__local_asset_creator.execute(self.__public_key_asset)
        local_create_user_script = self.__local_asset_creator.execute(self.__create_user_script_asset)
        local_deploy_kubeadm_script = self.__local_asset_creator.execute(self.__deploy_kubeadm_script_asset)
        local_kubeadm_config = self.__local_asset_creator.execute(self.__kubeadm_config_asset)

        self.__user_data.add_execute_file_command(
            file_path=local_deploy_master_script,
            arguments="{} {} {} {}".format(
                local_public_key,
                local_create_user_script,
                local_deploy_kubeadm_script,
                local_kubeadm_config
            )
        )

        return self.__user_data
