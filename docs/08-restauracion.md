# 08 · Restauración y recuperación ante desastres

[Volver al índice](../README.md)

## Restauración de prueba realizada

A partir de la primera copia se restauró un **CT101** nuevo, aislado y detenido. CT100 siguió siendo el servicio en producción.

```bash
# Consultar un ID libre (devolvió 101 en la prueba)
pvesh get /cluster/nextid

# Modelo del comando realizado: sustituye el archivo por el real
pct restore 101 \
  /mnt/backups/dump/vzdump-lxc-100-YYYY_MM_DD-HH_MM_SS.tar.zst \
  --storage local-lvm \
  --hostname CT101-prueba \
  --onboot 0 \
  --net0 'name=eth0,bridge=vmbr0,ip=manual,link_down=1'

pct status 101
pct config 101
```

Se observó `status: stopped`, `onboot: 0`, la interfaz desconectada (`link_down=1`) y `rootfs` restaurado de **8 GiB** en `local-lvm`.

Se montó el sistema sin arrancar el contenedor:

```bash
pct mount 101
ls -ld /var/lib/lxc/101/rootfs/var/lib/docker
ls -ld /var/lib/lxc/101/rootfs/var/lib/docker/volumes
du -xsh /var/lib/lxc/101/rootfs/var/lib/docker
```

En el original `du -xsh /var/lib/docker` mostró ~2,1 MiB; en restaurado ~2,3 MiB. La diferencia con los 2,5 GiB de `du -sh` original se debía a montajes de Docker, no a una prueba de datos faltantes.

Se comprobó que estaban presentes estas rutas restauradas:

```text
/var/lib/docker/volumes/vault_vaultwarden_data/_data
/var/lib/docker/volumes/vault_caddy_data/_data
/var/lib/docker/volumes/vault_caddy_config/_data
/root/uptime-kuma/data
/root/pihole/etc-pihole
/root/homepage/config
/root/vault/Caddyfile
```

Se desmontó y borró **solo CT101**, tras la prueba:

```bash
pct unmount 101
pct status 101
findmnt --mountpoint /var/lib/lxc/101/rootfs
# Ejecutar solo si CT101 es realmente la copia temporal y está desmontado
pct destroy 101
pct list
```

> `pct destroy` es destructivo. **Nunca** ejecutar con el ID `100` en este despliegue. La inspección de rutas es una prueba parcial: **no se arrancó CT101 ni se probó el funcionamiento de Vaultwarden y Pi-hole restaurados**.

## Recuperar desde MEGA si se pierde el disco USB

Procedimiento propuesto, **todavía no ensayado de extremo a extremo tras pérdida de disco**:

1. Disponer de otro host o reinstalar Proxmox sobre un disco en buen estado.
2. Instalar Rclone con backend MEGA e importar/configurar `mega:` y `mega-crypt:` con **las mismas claves Crypt**.
3. Recuperar un `.tar.zst` en un almacenamiento de backups válido, con espacio suficiente:

   ```bash
   rclone ls mega-crypt:CT100
   rclone copyto \
     mega-crypt:CT100/vzdump-lxc-100-YYYY_MM_DD-HH_MM_SS.tar.zst \
     /ruta-segura/vzdump-lxc-100-YYYY_MM_DD-HH_MM_SS.tar.zst
   zstd -t /ruta-segura/vzdump-lxc-100-YYYY_MM_DD-HH_MM_SS.tar.zst
   ```

4. Restaurar en un ID libre y **con red desactivada** para validar los datos primero.
5. Ajustar IP, bridge, almacenamiento, acceso HTTPS y rutas antes de poner el servicio en producción.
6. Arrancar las aplicaciones y realizar pruebas funcionales controladas, evitando lanzar dos Pi-hole o Vaultwarden con los mismos datos/red simultáneamente.

No subir a GitHub el fichero real `rclone.conf` ni las claves de descifrado. Conservarlas fuera del servidor; sin ellas puede ser imposible recuperar los respaldos.

## Recuperación parcial de archivos

Para ficheros sueltos, una técnica de laboratorio es restaurar un contenedor temporal **sin arrancarlo**, inspeccionar los datos con `pct mount`, copiar únicamente los archivos deseados a un destino seguro y desmontarlo. Comprobar los permisos/propietarios UID remapeados del LXC no privilegiado antes de reutilizarlos.
