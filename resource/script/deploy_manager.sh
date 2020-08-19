#!/bin/bash

function install_kubectl() {
    # install kubectl
    curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"
    chmod +x ./kubectl
    sudo mv ./kubectl /usr/local/bin/kubectl
}

function copy_kubectl_config() {
    private_key_file=$1
    master_ip_address=$2
    remote_kubeconfig_file_path=$3
    local_kubeconfig_dir_path=$4
    local_kubeconfig_file_path=$5

    echo "create local kubeconfig directory"
    mkdir -p "$local_kubeconfig_dir_path"
    chmod 600 "$PRIVATE_KEY_FILE"

    ssh -i "$private_key_file" manager@"$master_ip_address" "test $remote_kubeconfig_file_path"

    while [ $? != 0 ] ; do
        echo "config file haven't been generated yet, wait 5 second for next verification"
        sleep 5
        ssh -i "$private_key_file" manager@"$master_ip_address" "test $remote_kubeconfig_file_path"
    done

    echo "copy kubeconfig from master node"
    scp -i "$private_key_file" -o "ForwardAgent yes" manager@"$master_ip_address":"$remote_kubeconfig_file_path" "$local_kubeconfig_file_path"
    chown manager "$local_kubeconfig_file_path"
}

function wait_for_worker_node_join() {
    local_kubeconfig_file_path=$1
    number_of_worker_node=$2

    echo "wait for worker node join"

    join_finish=$(( $number_of_worker_node + 2 ))
    join_status=$(kubectl get nodes --kubeconfig "$local_kubeconfig_file_path" | wc -l)
    
    while [ $join_finish -ne $join_status ]; do
        echo "worker node haven't joined yet, wait 5 second for next verification"
        sleep 5
        join_status=$(kubectl get nodes --kubeconfig "$local_kubeconfig_file_path" | wc -l)
    done
}

function deploy_flannel() {
    local_kubeconfig_file_path=$1

    echo "deploy flannel"
    kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml --kubeconfig "$local_kubeconfig_file_path"

    deploy_finish=""
    deploy_status=$(kubectl get pods -n kube-system -l app=flannel --field-selector status.phase!=Running --kubeconfig "$local_kubeconfig_file_path")

    while [ "$deploy_status" != "$deploy_finish" ]; do
        echo "flannel haven't ready, wait 5 second for next verification"
        sleep 5
        deploy_status=$(kubectl get pods -n kube-system -l app=flannel --field-selector status.phase!=Running --kubeconfig "$local_kubeconfig_file_path")
    done
}

function restart_coredns() {
    local_kubeconfig_file_path=$1

    kubectl delete pod -l k8s-app=kube-dns -n kube-system --kubeconfig "$local_kubeconfig_file_path"
}

function deploy_rook_ceph() {
    local_kubeconfig_file_path=$1
    rook_pod_security_policy=$2

    rook_clone_path=/tmp/rook
    ceph_manifest_path=$rook_clone_path/cluster/examples/kubernetes/ceph

    echo "deploy rook-ceph"
    kubectl apply -f "$rook_pod_security_policy" --kubeconfig "$local_kubeconfig_file_path"

    git clone --single-branch --branch release-1.4 https://github.com/rook/rook.git $rook_clone_path

    kubectl create -f $ceph_manifest_path/common.yaml --kubeconfig "$local_kubeconfig_file_path"
    kubectl create -f $ceph_manifest_path/operator.yaml --kubeconfig "$local_kubeconfig_file_path"

    deploy_finish=""
    deploy_status=$(kubectl get pods -n rook-ceph --field-selector status.phase!=Running --kubeconfig "$local_kubeconfig_file_path")

    while [ "$deploy_status" != "$deploy_finish" ]; do
        echo "rook basic components haven't ready, wait 5 second for next verification"
        sleep 5
        deploy_status=$(kubectl get pods -n rook-ceph --field-selector status.phase!=Running --kubeconfig "$local_kubeconfig_file_path")
    done

    echo "deploy ceph cluster"

    kubectl create -f $ceph_manifest_path/cluster.yaml --kubeconfig "$local_kubeconfig_file_path"

    deploy_finish=""
    deploy_status=$(kubectl get pods -n rook-ceph --field-selector status.phase!=Running,status.phase!=Succeeded --kubeconfig "$local_kubeconfig_file_path")

    while [ "$deploy_status" != "$deploy_finish" ]; do
        echo "rook cluster haven't ready, wait 5 second for next verification"
        sleep 5
        deploy_status=$(kubectl get pods -n rook-ceph --field-selector status.phase!=Running,status.phase!=Succeeded --kubeconfig "$local_kubeconfig_file_path")
    done
}

function create_default_file_system() {
    local_kubeconfig_file_path=$1
    file_system_definition=$2
    storage_class_definition=$3

    echo "deploy rook ceph file system"

    kubectl create -f "$file_system_definition" --kubeconfig "$local_kubeconfig_file_path"

    deploy_finish=""
    deploy_status=$(kubectl get pods -l app=rook-ceph-mds -n rook-ceph --field-selector status.phase!=Running,status.phase!=Succeeded --kubeconfig "$local_kubeconfig_file_path")

    while [ "$deploy_status" != "$deploy_finish" ]; do
        echo "rook ceph file system haven't ready, wait 5 second for next verification"
        sleep 5
        deploy_status=$(kubectl get pods -l app=rook-ceph-mds -n rook-ceph --field-selector status.phase!=Running,status.phase!=Succeeded --kubeconfig "$local_kubeconfig_file_path")
    done

    echo "deploy storage class"

    kubectl create -f "$storage_class_definition" --kubeconfig "$local_kubeconfig_file_path"
}

function install_helm() {
    echo "install helm"

    curl https://baltocdn.com/helm/signing.asc | sudo apt-key add -
    sudo apt-get install apt-transport-https --yes
    echo "deb https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
    sudo apt-get update
    sudo apt-get install helm
}

PUBLIC_KEY_FILE=$1
CREATE_USER_SCRIPT=$2
CHECK_MASTER_READY_SCRIPT=$3
MASTER_IP_ADDRESS=$4
PRIVATE_KEY_FILE=$5

ROOK_POD_SECURITY_POLICY_FILE=$6
FILE_SYSTEM_DEFINITION=$7
STORAGE_CLASS_DEFINITION=$8

NUMBER_OF_WORKER_NODES=$9

REMOTE_KUBECONFIG_FILE_PATH=/home/manager/config
LOCAL_KUBECONFIG_DIR_PATH=/home/manager/.kube
LOCAL_KUBECONFIG_FILE_PATH=$LOCAL_KUBECONFIG_DIR_PATH/config

echo "wait until cloud-init finished"
cloud-init status --wait
echo "cloud-init finished, start deploy k8s components"

bash "$CREATE_USER_SCRIPT" "$PUBLIC_KEY_FILE"

bash "$CHECK_MASTER_READY_SCRIPT" "$MASTER_IP_ADDRESS"
wait_status=$?

if [ $wait_status -eq 0 ]; then
    install_kubectl
    ssh-keyscan "$MASTER_IP_ADDRESS" >>  ~/.ssh/known_hosts

    copy_kubectl_config "$PRIVATE_KEY_FILE" "$MASTER_IP_ADDRESS" $REMOTE_KUBECONFIG_FILE_PATH $LOCAL_KUBECONFIG_DIR_PATH $LOCAL_KUBECONFIG_FILE_PATH

    wait_for_worker_node_join "$LOCAL_KUBECONFIG_FILE_PATH" "$NUMBER_OF_WORKER_NODES"

    deploy_flannel "$LOCAL_KUBECONFIG_FILE_PATH"
    deploy_rook_ceph "$LOCAL_KUBECONFIG_FILE_PATH" "$ROOK_POD_SECURITY_POLICY_FILE"
    create_default_file_system "$LOCAL_KUBECONFIG_FILE_PATH" "$FILE_SYSTEM_DEFINITION" "$STORAGE_CLASS_DEFINITION"
    install_helm
else
    echo "wait for master node ready timeout."
fi

rm "$PRIVATE_KEY_FILE"
