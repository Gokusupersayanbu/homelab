#!/usr/bin/env python3
"""Avisos de vencimiento privados de Vikunja a un Telegram por usuario.

Deps: Python stdlib. Profiles /etc/vikunja-alertas/perfiles/*.env.
Run as systemd User=vikunja-alertas, StateDirectory=vikunja-alertas.
"""
import argparse
import html
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Madrid")
PROFILES = Path("/etc/vikunja-alertas/perfiles")
STATES = Path("/var/lib/vikunja-alertas/perfiles")


def get_json(url, *, headers=None, data=None):
    with urlopen(Request(url, headers=headers or {}, data=data), timeout=20) as rsp:
        return json.load(rsp), rsp.headers


def config_file(p):
    result = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Formato incorrecto en {p.name}")
        name, value = line.split("=", 1)
        result[name.strip()] = value.strip()
    for required in ("VIKUNJA_USERNAME", "VIKUNJA_TOKEN", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
        if not result.get(required):
            raise ValueError(f"Falta {required} en {p.name}")
    if "," in result["TELEGRAM_CHAT_ID"]:
        raise ValueError(f"Cada perfil debe tener un solo Chat ID: {p.name}")
    result.setdefault("VIKUNJA_API_URL", "http://127.0.0.1:3457")
    result.setdefault("VIKUNJA_WEB_URL", "http://vikunja.example.invalid:3456")
    return result


def all_tasks(cfg):
    base = cfg["VIKUNJA_API_URL"].rstrip("/")
    headers = {"Authorization": f"Bearer {cfg['VIKUNJA_TOKEN']}", "Accept": "application/json"}
    # v2 primero y v1 como alternativa para instalaciones anteriores.
    for endpoint in ("/api/v2/tasks", "/api/v1/tasks", "/api/v1/tasks/all"):
        tasks = []
        for page in range(1, 1001):
            params = urlencode({"page": page, "per_page": 50, "filter": "done = false"})
            try:
                data, hdrs = get_json(f"{base}{endpoint}?{params}", headers=headers)
            except HTTPError as e:
                if e.code == 404 and page == 1:
                    break
                raise RuntimeError(f"Error Vikunja HTTP {e.code} en {endpoint} (revisa permisos del token)") from None
            except URLError as e:
                raise RuntimeError(f"No se pudo conectar con Vikunja: {e.reason}") from None
            if isinstance(data, list):
                items = data
                count = int(hdrs.get("x-pagination-total-pages", page))
            elif isinstance(data, dict) and isinstance(data.get("items"), list):
                items = data["items"]
                count = int(data.get("total_pages") or page)
            else:
                raise RuntimeError("Formato de respuesta de Vikunja desconocido")
            tasks.extend(items)
            if page >= count or not items:
                return tasks
        else:
            raise RuntimeError("Límite de páginas excedido")
    raise RuntimeError("Endpoint de tareas de Vikunja no disponible")


def fetch_assignees(task, cfg):
    """Consulta los responsables reales en Vikunja para cada tarea.

    No deduce "sin asignar" de un valor `null` ni de un array
    vacío en un listado abreviado: el endpoint específico debe confirmarlo.
    """
    task_id = task.get("id")
    if not isinstance(task_id, int) or isinstance(task_id, bool) or task_id < 1:
        raise RuntimeError("ID de tarea no válido al consultar responsables")
    base = cfg["VIKUNJA_API_URL"].rstrip("/")
    headers = {"Authorization": f"Bearer {cfg['VIKUNJA_TOKEN']}", "Accept": "application/json"}
    for endpoint in (f"/api/v2/tasks/{task_id}/assignees", f"/api/v1/tasks/{task_id}/assignees"):
        users = []
        for page in range(1, 1001):
            url = f"{base}{endpoint}?{urlencode({'page': page, 'per_page': 50})}"
            try:
                data, meta = get_json(url, headers=headers)
            except HTTPError as e:
                if e.code == 404 and page == 1:
                    break
                raise RuntimeError(f"No se pueden verificar responsables de tarea {task_id} (HTTP {e.code})") from None
            except URLError as e:
                raise RuntimeError(f"Error de red al verificar responsables de tarea {task_id}: {e.reason}") from None
            if isinstance(data, list):
                items = data
                pages = int(meta.get("x-pagination-total-pages", page))
            elif isinstance(data, dict) and isinstance(data.get("items"), list):
                items = data["items"]
                pages = int(data.get("total_pages") or page)
            else:
                raise RuntimeError(f"Formato de responsables desconocido en tarea {task_id}")
            users.extend(items)
            if page >= pages:
                return users
        else:
            raise RuntimeError(f"Demasiadas páginas de responsables para tarea {task_id}")
    raise RuntimeError(f"No se pudo consultar la lista real de responsables de tarea {task_id}")


def belongs_to_user(task, username, cfg):
    """Tarea asignada explícitamente al usuario o, si no tiene responsable, creada por él.

    Nunca deduce una tarea sin asignar a partir de un `assignees: null`.
    """
    assignees = fetch_assignees(task, cfg)
    expected = username.casefold()
    if assignees:
        if any(not isinstance(a, dict) or not isinstance(a.get("username"), str) for a in assignees):
            raise RuntimeError("Formato de responsables inesperado; no se envían alertas")
        return any(a["username"].casefold() == expected for a in assignees)
    creator = task.get("created_by")
    if not isinstance(creator, dict) or not isinstance(creator.get("username"), str):
        task_id = task.get("id")
        base = cfg["VIKUNJA_API_URL"].rstrip("/")
        headers = {"Authorization": f"Bearer {cfg['VIKUNJA_TOKEN']}", "Accept": "application/json"}
        for prefix in ("/api/v2/tasks/", "/api/v1/tasks/"):
            try:
                details, _ = get_json(f"{base}{prefix}{task_id}", headers=headers)
            except HTTPError as e:
                if e.code == 404:
                    continue
                raise RuntimeError(f"No se puede verificar creador de tarea {task_id} (HTTP {e.code})") from None
            except URLError as e:
                raise RuntimeError(f"Error de red al verificar creador de tarea {task_id}: {e.reason}") from None
            if isinstance(details, dict):
                creator = details.get("created_by")
            break
    if not isinstance(creator, dict) or not isinstance(creator.get("username"), str):
        raise RuntimeError("No se pudo verificar el creador de una tarea sin responsables")
    return creator["username"].casefold() == expected


def due_local(value):
    if not value or str(value).startswith("0001-"):
        return None
    try:
        stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return stamp.astimezone(TZ)


def alert_stage(days):
    if days == 3:
        return ("3dias", "📅 Entrega en 3 días")
    if days == 1:
        return ("1dia", "⏰ Entrega mañana")
    if days == 0:
        return ("hoy", "🚨 Entrega hoy")
    if days < 0:
        return ("atrasada", "⚠️ Tarea atrasada")
    return (None, None)


def send_telegram(cfg, message):
    token = cfg["TELEGRAM_BOT_TOKEN"]
    payload = json.dumps({
        "chat_id": cfg["TELEGRAM_CHAT_ID"], "text": message,
        "parse_mode": "HTML", "disable_web_page_preview": True,
    }).encode("utf-8")
    try:
        res, _ = get_json(f"https://api.telegram.org/bot{token}/sendMessage",
                          headers={"Content-Type": "application/json"}, data=payload)
    except HTTPError as e:
        raise RuntimeError(f"Telegram rechazó el envío HTTP {e.code} (bot/chat sin permisos o token incorrecto)") from None
    except URLError as e:
        raise RuntimeError(f"Error de conexión a Telegram: {e.reason}") from None
    if not res.get("ok"):
        raise RuntimeError("Telegram no confirmó el envío")


def state_path(alias):
    return STATES / f"{alias}.json"


def load_state(alias):
    p = state_path(alias)
    if not p.exists():
        return {}
    o = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(o, dict):
        raise RuntimeError(f"Estado inválido para {alias}")
    return o


def save_state(alias, state):
    STATES.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{alias}-", dir=STATES)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as h:
            json.dump(state, h, ensure_ascii=False, sort_keys=True)
            h.flush()
            os.fsync(h.fileno())
        os.chmod(name, 0o600)
        os.replace(name, state_path(alias))
    finally:
        if os.path.exists(name):
            os.unlink(name)


def run_profile(alias, cfg, args):
    if args.test:
        send_telegram(cfg, f"✅ <b>Vikunja</b>: alertas personales configuradas para {html.escape(cfg['VIKUNJA_USERNAME'])}.")
        print(f"[{alias}] Prueba de Telegram enviada")
        return
    tasks = all_tasks(cfg)
    now = datetime.now(TZ)
    # Nunca confirmar un mensaje ya enviado; el estado se guarda por destinatario.
    state = load_state(alias)
    n_user = n_sent = 0
    for task in tasks:
        if task.get("done") or not task.get("id"):
            continue
        if not belongs_to_user(task, cfg["VIKUNJA_USERNAME"], cfg):
            continue
        n_user += 1
        due = due_local(task.get("due_date"))
        if due is None:
            continue
        stage, heading = alert_stage((due.date() - now.date()).days)
        if stage is None:
            continue
        key = f"{task['id']}|{task.get('due_date')}|{stage}"
        if key in state:
            continue
        due_text = due.strftime("%d/%m/%Y a las %H:%M")
        body = (f"<b>{heading}</b>\n<b>Tarea:</b> {html.escape(str(task.get('title') or '(sin título)'))}"
                f"\n<b>Fecha límite:</b> {html.escape(due_text)}"
                f"\n<b>Vikunja:</b> {html.escape(cfg['VIKUNJA_WEB_URL'])}")
        if args.dry_run:
            print(f"[{alias}] [SIMULACIÓN] {heading} — tarea {task['id']}: {task.get('title')}")
        else:
            send_telegram(cfg, body)
            state[key] = now.isoformat()
            save_state(alias, state)
            n_sent += 1
            print(f"[{alias}] Enviado aviso {stage} de tarea {task['id']}")
    print(f"[{alias}] Tareas visibles: {len(tasks)}; propias: {n_user}; "
          + ("simulación finalizada" if args.dry_run else f"avisos nuevos: {n_sent}"))


def main():
    p = argparse.ArgumentParser()
    grp = p.add_mutually_exclusive_group()
    grp.add_argument("--test", action="store_true")
    grp.add_argument("--dry-run", action="store_true")
    p.add_argument("--usuario", help="Alias del perfil a procesar; por omisión todos")
    args = p.parse_args()
    if not PROFILES.exists():
        raise RuntimeError(f"No existe el directorio de perfiles {PROFILES}")
    files = sorted(PROFILES.glob("*.env"))
    if args.usuario:
        if not args.usuario.replace("-", "").replace("_", "").isalnum():
            raise RuntimeError("Alias de usuario inválido")
        files = [f for f in files if f.stem == args.usuario]
    if not files:
        raise RuntimeError("No hay perfiles que procesar")
    errors = 0
    for f in files:
        try:
            run_profile(f.stem, config_file(f), args)
        except (RuntimeError, ValueError, OSError, json.JSONDecodeError) as e:
            print(f"[{f.stem}] ERROR: {e}", file=sys.stderr)
            errors += 1
    if errors:
        raise RuntimeError(f"{errors} perfil(es) fallaron")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
