# 10 · Operación y mantenimiento

[Volver al índice](../README.md)

## Rutina recomendada

| Frecuencia | Verificación | Herramienta |
| --- | --- | --- |
| Diaria | Existencia de nueva copia y heartbeat Push | Homepage y Uptime Kuma |
| Semanal | Estado del eMMC y espacio libre | `pvesm status`, `df -h /mnt/backups` |
| Semanal | Número y tamaño de copias en MEGA | `rclone ls mega-crypt:CT100` |
| Mensual | Comprobar una copia remota de lectura completa | `rclone cat ... | zstd -t -` |
| Trimestral | Restaurar en CT temporal sin red y comprobar aplicaciones en entorno aislado | `pct restore`, comprobaciones de servicio |
| Tras cambios importantes | Ejecutar backup de prueba y revisar secretos | `vzdump`, inspección de repositorio |

Estas frecuencias son **propuestas de mantenimiento**, no tareas periódicas todas ellas configuradas.

## Comandos de diagnóstico

```bash
# Host Proxmox
pvesm status
findmnt /mnt/backups
df -h /mnt/backups
pct status 100
pvesh get /cluster/backup --output-format json-pretty
pvesm list backups-emmc --content backup

# MEGA
rclone ls mega-crypt:CT100
rclone lsjson mega-crypt:CT100 --files-only
journalctl -u 'backup-mega-ct100-*' --since 'yesterday' --no-pager

# Homepage y Nginx internos (en CT100)
cd /root/homepage
docker compose ps
docker exec homepage node -e \
  'fetch("http://backup-status/backup.json").then(r=>r.json()).then(console.log).catch(console.error)'
```

## Capacidad y riesgos

- CT100: disco de **8 GiB**, uso observado **61 %**. Vigilar crecimiento de imágenes y volúmenes.
- eMMC: tras dos backups, Homepage reflejaba ~**4,08 GB utilizados de 61,2 GB** (lectura decimal del widget); retención local `keep-last=3`.
- MEGA: ~**19 GB libres** al inicio. La papelera puede mantener archivos eliminados y reducir espacio efectivo.
- Rclone consumió hasta **1,1 GiB** de RAM del host en una subida. Monitorizar estabilidad y rendimiento.
- Backup LXC en modo `stop`: interrupción de **Pi-hole** y demás servicios. El equipo debería tener un DNS alternativo de confianza si se requiere continuidad.

## Mejoras pendientes

- Prueba real de que Telegram alerta si se pierden heartbeats (no solo recepción de Push).
- Alertar también cuando la subida falla **en el momento**, sin esperar 26 horas, si es necesario.
- Revisar los errores del script, que hoy valida el tamaño y registra éxito; hacer pruebas periódicas remotas de integridad.
- Copias del propio Proxmox (`/etc/pve`, red, configuración del host), ya que el backup de CT100 **no restaura el host completo**.
- Guardar credenciales y claves de recuperación **fuera del homelab** y documentar cómo recuperarlas.
- Restringir acceso a `rclone.conf` y revisar periódicamente los permisos del archivo Push.
- Revisar sensibilidad de capturas antes de publicarlas.
