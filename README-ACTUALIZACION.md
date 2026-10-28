# Mi Homelab — Proxmox & Docker

> **Actualización de documentación · 28 de octubre de 2026**
>
> Ampliación de los 13 capítulos originales del repositorio [`Gokusupersayanbu/homelab`](https://github.com/Gokusupersayanbu/homelab).

Este paquete **añade documentación y ejemplos reproducibles**, no reemplaza los archivos anteriores del repositorio ni despliega cambios en el servidor. Está redactado para publicarse en GitHub sin credenciales privadas.

## Resumen de novedades

| Componente | Estado documentado | Mejoras incorporadas |
| --- | --- | --- |
| CT100 — Servicios | Operativo | Vikunja multiusuario, 4 perfiles de alertas y control de acceso con Tailscale |
| Uptime Kuma | Operativo | Monitores Push para eMMC, memoria/PSI, LXC y backups de RomM |
| CT101 — Samba | Operativo | Exclusiones documentadas: archivo grande y volumen de música |
| CT102 — RomM | Operativo | Backup específico para base de datos, configuración, assets y recursos |
| Proxmox | Operativo | Documentación de calendario systemd, almacenamiento y problemas detectados |

## Capítulos nuevos

14. [Vikunja: tareas y notificaciones privadas](docs/14-vikunja-telegram.md)
15. [Monitorización: Uptime Kuma y systemd](docs/15-monitorizacion-avanzada.md)
16. [Copias de RomM y recuperación](docs/16-backups-romm.md)
17. [Seguridad y acceso remoto](docs/17-seguridad-tailscale.md)
18. [Inventario y estado de respaldos](docs/18-estado-y-pendientes.md)

## Código y plantillas

- `scripts/vikunja/avisos_multi.py`: código multiusuario basado en la versión corregida probada en CT100.
- `scripts/monitorizacion/`: scripts Push utilizados para monitorizar el host Proxmox.
- `scripts/backups/`: creación y retención de backups selectivos de RomM.
- `systemd/`: unidades y temporizadores reproducibles como referencia.
- `ejemplos/`: archivo de ejemplo, sin secretos.

## Seguridad y privacidad

**Nunca subir** `/etc/vikunja-alertas/perfiles/*.env`, Push URLs, tokens de Telegram, API keys, contraseñas, dumps SQL, archivos de partidas privados ni bases de datos. El repositorio contiene **plantillas y scripts**, no copias reales del servidor.

## Límites de la documentación

- La primera copia manual de RomM (435 MiB aprox.) pasó `gzip -t`, lectura de `tar` y SHA-256. **No se realizó una restauración de prueba.**
- El temporizador diario de RomM quedó configurado para las 03:10 hora de Madrid; su primera ejecución programada aún estaba pendiente cuando se recopiló el estado.
- CT101 no tiene un backup periódico identificado, aunque existen copias manuales válidas.
- Los juegos de RomM y el volumen musical de Samba no están protegidos por estas copias.
- Los nombres reales de los otros usuarios y sus Chat ID se han omitido deliberadamente.

Consulta [INTEGRAR-EN-REPOSITORIO.md](INTEGRAR-EN-REPOSITORIO.md) para añadir estos archivos a tu repositorio existente.
