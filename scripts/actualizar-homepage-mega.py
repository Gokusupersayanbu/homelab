#!/usr/bin/env python3
"""Actualiza el JSON consumido por Homepage sin publicar credenciales."""
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime

resultado = subprocess.check_output(
    [
        "rclone", "--config", "/root/.config/rclone/rclone.conf",
        "lsjson", "mega-crypt:CT100", "--files-only"
    ],
    text=True,
)
archivos = json.loads(resultado)
patron = re.compile(r"vzdump-lxc-100-(\d{4}_\d{2}_\d{2}-\d{2}_\d{2}_\d{2})\.tar\.zst")
copias = []
for archivo in archivos:
    encontrado = patron.fullmatch(archivo["Name"])
    if encontrado:
        fecha = datetime.strptime(encontrado.group(1), "%Y_%m_%d-%H_%M_%S")
        copias.append((fecha, archivo))

if not copias:
    raise SystemExit("ERROR: no hay backups de CT100 en MEGA")

copias.sort(key=lambda x: x[0], reverse=True)
fecha, ultimo = copias[0]
resumen = {
    "copias": len(copias),
    "espacio_bytes": sum(a["Size"] for _, a in copias),
    "ultimo_backup": fecha.strftime("%d/%m/%Y %H:%M"),
    "ultima_subida": datetime.fromisoformat(
        ultimo["ModTime"].replace("Z", "+00:00")
    ).strftime("%d/%m/%Y %H:%M"),
}

with tempfile.NamedTemporaryFile(
    mode="w", encoding="utf-8", suffix=".json", delete=False
) as archivo:
    json.dump(resumen, archivo, ensure_ascii=False, indent=2)
    temporal = archivo.name

try:
    subprocess.run(
        [
            "pct", "push", "100", temporal,
            "/root/homepage/backup-status/backup.json.new", "--perms", "0644"
        ],
        check=True,
    )
    subprocess.run(
        [
            "pct", "exec", "100", "--", "mv", "-f",
            "/root/homepage/backup-status/backup.json.new",
            "/root/homepage/backup-status/backup.json"
        ],
        check=True,
    )
finally:
    os.unlink(temporal)

print("HOMEPAGE: Estadisticas de MEGA actualizadas")
print(json.dumps(resumen, ensure_ascii=False, indent=2))
