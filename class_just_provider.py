import json
from cdktf import Token, TerraformOutput, TerraformStack
from constructs import Construct
from jinja2 import Template
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.vpc import Vpc
from cdktf_cdktf_provider_aws.route_table import RouteTable
from cdktf_cdktf_provider_aws.subnet import Subnet
from cdktf_cdktf_provider_aws.internet_gateway import InternetGateway
from cdktf_cdktf_provider_aws.route_table_association import RouteTableAssociation
from cdktf_cdktf_provider_aws.route import Route
from cdktf_cdktf_provider_aws.security_group import SecurityGroup
from cdktf_cdktf_provider_aws.security_group_rule import SecurityGroupRule
from cdktf_cdktf_provider_aws.iam_role import IamRole
from cdktf_cdktf_provider_aws.iam_instance_profile import IamInstanceProfile
from cdktf_cdktf_provider_aws.ecs_cluster import EcsCluster
from cdktf_cdktf_provider_aws.ecs_task_definition import EcsTaskDefinition
from cdktf_cdktf_provider_aws.ecs_service import EcsService
from cdktf_cdktf_provider_aws.launch_configuration import LaunchConfiguration
from cdktf_cdktf_provider_aws.autoscaling_group import AutoscalingGroup
from cdktf_cdktf_provider_aws.data_aws_instance import DataAwsInstance
from cdktf_cdktf_provider_aws.data_aws_ssm_parameter import DataAwsSsmParameter

aws_region='us-east-1'
id_app="cdktf-jp"
ec2_instance_type="t2.micro"

user_data_script = '''
#!/bin/bash

echo "*** Put ECS config in place"
echo "ECS_CLUSTER={{ cluster_name }}" > /etc/ecs/ecs.config
'''
tm = Template(user_data_script)

container_definition = '''
[{
  "Name": "nginx",
  "Image": "nginx:stable-alpine",
  "Memory": 128,
  "Essential": true,
  "PortMappings": [
    {
        "ContainerPort": 80,
        "HostPort": 80
    }
  ]
}]
'''

class StackJustProvider(TerraformStack):

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        AwsProvider(self, 'Aws', region=aws_region)

        #
        # VPC
        #
        vpc = Vpc(
            self, "vpc",
            cidr_block="10.0.0.0/16",
            tags={
                'Name': id_app + '-vpc'
            }
        )
        public_subnet = Subnet(
            self, 'subnet',
            cidr_block='10.0.1.0/24',
            map_public_ip_on_launch=True,
            vpc_id=vpc.id,
            tags={
                'Name': id_app + '-subnet'
            }
        )
        igw = InternetGateway(
            self, 'igw',
            vpc_id=vpc.id, 
            tags={
                'Name': id_app + '-igw'
            }
        )
        route_table = RouteTable(
            self, "route_table",
            vpc_id=vpc.id, 
            tags={
                "Name": id_app + '-route-table'
            }
        )
        RouteTableAssociation(
            self, 'rta', 
            subnet_id=public_subnet.id, 
            route_table_id=route_table.id
        )
        Route(
            self, 'route', 
            route_table_id=route_table.id, 
            gateway_id=igw.id,
            destination_cidr_block='0.0.0.0/0'
        )

        #
        # Security Group
        #
        secgroup_ecs = SecurityGroup(
            self, "secgroup_ecs",
            description="ECS Security Group",
            name=id_app + "-secgroup-ecs",
            vpc_id=vpc.id,
            tags={
                "Name": id_app + "-secgroup-ecs"
            }
        )
        SecurityGroupRule(
            self, "secgroup_ecs_ingress",
            security_group_id=secgroup_ecs.id,
            type = "ingress",
            cidr_blocks=["0.0.0.0/0"],
            description="HTTP",
            from_port=80,
            to_port=80,
            protocol="TCP"
        )
        SecurityGroupRule(
            self, "secgroup_ecs_egress",
            security_group_id=secgroup_ecs.id,
            type = "egress",
            cidr_blocks=["0.0.0.0/0"],
            description="All",
            from_port=0,
            to_port=0,
            protocol="-1"
        )

        #
        # ECS-Cluster
        #
        ec2_role = IamRole(
            self, 'ec2_role',
            name=id_app + "-ec2role-ecscluster",
            path="/",
            assume_role_policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    }
                }]
            }),
            managed_policy_arns=["arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"]
        )
        ec2_profile = IamInstanceProfile(
            self, 'ec2_instance_profile',
            name=id_app + "-ec2_instance_profile_ecscluster",
            role=ec2_role.name
        )
        ecs_cluster = EcsCluster(
            self, 'ecs_cluster',
            name=id_app + "-cluster",
        )
        ami = DataAwsSsmParameter(
            self, "ami_id",
            name="/aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id"
        )
        lc_ecs = LaunchConfiguration(
            self, "launch_template",
            name_prefix=id_app + "-",
            image_id=ami.value,
            instance_type=ec2_instance_type,
            iam_instance_profile=ec2_profile.id,
            security_groups=[secgroup_ecs.id],
            root_block_device={
                "volume_type": "gp2",
                "volume_size": 30,
                "delete_on_termination": True
            },
            user_data=tm.render(cluster_name=id_app + "-cluster"),
            lifecycle={
               "create_before_destroy": True
            }
        )
        ecs_asg = AutoscalingGroup(
            self, "asg",
            name=id_app + "-asg",
            launch_configuration=lc_ecs.name,
            min_size=1,
            max_size=1,
            desired_capacity=1,
            vpc_zone_identifier=[
                public_subnet.id
            ],
            tag=[{
                "key": "Name",
                "value": id_app,
                "propagateAtLaunch": True
            }],
            lifecycle={
               "create_before_destroy": True,
               "ignore_changes": [
                    "min_size",
                    "max_size",
                    "desired_capacity"
                ]
            }
        )

        #
        # ECS-Service
        #
        task_def = EcsTaskDefinition(
            self, "taskdef",
            family=id_app,
            container_definitions=container_definition,
            network_mode="bridge"
        )
        EcsService(
            self, "escser",
            name=id_app,
            cluster=ecs_cluster.arn,
            task_definition=task_def.arn,
            desired_count=1,
            deployment_minimum_healthy_percent=0,
            lifecycle={
               "ignore_changes": ["desired_count"]
            }
        )

        #
        # Outputs
        #
        data_ec2 = DataAwsInstance(
            self, "data_ec2",
            filter=[{
                "name": "tag:Name",
                "values": [id_app]
            }],
            depends_on=[ecs_asg]
        )
        TerraformOutput(
            self, 'ec2_eip',
            value=Token().as_string(data_ec2.public_ip)
        )
