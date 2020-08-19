
# kubeadm-CDK

This is a project uses [AWS CDK](https://github.com/aws/aws-cdk) and [kubeamin toolbox](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/) to deploy **single** master node [Kubernetes](https://kubernetes.io/) (K8s) cluster.

***note: currently, K8s v1.18.8 cluster will be provisioned by latest kubeadm*** 

## What will be deployed

### ***Physical*** resources

Once you deploy K8s cluster though this project, the following resources will be created under your AWS account:

- 1 EC2 instance works as K8s master node. The master node is not publicly accessible to the internet.
- Arbitrary number of EC2 instance(specified in `config.json`) work as K8s worker node.
- 1 additional EC2 instance works as manager node. This is the only instance could fully access(all ports and protocols) other instances.
- VPC, subnet and related security group for each EC2 instance.
- All instances share the same SSH key pair(automatically generated under `/resource/key/` while deploying) and the super user, `manager`.

### ***K8s*** resources

The following K8s resource will be created as Pods in cluster:

- etcd, API Server and kube-proxy provisioned by kubeadm
- CoreDNS
- [Flannel](https://github.com/coreos/flannel) (CNI Plugin)
- Ceph storage, Ceph filesystem and Ceph filesystem StorageClass(`default-rook-cephfs`) as default persistent storage for cluster(provisioned by [Rook](https://rook.io/docs/rook/v1.4/ceph-filesystem.html))

## Deployment

### Prerequest

- [AWS CLI v2]([] Installing the AWS CLI version 2 - https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) (Ensure default user is [configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-config) with administrator permission)
- [AWS CDK 1.57.0 or later](https://github.com/aws/aws-cdk#getting-started) (Please install it **globally** with npm)
- Python 3.8 and PIP
- [virtualenv 20.0.32 or later](https://pypi.org/project/virtualenv/)
- ssh-keygen
- OpenSSH client

### Quick Start

1. Clone this repository.

2. Switch working directory to the path(`REPOSITORY_PATH`) you clone this repository. 

   ```
   cd REPOSITORY_PATH
   ```

3. Create configuration based on configuration template.

   ```
   cp resource/config.json.sample resource/config.json
   ```

4. Replace value of the following keys in `config.json` :

   - `ACCOUNT` : Same account ID as default user you configured for AWS CLI.
   - `REGION` : The region you'd like to deploy the AWS resources in this project.

5. Create virtual environment.

   ```
   python -m venv .env
   ```

6. Activate virtual environment(depends on your OS).

   - Linux

     ```
     source .env/bin/activate
     ```

   - Windows

     ```
     .env\Scripts\activate.bat
     ```

7. Install Python dependencies.

   ```
   pip install -r requirements.txt
   ```

8. Deploy through `deploy.sh`.

   ```
   chmod +x deploy.sh
   ./deploy.sh
   ```

9. After deploy finished, you could retrieve manager node's IP address through the command below:

   ```
   aws ec2 describe-instances --filters "Name=tag:aws:cloudformation:logical-id,Values=$(cdk metadata KubernetesHandyManager --json | jq -r ".\"/KubernetesHandyManager/manager/Resource\"[0].\"data\"")" "Name=instance-state-name,Values=running" |
   jq -r ".Reservations[0].Instances[0].NetworkInterfaces[0].Association.PublicIp"
   ```

   Then you could use the private key, `resource/key/id_rsa`, and user, `manager` to access the manager instance.

   ```
   ssh -i resource/key/id_rsa manager@MANAGER_INSTANCE_PUBLIC_IP
   ```

   The `manager` instance will already have prepare kubeconfig for `kubectl` CLI tool and `helm` to perform any operation to the create K8s cluster. Enjoy it!

10. If you'd like to clean up all resources created by this project, simply run the following command in project repository:

    ```
    cdk destroy -f "*"
    ```

## Advanced usage

### Parameters in `config.json`

- `ENVIRONMENT_NAME` - AWS resources and CloudFormation(CFN) stacks created by this project will be attached with the prefix. If you'd like to modify it, command in step 9 in **Quick Start** session should be modified. For instance, the default value is `KubernetesHandy`. You would need to replace `KubernetesHandy` with prefix you define in the command to retrieve IP address correctly.
- `ACCOUNT` - AWS account to deploy resource. It should be the same account ID as default user you configured for AWS CLI. AWS CDK will use the default user to perform resource creation while deploying. So please make sure the default user have administrator IAM role to perform arbitrary operations to the AWS account.
- `REGION` - Region to deploy K8s cluster. Please refer to the [AWS region codes](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-available-regions).
- `INSTANCE_TYPE` - Each EC2 instance created by this project will be the same instance type defined there. If you prefer other instance types, please replace the value with instance type listed [there](https://aws.amazon.com/ec2/instance-types/?nc1=h_ls). Please notice that ARM architecture based instance types(C6g/M6g/R6g) and instance types with [insufficient resource](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#before-you-begin) are not recommended. Instance type with greater resource capacity than `t3.large` is recommended.
- `STORAGE_SIZE` - Disk size of each EC2 instance. [Insufficient disk space](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#before-you-begin) is not recommended. Disk size greater than 256 GB is recommended.
- `NUMBER_OF_WORKER` - Number of K8s worker node to create for the cluster.
- `IMAGE_ID` - EC2 AMI used to create each EC2 instance. In this project, instructions are tested under Ubuntu based AMI([Xenial](https://releases.ubuntu.com/16.04/), [Bionic](https://releases.ubuntu.com/18.04/) and [Focal](https://releases.ubuntu.com/20.04/)). Using other Linux distribution or older version of Ubuntu AMI is not recommended.
- `IMAGE_OWNER` - Owner of `IMAGE_ID`. If wrong `IMAGE_ID` and `IMAGE_OWNER` pair is provided, the deployment process will be broken.
-  `DEFAULT_KEY` - Default key to inject to EC2 instance. It should be the existing AWS EC2 Key pair name. Instead of using `manager` user and `id_rsa` generated by this project to login to EC2 instances. You could use `DEFAULT_KEY` and default AMI user(e.g., for Ubuntu AMI, the default user is `ubuntu`) to access them. Leave the field `null` to disable injecting `DEFAULT_KEY` to EC2 instances. Basically, this option is used for troubleshooting purpose.

### How it works

#### AWS resource management

This project is built on top of AWS ***C***loud ***D***evelopment ***T***oolkit(AWS CDK). AWS CDK is an open source software development framework to model and  provision your cloud application resources using familiar programming languages. While deploying, codes will be converted to AWS CloudFormation(CFN) templates, then deploy as CFN stacks.

When you use this project to deploy K8s Cluster, the following CFN stacks will be created under your account(if you don't modify `ENVIRONMENT_NAME` prefix):

- `KubernetesHandyVpc` - VPC and subnets to place EC2 instances.
- `KubernetesHandyAssets` - Scripts used by each EC2 instance while bootstrapping.
- `KubernetesHandySG` - Security group of each EC2 instance.
- `KubernetesHandyMaster` - Master node.
- `KubernetesHandyManager` - Manager node.
- `KubernetesHandyWorker` - Worker node.

CDK will automatically decide dependency relations between each stack, then decide order to deploy each stack.

#### K8s level bootstrapping

It relies on how kubeadm works. K8s cluster deployment follow the following order:

- Master node - Start master node.
- Worker nodes - Register worker nodes to Master node.
- Manager node - Deploy additional components(CNI Plugins, Persistent Storage).

Each node runs shell scripts defined in `resource/script` while bootstrapping. Scripts will be ran when [cloud-init](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html) finish running `module.final` to ensure instance is ready for K8s components deployment.

In addition, to enable automatically deployment, token is automatically generated and inject to master node and worker node. The following links describe how it work:

- https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-join/#token-based-discovery-without-ca-pinning
- https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-join/#config-file

You could check shell scripts and `resource/template/kubeadm-confg.yaml.j2` to gain more insights.