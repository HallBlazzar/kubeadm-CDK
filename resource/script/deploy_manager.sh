#!/bin/bash

function install_kubectl() {
    # install kubectl
    curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"
    chmod +x ./kubectl
    sudo mv ./kubectl /usr/local/bin/kubectl
}

PUBLIC_KEY_FILE=$1
CREATE_USER_SCRIPT=$2
CHECK_MASTER_READY_SCRIPT=$3
MASTER_IP_ADDRESS=$4
PRIVATE_KEY_FILE=$5

bash "$CREATE_USER_SCRIPT" "$PUBLIC_KEY_FILE"

bash "$CHECK_MASTER_READY_SCRIPT" "$MASTER_IP_ADDRESS"
wait_status=$?

if [ $wait_status -eq 0 ]; then
    install_kubectl
    ssh-keyscan "$MASTER_IP_ADDRESS" >>  ~/.ssh/known_hosts
    mkdir -p /home/manager/.kube
    chmod 600 "$PRIVATE_KEY_FILE"
    scp -i "$PRIVATE_KEY_FILE" -o "ForwardAgent yes" manager@"$MASTER_IP_ADDRESS":/home/manager/config /home/manager/.kube/config
    chown manager /home/manager/.kube/config
else
    echo "wait for master node ready timeout."
fi

# todo: remove private key
