from aws_cdk.aws_s3_assets import Asset
from aws_cdk.aws_ec2 import UserData
from aws_cdk.aws_ec2 import Instance


class LocalAssetCreator:
    @staticmethod
    def execute(target_asset: Asset, user_data: UserData):
        return user_data.add_s3_download_command(
            bucket=target_asset.bucket,
            bucket_key=target_asset.s3_object_key
        )


class AttachAWSCliInstallation:
    @staticmethod
    def execute(user_data: UserData):
        user_data.add_commands(
            "apt-get update",
            "apt-get install -y awscli",
            "aws configure set s3.signature_version s3v4"
        )


class AccessGranter:
    @staticmethod
    def execute(instance: Instance, *assets):
        for asset in assets:
            asset.grant_read(instance.role)
