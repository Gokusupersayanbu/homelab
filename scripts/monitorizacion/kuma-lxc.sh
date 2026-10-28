#!/usr/bin/env bash
# Verifica CT100, CT101 y CT102 por pct status.
set -euo pipefail
URL=$(</etc/homelab-monitor/lxc-url)
URL=${URL%%\?*}
ESTADO=up
MENSAJE=''
for ID in 100 101 102; do
  if RESPUESTA=$(pct status "$ID" 2>&1) && [[ "$RESPUESTA" == 'status: running' ]]; then
    MENSAJE+="CT${ID}=OK "
  else
    ESTADO=down
    MENSAJE+="CT${ID}=DETENIDO "
  fi
done
echo "Estado: $ESTADO"; echo "$MENSAJE"
curl --fail --silent --show-error --max-time 15 --get \
  --data-urlencode "status=$ESTADO" --data-urlencode "msg=$MENSAJE" "$URL"
echo
