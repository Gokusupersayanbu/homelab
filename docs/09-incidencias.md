# 09 · Incidencias encontradas y solucionadas

[Volver al índice](../README.md)

| Síntoma | Causa / diagnóstico | Solución aplicada |
| --- | --- | --- |
| `parted: command not found` | La herramienta no estaba instalada | `apt update && apt install -y parted` |
| `mount: can't find UUID=...` | Se introdujo un UUID incompleto | Se verificó con `blkid -p /dev/mmcblk0p1` y se usó el UUID completo |
| `findmnt --verify` avisa de `fstab` modificada | systemd aún no había recargado la definición | `systemctl daemon-reload` |
| `rclone` sin backend `mega` | Paquete Debian `rclone v1.60.1-DEV` no lo incluía | Se instaló la distribución oficial y se verificó `rclone help backends` |
| `Status Page Not Found` en Homepage | Existía el monitor Push pero no la página de estado `backups` | Creación de página de estado con slug correcto y monitor asignado |
| `du -sh /var/lib/docker` muy distinto en CT101 | Docker OverlayFS aporta montajes que cambian el cálculo | Comparación con `du -xsh` y comprobación directa de datos persistentes |
| `journalctl ... --since 04:00` sin entradas | Se consultó **antes** de las 04:00 | Esperar a la tarea programada; `pvescheduler` estaba activo |
| Aviso Pi-hole: `1.2 > 1 CPU` | Pico temporal de carga observada cerca del backup/subida | Se comprobó `uptime` posterior (`0.30,0.25,0.20`); sin pruebas de fallo DNS |
| Dashboard con estilos inconsistentes | CSS acumulaba duplicados y errores como `B/*` | Sustitución por CSS ordenado; eliminación de `plexData` |
| MEGA solo mostraba `sitios activos / tiempo activo` | Widget Kuma mostraba disponibilidad, no metadatos de backup | Nginx interno + JSON de Rclone + widget `customapi display: list` |
| Acceso a `/root/homepage` falla | Se ejecutó `cd` en host Proxmox en vez de CT100 | `pct enter 100` y trabajar desde CT100 |

## Nota sobre el aviso de Pi-hole

El aviso de Pi-hole fue el **15/10/2026 a las 04:13:55**, `Long-term load (15min avg) larger than number of processors: 1.2 > 1`. En paralelo, `backup-mega.sh` llevaba subiendo desde las 04:07:37 hasta las 04:15:52; systemd registró pico de RAM de 1,1 GiB.

**Correlación temporal no es causalidad demostrada.** Pi-hole se encontraba en CT100 con 1 core, y el valor de load puede corresponder a actividad de host / sistema de archivos. Si se repite, analizar CPU, I/O, RAM, latencia DNS y registro del proceso antes de aumentar recursos.
