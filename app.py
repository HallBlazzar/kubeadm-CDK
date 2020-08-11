#!/usr/bin/env python3

from aws_cdk import core

from vpc.vpc_stack import VpcStack
from cluster_security_group.cluster_security_group_stack import ClusterSecurityGroupStack
from manager.manager_stack import ManagerStack
from master.master_stack import MasterStack
from utils.instance_constructor import InstanceConstructionProperties
from worker.worker_stack import WorkerStack
from deployment_asset.deployment_asset_stack import DeploymentAssetStack

from utils.config_loader import ConfigLoader
import os
from utils.kubeadm_config_creator import KubeadmConfigCreator

config = ConfigLoader(config_path="resource/config/config.json").fetch_config_from_json_file()

app = core.App()

env = core.Environment(account=config["ACCOUNT"], region=config["REGION"])

vpc_stack = VpcStack(scope=app, id="{}Vpc".format(config["ENVIRONMENT_NAME"]), env=env)

cluster_security_group_stack = ClusterSecurityGroupStack(
    scope=app, id="{}SG".format(config["ENVIRONMENT_NAME"]), vpc=vpc_stack.vpc, env=env
)

instance_construction_properties = InstanceConstructionProperties(
    vpc=vpc_stack.vpc, instance_type=config["INSTANCE_TYPE"], storage_size=config["STORAGE_SIZE"]
)

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
    env=env
)

manager_stack = ManagerStack(
    scope=app, id="{}Manager".format(config["ENVIRONMENT_NAME"]),
    instance_construction_properties=instance_construction_properties,
    deployment_asset_stack=deployment_asset_stack,
    security_group=cluster_security_group_stack.manager_security_group, env=env
)

master_stack = MasterStack(
    scope=app, id="{}Master".format(config["ENVIRONMENT_NAME"]),
    instance_construction_properties=instance_construction_properties,
    deployment_asset_stack=deployment_asset_stack,
    security_group=cluster_security_group_stack.master_security_group, env=env
)

worker_stack = WorkerStack(
    scope=app, id="{}Worker".format(config["ENVIRONMENT_NAME"]),
    instance_construction_properties=instance_construction_properties,
    deployment_asset_stack=deployment_asset_stack,
    security_group=cluster_security_group_stack.worker_security_group,
    number_of_worker=config["NUMBER_OF_WORKER"], env=env
)

app.synth()
