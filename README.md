# CDKTF-AWS

A CDK for Terraform application in Python that runs a nginx container on AWS ECS using a EC2 instance.

Some context:
- Developed in Windows 11 using WSL and Ubuntu 22.04 LTS. I use VSCode with extension Dev Containers.
- Stack `just_modules` create resources using public modules found in [registry.terraform.io](https://registry.terraform.io/).
- Stack `just_provider` create resources using the provider classes, without external modules.

## Software prerequisites

```bash
$ python3 --version
Python 3.10.12

$ pipenv --version
pipenv, version 2023.9.8

$ npm --version
9.8.1

$ aws --version
aws-cli/2.13.21 Python/3.11.5 Linux/5.15.90.1-microsoft-standard-WSL2 exe/x86_64.ubuntu.22 prompt/off

$ terraform --version
Terraform v1.5.0
on linux_amd64

$ cdktf --version
0.14.3
```

## Install prerequisites

All prerequisites are installed using Dev Containers. All the commands need to be run from inside the container, you can use the terminal provided by VSCode to do so.

## Usage

Create/update AWS credencials in `~/.aws/credentials`

Install Python dependencies

```bash
pipenv sync
```

Get Terraform modules used in the `just_modules` stack.

```bash
cdktf get
```

You can now edit the python files if you want to modify any code.

Run cdktf-cli commands (similar to plan and apply in terraform)

```bash
cdktf plan
cdktf deploy
```

After deploy the `just_modules` stack, you need to enable manually the port 80 on the security group associated with the ec2 instance and get the EIP assigned to the instance to access nginx via browser.

After deploy the `just_provider` stack, you can copy the EIP from the output to access nginx via browser.

Delete all AWS resources

```bash
cdktf destroy
```

Compile and generate Terraform configuration for debugging

```bash
cdktf synth
```

The above command will create a folder called `cdktf.out` that contains all Terraform JSON configuration that was generated.

## Update prerequisites

To update modules used in the `just_modules` stack you need to update `cdktf.json` file and run `cdktf get`

To update CDKTF and AWS provider you need to update `Pipfile`, after that, you need to delete `Pipfile.lock` and run `pipenv lock` and finally `pipenv sync`

## Links

- [CDK for Terraform](https://www.terraform.io/cdktf)
- [Build AWS infrastructure with CDK for Terraform using Python](https://developer.hashicorp.com/terraform/tutorials/cdktf/cdktf-build)
- [Official sample CDKTF + AWS + Python](https://github.com/hashicorp/terraform-cdk/tree/524d63fb09b9fb9244d588018fb6267011c41cf0/examples/python/aws)
- [Other sample CDKTF + AWS + Python](https://github.com/celeguim/cdktf-aws-python/tree/ac02109830b11512f54ee1a6d40a54598ac38ca8)
- [Using Dev Containers in WSL 2](https://code.visualstudio.com/blogs/2020/07/01/containers-wsl)
- [Create a Dev Container](https://code.visualstudio.com/docs/devcontainers/create-dev-container)
- [Fix error NVM on Dockerfile](https://stackoverflow.com/a/28390848)

## Tips

- To find the import that is needed, search the name of the Terraform resource in the imports directory
