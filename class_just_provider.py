import json
from cdktf import Token, TerraformOutput, TerraformStack
from constructs import Construct
from imports.aws import AwsProvider
from imports.aws.vpc import Vpc, RouteTable, Subnet, InternetGateway, RouteTableAssociation, Route, SecurityGroup, SecurityGroupRule
from imports.aws.iam import IamRole, IamInstanceProfile
from imports.aws.ecs import EcsCluster
from imports.aws.datasources import LaunchConfiguration
from imports.aws.autoscaling import AutoscalingGroup

aws_region='us-east-1'
id_app="jp"

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
        # ECSCluster
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
        EcsCluster(
            self, 'ecs_cluster',
            name=id_app + "-cluster",
        )

        f = open("bootstrap.sh", "r")
        lc_ecs = LaunchConfiguration(
            self, "launch_template",
            name_prefix=id_app + "-",
            image_id="ami-03f8a7b55051ae0d4",
            instance_type="t3a.micro",
            iam_instance_profile=ec2_profile.id,
            security_groups=[secgroup_ecs.id],
            root_block_device={
                "volume_type": "gp2",
                "volume_size": 30,
                "delete_on_termination": True
            },
            user_data=f.read(),
            #lifecycle={
            #    "create_before_destroy": True
            #}
        )
        f.close()

        AutoscalingGroup(
            self, "asg",
            name=id_app + "-asg",
            launch_configuration=lc_ecs.name,
            min_size=1,
            max_size=1,
            desired_capacity=1,
            vpc_zone_identifier=[
                public_subnet.id
            ]
            #lifecycle={
            #    "create_before_destroy": True
            #    "ignore_changes"=["min_size", "max_size", "desired_capacity"]
            #}
        )
