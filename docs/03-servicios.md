# 03 · Servicios desplegados en Docker

[Volver al índice](../README.md)

**Alcance:** sabemos qué servicios funcionan y dónde están sus volúmenes, pero no se compartieron los archivos Compose completos de **Pi-hole, Vaultwarden, Uptime Kuma ni Caddy**. Por tanto, este documento es un **inventario verificable**, no un instalador que invente ajustes inexistentes.

| Servicio | Acceso interno | Función | Persistencia encontrada mediante `docker inspect` |
| --- | --- | --- | --- |
| **Pi-hole** | `http://192.168.0.12/admin/` | DNS y listas de bloqueo | `/root/pihole/etc-pihole` → `/etc/pihole` |
| **Vaultwarden** | `https://192.168.0.12:8443` | Contraseñas | `vault_vaultwarden_data` → `/data` |
| **Caddy** | HTTPS delante de Vaultwarden | Proxy HTTPS | `/root/vault/Caddyfile` → `/etc/caddy/Caddyfile`, volúmenes `vault_caddy_data`, `vault_caddy_config` |
| **Uptime Kuma** | `http://192.168.0.12:3001` | Monitorización + Telegram | `/root/uptime-kuma/data` → `/app/data` |
| **Homepage** | `http://192.168.0.12:3000` | Dashboard | `/root/homepage/config` → `/app/config` |
| **Nginx backup-status** | Solo red Docker | Sirve el JSON de estadísticas | `/root/homepage/backup-status` → `/usr/share/nginx/html:ro` |

## Comprobar volúmenes sin mostrar secretos

En CT100:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker inspect $(docker ps -q) --format \
  '{{.Name}} {{range .Mounts}}{{.Type}}:{{.Source}} -> {{.Destination}}; {{end}}'
```

> No subas a GitHub los directorios de datos de Vaultwarden ni de Kuma, aunque parezcan contener solo ficheros SQLite. El archivo `Caddyfile` real puede incluir referencias internas o secretos; documenta su estructura con un ejemplo revisado.

## Pi-hole

- Instancia Pi-hole 6 con panel DNS y porcentaje de bloqueo en Homepage.
- La supervisión combina monitor DNS en Uptime Kuma y widget de Homepage.
- Hubo un aviso de carga el 15/10/2026 04:13:55 (`load15=1,2 > 1 CPU`). Fue cercano al backup y subida, pero **no se demostró un fallo DNS**.
- La API de Pi-hole 6 se enlazó con Homepage usando una variable `HOMEPAGE_VAR_PIHOLE_KEY`, no el valor literal dentro de YAML.

## Vaultwarden + Caddy

- Vaultwarden se ejecuta con volumen `vault_vaultwarden_data` para sus datos.
- Caddy tiene configuración y volúmenes propios, delante de Vaultwarden para HTTPS.
- Homepage muestra la disponibilidad usando la página de estado de Kuma de slug `vaultwarden`.
- La verificación/restauración de datos es especialmente sensible: no basta con comprobar que existe el directorio `/data`; realizar pruebas funcionales aisladas y con contraseñas seguras.

## Uptime Kuma

- Página `homelab`: 3 monitores de servicios.
- Página `red`: 2 monitores (router y DNS).
- Página `vaultwarden`: 1 monitor.
- Página `backups`: 1 monitor Push de la tarea de MEGA.
- Alertas Telegram configuradas (comprobar que el monitor Push tiene la notificación habilitada).

## Homepage

Ver [04 · Homepage](04-homepage.md) y sus [ejemplos reproducibles](../ejemplos/homepage/).
