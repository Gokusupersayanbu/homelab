#!/usr/bin/env bash
# Vigila edad de respaldo RomM, montaje y timer systemd.
set -euo pipefail
URL=$(</etc/homelab-monitor/romm-backup-url)
URL=${URL%%\?*}
DIR='/mnt/backups/romm-data'
ESTADO=up
MENSAJE='Backup RomM correcto'
if ! mountpoint -q /mnt/backups; then
    ESTADO=down; MENSAJE='CRITICO: eMMC de backups desmontada'
elif ! systemctl is-active --quiet backup-romm.timer; then
    ESTADO=down; MENSAJE='CRITICO: temporizador RomM detenido'
elif systemctl is-failed --quiet backup-romm.service; then
    ESTADO=down; MENSAJE='ERROR: ultimo backup RomM fallido'
else
    ULTIMO=$(find "$DIR" -mindepth 1 -maxdepth 1 -type d -name 'romm-*' | sort | tail -n 1)
    if [[ -z "$ULTIMO" ]]; then
        ESTADO=down; MENSAJE='ERROR: no existen backups RomM'
    else
        AHORA=$(date +%s)
        FECHA=$(stat -c %Y "$ULTIMO")
        HORAS=$(( (AHORA - FECHA) / 3600 ))
        if (( HORAS > 30 )); then
            ESTADO=down; MENSAJE="ERROR: ultimo backup hace ${HORAS}h"
        else
            for F in mariadb.sql.gz archivos.tar.gz SHA256SUMS; do
                if [[ ! -s "$ULTIMO/$F" ]]; then
                    ESTADO=down; MENSAJE="ERROR: archivo faltante $F"
                    break
                fi
            done
            if [[ "$ESTADO" == up ]]; then MENSAJE="RomM OK: ultimo backup hace ${HORAS}h"; fi
        fi
    fi
fi
curl --fail --silent --show-error --max-time 15 --get \
    --data-urlencode "status=$ESTADO" --data-urlencode "msg=$MENSAJE" "$URL"
echo; echo "Estado: $ESTADO"; echo "$MENSAJE"
