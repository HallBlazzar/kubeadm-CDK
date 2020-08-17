#!/usr/bin/env python3

from aws_cdk import core

from vpc.vpc_stack_constructor import VpcStackConstructor
from cluster_security_group.cluster_security_group_stack_constructor import ClusterSecurityGroupStackConstructor
from manager.manager_stack import ManagerStack
from master.master_stack import MasterStack
from utils.instance_constructor import InstanceConstructionProperties
from worker.worker_stack import WorkerStack
from deployment_asset.deployment_asset_stack import DeploymentAssetStack

from utils.config_loader import ConfigLoader
import os
from utils.kubeadm_config_creator import KubeadmConfigCreator
from utils.file_reader import FileReader

config = ConfigLoader(config_path=os.path.join("resource", "config", "config.json")).fetch_config_from_json_file()

app = core.App()

env = core.Environment(account=config["ACCOUNT"], region=config["REGION"])

vpc_stack = VpcStackConstructor(scope=app, env=env, config=config).execute()

cluster_security_group_stack = ClusterSecurityGroupStackConstructor(
    scope=app, env=env, config=config, vpc_stack=vpc_stack
).execute()


deployment_asset_stack = DeploymentAssetStack(
    scope=app, id="{}Assets".format(config["ENVIRONMENT_NAME"]),
    create_user_script_path=os.path.join("resource", "script", "create_user.sh"),
    public_key_path=os.path.join("resource", "key", "id_rsa.pub"),
    deploy_kubeadm_script_path=os.path.join("resource", "script", "deploy_kubeadm.sh"),
    deploy_master_script_path=os.path.join("resource", "script", "deploy_master.sh"),
    kubeadm_config_path=KubeadmConfigCreator(
        kubeadm_config_template_path=os.path.join("resource", "template", "kubeadm-config.yaml.j2"),
        token_path=os.path.join("resource", "key", "token.txt")
    ).execute(),
    deploy_worker_script_path=os.path.join("resource", "script", "deploy_worker.sh"),
    check_master_ready_script_path=os.path.join("resource", "script", "check_master_ready.sh"),
    deploy_manager_script_asset=os.path.join("resource", "script", "deploy_manager.sh"),
    private_key_path=os.path.join("resource", "key", "id_rsa"),
    rook_pod_security_policy=os.path.join("resource", "rook", "pod-security-policy.yaml"),
    ceph_file_system=os.path.join("resource", "rook", "ceph-file-system.yaml"),
    storage_class=os.path.join("resource", "rook", "storage-class.yaml"),
    env=env
)

instance_construction_properties = InstanceConstructionProperties(
    vpc=vpc_stack.vpc, instance_type=config["INSTANCE_TYPE"], storage_size=config["STORAGE_SIZE"]
)

master_stack = MasterStack(
    scope=app, id="{}Master".format(config["ENVIRONMENT_NAME"]),
    instance_construction_properties=instance_construction_properties,
    deployment_asset_stack=deployment_asset_stack,
    security_group=cluster_security_group_stack.master_security_group, env=env
)

manager_stack = ManagerStack(
    scope=app, id="{}Manager".format(config["ENVIRONMENT_NAME"]),
    instance_construction_properties=instance_construction_properties,
    deployment_asset_stack=deployment_asset_stack,
    master_instance_private_ip=master_stack.master_instance.instance_private_ip,
    security_group=cluster_security_group_stack.manager_security_group,
    number_of_worker_node=config["NUMBER_OF_WORKER"],
    env=env
)

worker_stack = WorkerStack(
    scope=app, id="{}Worker".format(config["ENVIRONMENT_NAME"]),
    instance_construction_properties=instance_construction_properties,
    deployment_asset_stack=deployment_asset_stack,
    security_group=cluster_security_group_stack.worker_security_group,
    number_of_worker=config["NUMBER_OF_WORKER"],
    token=FileReader.execute(os.path.join("resource", "key", "token.txt")),
    master_instance_private_ip=master_stack.master_instance.instance_private_ip,
    env=env
)

app.synth()
