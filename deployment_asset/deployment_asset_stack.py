from aws_cdk import core
from aws_cdk.aws_s3_assets import Asset


class DeploymentAssetStack(core.Stack):
    def __init__(
        self, scope: core.Construct, id: str,
        public_key_path: str,
        create_user_script_path: str,
        deploy_kubeadm_script_path: str,
        deploy_master_script_path: str,
        kubeadm_config_path: str,
        deploy_worker_script_path: str,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        self.public_key_asset = Asset(scope=self, id="public_key_asset", path=public_key_path)
        self.create_user_script_asset = Asset(scope=self, id="create_user_script_asset", path=create_user_script_path)
        self.deploy_kubeadm_script_asset = Asset(scope=self, id="deploy_kubeadm_script_asset", path=deploy_kubeadm_script_path)
        self.deploy_master_script_asset = Asset(scope=self, id="deploy_master_script_asset", path=deploy_master_script_path)
        self.kubeadm_config_asset = Asset(scope=self, id="deploy_kubeadm_asset", path=kubeadm_config_path)
        self.deploy_worker_script_asset = Asset(scope=self, id="deploy_worker_script_asset", path=deploy_worker_script_path)
