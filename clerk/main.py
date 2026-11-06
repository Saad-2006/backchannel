"""The Clerk. Wires Switch events into the rules and posts what the rules decide.

Run from the repo root:  python -m clerk.main
Set CLERK_GUARD=off to switch the leak scan off (only for the guard on/off test).
Set CLERK_PACE=8 to wait eight seconds before carrying an offer across, so a recording can keep up.
By default only amounts cross. Set CLERK_NOTES=on to let a scanned sentence travel with each offer.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from clerk import rules
from clerk.deal import ENVOY, ROUND_CAP, Deal
from clerk.switch import NAME, Switch, log

# Room names from Switch look like "Context Switch: agency-war-room". The side is read from the name.
SIDES = {"agency-war-room": "agency", "client-war-room": "client", "deal-table": "table"}
LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "clerk.jsonl"
GUARD = os.environ.get("CLERK_GUARD", "on").lower() != "off"
PACE = float(os.environ.get("CLERK_PACE", "0"))
NOTES = os.environ.get("CLERK_NOTES", "off").lower() == "on"

deal = Deal(guard=GUARD, notes=NOTES)
switch = Switch()


def record(room: str, command: str, verdict: str, reason: str) -> None:
    """One JSON line per decision: time, room, command, verdict, reason. Never a sealed value."""
    line = {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "room": room, "command": command,
            "decision": verdict, "reason": reason, "guard": "on" if GUARD else "off"}
    LOG_FILE.parent.mkdir(exist_ok=True)
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(line) + "\n")
    log(f"[{room}] {command}: {verdict} ({reason})")


def side_of(room_name: str) -> str | None:
    for key, side in SIDES.items():
        if key in room_name:
            return side
    return None


def room_for(side: str) -> str | None:
    for _ in range(2):
        for rid, name in switch.rooms.items():
            if side_of(name) == side:
                return rid
        switch.refresh_rooms()
    return None


def say(side: str, text: str) -> None:
    rid = room_for(side)
    if rid is None:
        log(f"no room for side {side!r}; wanted to say: {text[:80]!r}")
        return
    switch.post(rid, text)


def on_message(ev: dict) -> None:
    p = ev.get("payload") or {}
    room_name = switch.rooms.get(ev.get("room_id") or "") or ""
    body = p.get("body") or ""
    sender = p.get("sender_name") or p.get("sender") or "?"
    if sender == NAME or p.get("sender") == switch.agent_id:
        return  # never act on our own posts
    side = side_of(room_name)
    if side is None or side == "table":
        return  # Mattermost rooms, and nobody commands from the public table
    cmd = rules.parse_command(body)
    if cmd is None:
        return  # chatter
    is_person = sender not in ENVOY.values()
    before = len(deal.log)
    actions = deal.handle(side, sender, is_person, cmd)
    for command, verdict, reason in deal.log[before:]:
        record(room_name, command, verdict, reason)
    for a in actions:
        if PACE and a.to not in (side, "table") and a.text.startswith("@"):
            time.sleep(PACE)  # give the camera and the narrator time before the offer crosses
        say(a.to, a.text)


def on_event(event: str, ev: dict) -> None:
    if event == "message":
        on_message(ev)
    elif event in ("gap", "evicted", "room_released"):
        log(f"{event}: {ev}")


def main() -> None:
    switch.check_health()
    switch.load_or_register()
    log(f"Clerk up. Guard {'ON' if GUARD else 'OFF'}. Notes {'ON' if NOTES else 'OFF'}. Pace {PACE:g}s. Commands: {', '.join(rules.COMMANDS)}. Round cap {ROUND_CAP}. Log: {LOG_FILE}")
    switch.run(on_event)


if __name__ == "__main__":
    main()
