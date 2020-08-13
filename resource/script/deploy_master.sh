#!/bin/bash

PUBLIC_KEY_FILE=$1
CREATE_USER_SCRIPT=$2
DEPLOY_KUBEADM_SCRIPT=$3
KUBEADM_CONFIG_FILE=$4

bash "$CREATE_USER_SCRIPT" "$PUBLIC_KEY_FILE"

bash "$DEPLOY_KUBEADM_SCRIPT"

kubeadm init --config "$KUBEADM_CONFIG_FILE" --upload-certs

cp /etc/kubernetes/admin.conf /home/manager/config
chown manager /home/manager/config
