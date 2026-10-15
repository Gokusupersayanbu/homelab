# 06 · Backups cifrados en MEGA con Rclone

[Volver al índice](../README.md)

## Por qué MEGA

El PC de sobremesa estaba casi sin espacio y se disponía de **19 GB libres en MEGA**. Se eligió una segunda copia fuera del servidor, cifrada independientemente con **Rclone Crypt**.

Cada backup ZSTD observado ocupa unos **2,04 GB**. Tres copias de tamaño parecido ocuparían unos **6,1 GB** (más sobrecarga menor de cifrado). Hay que vigilar el crecimiento y la papelera de MEGA.

## Instalación

En el host `homelab` Debian 13 se probó `apt install rclone`, pero `rclone v1.60.1-DEV` no ofrecía `mega` entre sus backends. Se reemplazó por la distribución oficial de Rclone y se verificó:

```bash
rclone version
rclone help backends | grep -i mega
```

No se publica una versión exacta de la distribución oficial porque no quedó registrada en la conversación. Fuente: [Rclone MEGA](https://rclone.org/mega/).

## Remotos

Se crearon mediante `rclone config`:

- `mega:` → cuenta MEGA autenticada.
- `mega-crypt:` → tipo **crypt**, `remote=mega:Homelab-Backups-Cifrados`, cifrado estándar de nombres y cifrado de directorios activado.

Las claves de Crypt (`password` y `password2`) se generaron y **se deben guardar fuera del host**, junto con los datos de recuperación de MEGA. No se incluyen en este repositorio. La ofuscación de `rclone.conf` **no es una protección fuerte de secretos**.

La ruta de configuración utilizada por root fue:

```text
/root/.config/rclone/rclone.conf
```

Comprobaciones realizadas:

```bash
rclone listremotes
rclone lsd mega:
rclone ls mega-crypt:CT100
rclone lsjson mega-crypt:CT100 --files-only
```

Primero se subió y recuperó un fichero de prueba pequeño. Después se subió una copia real:

```bash
rclone copyto /mnt/backups/dump/vzdump-lxc-100-YYYY_MM_DD-HH_MM_SS.tar.zst \
  mega-crypt:CT100/vzdump-lxc-100-YYYY_MM_DD-HH_MM_SS.tar.zst -P
```

La **primera copia remota** se probó descargándola y descomprimiéndola en streaming:

```bash
bash -o pipefail -c \
  'rclone cat "mega-crypt:CT100/vzdump-lxc-100-YYYY_MM_DD-HH_MM_SS.tar.zst" | zstd -t -'
```

Esto confirma que la copia remota verificada podía descifrarse y descomprimirse. No requiere crear otro fichero del tamaño del backup en el host.

## Automatización real

La tarea `backup-ca4d4a83-afd9` incluye un hook:

```bash
pvesh set /cluster/backup/backup-ca4d4a83-afd9 \
  --script /usr/local/sbin/vzdump-mega-hook.sh
```

El script de hook escucha `backup-end` de CT100, comprueba `STOREID=backups-emmc` y que `TARGET` es un archivo `.tar.zst`, y lanza **systemd-run** como tarea independiente. Esto permite finalizar el backup local sin esperar a la subida en MEGA. Fuente: [hook oficial Proxmox](https://github.com/proxmox/pve-manager/blob/master/vzdump-hook-script.pl).

Scripts de ejemplo, **sin credenciales**:

- [`backup-mega.sh`](../scripts/backup-mega.sh)
- [`vzdump-mega-hook.sh`](../scripts/vzdump-mega-hook.sh)
- [`actualizar-homepage-mega.py`](../scripts/actualizar-homepage-mega.py)

Orden del script de subida, confirmado en prueba manual:

1. Comprueba que existe el backup en la eMMC y que `/mnt/backups` está montado.
2. `rclone copyto` de CT100 hacia `mega-crypt:CT100`.
3. Comprueba el **tamaño** del archivo remoto.
4. Lista backups con nombres reconocidos, conserva tres y elimina los antiguos según fecha en nombre.
5. Genera el resumen JSON de Homepage por `pct push`.
6. Envía el heartbeat al monitor Push de Uptime Kuma.

Las confirmaciones de **tamaño igual** y **subida completa** no sustituyen un test de lectura o restauración remota periódico. La prueba de `zstd -t` remota se hizo explícitamente en una copia anterior.

## Ejecución real de las 04:00

Fragmento registrado el 15/10/2026:

```text
04:07:37  Subiendo backup cifrado: vzdump-lxc-100-2026_10_15-04_00_26.tar.zst
04:15:52  Subida comprobada correctamente
04:15:53  BACKUP MEGA COMPLETADO
04:15:53  systemd: Deactivated successfully
```

El proceso registró pico de memoria de **1,1 GiB** en el host Proxmox y **52,037 s** de tiempo CPU acumulado (no duración). Este último dato es un buen candidato para optimización si se observa saturación.

## Retención y papelera de MEGA

La limpieza del script usa `rclone deletefile`, que por defecto puede enviar el contenido eliminado a la **papelera de MEGA**. Por eso, el uso real de espacio puede crecer incluso con `keep-last=3`. **No se ha activado eliminación permanente** en el sistema desplegado.

Rclone ofrece la opción `--mega-hard-delete`, pero **eliminar permanentemente es irreversible**. Antes de activarla, estudiar una prueba controlada y una política de retención segura. Referencia: [opciones de MEGA en Rclone](https://rclone.org/mega/).

## Recuperación

Leer [08 · Restauración](08-restauracion.md). Nunca guardar la única copia de la clave Crypt dentro de Vaultwarden respaldado por esa misma clave.
