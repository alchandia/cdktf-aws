from constructs import Construct
from cdktf import App, TerraformStack, Token, TerraformOutput
from imports.aws import AwsProvider
from imports.vpc import Vpc
from imports.ecscluster import Ecscluster
from imports.ecsservice import Ecsservice

aws_region='us-east-1'
ec2_instance_type="t3a.nano"
id_app="cap"

class Stack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        AwsProvider(self, 'Aws', region=aws_region)

        my_vpc = Vpc(self, id_app + "-vpc",
            name=id_app + "-vpc",
            cidr='10.0.0.0/16',
            azs=["us-east-1a", "us-east-1b"],
            public_subnets=["10.0.1.0/24", "10.0.2.0/24"]
        )

        my_ecscluster = Ecscluster(self, id_app + "-ecs-cluster",
            region=aws_region,
            vpc_id=Token().as_string(my_vpc.vpc_id_output),
            subnet_ids=Token().as_list(my_vpc.public_subnets_output),
            component="poc",
            deployment_identifier="web",
            cluster_name=id_app + "-ecs-cluster",
            cluster_instance_type=ec2_instance_type,
            cluster_minimum_size="1",
            cluster_maximum_size="1",
            cluster_desired_capacity="1",
            cluster_instance_root_block_device_type="gp2",
            associate_public_ip_addresses="yes"
        )

        Ecsservice(self, id_app + "-ecs-service",
            ecs_cluster_id=Token().as_string(my_ecscluster.cluster_id_output),
            service_name='nginx',
            image_name='nginx:stable-alpine',
            service_memory=256,
            port_mappings=[
                {
                "containerPort": 80,
                "hostPort": 80,
                "protocol": "tcp"
                }
            ]
        )

        TerraformOutput(self, 'security_group_id_output',
            value=Token().as_string(my_ecscluster.security_group_id_output)
        )

app = App()
Stack(app, "cdktf-aws-python")

app.synth()
