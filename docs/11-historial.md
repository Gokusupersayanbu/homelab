# 11 · Bitácora de despliegue — 14–15 de octubre de 2026

[Volver al índice](../README.md)

## Servicios y dashboard

1. Se montó Proxmox con un LXC CT100 (Fedora, Docker) y se configuraron Pi-hole, Vaultwarden+Caddy, Uptime Kuma, Homepage.
2. Se añadieron las páginas de estado `homelab`, `red`, `vaultwarden` y posteriormente `backups`; Kuma ya tenía integración con Telegram.
3. Homepage pasó de tarjetas básicas a una vista organizada por servicios, red, discos y copias.
4. Se implementaron barras de ocupación mediante `custom.js`, estado general de Kuma y estilos oscuros en CSS.
5. Se simplificó la sección de almacenamiento de tres tarjetas a `local` y `local-lvm`: `rootfs` y `local` reflejaban el mismo disco físico.
6. Se rediseñó la UI reemplazando CSS acumulado y eliminando `font: plexData`.

## Protección local

1. Se identificó `/dev/sda` como USB Toshiba (1 TB) y `/dev/mmcblk0` como eMMC interna (58,2 GiB).
2. Se verificó EFI/arranque desde USB, ausencia visible de particiones en eMMC y su estado de escritura.
3. Se obtuvo permiso explícito para inicializar eMMC; tabla GPT + EXT4, etiqueta `pve-backups`.
4. Se montó en `/mnt/backups`, se añadió a `/etc/fstab` y se registró como `backups-emmc` con `--is_mountpoint yes`.
5. Se hizo `vzdump 100` en modo `stop`, zstd, manual; resultado satisfactorio.
6. Se creó tarea diaria 04:00 con retención de tres backups y se probó la primera ejecución automática.
7. Se verificó el archivo zstd y se restauró un CT101 de prueba con la red deshabilitada; tras comprobar rutas, se desmontó y eliminó.

## Copia cifrada externa y monitorización

1. Se instaló Rclone oficial porque el paquete Debian no ofrecía backend MEGA.
2. Se configuraron remotos `mega:` y `mega-crypt:`, guardando claves fuera del repositorio.
3. Se subió el primer archivo y se comprobó su descarga/descifrado/descompresión en streaming.
4. Se implementaron `backup-mega.sh`, `vzdump-mega-hook.sh` y `systemd-run` para subir tras backup local.
5. Se verificó el hook manualmente y su ejecución automática real desde las 04:07 hasta las 04:15.
6. Se creó el monitor Push de Kuma y se integró al final del script tras una subida correcta.
7. Se añadió `backup-status` Nginx dentro de la red Docker para exponer solo `backup.json`.
8. Se creó `actualizar-homepage-mega.py`, se enlazó al script de subida y se probó la cadena: MEGA → JSON → Homepage → Kuma.

## Hechos verificados más importantes

| Evento | Registro |
| --- | --- |
| Primer backup manual | 15/10/2026 01:56:25 — 02:03:13 |
| Primera copia local | 2.039.586.174 bytes |
| Primera copia programada | 15/10/2026 04:00:26 |
| Segunda copia local y remota | 2.040.816.868 bytes |
| Inicio primera subida automática | 04:07:37 |
| Fin primera subida automática | 04:15:53 |
| Resultado prueba manual completa | `HOMEPAGE: Estadisticas actualizadas correctamente` + `UPTIME KUMA: Backup confirmado correctamente` |
