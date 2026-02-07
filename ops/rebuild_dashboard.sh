#!/bin/bash
set -e

cd /opt/NOC-Guardian-Project

git fetch origin
git reset --hard origin/master

docker compose build dashboard
docker compose up -d dashboard

echo "Dashboard atualizado!"
