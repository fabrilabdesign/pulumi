#!/bin/bash

# Required environment variables:
# APP_NAME - Name of the application
# ENVIRONMENT - dev or prod
# CONTAINER_NAME - Docker container name
# CONTAINER_PORT - Container port
# DOMAIN - Optional custom domain

set -e

# Configuration directories
NGINX_CONFIG_DIR="/etc/nginx/conf.d/apps"
TEMPLATE_DIR="/etc/nginx/templates"

# Create environment-specific directory if it doesn't exist
mkdir -p "${NGINX_CONFIG_DIR}/${ENVIRONMENT}"

# If custom domain is provided, use it, otherwise use default subdomain
if [ -n "$DOMAIN" ]; then
    export SERVER_NAME="$DOMAIN"
else
    export SERVER_NAME="${APP_NAME}.${ENVIRONMENT}.addidaire.com"
fi

# Generate configuration from template
envsubst '${APP_NAME} ${ENVIRONMENT} ${CONTAINER_NAME} ${CONTAINER_PORT} ${SERVER_NAME}' \
    < "${TEMPLATE_DIR}/app.conf.template" \
    > "${NGINX_CONFIG_DIR}/${ENVIRONMENT}/${APP_NAME}.conf"

# Test Nginx configuration
nginx -t

# Reload Nginx if test passes
nginx -s reload

echo "Nginx configuration updated and reloaded successfully" 