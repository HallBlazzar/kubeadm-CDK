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

KEY_DIR=resource/key
PRIVATE_KEY_PATH=$KEY_DIR/id_rsa
TOKEN_PATH=$KEY_DIR/token.txt

mkdir -p $KEY_DIR
echo "check private key existence."
generate_private_key_file_if_not_exist $PRIVATE_KEY_PATH
echo "check private key existence."
generate_token_file_if_not_exist $TOKEN_PATH

cdk synth
cdk deploy '*' --require-approval never

