# 07 · Supervisión, Uptime Kuma y Telegram

[Volver al índice](../README.md)

## Monitores desplegados

- Pi-hole DNS.
- Router LAN.
- Vaultwarden.
- `Backup Proxmox → MEGA` (**Push**).

Los servicios están agrupados en páginas de estado para Homepage:

| Slug | Qué agrupa | Uso |
| --- | --- | --- |
| `homelab` | Tres monitores de servicios | Widget de disponibilidad y badge global |
| `red` | Router y DNS | Sección Red y conectividad |
| `vaultwarden` | Un monitor | Tarjeta Vaultwarden |
| `backups` | Push de MEGA | Estado de copia externa (antes de usar JSON) |

**Importante:** el monitor Push y la página de estado no son lo mismo. Un error `Status Page Not Found` se resolvió creando la página con slug exacto `backups` y añadiendo el monitor Push.

## Heartbeat del backup

Al monitor Push se le asignó una ventana de **93.600 segundos = 26 horas**. El programa de subida envía una señal a Kuma **solo después de terminar** sus operaciones de subida y actualización de estadísticas.

La URL privada contiene un token. Se guardó, **no en el repositorio**, en:

```text
/root/.config/backup-mega-kuma.curl
```

El fichero real contiene una línea `url = "..."`. Plantilla: [`ejemplos/backup-mega-kuma.curl.example`](../ejemplos/backup-mega-kuma.curl.example).

Test manual:

```bash
curl --config /root/.config/backup-mega-kuma.curl \
  --fail --silent --show-error --max-time 15
# Respuesta observada: {"ok":true}
```

La prueba final del script devolvió:

```text
Subida comprobada correctamente
BACKUP MEGA COMPLETADO
HOMEPAGE: Estadisticas de MEGA actualizadas
HOMEPAGE: Estadisticas actualizadas correctamente
UPTIME KUMA: Backup confirmado correctamente
```

## Telegram

Uptime Kuma estaba configurado para enviar alertas a Telegram. Es importante asegurarse de que la notificación esté asignada **también al monitor Push de backup**, y realizar una prueba de alerta controlada. La notificación por ausencia de heartbeat **aún no consta comprobada de extremo a extremo**.

## Advertencia de exposición de token

Durante la configuración se compartió una captura con la **URL Push completa del monitor** visible. Si la captura puede compartirse fuera de un entorno privado, **regenerar el token del monitor y actualizar el archivo `.curl` del host** antes de publicar documentación.

## Criterio de salud

Que Kuma muestre `100 %` significa que el monitor responde según la lógica de Kuma. **No implica** que las tres copias sean restaurables. Combinarlo con verificaciones de integridad y restauraciones periódicas.
