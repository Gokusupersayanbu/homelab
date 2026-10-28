# 16. Backups selectivos de RomM — CT102

## Objetivo

Proteger la base de datos, configuración, partidas, portadas y recursos de RomM **sin copiar la biblioteca de juegos completa**.

## Almacenamiento

| Ubicación | Uso | ¿Respaldado por esta tarea? |
| --- | --- | --- |
| `/var/lib/docker/volumes/romm_mysql_data/_data` | Archivos internos MariaDB | **No se copian directamente**; se usa dump SQL |
| `/opt/romm` | Configuración y Docker Compose | Sí, vía archivo comprimido |
| `/mnt/romm-library/.romm-data/assets` | Partidas, assets | Sí |
| `/mnt/romm-library/.romm-data/resources` | Portadas y recursos | Sí |
| `/mnt/romm-library` (resto) | Biblioteca de juegos (~22 GB) | **No** |
| Redis Docker | Caché/colas | No, deliberadamente |

En Proxmox, el volumen extra de 100 GB está en `mp0` con `backup=0`, por lo que tampoco entra en el `vzdump` de CT102.

## Procedimiento

1. Validar que `/mnt/backups` está montado y CT102 está encendido.
2. Realizar `mariadb-dump --single-transaction` desde `romm-db` con credenciales de entorno que nunca se escriben en el repositorio.
3. Comprimir assets/resources y `/opt/romm`.
4. Validar `gzip -t`, listar contenido con `tar -tzf` y generar `SHA256SUMS`.
5. Publicar directorio final solo después de completar todas las validaciones.
6. Conservar las tres últimas copias después de una ejecución exitosa.

Scripts: `scripts/backups/backup-romm.sh`, `rotar-romm.sh`.

## Horarios

- `backup-romm.timer`: diariamente a las **03:10 Europe/Madrid**.
- `kuma-romm-backup.timer`: comprobar salud de respaldo cada 15 min.
- El `vzdump` de CT100 permanece a las **04:00**.

## Primera copia verificada

El 28/10/2026 se generó `romm-20261028-010344`, tamaño aproximado **435 MB**. Los archivos `mariadb.sql.gz` y `archivos.tar.gz` devolvieron `OK` al verificar SHA-256.

**Pendiente**: comprobar la primera ejecución automática, realizar restauración de prueba aislada y definir una segunda ubicación de backup fuera de la eMMC.

## Verificación

```bash
systemctl list-timers backup-romm.timer
journalctl -u backup-romm.service -n 80 --no-pager
find /mnt/backups/romm-data -maxdepth 1 -name 'romm-*' -type d
# En el directorio de una copia:
sha256sum -c SHA256SUMS
gzip -t mariadb.sql.gz archivos.tar.gz
```

## Restauración — precauciones

No ejecutar una restauración sobre el servicio de producción sin detener las escrituras, respaldar el estado actual y verificar la versión de MariaDB/RomM. El backup selectivo **no contiene la biblioteca de juegos** y puede no ser completamente consistente si se modificaron partidas durante la copia de archivos. También puede contener `.env` u otras credenciales dentro de `/opt/romm`: **proteger el archivo de respaldo como información sensible**.

## Limitaciones de integridad

La prueba SHA-256 verifica la integridad de los archivos generados, **no garantiza** que el volcado SQL se pueda importar o que las partidas se restauren correctamente. Se recomienda probar la recuperación en un contenedor aislado y documentar los pasos observados.
