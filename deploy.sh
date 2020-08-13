function generate_private_key_file_if_not_exist() {
    private_key_path=$1
    if [ ! -f "$private_key_path" ]; then
        echo "private key doesn't exist, create it."
        echo 'y/n' | ssh-keygen -f "$private_key_path" -t rsa -N ''
    fi
}

function generate_token() {
    prefix=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 6 | head -n 1)
    postfix=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 16 | head -n 1)
    echo "$prefix"."$postfix"
}

function generate_token_file_if_not_exist() {
    token_path=$1
    if [ ! -f "$token_path" ]; then
        echo "token doesn't exist, create it."
        token=$(generate_token)
        echo -n "$token" > "$token_path"
    fi
}

#function enable_ssh_key_retransmission() {
#    private_key_path=$1
#    eval "$(ssh-agent)"
#    chmod 600 "$private_key_path"
#    ssh-add "$private_key_path"
#}

#function fetch_manager_public_ip_address() {
#    manager_logical_id=$(cdk metadata KubernetesHandyManager --json | jq -r ".\"/KubernetesHandyManager/manager/Resource\"[0].\"data\"")
#    manager_public_ip_address=$(aws ec2 describe-instances --filters "Name=tag:aws:cloudformation:logical-id,Values=$manager_logical_id" "Name=instance-state-name,Values=running" |
#jq -r ".Reservations[0].Instances[0].NetworkInterfaces[0].Association.PublicIp")
#    echo "$manager_public_ip_address"
#}
#
#function fetch_master_private_ip_address() {
#    master_logical_id=$(cdk metadata KubernetesHandyMaster --json | jq -r ".\"/KubernetesHandyMaster/master/Resource\"[0].\"data\"")
#    master_private_ip_address=$(aws ec2 describe-instances --filters "Name=tag:aws:cloudformation:logical-id,Values=$master_logical_id" "Name=instance-state-name,Values=running" |
#jq -r ".Reservations[0].Instances[0].NetworkInterfaces[0].PrivateIpAddress")
#    echo "$master_private_ip_address"
#}

#function register_hosts() {
#    manager_public_ip_address=$1
#    master_private_ip_address=$2
#
#    echo "register manger host on local machine"
#    ssh-keyscan "$manager_public_ip_address" >> ~/.ssh/known_hosts
#
#    echo "register master host on masnager host"
#    ssh -A manager@"$manager_public_ip_address" "ssh-keyscan $master_private_ip_address >> ~/.ssh/known_hosts"
#}



KEY_DIR=resource/key
PRIVATE_KEY_PATH=$KEY_DIR/id_rsa
TOKEN_PATH=$KEY_DIR/token.txt

mkdir -p $KEY_DIR
echo "check private key existence."
generate_private_key_file_if_not_exist $PRIVATE_KEY_PATH
echo "check private key existence."
generate_token_file_if_not_exist $TOKEN_PATH
#echo "enable ssh key retransmission"
#enable_ssh_key_retransmission $PRIVATE_KEY_PATH

cdk synth
cdk deploy '*' --require-approval never

#echo "fetch manager public ip address"
#manager_public_ip_address=$(fetch_manager_public_ip_address)
#echo "fetch master private ip address"
#master_private_ip_address=$(fetch_master_private_ip_address)
#
#echo "register hosts"
#register_hosts "$manager_public_ip_address" "$master_private_ip_address"
