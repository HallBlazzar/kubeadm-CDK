from aws_cdk.core import Construct
from aws_cdk.core import Environment
from deployment_asset.utils import KubeadmConfigCreator
import os
from aws_cdk import core
from aws_cdk.aws_s3_assets import Asset


class DeploymentAssetStack(core.Stack):
    def __init__(
        self, scope: core.Construct, id: str,
        public_key_path: str,
        private_key_path: str,
        create_user_script_path: str,

        kubeadm_config_path: str,
        check_master_ready_script_path: str,
        deploy_kubeadm_script_path: str,

        deploy_master_script_path: str,
        deploy_manager_script_asset: str,
        deploy_worker_script_path: str,

        rook_pod_security_policy: str,
        ceph_file_system: str,
        storage_class: str,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        self.public_key_asset = self.__create_asset(id="public_key_asset", path=public_key_path)
        self.private_key_asset = self.__create_asset(id="private_key_asset", path=private_key_path)
        self.create_user_script_asset = self.__create_asset(id="create_user_script_asset", path=create_user_script_path)

        self.kubeadm_config_asset = self.__create_asset(id="deploy_kubeadm_asset", path=kubeadm_config_path)
        self.check_master_ready_script_asset = self.__create_asset(id="check_master_ready_script_asset", path=check_master_ready_script_path)
        self.deploy_kubeadm_script_asset = self.__create_asset(id="deploy_kubeadm_script_asset", path=deploy_kubeadm_script_path)

        self.deploy_master_script_asset = self.__create_asset(id="deploy_master_script_asset", path=deploy_master_script_path)
        self.deploy_manager_script_asset = self.__create_asset(id="deploy_manager_script_asset", path=deploy_manager_script_asset)
        self.deploy_worker_script_asset = self.__create_asset(id="deploy_worker_script_asset", path=deploy_worker_script_path)

        self.rook_pod_security_policy_asset = self.__create_asset(id="rook_pod_security_policy_asset", path=rook_pod_security_policy)
        self.ceph_file_system_asset = self.__create_asset(id="ceph_file_system_asset", path=ceph_file_system)
        self.storage_class_asset = self.__create_asset(id="storage_class_asset", path=storage_class)

    def __create_asset(self, id: str, path: str):
        return Asset(scope=self, id=id, path=path)


class DeploymentAssetStackConstructor:
    def __init__(self, scope: Construct, env: Environment, config: dict):
        self.__scope = scope
        self.__env = env
        self.__config = config

    def execute(self):
        kubeadm_config_path = KubeadmConfigCreator(
            kubeadm_config_template_path=os.path.join("resource", "template", "kubeadm-config.yaml.j2"),
            token_path=os.path.join("resource", "key", "token.txt")
        ).execute()

        return DeploymentAssetStack(
            scope=self.__scope,
            id="{}Assets".format(self.__config["ENVIRONMENT_NAME"]),
            env=self.__env,

            private_key_path=os.path.join("resource", "key", "id_rsa"),
            public_key_path=os.path.join("resource", "key", "id_rsa.pub"),
            create_user_script_path=os.path.join("resource", "script", "create_user.sh"),

            kubeadm_config_path=kubeadm_config_path,
            check_master_ready_script_path=os.path.join("resource", "script", "check_master_ready.sh"),
            deploy_kubeadm_script_path=os.path.join("resource", "script", "deploy_kubeadm.sh"),

            deploy_master_script_path=os.path.join("resource", "script", "deploy_master.sh"),
            deploy_manager_script_asset=os.path.join("resource", "script", "deploy_manager.sh"),
            deploy_worker_script_path=os.path.join("resource", "script", "deploy_worker.sh"),

            rook_pod_security_policy=os.path.join("resource", "rook", "pod-security-policy.yaml"),
            ceph_file_system=os.path.join("resource", "rook", "ceph-file-system.yaml"),
            storage_class=os.path.join("resource", "rook", "storage-class.yaml"),
        )
