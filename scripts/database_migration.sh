#!/bin/bash

if [ ! -f set_environment_variables.sh ]; then
    echo "set_environment_variables.sh was not found!"
fi

source set_environment_variables.sh
DATE=`date +%Y-%m-%d`
mysqldump -P ${STORAGE_PORT} -h ${HOST} --protocol TCP -u ${MYSQL_USERNAME} \
    -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} > ../storage/migrations/${DATE}.sql
