#!/usr/bin/env bash
# Hook invocado por vzdump en la tarea CT100.
[[ "${1:-}" == "backup-end" ]] || exit 0
[[ "${3:-}" == "100" ]] || exit 0
[[ "${STOREID:-}" == "backups-emmc" ]] || exit 0

FILE="${TARGET:-}"
if [[ "$FILE" != /mnt/backups/dump/vzdump-lxc-100-*.tar.zst || ! -s "$FILE" ]]; then
  echo "AVISO: archivo de backup no encontrado" >&2
  exit 0
fi

UNIT="backup-mega-ct100-$(date +%s)"
if /usr/bin/systemd-run --collect --unit="$UNIT" \
  /usr/local/sbin/backup-mega.sh "$FILE"; then
  echo "Subida a MEGA programada: $UNIT"
else
  echo "AVISO: no se pudo iniciar la subida a MEGA" >&2
fi
exit 0
