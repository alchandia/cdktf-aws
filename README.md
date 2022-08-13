# CDKTF-AWS

A CDK for Terraform application in Python that runs a nginx container on AWS ECS.

Some context:
- Developed in Ubuntu 20.04 LTS
- Depend only of public modules found in [registry.terraform.io](https://registry.terraform.io/)

## Software prerequisites

```bash
$ python --version
Python 3.8.10

$ pipenv --version
pipenv, version 2022.8.5

$ npm --version
6.14.17

$ aws --version
aws-cli/2.7.13 Python/3.9.11 Linux/5.15.0-43-generic exe/x86_64.ubuntu.20 prompt/off

$ terraform --version
Terraform v1.2.3
on linux_amd64

$ cdktf --version
0.12.0
```

## Install prerequisites

Install Pipenv by running:

```bash
sudo apt install python3-pip
sudo pip install pipenv
```

[Installing Node.js and npm from NodeSource](https://linuxize.com/post/how-to-install-node-js-on-ubuntu-20-04/)

```bash
curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt update && \
    sudo apt install nodejs
```

[Install cdktf-cli](https://learn.hashicorp.com/tutorials/terraform/cdktf-install?in=terraform/cdktf)

```bash
sudo npm install --global cdktf-cli@0.12.0
```

## Usage

Create/Update AWS credencials in `~/.aws/credentials`

Generate CDK for Terraform constructs for Terraform providers and modules used in the project.

```bash
# this command take several minutes to finish
cdktf get
```

You can now edit the `main.py` file if you want to modify any code.

Run cdktf-cli commands (similar to plan and apply in terraform)

```bash
cdktf diff
cdktf deploy
# After deployment, you need to enable manually the port 80 on the security group associated with the ec2 instance
```

Delete all AWS resources

```bash
cdktf destroy
```

Compile and generate Terraform configuration for debugging

```bash
cdktf synth
```

The above command will create a folder called `cdktf.out` that contains all Terraform JSON configuration that was generated.

## Links

- https://www.terraform.io/cdktf
- https://github.com/hashicorp/terraform-cdk/tree/43ed33370510c31cd62b5f0b07a812197e89d252/examples/python
- https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws
- https://registry.terraform.io/modules/infrablocks/ecs-cluster/aws
- https://registry.terraform.io/modules/lazzurs/ecs-service/aws
- https://github.com/celeguim/cdktf-aws-python/tree/ac02109830b11512f54ee1a6d40a54598ac38ca8
