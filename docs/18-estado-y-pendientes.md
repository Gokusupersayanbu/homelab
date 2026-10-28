# 18. Inventario, copias y próximas mejoras

## Inventario verificado (28/10/2026)

| Recurso | Entorno | Principales servicios |
| --- | --- | --- |
| Host Proxmox | Proxmox VE, ~3,7 GiB RAM | LXC, storage local-LVM, backups eMMC |
| CT100 | Contenedor de servicios | Pi-hole, Uptime Kuma, Homepage, Vaultwarden/Caddy, Vikunja |
| CT101 | Contenedor Samba | Samba y Navidrome |
| CT102 | Contenedor RomM | RomM y MariaDB (Docker) |

## Almacenamiento y backups

- eMMC: 58 GB, **~75–76 % ocupado**, ~14 GB libres al tomar las medidas.
- CT100: `vzdump` diario a las 04:00, compresión zstd, retención `keep-last=3`, con hook MEGA. Últimas tres ejecuciones consultadas: OK.
- CT101: copia completa previa de ~31,85 GB y copia reciente de ~3,39 GB. La reducción concuerda con la exclusión explícita de un archivo de 30 GB. La copia reciente terminó OK.
- CT101: disco adicional `/srv/musica` (`mp0`, 100 GB) con `backup=0`, biblioteca ~2,2 GB sin cubrir por `vzdump`.
- CT102: `rootfs` 16 GB, utilizado ~4,8 GB; `mp0` adicional de 100 GB con ~22 GB utilizados y `backup=0`.
- CT102: backup específico de datos importantes, 435 MB en primera copia manual, programa diario 03:10 y monitor Push cada 15 min.

## Incidencias y riesgos

1. Una ejecución de `vzdump` CT101 del 27/10 a las 01:23 tuvo estado `unexpected status`; una copia posterior a las 09:21 terminó correctamente.
2. Proxmox advirtió que el conjunto de tamaños virtuales aprovisionados supera el thin pool real y que no está activada la autoextensión preventiva del thin pool. **No cambiar LVM sin plan de capacidad y copias verificadas.**
3. La eMMC de backups está relativamente llena; no añadir copias de bibliotecas de juegos o música sin plan de almacenamiento.
4. Los backups locales almacenados en la eMMC no protegen frente a fallo físico del propio dispositivo.
5. Los monitores Push no pueden avisar por Telegram si Uptime Kuma (CT100) está caído.

## Backlog recomendado

| Prioridad | Trabajo pendiente | Motivo |
| --- | --- | --- |
| Alta | Restauración de prueba de RomM en entorno aislado | Verificar recuperabilidad real |
| Alta | Segunda ubicación de backups | Proteger frente a fallo de eMMC |
| Alta | Monitor de resultados `vzdump` CT100/CT101 | Detectar fallos y copias demasiado antiguas |
| Media | Revisar y documentar protección musical y ROMs | Volúmenes extra excluidos |
| Media | Verificar el primer backup automático de RomM | Se probó la ejecución manual y el temporizador |
| Media | Monitor independiente fuera de Proxmox | Detectar apagado del host/CT100 |
| Media | Revisar advertencias del thin pool | Evitar problemas futuros de almacenamiento |
| Baja | Confirmar monitores HTTP para Vikunja y Homepage | Comprobar servicio, no solo contenedor |
