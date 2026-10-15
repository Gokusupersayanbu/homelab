# 13 · Publicación del repositorio en GitHub

[Volver al índice](../README.md)

## Antes de subirlo

**No publicar nunca:**

- `/root/homepage/.env` ni ficheros con `HOMEPAGE_VAR_*` resueltos.
- `/root/.config/rclone/rclone.conf` (contiene contraseñas **ofuscadas**, no protegidas adecuadamente contra lectura).
- `/root/.config/backup-mega-kuma.curl` (contiene una URL Push con token).
- Claves de Crypt (`password` y `password2`), códigos 2FA, secretos de la API de Proxmox.
- Bases de datos y volúmenes persistentes de Vaultwarden, Caddy, Pi-hole, Kuma.
- Capturas de pantalla con URLs privadas de Push (durante la configuración se compartió una).
- Backups `.tar.zst`, datos personales, volcados de logs con tokens.

**Rotar el token Push** si la URL completa quedó expuesta en una captura que se publicará o compartirá de manera amplia. Después actualizar `backup-mega-kuma.curl` en Proxmox.

Los ejemplos del repositorio ya usan placeholders en credenciales y no incluyen `rclone.conf`. Los enlaces de red son IPs privadas reales del escenario: si prefieres anonimizar la topología, sustitúyelas por nombres como `proxmox.lan`, `docker.lan`, etc.

## Crear el repo

Descomprime el ZIP de documentación en tu ordenador y abre una terminal **dentro de la carpeta** `homelab-proxmox-documentacion`:

```bash
git init -b main
git add .
git status
git diff --cached --stat
git commit -m "docs: documentar homelab Proxmox y backups cifrados"
```

Crea en GitHub un repositorio vacío, sin autogenerar README; usa la URL que GitHub te proporcione:

```bash
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

Si ya hay un README remoto, adapta el procedimiento sin sobrescribir cambios. **No hace falta subir nada desde el servidor Proxmox**: publica solo la documentación saneada del ZIP.

## Mantener documentación sincronizada

Cuando cambie una tarea de backup, un servicio o un volumen, actualiza el documento correspondiente. El README es una fotografía de la infraestructura a fecha **15/10/2026**; no pretende representar automáticamente el estado futuro.

## Referencias técnicas

- [Proxmox — documentación vzdump](https://github.com/proxmox/pve-docs/blob/master/vzdump.adoc)
- [Rclone Crypt](https://rclone.org/crypt/)
- [Rclone MEGA](https://rclone.org/mega/)
- [Homepage Custom API](https://gethomepage.dev/widgets/services/customapi/)
