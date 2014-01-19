#!/bin/sh
#
# Serve TinyCM via Busybox HTTPd
#

port=8084
cd tools 2/dev/null || continue

echo "Starting server on port: $port"
echo "URL: http://localhost:$port/"
httpd -f -u www:www -p $port -c httpd.conf

exit 0
