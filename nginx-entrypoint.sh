#!/bin/sh

# Set default values if environment variables are not set
export NGINX_PORT=${NGINX_PORT:-8811}

# Process the nginx configuration template
envsubst '${NGINX_PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Test nginx configuration
nginx -t

# Start nginx
exec nginx -g "daemon off;"
