from aws_cdk import core
from aws_cdk.aws_s3_assets import Asset


class DeploymentAssetStack(core.Stack):
    def __init__(
        self, scope: core.Construct, id: str,
        public_key_path: str,
        private_key_path: str,
        create_user_script_path: str,
        deploy_kubeadm_script_path: str,
        deploy_master_script_path: str,
        kubeadm_config_path: str,
        deploy_worker_script_path: str,
        check_master_ready_script_path: str,
        deploy_manager_script_asset: str,
        rook_pod_security_policy: str,
        ceph_file_system: str,
        storage_class: str,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        self.public_key_asset = Asset(scope=self, id="public_key_asset", path=public_key_path)
        self.private_key_asset = Asset(scope=self, id="private_key_asset", path=private_key_path)
        self.create_user_script_asset = Asset(scope=self, id="create_user_script_asset", path=create_user_script_path)
        self.deploy_kubeadm_script_asset = Asset(scope=self, id="deploy_kubeadm_script_asset", path=deploy_kubeadm_script_path)
        self.deploy_master_script_asset = Asset(scope=self, id="deploy_master_script_asset", path=deploy_master_script_path)
        self.kubeadm_config_asset = Asset(scope=self, id="deploy_kubeadm_asset", path=kubeadm_config_path)
        self.deploy_worker_script_asset = Asset(scope=self, id="deploy_worker_script_asset", path=deploy_worker_script_path)
        self.check_master_ready_script_asset = Asset(scope=self, id="check_master_ready_script_asset", path=check_master_ready_script_path)
        self.deploy_manager_script_asset = Asset(scope=self, id="deploy_manager_script_asset", path=deploy_manager_script_asset)

        self.rook_pod_security_policy_asset = Asset(scope=self, id="rook_pod_security_policy_asset", path=rook_pod_security_policy)
        self.ceph_file_system_asset = Asset(scope=self, id="ceph_file_system_asset", path=ceph_file_system)
        self.storage_class_asset = Asset(scope=self, id="storage_class_asset", path=storage_class)
