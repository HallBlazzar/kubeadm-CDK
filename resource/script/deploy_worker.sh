#!/bin/bash

PUBLIC_KEY_FILE=$1
CREATE_USER_SCRIPT=$2
DEPLOY_KUBEADM_SCRIPT=$3

bash "$CREATE_USER_SCRIPT" "$PUBLIC_KEY_FILE"

bash "$DEPLOY_KUBEADM_SCRIPT"