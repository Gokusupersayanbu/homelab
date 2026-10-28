#!/usr/bin/env bash
# Retencion de tres copias. Revisar antes de despliegue; elimina carpetas antiguas.
set -euo pipefail
DIR=/mnt/backups/romm-data
mountpoint -q /mnt/backups || exit 1
mapfile -t COPIAS < <(
  find "$DIR" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended \
    -regex '.*/romm-[0-9]{8}-[0-9]{6}' | sort
)
TOTAL=${#COPIAS[@]}
if (( TOTAL <= 3 )); then
  echo "Retencion OK: $TOTAL copias, ninguna eliminada"
  exit 0
fi
for ((i=TOTAL-3; i<TOTAL; i++)); do
  for archivo in mariadb.sql.gz archivos.tar.gz SHA256SUMS; do
    test -s "${COPIAS[$i]}/$archivo" || {
      echo 'ERROR: copia incompleta; no se elimina nada' >&2
      exit 1
    }
  done
done
for ((i=0; i<TOTAL-3; i++)); do
  echo "Eliminando copia antigua: ${COPIAS[$i]}"
  rm -r -- "${COPIAS[$i]}"
done
echo 'Retencion completada'
