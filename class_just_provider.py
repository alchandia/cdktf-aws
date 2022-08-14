from cdktf import Token, TerraformOutput, TerraformStack
from constructs import Construct
from imports.aws import AwsProvider
from imports.aws.vpc import Vpc, RouteTable, Subnet, InternetGateway, RouteTableAssociation, Route, SecurityGroup, \
    SecurityGroupIngress, NatGateway, SecurityGroupEgress, NetworkAcl, NetworkAclIngress, NetworkAclEgress

aws_region='us-east-1'
id_app="jp"

class StackJustProvider(TerraformStack):

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        AwsProvider(self, 'Aws', region=aws_region)

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