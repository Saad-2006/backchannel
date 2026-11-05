"""The only file that talks HTTP to Switch: register, stream, beat, list_rooms, post.

Standard library only. It never prints a secret: the registration token is read from the
Console env file and used once, and the agent key lives in .clerk-creds.json (mode 600).
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections.abc import Callable
from pathlib import Path

BASE = os.environ.get("SWITCH_BASE", "http://127.0.0.1:54083")
ENV_FILE = Path(os.environ.get(
    "SWITCH_ENV_FILE",
    Path.home() / "Library/Application Support/switchdash/local-switch-server/native/run/switch-core.env",
))
CREDS = Path(__file__).with_name(".clerk-creds.json")
NAME = "clerk"
CLIENT = "backchannel-clerk"
VERSION = "0.1.0"


def log(*parts) -> None:
    print(time.strftime("%H:%M:%S"), *parts, flush=True)


class Switch:
    """One agent's connection to a Switch server."""

    def __init__(self) -> None:
        self.conn = str(uuid.uuid4())
        self.cursor: int | None = None
        self.rooms: dict[str, str] = {}  # room_id -> name
        self.creds = {"id": None, "api_key": None}
        self._beating = False

    # ---- plumbing -------------------------------------------------------------------
    def _call(self, method: str, path: str, token: str, body=None, timeout: int = 15):
        data = None if body is None else json.dumps(body).encode()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Switch-Connection-Id": self.conn,
        }
        req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else None

    def _api(self, method: str, path: str, body=None, timeout: int = 15):
        return self._call(method, path, self.creds["api_key"], body, timeout)

    @property
    def agent_id(self) -> str:
        return self.creds["id"]

    # ---- health and registration ----------------------------------------------------
    def check_health(self) -> None:
        try:
            self._call("GET", "/health", "none", timeout=5)
        except Exception as e:  # noqa: BLE001
            sys.exit(f"Switch server not reachable at {BASE}: {e}")

    @staticmethod
    def _registration_token() -> str:
        try:
            lines = ENV_FILE.read_text().splitlines()
        except OSError:
            sys.exit(f"Console env file not found at {ENV_FILE}. Set SWITCH_ENV_FILE or register by hand.")
        for line in lines:
            if line.startswith("AGENT_REGISTRATION_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
        sys.exit("No AGENT_REGISTRATION_TOKEN in the Console env file.")

    def load_or_register(self) -> None:
        if CREDS.exists():
            self.creds = json.loads(CREDS.read_text())
            log(f"Using saved agent '{NAME}' (id {self.creds['id']}).")
            return
        body = {
            "name": NAME,
            "display_name": "Clerk",
            "description": "Backchannel Clerk. Plain Python, no AI: checks offers for leaks and relays clean ones.",
            "connector_type": "Python (no AI)",
            "integration_profile": {
                "connection_model": "always_on",
                "message_exchange": True,
                "pre_invocation_mediation": [],
                "post_invocation_mediation": [],
                "event_reporting": [],
            },
        }
        try:
            out = self._call("POST", "/agents", self._registration_token(), body)
        except urllib.error.HTTPError as e:
            sys.exit(f"Registration failed: HTTP {e.code} {e.read().decode(errors='replace')[:600]}")
        if not isinstance(out, dict) or "id" not in out or "api_key" not in out:
            sys.exit("Registration answered with unexpected fields.")
        self.creds = {"id": out["id"], "api_key": out["api_key"]}
        CREDS.write_text(json.dumps(self.creds))
        CREDS.chmod(0o600)
        log(f"Registered agent '{NAME}' (id {self.creds['id']}). Key saved to {CREDS.name}; not printed.")

    # ---- rooms and posting ----------------------------------------------------------
    def refresh_rooms(self) -> dict[str, str]:
        """Return {room_id: name} for every room the agent is in (the stream's own list is empty)."""
        try:
            out = self._api("POST", f"/agents/{self.agent_id}/ops/list_rooms", {})
        except Exception as e:  # noqa: BLE001
            log(f"list_rooms failed: {e}")
            return self.rooms
        res = (out or {}).get("result")
        items = res if isinstance(res, list) else (res.get("rooms") if isinstance(res, dict) else None) or []
        rooms = {}
        for it in items:
            if isinstance(it, dict) and not it.get("archived"):
                rid = it.get("room_id") or it.get("id")
                name = it.get("name") or it.get("display_name") or ""
                if rid:
                    rooms[rid] = name
        self.rooms = rooms
        return rooms

    def post(self, room_id: str, content: str) -> bool:
        try:
            self._api("POST", f"/agents/{self.agent_id}/message", {"room_id": room_id, "content": content})
            return True
        except urllib.error.HTTPError as e:
            log(f"post into {self.rooms.get(room_id, room_id)} failed: HTTP {e.code} {e.read().decode(errors='replace')[:300]}")
            return False

    # ---- heartbeat and stream -------------------------------------------------------
    def _heartbeat(self) -> None:
        last_err = None
        while True:
            body = {"connection_id": self.conn}
            if self.cursor is not None:
                body["cursor"] = self.cursor
            try:
                self._api("POST", f"/agents/{self.agent_id}/connection/beat", body, timeout=5)
                if last_err:
                    log("heartbeat ok again")
                last_err = None
            except urllib.error.HTTPError as e:
                if last_err != e.code:
                    log(f"heartbeat HTTP {e.code} (the stream loop will reopen)")
                last_err = e.code
            except Exception as e:  # noqa: BLE001
                if last_err != "x":
                    log(f"heartbeat error: {e}")
                last_err = "x"
            time.sleep(2)

    def _stream_once(self, on_event: Callable[[str, dict], None]) -> None:
        q = urllib.parse.urlencode({
            "connection_id": self.conn, "scope": "all", "filter": "all", "start_from": "head",
            "client": CLIENT, "client_version": VERSION,
        })
        req = urllib.request.Request(f"{BASE}/agents/{self.agent_id}/events?{q}", headers={
            "Authorization": f"Bearer {self.creds['api_key']}", "Accept": "text/event-stream"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            event, data = None, []
            for raw in resp:
                line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
                if line == "":
                    if event or data:
                        self._dispatch(event, "\n".join(data), on_event)
                    event, data = None, []
                elif line.startswith(":"):
                    continue
                elif line.startswith("event:"):
                    event = line[6:].strip()
                elif line.startswith("data:"):
                    data.append(line[5:].lstrip())

    def _dispatch(self, event: str | None, data: str, on_event) -> None:
        try:
            ev = json.loads(data) if data else {}
        except json.JSONDecodeError:
            log(f"unparsed {event} frame")
            return
        if isinstance(ev, dict) and isinstance(ev.get("sequence"), int):
            self.cursor = ev["sequence"]
        if event == "connection_state":
            if ev.get("cursor") is not None:
                self.cursor = ev["cursor"]
            if not self._beating:
                threading.Thread(target=self._heartbeat, daemon=True).start()
                self._beating = True
            self.refresh_rooms()
            log(f"Connected. In {len(self.rooms)} room(s): {sorted(self.rooms.values())}")
        elif event == "subscription_changed":
            self.refresh_rooms()
            log(f"Rooms changed ({ev.get('reason')}): {sorted(self.rooms.values())}")
        on_event(event or "", ev)

    def run(self, on_event: Callable[[str, dict], None]) -> None:
        """Stream forever, reopening on errors. on_event(event_name, event_dict) is called for every frame."""
        while True:
            try:
                self._stream_once(on_event)
                log("stream closed; reopening")
            except urllib.error.HTTPError as e:
                log(f"stream HTTP {e.code} {e.read().decode(errors='replace')[:300]}")
            except Exception as e:  # noqa: BLE001
                log(f"stream error: {e}; reopening")
            time.sleep(3)
