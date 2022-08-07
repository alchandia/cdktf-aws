from constructs import Construct
from cdktf import App, TerraformStack, Token
from imports.aws import AwsProvider
from imports.vpc import Vpc
from imports.secgroup import Secgroup
from imports.s3bucket import S3Bucket


class Stack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        AwsProvider(self, 'Aws', region='us-east-1')

        cap_vpc = Vpc(self, 'cap-vpc',
            name='cap-vpc',
            cidr='10.0.0.0/16',
            azs=["us-east-1a", "us-east-1b"],
            public_subnets=["10.0.1.0/24", "10.0.2.0/24"]
            )

        Secgroup(self, 'cap-ecs',
            name='cap-ecs',
            description='Security Group for ECS instances',
            vpc_id=Token().as_string(cap_vpc.vpc_id_output),
            ingress_with_cidr_blocks=[
                {
                "from_port": "80",
                "to_port": "80",
                "protocol": "tcp",
                "description": "Public HTTP",
                "cidr_blocks": "0.0.0.0/0"
                }
              ]
            )

        S3Bucket(self, 'cap-backups',
            bucket='cap-backups-663423874867',
            force_destroy=False,
            acl="private",
            block_public_acls=True,
            block_public_policy=True,
            ignore_public_acls=True,
            restrict_public_buckets=True
            )

app = App()
Stack(app, "cdktf-aws-python")

app.synth()
