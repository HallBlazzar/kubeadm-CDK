#!/bin/bash

PUBLIC_KEY_FILE=$1
CREATE_USER_SCRIPT=$2
DEPLOY_KUBEADM_SCRIPT=$3
KUBEADM_CONFIG_FILE=$4

echo "wait until cloud-init finished"
cloud-init status --wait
echo "cloud-init finished, start deploy master node components"

bash "$CREATE_USER_SCRIPT" "$PUBLIC_KEY_FILE"

apt-get update
sudo apt-get install -y lvm2

bash "$DEPLOY_KUBEADM_SCRIPT"

kubeadm init --config "$KUBEADM_CONFIG_FILE" --upload-certs

cp /etc/kubernetes/admin.conf /home/manager/config
chown manager /home/manager/config
