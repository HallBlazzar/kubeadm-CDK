from aws_cdk.aws_ec2 import Instance
from aws_cdk.aws_ec2 import InstanceType
from aws_cdk.aws_ec2 import MachineImage
from aws_cdk.aws_ec2 import BlockDevice, BlockDeviceVolume
from aws_cdk.aws_ec2 import SubnetSelection

from aws_cdk.core import Construct
from vpc.vpc_stack_constructor import VpcStack


class InstanceConstructor:
    def __init__(
        self,
        scope: Construct,
        config: dict,
        vpc_stack: VpcStack,
        selected_subnet: SubnetSelection,
        instance_id: str
    ):
        self.__scope = scope
        self.__vpc = vpc_stack.vpc
        self.__instance_type = config["INSTANCE_TYPE"]
        self.__storage_size = config["STORAGE_SIZE"]
        self.__image_id = config["IMAGE_ID"]
        self.__image_owner = config["IMAGE_OWNER"]
        self.__selected_subnet = selected_subnet
        self.__instance_id = instance_id
        self.__default_key = config["DEFAULT_KEY"]

    def execute(self) -> Instance:
        block_device_list = self.__get_block_device_list()

        if self.__default_key is None:
            instance = self.__get_instance_without_default_key(block_device_list)
        else:
            instance = self.__get_instance_with_default_key(block_device_list)

        return instance

    def __get_block_device_list(self):
        block_device_list = [
            BlockDevice(
                device_name="/dev/sda1",
                volume=BlockDeviceVolume.ebs(self.__storage_size)
            )
        ]

        return block_device_list

    def __get_instance_without_default_key(self, block_device_list):
        return Instance(
            scope=self.__scope,
            id=self.__instance_id,
            instance_type=InstanceType(self.__instance_type),
            machine_image=MachineImage().lookup(name=self.__image_id, owners=[self.__image_owner]),
            vpc=self.__vpc,
            block_devices=block_device_list,
            vpc_subnets=self.__selected_subnet
        )

    def __get_instance_with_default_key(self, block_device_list):
        return Instance(
            scope=self.__scope,
            id=self.__instance_id,
            instance_type=InstanceType(self.__instance_type),
            machine_image=MachineImage().lookup(name=self.__image_id, owners=[self.__image_owner]),
            vpc=self.__vpc,
            block_devices=block_device_list,
            vpc_subnets=self.__selected_subnet,
            key_name=self.__default_key
        )


class PublicInstanceConstructor:
    def __init__(
        self,
        scope: Construct,
        config: dict,
        vpc_stack: VpcStack,
        instance_id: str
    ):
        self.__scope = scope
        self.__config = config
        self.__vpc_stack = vpc_stack
        self.__instance_id = instance_id

    def execute(self) -> Instance:
        return InstanceConstructor(
            scope=self.__scope,
            config=self.__config,
            vpc_stack=self.__vpc_stack,
            instance_id=self.__instance_id,
            selected_subnet=SubnetSelection(subnets=self.__vpc_stack.vpc.public_subnets)
        ).execute()


class PrivateInstanceConstructor:
    def __init__(
        self,
        scope: Construct,
        config: dict,
        vpc_stack: VpcStack,
        instance_id: str
    ):
        self.__scope = scope
        self.__config = config
        self.__vpc_stack = vpc_stack
        self.__instance_id = instance_id

    def execute(self) -> Instance:
        return InstanceConstructor(
            scope=self.__scope,
            config=self.__config,
            vpc_stack=self.__vpc_stack,
            instance_id=self.__instance_id,
            selected_subnet=SubnetSelection(subnets=self.__vpc_stack.vpc.private_subnets)
        ).execute()
