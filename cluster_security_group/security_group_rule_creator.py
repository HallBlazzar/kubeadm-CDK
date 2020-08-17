from aws_cdk.aws_ec2 import Port
from abc import ABCMeta, abstractmethod
from aws_cdk.aws_ec2 import SecurityGroup


class SecurityGroupRuleCreatorBase(metaclass=ABCMeta):
    def __init__(
            self, manager_security_group: SecurityGroup, master_security_group: SecurityGroup,
            worker_security_group: SecurityGroup
    ):
        self._manager_security_group = manager_security_group
        self._master_security_group = master_security_group
        self._worker_security_group = worker_security_group

    @abstractmethod
    def execute(self):
        pass


class ManagerSecurityGroupRuleCreator(SecurityGroupRuleCreatorBase):
    def __init__(
            self, manager_security_group: SecurityGroup, master_security_group: SecurityGroup,
            worker_security_group: SecurityGroup
    ):
        super().__init__(
            manager_security_group=manager_security_group, master_security_group=master_security_group,
            worker_security_group=worker_security_group
        )

    def execute(self):
        self._manager_security_group.connections.allow_from_any_ipv4(port_range=Port.tcp(22))


class MasterSecurityGroupRuleCreator(SecurityGroupRuleCreatorBase):
    def __init__(
            self, manager_security_group: SecurityGroup, master_security_group: SecurityGroup,
            worker_security_group: SecurityGroup
    ):
        super().__init__(
            manager_security_group=manager_security_group, master_security_group=master_security_group,
            worker_security_group=worker_security_group
        )

    def execute(self):
        self.__attach_api_server_access_rule()
        self.__attach_etcd_server_access_rule()
        self.__attach_api_server_internal_access_rule()
        self.__attach_manager_full_access()

    def __attach_api_server_access_rule(self):
        api_server_access_port = Port.tcp(port=6443)
        self._master_security_group.connections.allow_from_any_ipv4(port_range=api_server_access_port)

    def __attach_etcd_server_access_rule(self):
        etcd_server_access_port = Port.tcp_range(start_port=2379, end_port=2380)
        self._master_security_group.connections.allow_internally(port_range=etcd_server_access_port)

    def __attach_api_server_internal_access_rule(self):
        api_server_internal_port = Port.tcp_range(start_port=10250, end_port=10252)
        self._master_security_group.connections.allow_internally(port_range=api_server_internal_port)

    def __attach_manager_full_access(self):
        self._master_security_group.connections.allow_from(
            other=self._manager_security_group.connections, port_range=Port.all_traffic()
        )


class WorkerSecurityGroupRuleCreator(SecurityGroupRuleCreatorBase):
    def __init__(
            self, manager_security_group: SecurityGroup, master_security_group: SecurityGroup,
            worker_security_group: SecurityGroup
    ):
        super().__init__(
            manager_security_group=manager_security_group, master_security_group=master_security_group,
            worker_security_group=worker_security_group
        )

    def execute(self):
        self.__attach_api_server_control_rule()
        self.__attach_public_access_rule()
        self.__attach_manager_full_access_rule()
        self.__attach_inter_worker_access_rule()

    def __attach_api_server_control_rule(self):
        api_server_control_port = Port.tcp(port=10250)
        self._worker_security_group.connections.allow_from(
            other=self._master_security_group.connections, port_range=api_server_control_port
        )

    def __attach_public_access_rule(self):
        public_access_port = Port.tcp_range(start_port=30000, end_port=32767)
        self._worker_security_group.connections.allow_from_any_ipv4(port_range=public_access_port)

    def __attach_manager_full_access_rule(self):
        self._worker_security_group.connections.allow_from(
            other=self._manager_security_group.connections, port_range=Port.all_traffic()
        )

    def __attach_inter_worker_access_rule(self):
        self._worker_security_group.connections.allow_from(
            other=self._worker_security_group.connections, port_range=Port.all_traffic()
        )
