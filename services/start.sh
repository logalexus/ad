#!/bin/bash -e

SERVICES=$(ls /services)

for SERVICE in $SERVICES; do

  if [[ -n "$1" ]] && [[ "$1" != "$SERVICE" ]] && [[ "$1" != "all" ]]; then
    continue
  fi

  COMPOSE="/services/$SERVICE/docker-compose.yml"

  echo "Starting service $SERVICE, compose file $COMPOSE"
  time sudo docker compose -f "$COMPOSE" up --build -d
  echo "Started!"
done
