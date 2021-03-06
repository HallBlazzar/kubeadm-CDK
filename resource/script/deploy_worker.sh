#!/bin/bash

PUBLIC_KEY_FILE=$1
CREATE_USER_SCRIPT=$2
DEPLOY_KUBEADM_SCRIPT=$3
TOKEN=$4
MASTER_IP_ADDRESS=$5
CHECK_MASTER_READY_SCRIPT=$6

echo "wait until cloud-init finished"
cloud-init status --wait
echo "cloud-init finished, start deploy worker node components"

bash "$CREATE_USER_SCRIPT" "$PUBLIC_KEY_FILE"

apt-get update
sudo apt-get install -y lvm2

bash "$DEPLOY_KUBEADM_SCRIPT"

bash "$CHECK_MASTER_READY_SCRIPT" "$MASTER_IP_ADDRESS"
wait_status=$?

if [ $wait_status -eq 0 ]; then
    kubeadm join "$MASTER_IP_ADDRESS":6443 --token "$TOKEN" --discovery-token-unsafe-skip-ca-verification
else
    echo "wait for master node ready timeout."
fi
