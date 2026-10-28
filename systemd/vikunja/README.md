# Unidades de Vikunja

Este repositorio no incluye el archivo `service` completo del servidor porque puede contener parámetros específicos de usuario, seguridad y directorios de la instalación. Documentamos únicamente la anulación aplicada:

```ini
[Service]
EnvironmentFile=
ExecStart=
ExecStart=/usr/bin/python3 /opt/vikunja-alertas/avisos_multi.py
```

El script debe ejecutarse con los privilegios y permisos definidos en la unidad real. Para verificar la instalación:

```bash
systemctl show vikunja-alertas.service -p ExecStart --no-pager
systemctl list-timers vikunja-alertas.timer
```

El calendario configurado en CT100 es horario. No incluir perfiles `.env`, claves ni registros personales en GitHub.
