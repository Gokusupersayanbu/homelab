# 05 · Backups locales en la eMMC

[Volver al índice](../README.md)

## Objetivo

Guardar backups completos del LXC **CT100** en un **segundo dispositivo físico** dentro del host, sin ocupar el PC de sobremesa.

## 1. Identificación de los dispositivos

```bash
lsblk -o NAME,SIZE,TYPE,TRAN,MODEL,MOUNTPOINTS
efibootmgr -v
lsblk -f /dev/mmcblk0
wipefs -n /dev/mmcblk0
lsblk -d -o NAME,SIZE,RO,TRAN,MODEL /dev/mmcblk0
```

Verificación realizada: `/dev/sda` es el Toshiba USB de 1 TB usado por Proxmox; `/dev/mmcblk0` era el eMMC interno aparentemente vacío y con `RO=0`. **Se obtuvo autorización explícita del propietario antes del particionado y formato.**

> **¡Peligro!** Los siguientes comandos de preparación **borran datos**. Son el registro del procedimiento realizado, **no comandos para ejecutar sin volver a identificar discos y respaldar sus datos**. Nunca confundir `/dev/mmcblk0` con `/dev/sda`.

## 2. Preparación inicial (destructiva)

`parted` no estaba instalado y se instaló con `apt update && apt install -y parted`. Se creó la tabla GPT y una partición EXT4:

```bash
parted -s -a optimal /dev/mmcblk0 -- mklabel gpt mkpart primary ext4 1MiB 100%
mkfs.ext4 -L pve-backups /dev/mmcblk0p1
lsblk -f /dev/mmcblk0
```

Se montó la partición:

```bash
mkdir -p /mnt/backups
# Sustituye por el UUID auténtico obtenido con blkid, nunca copies un UUID ajeno
blkid -p /dev/mmcblk0p1
mount /dev/mmcblk0p1 /mnt/backups
df -h /mnt/backups
```

En `/etc/fstab` se añadió una entrada con `defaults,nofail,x-systemd.device-timeout=10s 0 2`. Ejemplo sin UUID real: [`fstab-backups.example`](../ejemplos/proxmox/fstab-backups.example).

```bash
cp /etc/fstab /etc/fstab.bak
nano /etc/fstab
findmnt --verify --verbose
systemctl daemon-reload
umount /mnt/backups
mount /mnt/backups
findmnt /mnt/backups
```

`nofail` evita que el arranque quede bloqueado por la ausencia del eMMC; **no sustituye** a la verificación de montaje del almacenamiento antes de escribir backups.

## 3. Registrar el almacenamiento en Proxmox

```bash
pvesm add dir backups-emmc \
  --path /mnt/backups \
  --content backup \
  --is_mountpoint yes \
  --prune-backups 'keep-last=3'
pvesm status
```

`--is_mountpoint yes` evita utilizar accidentalmente el directorio si el dispositivo no está realmente montado.

## 4. Primer backup y job automático

```bash
vzdump 100 --storage backups-emmc --mode stop --compress zstd
```

El backup manual del **15/10/2026 01:56:25** terminó con éxito a las **02:03:13**, con tamaño **2.039.586.174 bytes**. El modo `stop` interrumpió CT100 durante unos **6 min 48 s**. Esto afectó temporalmente al DNS Pi-hole y al acceso a los otros servicios.

Trabajo configurado en **Datacenter → Backup**, e inspeccionado con:

```bash
pvesh get /cluster/backup --output-format json-pretty
```

Resumen confirmado:

```json
{
  "compress": "zstd",
  "enabled": 1,
  "mode": "stop",
  "node": "homelab",
  "prune-backups": { "keep-last": "3" },
  "schedule": "04:00",
  "storage": "backups-emmc",
  "vmid": "100"
}
```

ID de job observado: `backup-ca4d4a83-afd9`. El hook concreto se enlazó a esta tarea con `pvesh set /cluster/backup/... --script ...`.

La primera ejecución automática real comenzó a las **04:00:26**, creó `vzdump-lxc-100-2026_10_15-04_00_26.tar.zst` y el archivo quedó almacenado en la eMMC. Su tamaño fue **2.040.816.868 bytes**.

## 5. Verificación

```bash
pct status 100
pvesm list backups-emmc --content backup
zstd -t /mnt/backups/dump/vzdump-lxc-100-YYYY_MM_DD-HH_MM_SS.tar.zst
```

El test ZSTD comprueba legibilidad e integridad del flujo comprimido, **pero no es equivalente** a arrancar y probar todos los servicios restaurados. Ver [restauración](08-restauracion.md).

## Consideraciones

- La eMMC y el USB están dentro del mismo servidor. Se protege frente a algunos fallos de disco, **no** frente a robo, incendio o avería general del equipo.
- Para cubrir ese riesgo se mantiene otra copia cifrada en MEGA.
- La retención `keep-last=3` es una política aplicada por el mecanismo de poda; no implica que siempre existan tres backups válidos.
