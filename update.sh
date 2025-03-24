#!/bin/bash
git add .
git remote update
git reset --hard origin/main

docker-compose down
docker-compose up -d
