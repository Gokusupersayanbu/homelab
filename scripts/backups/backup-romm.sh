#!/usr/bin/env bash
# Copia selectiva RomM. Copia privada que puede CONTENER SECRETOS en /opt/romm.
set -euo pipefail
umask 077
DEST='/mnt/backups/romm-data'
FECHA=$(date +%Y%m%d-%H%M%S)
FINAL="$DEST/romm-$FECHA"
mountpoint -q /mnt/backups || { echo 'ERROR: eMMC no montada' >&2; exit 1; }
[[ "$(pct status 102)" == 'status: running' ]] || { echo 'ERROR: CT102 no está funcionando' >&2; exit 1; }
install -d -m 700 "$DEST"
TMP=$(mktemp -d "$DEST/.incompleto-XXXXXXXX")
trap 'rm -rf -- "$TMP"' EXIT
printf '===== EXPORTANDO MARIADB =====\n'
pct exec 102 -- docker exec romm-db sh -c '
    set -eu
    : "${MARIADB_USER:?}"
    : "${MARIADB_PASSWORD:?}"
    : "${MARIADB_DATABASE:?}"
    export MYSQL_PWD="$MARIADB_PASSWORD"
    exec mariadb-dump --user="$MARIADB_USER" --single-transaction --quick \
        --routines --events --triggers --databases "$MARIADB_DATABASE"
' | gzip -1 > "$TMP/mariadb.sql.gz"
printf '===== COPIANDO DATOS IMPORTANTES =====\n'
pct exec 102 -- tar -cf - \
    -C /mnt/romm-library/.romm-data assets resources \
    -C /opt romm | gzip -1 > "$TMP/archivos.tar.gz"
printf '===== VERIFICANDO INTEGRIDAD =====\n'
test -s "$TMP/mariadb.sql.gz"
test -s "$TMP/archivos.tar.gz"
gzip -t "$TMP/mariadb.sql.gz"
gzip -t "$TMP/archivos.tar.gz"
tar -tzf "$TMP/archivos.tar.gz" >/dev/null
(cd "$TMP" && sha256sum mariadb.sql.gz archivos.tar.gz > SHA256SUMS)
mv "$TMP" "$FINAL"
trap - EXIT
printf '===== BACKUP COMPLETADO =====\n'
du -sh "$FINAL"
echo "Ubicación: $FINAL"
