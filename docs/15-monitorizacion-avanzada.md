# 15. Monitorización avanzada — Uptime Kuma y systemd

## Objetivo

Monitorizar el host Proxmox con **scripts ligeros ejecutados por timers** que publican un estado (`up` o `down`) en monitores Push de Uptime Kuma dentro de CT100.

## Diagrama

```text
Proxmox host
 ├─ kuma-backups.timer -> kuma-backups.sh (eMMC)
 ├─ kuma-memoria.timer -> kuma-memoria.sh (RAM / swap / PSI)
 ├─ kuma-lxc.timer -> kuma-lxc.sh (CT100, 101, 102)
 └─ kuma-romm-backup.timer -> kuma-romm-backup.sh (antigüedad backup)
                                        │
                                        ▼
                          Uptime Kuma (CT100:3001)
                                        │
                                        ▼
                                Telegram privado
```

## Monitores configurados

| Monitor | Frecuencia | Condición de aviso |
| --- | --- | --- |
| Backups eMMC | Cada 60 min (minuto 10) | Montaje ausente; ocupación >= 80 % |
| RAM, swap y presión PSI | Cada 5 min | RAM disponible < 10 %; PSI some >= 10 %; PSI full >= 2 %; o swap >= 90 % y RAM < 20 % |
| Contenedores LXC | Cada 5 min | Alguno entre CT100, CT101 y CT102 no aparece `running` |
| Estado de backup RomM | Cada 15 min | Timer caído, backup fallido, faltan archivos o copia con más de 30 h |

El valor de swap ocupada **no es por sí mismo una alerta**: el diagnóstico real mostró 1,4/4 GiB de swap, pero casi ninguna actividad `si/so` ni presión PSI.

## Comprobaciones generales

```bash
systemctl list-timers 'kuma-*'
systemctl start kuma-backups.service
systemctl start kuma-memoria.service
systemctl start kuma-lxc.service
systemctl start kuma-romm-backup.service
journalctl -u kuma-lxc.service -n 20 --no-pager
```

Los scripts se instalan en `/usr/local/sbin`, sus Push URLs van a `/etc/homelab-monitor/*-url` con permisos privados y las unidades a `/etc/systemd/system`. **Las Push URLs no se publican**.

## Configuración de Kuma

- Crear cuatro monitores de tipo `Push` independientes con los nombres anteriores.
- Intervalo recomendado de ausencia: memoria/LXC mayor que 5 min (p. ej. 15 min); RomM mayor que 15 min (p. ej. 45 min); eMMC mayor que 60 min (p. ej. 90 min).
- Asociar cada monitor a una notificación de Telegram de infraestructura.
- Si se desea distinguir claramente el umbral de eMMC 80 % del 90 %, crear monitores distintos. Un monitor que ya está `down` puede no notificar otra vez al pasar de aviso a crítico.

## Limitaciones

**Uptime Kuma vive en CT100:** si CT100 o Proxmox se apagan, el monitor Push podría dejar de recibir comprobaciones, pero tampoco podrá avisar por Telegram porque su propio Kuma estará caído. Para cubrir esto es necesario un monitor fuera del host.

Las comprobaciones LXC solo verifican el estado del contenedor. Los servicios individuales se supervisan mediante HTTP, DNS o TCP en Kuma: Navidrome, Pi-hole, Samba, RomM y Vaultwarden, entre otros. La captura mostraba estos monitores operativos; Vikunja y Homepage se propusieron como monitores adicionales y requieren confirmar su alta.

## Valores observados (28/10/2026)

| Métrica | Valor observado |
| --- | --- |
| RAM host | 3,7 GiB total, ~1,6 GiB disponible |
| Swap | 4 GiB total, ~1,4 GiB ocupada |
| PSI some avg60 | ~0,02 % |
| PSI full avg60 | 0 % |
| eMMC backups | ~75–76 % ocupado |
| LXC | CT100, CT101, CT102 en ejecución |

Estos valores son **fotografía histórica**, no monitorización en vivo.
