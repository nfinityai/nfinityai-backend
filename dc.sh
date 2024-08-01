#!/bin/bash
git pull
docker compose -f docker-compose.yml "$@"