from aws_cdk.aws_s3_assets import Asset
from aws_cdk.aws_ec2 import UserData
from aws_cdk.aws_ec2 import Instance


class AWSCliInstallationAttacher:
    def __init__(self, user_data):
        self.__user_data = user_data

    def execute(self):
        self.__user_data.add_commands(
            "apt-get update",
            "apt-get install -y awscli",
            "aws configure set s3.signature_version s3v4"
        )


class LocalAssetCreator:
    def __init__(self, user_data: UserData, instance: Instance):
        self.__user_data = user_data
        self.__instance = instance

    def execute(self, target_asset: Asset):
        local_asset = self.__user_data.add_s3_download_command(
            bucket=target_asset.bucket,
            bucket_key=target_asset.s3_object_key
        )

        target_asset.grant_read(self.__instance.role)

        return local_asset
