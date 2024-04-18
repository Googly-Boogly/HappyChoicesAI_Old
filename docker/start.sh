#!/bin/bash

# Check if running as a web server or a Celery worker
if [ "$SERVICE_TYPE" = "celery_worker" ]; then
    # Start Celery worker
    if [ -z "$AGENT_GROUPS" ]; then
        echo "No AGENT_GROUPS specified."
        exit 1
    fi
    # Customize the app name and worker name as needed
    exec celery -A base_agent worker --loglevel=info -Q $AGENT_GROUPS --hostname $HOSTNAME
else
    # Start Daphne server
    exec daphne -b 0.0.0.0 -p 8000 ai_backend.asgi:application
fi
