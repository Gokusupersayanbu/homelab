# 14. Vikunja — tareas, usuarios y notificaciones de Telegram

## Objetivo

Usar Vikunja como gestor de tareas compartido en CT100 y enviar alertas privadas a Telegram. **Un bot y un token API por usuario.** La notificación de una tarea no debe revelarse a destinatarios ajenos.

## Arquitectura

```text
CT100 (Proxmox LXC)
 ├─ Docker: Vikunja (puerto local publicado)
 ├─ /opt/vikunja-alertas/avisos_multi.py
 ├─ /etc/vikunja-alertas/perfiles/<alias>.env  [PRIVADO]
 ├─ /var/lib/vikunja-alertas/perfiles/<alias>.json [estado]
 └─ vikunja-alertas.timer -> vikunja-alertas.service
                         -> API de Vikunja -> Bot personal de Telegram
```

## Lógica de asignación

- Se consulta la lista de tareas pendientes con el token de cada cuenta.
- Para **cada tarea**, se consulta el endpoint de responsables. Es importante: la API puede entregar `assignees: null` en el listado resumido.
- Si la tarea tiene responsables, solo avisa al usuario asignado.
- Si no tiene responsables, solo se considera propia del usuario que creó la tarea.
- Si no se puede confirmar el creador o la lista de responsables, **se omite la alerta** para proteger la privacidad.
- Avisos al faltar **3 días, 1 día, el mismo día y cuando la tarea se atrasa**. Se guarda el historial para evitar duplicados.

## Calendario

La revisión se ejecuta cada hora en el CT100, con una unidad systemd de ejecución puntual. Ejemplo en `systemd/vikunja/`; una unidad `oneshot` finalizada se muestra `inactive` entre ejecuciones: eso no significa error.

## Archivos relevantes

| Ruta en el servidor | Uso |
| --- | --- |
| `/opt/vikunja-alertas/avisos_multi.py` | Programa de lectura y avisos |
| `/etc/vikunja-alertas/perfiles/*.env` | Datos privados de cada perfil |
| `/var/lib/vikunja-alertas/perfiles/*.json` | Control de avisos ya enviados |
| `/etc/systemd/system/vikunja-alertas.service` | Servicio de ejecución |
| `/etc/systemd/system/vikunja-alertas.timer` | Programación horaria |

## Comprobaciones y diagnóstico

```bash
# Ejecutar desde CT100
runuser -u vikunja-alertas -- python3 /opt/vikunja-alertas/avisos_multi.py --dry-run
systemctl show vikunja-alertas.service -p ExecStart --no-pager
systemctl list-timers vikunja-alertas.timer
journalctl -u vikunja-alertas.service -n 50 --no-pager
```

La simulación verificada mostraba cuatro perfiles y filtrado individual (tres perfiles con tareas propias y uno sin tareas propias). No almacenar los perfiles reales en GitHub.

## Incidencias resueltas

1. El sistema original enviaba tareas a varios Chat ID; se sustituyó por **perfiles independientes**.
2. El programa inicial fallaba porque esperaba `assignees` como lista en el listado. La solución consulta `/api/v2/tasks/<id>/assignees`, que entrega `items` y paginación.
3. Se corrigió una sobrescritura accidental de `avisos_multi.py` por un instalador anterior.
4. Un HTTP `401` en consultas de tareas exige revisar el token y sus permisos; un `401` en `/user` no demuestra por sí solo que el token de lectura de tareas sea inválido.

## Seguridad

- Cada cuenta debe generar su propio token API, con permisos mínimos de lectura.
- Confirmar la propiedad de cada token y el Chat ID antes de activar los avisos reales.
- Permisos recomendados: `0600` en archivos privados, acceso solo al usuario del servicio.
- Evitar incluir enlaces internos accesibles desde Internet en los mensajes si no están protegidos.
- **No publicar** tokens, Chat ID, direcciones Tailscale particulares o nombres de usuarios reales.

## Archivo de ejemplo

Ver `ejemplos/vikunja-perfil.env.example`. El archivo contiene marcadores, no datos válidos.
