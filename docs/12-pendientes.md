# 12 · Estado de verificación y limitaciones

[Volver al índice](../README.md)

## Verificado con comandos o capturas

- Dispositivos USB/eMMC y arranque EFI por USB.
- CT100 LXC con disco 8 GiB, Fedora, Docker, volúmenes persistentes principales.
- Backup local `vzdump`, validación con ZSTD, recuperación a CT101 y presencia de los directorios de datos.
- Tarea automática 04:00, modo stop, retención de tres.
- Remotos `mega:` y `mega-crypt:` y subida real de archivo cifrado.
- Lectura/descifrado remoto de una copia y test ZSTD completo.
- Hook `backup-end` lanzado mediante systemd y subida real a MEGA tras backup programado.
- Servidor JSON en red Docker, widget customapi, actualización desde Proxmox y heartbeat Push de Kuma.

## No verificado todavía / no incluido en este repositorio

- No se ha arrancado un CT101 restaurado aislado para validar funcionalmente Pi-hole, Vaultwarden y Kuma tras un desastre.
- No se ha probado la recuperación integral del **host** Proxmox ni la reinstalación desde cero del disco USB.
- No se ha demostrado la notificación Telegram **tras transcurrir 26 horas sin Push**; recepción de heartbeat sí.
- No se ha probado que MEGA elimine permanentemente las copias viejas de su papelera.
- No se han auditado todas las reglas de firewall/puertos ni se incluyen secretos o certificados.
- Los Compose completos de Pi-hole, Vaultwarden y Kuma no se proporcionaron; se documentan rutas comprobadas, no configuraciones inventadas.
- No hay evidencias de prueba remota de integridad **en cada madrugada**; se hizo una prueba completa manual, luego comparación de tamaños.

## Protección de datos

El repositorio no contiene bases de datos ni credenciales. La captura publicada de Homepage no muestra la URL Push, aunque sí identifica servicios y métricas. Si el repositorio es público, revisa también que la topología (IPs) no revele más de lo deseado.
