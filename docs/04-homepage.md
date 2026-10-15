# 04 · Homepage — dashboard

[Volver al índice](../README.md)

## Ubicación y configuración

Homepage corre en Docker dentro de **CT100**, no directamente en el host Proxmox:

```text
/root/homepage/
├── compose.yaml
├── .env                     # privado, nunca publicar
├── config/
│   ├── settings.yaml
│   ├── services.yaml
│   ├── widgets.yaml
│   ├── bookmarks.yaml
│   ├── custom.css
│   └── custom.js
└── backup-status/
    └── backup.json          # generado, no versionar
```

Ejemplo de Compose: [`ejemplos/homepage/compose.yaml`](../ejemplos/homepage/compose.yaml).

El proyecto contiene dos servicios Docker:

- **homepage** publicado en `3000:3000`, con `HOMEPAGE_ALLOWED_HOSTS` configurado y variables `HOMEPAGE_VAR_*` desde `.env`.
- **backup-status** basado en `nginx:alpine`, sin publicar puertos. Sirve **solo** el JSON de datos no sensibles a la red Docker.

## Panel y widgets

Orden del dashboard: **Servicios del Homelab → Red y conectividad → Almacenamiento → Copias de seguridad → Accesos rápidos**.

- `Servicios del Homelab`: Pi-hole, Uptime Kuma, Proxmox, Vaultwarden (2 columnas).
- `Red y conectividad`: monitorización DNS y router (1 columna).
- `Almacenamiento`: discos lógicos `local`, `local-lvm` de Proxmox.
- `Copias de seguridad`: `backups-emmc` y MEGA con resumen JSON.
- Cabecera: CPU, RAM, espacio, red, uptime y fecha (configuración de widget de recursos de CT100).

El token Proxmox `homepage@pve!dashboard` se guarda **solo en entorno**, referenciado desde `services.yaml` como `{{HOMEPAGE_VAR_PROXMOX_USER}}` y `{{HOMEPAGE_VAR_PROXMOX_SECRET}}`. No se publica su secreto. Utiliza permisos de solo lectura adecuados para los endpoints que consumes.

## Tarjeta MEGA con estadísticas reales

El host Proxmox ejecuta Rclone con `mega-crypt:` y crea este JSON **sin contraseñas**:

```json
{
  "copias": 2,
  "espacio_bytes": 4080403042,
  "ultimo_backup": "15/10/2026 04:00",
  "ultima_subida": "15/10/2026 04:15"
}
```

La estadística se basa en `rclone lsjson mega-crypt:CT100 --files-only`. Su `ModTime` representa la fecha registrada por el proveedor, mientras que la fecha del backup procede del nombre del archivo. **El JSON es una fotografía; si el script de actualización falla, podría mostrar datos antiguos.**

El programa [`scripts/actualizar-homepage-mega.py`](../scripts/actualizar-homepage-mega.py) copia `backup.json.new` a CT100 con `pct push` y lo renombra atómicamente a `backup.json`.

`services.yaml` utiliza:

```yaml
widget:
  type: customapi
  url: http://backup-status/backup.json
  refreshInterval: 60000
  display: list
  mappings:
    - field: copias
      label: Copias
      format: number
    - field: espacio_bytes
      label: Espacio ocupado
      format: bytes
    - field: ultimo_backup
      label: Ultimo backup
      format: text
    - field: ultima_subida
      label: Ultima subida
      format: text
```

El endpoint **no incluye las contraseñas** pero expone metadatos de copias a los contenedores que compartan red Docker. El servicio Nginx carece de puertos publicados en la LAN.

## CSS y JavaScript personalizados

- `custom.css`: estética oscura, bordes por servicio, tarjetas y jerarquía tipográfica.
- `custom.js`: barras de ocupación para `almacenamiento-local`, `almacenamiento-lvm`, `backup-emmc`; indicador del estado de los monitores de Kuma en la cabecera.
- El JavaScript lee texto y nodos del HTML generado por Homepage. **Podría necesitar ajustes cuando Homepage cambie su DOM**. No depende de nuevas peticiones a la API de Proxmox.
- El diseño final usa la tipografía por defecto de Homepage (Manrope). `font: plexData` se retiró por problemas de legibilidad.

Ejemplos: [`settings.yaml`](../ejemplos/homepage/config/settings.yaml), [`services.yaml`](../ejemplos/homepage/config/services.yaml), [`custom.css`](../ejemplos/homepage/config/custom.css), [`custom.js`](../ejemplos/homepage/config/custom.js).

## Comprobación tras editar

En CT100:

```bash
cd /root/homepage
docker compose config --quiet
docker compose ps
docker exec homepage node -e \
  'fetch("http://backup-status/backup.json").then(r=>r.json()).then(console.log).catch(console.error)'
```

En el navegador: `http://192.168.0.12:3000`; refrescar caché con `Ctrl + F5`.

## Documentación oficial

- [Configuración de Homepage](https://gethomepage.dev/configs/settings/)
- [Custom API widget](https://gethomepage.dev/widgets/services/customapi/)
