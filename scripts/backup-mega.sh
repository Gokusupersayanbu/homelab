#!/usr/bin/env bash
# Ejemplo fiel a la lógica desplegada. Ejecutar solo después de comprobar entorno.
set -Eeuo pipefail
umask 077

FILE="${1:?Falta indicar el archivo de backup}"
CONFIG="/root/.config/rclone/rclone.conf"
REMOTE="mega-crypt:CT100"

case "$FILE" in
  /mnt/backups/dump/vzdump-lxc-100-*.tar.zst) ;;
  *) echo "ERROR: archivo no permitido" >&2; exit 1 ;;
esac

mountpoint -q /mnt/backups || { echo "ERROR: memoria eMMC no montada" >&2; exit 1; }
test -s "$FILE"
test -r "$CONFIG"

NAME="$(basename "$FILE")"
LOCAL_SIZE="$(stat -c %s "$FILE")"
echo "Subiendo backup cifrado: $NAME"

rclone --config "$CONFIG" copyto "$FILE" "$REMOTE/$NAME" --retries 3

REMOTE_SIZE="$(rclone --config "$CONFIG" ls "$REMOTE/$NAME" | awk 'NR==1 {print $1}')"
if [[ "$LOCAL_SIZE" != "$REMOTE_SIZE" ]]; then
  echo "ERROR: tamaño remoto incorrecto" >&2
  exit 1
fi

echo "Subida comprobada correctamente"
LISTING="$(rclone --config "$CONFIG" lsf "$REMOTE" --files-only)"
mapfile -t BACKUPS < <(
  printf '%s\n' "$LISTING" |
    grep -E '^vzdump-lxc-100-[0-9]{4}_[0-9]{2}_[0-9]{2}-[0-9]{2}_[0-9]{2}_[0-9]{2}\.tar\.zst$' |
    LC_ALL=C sort -r
)

if ! printf '%s\n' "${BACKUPS[@]}" | grep -Fxq "$NAME"; then
  echo "ERROR: backup nuevo no encontrado en el listado" >&2
  exit 1
fi

# Sólo después de subir y validar el tamaño se borran archivos anteriores.
# ADVERTENCIA: MEGA puede moverlos a la papelera en vez de liberar espacio.
for ((i=3; i<${#BACKUPS[@]}; i++)); do
  echo "Eliminando copia antigua: ${BACKUPS[i]}"
  rclone --config "$CONFIG" deletefile "$REMOTE/${BACKUPS[i]}"
done

echo "BACKUP MEGA COMPLETADO"

if /usr/local/sbin/actualizar-homepage-mega.py; then
  echo "HOMEPAGE: Estadisticas actualizadas correctamente"
else
  echo "AVISO: No se pudieron actualizar las estadisticas de Homepage" >&2
fi

KUMA_CONFIG="/root/.config/backup-mega-kuma.curl"
if RESPONSE=$(curl --config "$KUMA_CONFIG" --fail --silent --show-error --max-time 15); then
  if [[ "$RESPONSE" == *'"ok":true'* ]]; then
    echo "UPTIME KUMA: Backup confirmado correctamente"
  else
    echo "ERROR: Uptime Kuma no ha confirmado la notificacion" >&2
    exit 1
  fi
else
  echo "ERROR: No se ha podido notificar a Uptime Kuma" >&2
  exit 1
fi
