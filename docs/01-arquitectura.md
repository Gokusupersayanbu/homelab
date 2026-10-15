# 01 · Arquitectura e infraestructura

[Volver al índice](../README.md)

## Hardware identificado

| Dispositivo | Identificación / función | Evidencia |
| --- | --- | --- |
| `/dev/sda` | Disco duro **TOSHIBA MQ04ABF100**, USB, **931,5 GiB** | `lsblk -o NAME,SIZE,TYPE,TRAN,MODEL,MOUNTPOINTS` |
| `/dev/mmcblk0` | Memoria **eMMC interna**, **58,2 GiB** disponibles | `lsblk`, `wipefs -n`, `blkid` |
| `/dev/sda2` | Partición EFI de **1 GiB** | Montada en `/boot/efi` |
| `pve-root` | **96 GiB**, ext4 | Sistema `/` |
| `pve-data` | LVM-thin ~**798,2 GiB** | Almacena `vm-100-disk-0` de **8 GiB** |
| `pve-swap` | **4 GiB** | Swap del host |
| `/dev/mmcblk0p1` | EXT4, etiqueta `pve-backups` | Destino de backups `/mnt/backups` |

Los dos almacenamientos Proxmox `local` y `local-lvm` comparten el dispositivo físico **USB** `/dev/sda`. **No son dos discos distintos.** La eMMC es un dispositivo físico separado, aunque ambos están en el mismo equipo.

`efibootmgr -v` confirmó que el arranque actual UEFI usaba el disco USB. La entrada de Proxmox apuntaba al fichero `\\EFI\\proxmox\\shimx64.efi` de la partición EFI del mismo disco.

## Red

| Componente | Dirección usada durante la instalación |
| --- | --- |
| Router/gateway | `192.168.0.1` |
| Proxmox `homelab` | `192.168.0.15` |
| CT100 (Docker y servicios) | `192.168.0.12/24` |
| Homepage | `http://192.168.0.12:3000` |
| Uptime Kuma | `http://192.168.0.12:3001` |
| Pi-hole | `http://192.168.0.12/admin/` |
| Vaultwarden por Caddy | `https://192.168.0.12:8443` |
| Proxmox | `https://192.168.0.15:8006` |

> Estas direcciones son IP privadas RFC1918 para documentar el despliegue. Si el repositorio será público y no deseas divulgar la topología, sustitúyelas por marcadores antes de publicar.

## Dependencias

1. Proxmox debe arrancar desde el USB.
2. CT100 debe arrancar (`onboot: 1`) para que Docker y los servicios estén disponibles.
3. Homepage y el Nginx interno comparten red Docker; Homepage consulta `http://backup-status/backup.json`.
4. En el host Proxmox, Rclone consulta MEGA y genera estadísticas; el host copia el JSON a CT100 con `pct push`.
5. El monitor Push de Kuma recibe confirmación al final de una subida correcta. Telegram envía alertas cuando falta el heartbeat, según su configuración.

No se publican rutas de gestión desde Internet como parte de esta arquitectura. Cualquier acceso remoto requeriría otra configuración de red y de seguridad no detallada aquí.
