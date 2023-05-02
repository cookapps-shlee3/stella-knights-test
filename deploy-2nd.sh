#!/bin/sh

## Config
PEM_PATH="${HOME}/.ssh/burgermonster-seoul.pem"
PROJECT_LOCAL_PATH=`pwd -P`
PROJECT_REMOTE_PATH="/home/ec2-user/www/unknown-knight-idle-USA"
REMOTE_ADDR='ec2-user@54.180.202.137'

###### Do Not Change ######
## ${PROJECT_LOCAL_PATH}/venv/bin/pip3 freeze > ${PROJECT_LOCAL_PATH}/requirements.txt

##if [[ ! $PROJECT_LOCAL_PATH =~ "factory" ]]; then
    ##echo "Invalid Project Path"
    ##exit 0
##fi

rsync -rave "ssh -i ${PEM_PATH}" --exclude-from "${PROJECT_LOCAL_PATH}/rsync-exclude.list" ${PROJECT_LOCAL_PATH}/* ${REMOTE_ADDR}:${PROJECT_REMOTE_PATH}
