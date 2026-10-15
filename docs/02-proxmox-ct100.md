# 02 · Proxmox y CT100

[Volver al índice](../README.md)

## Configuración verificada

Salida relevante de `pct config 100`:

```ini
arch: amd64
cores: 1
dev0: /dev/net/tun
features: nesting=1
hostname: CT100
memory: 2048
nameserver: 8.8.8.8
net0: name=eth0,bridge=vmbr0,firewall=1,gw=192.168.0.1,ip=192.168.0.12/24,type=veth
onboot: 1
ostype: fedora
rootfs: local-lvm:vm-100-disk-0,size=8G
swap: 2048
unprivileged: 1
```

Se omitió la MAC de red del ejemplo. En el host el disco LXC es `/dev/mapper/pve-vm--100--disk--0`.

El uso observado del sistema de archivos raíz de CT100 fue **4,5 GiB de 7,8 GiB (61 %)**. Quedaban unos **3 GiB libres**: vigilar porque la instalación de más contenedores e imágenes Docker podría llenarlo.

Comandos de inventario:

```bash
pct config 100
pct status 100
pct exec 100 -- df -h / /var/lib/docker
pct exec 100 -- docker ps
lsblk -o NAME,SIZE,TYPE,TRAN,MODEL,MOUNTPOINTS
pvesm status
```

## Particularidades

- LXC **sin privilegios**, con `nesting=1`, lo que permite usar Docker dentro de CT100.
- Pi-hole, Vaultwarden, Uptime Kuma, Homepage y Caddy son contenedores Docker dentro del LXC.
- `pct config 100` no mostró montajes `mp0`, `mp1`, etc. En el caso examinado, las rutas persistentes principales estaban dentro del `rootfs` respaldado.
- Docker usa `/var/lib/docker` como `DockerRootDir`.
- La diferencia `du -sh /var/lib/docker` (~2,5 GiB) frente a `du -xsh` (~2 MiB) se explicó por montajes `overlay` de Docker. **No implica pérdida de datos** en el backup.

## Buenas prácticas

- Reservar suficiente espacio antes de ampliar el disco de CT100.
- Evitar actualizar Proxmox, el kernel y Docker simultáneamente sin un backup verificado.
- Mantener los servicios DNS disponibles durante intervenciones: el backup en modo `stop` interrumpe CT100.
- No interpretar automáticamente los avisos de *load average* de Pi-hole como saturación de CPU: comprobar las métricas reales.
