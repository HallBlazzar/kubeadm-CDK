from aws_cdk.aws_ec2 import Instance
from aws_cdk.aws_ec2 import InstanceType
from aws_cdk.aws_ec2 import MachineImage
from aws_cdk.aws_ec2 import Vpc
from aws_cdk.aws_ec2 import BlockDevice, BlockDeviceVolume
from aws_cdk.aws_ec2 import SubnetSelection
from aws_cdk.core import Construct
from aws_cdk.aws_ec2 import UserData


class InstanceConstructionProperties:
    def __init__(self, vpc: Vpc, instance_type: str, storage_size: int):
        self.vpc = vpc
        self.instance_type = instance_type
        self.storage_size = storage_size


class InstanceConstructor:
    def __init__(
        self, scope: Construct, instance_construction_properties: InstanceConstructionProperties, user_data: UserData
    ):
        self.__scope = scope
        self.__instance_construction_properties = instance_construction_properties
        self.__user_data = user_data

    def construct_public_node(self, instance_id: str) -> Instance:
        return self.construct_node_in_selected_subnet(
            instance_id=instance_id, selected_subnet=SubnetSelection(
                subnets=self.__instance_construction_properties.vpc.public_subnets
            )
        )

    def construct_private_node(self, instance_id: str) -> Instance:
        return self.construct_node_in_selected_subnet(
            instance_id=instance_id, selected_subnet=SubnetSelection(
                subnets=self.__instance_construction_properties.vpc.private_subnets
            )
        )

    def construct_node_in_selected_subnet(self,  selected_subnet: SubnetSelection, instance_id: str) -> Instance:
        block_device_list = self.__get_block_device_list()

        instance = Instance(
            scope=self.__scope,
            id=instance_id,
            instance_type=InstanceType(self.__instance_construction_properties.instance_type),
            machine_image=MachineImage().lookup(
                name="ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20200716", owners=["099720109477"]
            ),
            vpc=self.__instance_construction_properties.vpc,
            block_devices=block_device_list,
            vpc_subnets=selected_subnet,
            user_data=self.__user_data,
            key_name="default-key"
        )

        return instance

    def __get_block_device_list(self):
        block_device_list = [
            BlockDevice(
                device_name="/dev/xvda",
                volume=BlockDeviceVolume.ebs(self.__instance_construction_properties.storage_size)
            )
        ]

        return block_device_list
