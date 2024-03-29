#!/bin/bash

# get user and password from .env file
export $(cat .env | grep NEO4J_USER)
export $(cat .env | grep NEO4J_PWD)

docker run -it --rm \
    -p 7474:7474 \
    -p 7687:7687 \
    -d \
    -e NEO4J_AUTH=$NEO4J_USER/$NEO4J_PWD \
    --env NEO4J_PLUGINS='["graph-data-science"]' \
   neo4j:latest