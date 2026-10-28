# Registro de cambios

## 2026-10-28 — Vikunja, monitorización y RomM

### Añadido

- Vikunja integrado en CT100 con cuatro perfiles de notificación de Telegram independientes.
- Filtrado por asignación real/creador con verificación explícita de responsables desde la API.
- Programación horaria de avisos de vencimiento con prevención de duplicados.
- Monitores Push: eMMC, RAM/swap/PSI, estado de LXC y antigüedad de copias RomM.
- Copia selectiva de RomM: MariaDB, configuración, partidas, assets y recursos.
- Timer diario de RomM a las 03:10 `Europe/Madrid` y retención de tres copias.
- Documento de aislamiento con Tailscale y procedimientos de comprobación.

### Verificado

- Primera copia manual RomM de ~435 MB con `gzip`, `tar` y SHA-256 OK.
- Respuesta `{"ok":true}` de Uptime Kuma en las pruebas Push.
- LXC CT100, CT101 y CT102 encendidos en el inventario revisado.
- Copias recientes CT100 y CT101 completadas correctamente.

### Pendiente

- Primera ejecución automática de backup RomM y restauración real de prueba.
- Proteger la música de CT101 y la biblioteca completa de RomM en almacenamiento separado.
- Copia externa de seguridad distinta de la eMMC.
- Monitor del resultado de `vzdump` y protección ante caída del propio host.
