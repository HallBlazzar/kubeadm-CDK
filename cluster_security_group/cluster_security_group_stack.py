from aws_cdk.aws_ec2 import SecurityGroup
from cluster_security_group.security_group_rule_creator import ManagerSecurityGroupRuleCreator
from cluster_security_group.security_group_rule_creator import MasterSecurityGroupRuleCreator
from cluster_security_group.security_group_rule_creator import WorkerSecurityGroupRuleCreator

from aws_cdk import core
from aws_cdk.aws_ec2 import Vpc


class ClusterSecurityGroupStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, vpc: Vpc, **kwargs):
        super(ClusterSecurityGroupStack, self).__init__(scope, id, **kwargs)
        self.__scope = scope

        self.manager_security_group = SecurityGroup(scope=self, id="manager-sg", vpc=vpc, allow_all_outbound=True)
        self.master_security_group = SecurityGroup(scope=self, id="master-sg", vpc=vpc, allow_all_outbound=True)
        self.worker_security_group = SecurityGroup(scope=self, id="worker-sg", vpc=vpc, allow_all_outbound=True)

        self.__create_rules()

    def __create_rules(self):
        self.__create_manager_security_group_rules()
        self.__create_master_security_group_rules()
        self.__create_worker_security_group_rule()

    def __create_manager_security_group_rules(self):
        ManagerSecurityGroupRuleCreator(
            manager_security_group=self.manager_security_group, master_security_group=self.master_security_group,
            worker_security_group=self.worker_security_group
        ).execute()

    def __create_master_security_group_rules(self):
        MasterSecurityGroupRuleCreator(
            manager_security_group=self.manager_security_group, master_security_group=self.master_security_group,
            worker_security_group=self.worker_security_group
        ).execute()

    def __create_worker_security_group_rule(self):
        WorkerSecurityGroupRuleCreator(
            manager_security_group=self.manager_security_group, master_security_group=self.master_security_group,
            worker_security_group=self.worker_security_group
        ).execute()
