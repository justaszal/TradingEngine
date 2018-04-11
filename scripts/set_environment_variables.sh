#!/bin/bash

if [ ! -f ../.env ]; then
    echo ".env was not found!"
fi

while read line; do
    echo $line
    export $line >/dev/null
done < ../.env
