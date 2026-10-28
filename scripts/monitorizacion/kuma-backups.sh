#!/usr/bin/env bash
# Push de estado de eMMC de backups. Ejecutar en host Proxmox.
set -euo pipefail
URL=$(</etc/homelab-monitor/backups-url)
URL=${URL%%\?*}
if ! mountpoint -q /mnt/backups; then
    ESTADO=down
    MENSAJE='CRITICO: disco de backups desmontado'
else
    USO=$(df -P /mnt/backups | awk 'NR==2 {gsub(/%/, "", $5); print $5}')
    [[ "$USO" =~ ^[0-9]+$ ]] || { echo 'ERROR: uso de disco invalido' >&2; exit 1; }
    if (( USO >= 90 )); then
        ESTADO=down; MENSAJE="CRITICO: backups al ${USO}%"
    elif (( USO >= 80 )); then
        ESTADO=down; MENSAJE="AVISO: backups al ${USO}%"
    else
        ESTADO=up; MENSAJE="Backups OK: ${USO}%"
    fi
fi
curl --fail --silent --show-error --max-time 15 --get \
    --data-urlencode "status=$ESTADO" --data-urlencode "msg=$MENSAJE" "$URL"
echo; echo "$MENSAJE"
