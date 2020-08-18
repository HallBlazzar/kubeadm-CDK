#!/usr/bin/env python3

from aws_cdk import core

from vpc.vpc_stack_constructor import VpcStackConstructor
from cluster_security_group.cluster_security_group_stack_constructor import ClusterSecurityGroupStackConstructor
from deployment_asset.deployment_asset_stack_constructor import DeploymentAssetStackConstructor
from manager.manager_stack_constructor import ManagerStackConstructor
from master.master_stack_constructor import MasterStackConstructor
from worker.worker_stack_constructor import WorkerStackConstructor

from utils.config_loader import ConfigLoader
import os
from utils.file_reader import FileReader

config = ConfigLoader(config_path=os.path.join("resource", "config", "config.json")).fetch_config_from_json_file()
config["TOKEN"] = FileReader.execute(os.path.join("resource", "key", "token.txt"))

app = core.App()
env = core.Environment(account=config["ACCOUNT"], region=config["REGION"])

vpc_stack = VpcStackConstructor(scope=app, env=env, config=config).execute()
cluster_security_group_stack = ClusterSecurityGroupStackConstructor(
    scope=app, env=env, config=config, vpc_stack=vpc_stack
).execute()
deployment_asset_stack = DeploymentAssetStackConstructor(scope=app, env=env, config=config).execute()

master_stack = MasterStackConstructor(
    scope=app,
    env=env,
    config=config,

    vpc_stack=vpc_stack,
    deployment_asset_stack=deployment_asset_stack,
    cluster_security_group_stack=cluster_security_group_stack
).execute()

manager_stack = ManagerStackConstructor(
    scope=app,
    env=env,
    config=config,

    vpc_stack=vpc_stack,
    deployment_asset_stack=deployment_asset_stack,
    cluster_security_group_stack=cluster_security_group_stack,
    master_stack=master_stack
).execute()

worker_stack = WorkerStackConstructor(
    scope=app,
    env=env,
    config=config,

    vpc_stack=vpc_stack,
    deployment_asset_stack=deployment_asset_stack,
    cluster_security_group_stack=cluster_security_group_stack,
    master_stack=master_stack,
).execute()

app.synth()
