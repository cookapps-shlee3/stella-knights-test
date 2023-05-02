#!/bin/sh

## Config
PROJECT_LOCAL_PATH=`pwd -P`
REMOTE_ADDR_PEM="burgermonster-seoul.pem"
PROJECT_REMOTE_PATH="/home/ec2-user/www/unknown-knight-idle"

declare -a SERVERS=(
  "BMStageGameServer-1:ec2-15-165-32-51.ap-northeast-2.compute.amazonaws.com"
  "BMStageGameServer-2:ec2-52-78-88-18.ap-northeast-2.compute.amazonaws.com"
)


if [[ ! $PROJECT_LOCAL_PATH =~ "bm_py_unknown_knight_idle_server" ]]; then
    echo "Invalid Project Path"
    exit 0
fi

for SERVER in ${SERVERS[@]}; do
  INFO=($(echo $SERVER | tr ":" "\n"))
  NAME=${INFO[0]}
  HOST=${INFO[1]}
  echo "Deploying...${NAME} (${HOST})"
  rsync -rave "ssh -i ${HOME}/.ssh/${REMOTE_ADDR_PEM}" --exclude-from "${PROJECT_LOCAL_PATH}/rsync-exclude.list" ${PROJECT_LOCAL_PATH}/* "ec2-user@${HOST}:${PROJECT_REMOTE_PATH}"
done