# 17. Seguridad y aislamiento de usuarios con Tailscale

## Objetivo

Compartir **solo Vikunja** con usuarios externos, conservando el acceso administrativo a Proxmox, Vaultwarden, Samba y el resto de servicios únicamente en dispositivos autorizados.

## Incidencia detectada

Una regla otorgaba, por error, `tcp:*` hacia CT100 a un colaborador. Esto abría **todos los puertos TCP del contenedor**, incluidos otros servicios publicados, aunque la intención era permitir únicamente Vikunja.

Se corrigió limitándola al puerto `tcp:3456`.

## Ejemplo de grant restringido

```json
{
  "src": ["amigo@example.invalid"],
  "dst": ["100.100.100.100"],
  "ip": ["tcp:3456"]
}
```

**Ejemplo, no configuración real.** No sustituir íntegramente el fichero ACL existente por este bloque. Las políticas de Tailscale son acumulativas: una regla adicional con más permisos puede ampliar el acceso.

## Pruebas recomendadas

- Comprobar acceso HTTP a Vikunja por la IP Tailscale de CT100.
- Confirmar bloqueo a Homepage, Uptime Kuma y los puertos administrativos.
- Confirmar que los dispositivos propios siguen accediendo a sus servicios.
- Si el usuario externo está conectado también a la LAN o a una ruta de subred, las ACL de Tailscale pueden no cubrir ese acceso; añadir firewall apropiado.
- No compartir credenciales de administrador con usuarios de Vikunja.

## Buenas prácticas de publicación

- No subir IPs de la tailnet, correos reales, claves API, IDs de Telegram, Push URLs ni contraseñas.
- Evitar publicar configuraciones reales de Vaultwarden, Pi-hole y el firewall sin redactarlas.
- Revisar permisos `600/700` de los archivos de secretos.
- Conservar la política ACL completa únicamente en un repositorio privado si incluye información sensible, o publicarla solo anonimizada.
