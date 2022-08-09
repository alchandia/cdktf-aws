from constructs import Construct
from cdktf import App, TerraformStack, Token, TerraformOutput
from imports.aws import AwsProvider
from imports.vpc import Vpc
from imports.secgroup import Secgroup
from imports.s3bucket import S3Bucket
from imports.asg import Asg
from imports.ecscluster import Ecscluster
import base64

user_data_script='''
#!/bin/bash
cat <<'EOF' >> /etc/ecs/ecs.config
ECS_CLUSTER=cap-ecs
EOF
'''[1:-1]
user_data_script_bytes = user_data_script.encode("ascii")
user_data_script_base64_bytes = base64.b64encode(user_data_script_bytes)
user_data_script_base64_string = user_data_script_base64_bytes.decode("ascii")

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

        cap_secgroup_ecs = Secgroup(self, 'cap-ecs',
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

        my_asg = Asg(self, 'cap-asg',
            name='cap-asg-ecs',
            vpc_zone_identifier=Token().as_list(cap_vpc.public_subnets_output),
            security_groups=Token().as_list(cap_secgroup_ecs.security_group_id),
            user_data = user_data_script_base64_string,
            ignore_desired_capacity_changes=True,
            create_iam_instance_profile=True,
            iam_role_name='ecs-instance',
            iam_role_policies={
                "AmazonEC2ContainerServiceforEC2Role": "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
            },
            health_check_type='EC2',
            autoscaling_group_tags={
                "AmazonECSManaged": 'True'
            },
            min_size=1,
            max_size=1,
            desired_capacity=1,
            instance_type="t3a.nano",
            image_id='ami-040d909ea4e56f8f3'
            )

        Ecscluster(self, 'cap-ecs-cluster',
            cluster_name='cap-ecs-cluster',
            default_capacity_provider_use_fargate=False,
            autoscaling_capacity_providers=dict({
                "one": dict({
                    "auto_scaling_group_arn": Token().as_string(my_asg.autoscaling_group_arn_output)
                })
            })
        )

        TerraformOutput(self, 'my_asg_arn',
            value=Token().as_string(my_asg.autoscaling_group_arn_output)
        )

app = App()
Stack(app, "cdktf-aws-python")

app.synth()
