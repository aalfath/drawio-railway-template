#!/bin/bash
# Start wrapper for draw.io on Railway. It sets a few defaults, then hands over to the
# image's own /docker-entrypoint.sh (which writes PreConfig.js from the DRAWIO_* variables),
# and that runs railway-configure.py before Tomcat starts.
set -e

# Tomcat's HTTP port: Railway's PORT (the public domain targets it).
export PORT="${PORT:-8080}"

# Public URL for embed, viewer and lightbox links: the service's Railway domain unless set.
if [ -z "${DRAWIO_BASE_URL}" ] && [ -z "${DRAWIO_SERVER_URL}" ] && [ -n "${RAILWAY_PUBLIC_DOMAIN}" ]; then
  export DRAWIO_BASE_URL="https://${RAILWAY_PUBLIC_DOMAIN}"
fi

# The image creates a self-signed keystore with a published default password when none is
# given. Railway terminates TLS itself, so use a random one per start (the 8443 connector is
# removed again by railway-configure.py).
if [ -z "${KEYSTORE_PASS}" ]; then
  KEYSTORE_PASS="$(head -c 24 /dev/urandom | od -An -tx1 | tr -d ' \n')"
  export KEYSTORE_PASS
fi

# draw.io's server side is small (static files, a URL proxy, OAuth helpers): keep the heap small.
export CATALINA_OPTS="${CATALINA_OPTS:--Xms64m -Xmx512m -XX:+UseSerialGC}"

exec /docker-entrypoint.sh /usr/local/bin/railway-configure.py "$@"
