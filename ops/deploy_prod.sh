#!/bin/bash
set -e

echo "=============================="
echo "NOC Guardian Production Deploy"
echo "=============================="

cd /opt/NOC-Guardian-Project

echo "Atualizando código do GitHub..."
git fetch origin
git reset --hard origin/master

echo "Removendo imagens antigas..."
docker image prune -f

echo "Rebuildando serviços..."
docker compose down
docker compose up -d --build

echo "Deploy concluído com sucesso!"
