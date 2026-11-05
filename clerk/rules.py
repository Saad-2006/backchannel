"""Pure rules for the Clerk. No I/O, no Switch, no AI.

Every function here takes plain values and returns a decision, so the whole
file can be tested without a server. A judge should be able to read it in one pass.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# The Clerk acts only on a message whose first word is one of these, in capitals.
COMMANDS = ("SEAL", "OFFER", "APPROVE", "REJECT", "SIGN")
WITH_AMOUNT = ("SEAL", "OFFER")

# An amount is digits, optionally with a leading $ and thousands commas: 7500, $7,500.
_AMOUNT = re.compile(r"^\$?(\d{1,3}(?:,\d{3})+|\d+)$")

NOTE_MAX = 280


@dataclass(frozen=True)
class Command:
    word: str
    amount: int | None = None
    note: str = ""
    error: str | None = None


def parse_command(text: str) -> Command | None:
    """Read the first line of a message.

    Returns None for ordinary chatter (no command word), a Command for a well-formed
    command, and a Command with .error set for a command the Clerk could not read.
    Only the first line is ever looked at; nothing else in the message travels anywhere.
    """
    stripped = text.strip()
    if not stripped:
        return None
    first = stripped.splitlines()[0].strip()
    parts = first.split()
    word = parts[0]
    if word not in COMMANDS:
        return None
    if word in WITH_AMOUNT:
        if len(parts) < 2:
            return Command(word, error=f"{word} needs an amount, for example `{word} 7500`.")
        m = _AMOUNT.match(parts[1])
        if not m:
            return Command(word, error=f"I couldn't read {parts[1]!r} as an amount. Use digits, like `7500` or `$7,500`.")
        amount = int(m.group(1).replace(",", ""))
        if amount <= 0:
            return Command(word, error="The amount has to be more than zero.")
        return Command(word, amount, clean_note(" ".join(parts[2:])))
    return Command(word)


def clean_note(note: str) -> str:
    """Make a note safe to carry into the other room.

    Mentions are neutralised so a note can never address an agent or person on the other
    side, Switch's `!` commands are defused, and the note is capped at NOTE_MAX characters.
    """
    note = " ".join(note.split())
    note = note.replace("@", "at ")
    note = note.lstrip("!")
    if len(note) > NOTE_MAX:
        note = note[: NOTE_MAX - 1].rstrip() + "…"
    return note


def money(amount: int) -> str:
    return f"${amount:,}"


# ---- leak scan ------------------------------------------------------------------------
# The only number allowed in an offer is the offer. The sentence may carry no other digits,
# no number words, and none of the words people use when they talk about their limit.
_DIGITS = re.compile(r"\d")
_NUMBER_WORDS = {
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
    "nineteen", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
    "hundred", "thousand", "grand", "k",
}
_LIMIT_WORDS = {
    "floor", "ceiling", "minimum", "maximum", "min", "max", "budget", "limit", "lowest",
    "highest", "bottom", "cap", "under", "below", "above", "over", "beneath", "exceed",
    "mandate", "authorised", "authorized", "walk",
}
_WORD = re.compile(r"[a-z]+")


def scan_for_leaks(sentence: str) -> list[str]:
    """Return the reasons a sentence may not travel. An empty list means it is clean."""
    reasons: list[str] = []
    if _DIGITS.search(sentence):
        reasons.append("it carries a second number")
    words = set(_WORD.findall(sentence.lower()))
    hit = sorted(words & _NUMBER_WORDS)
    if hit:
        reasons.append("it spells out a number (" + ", ".join(hit) + ")")
    hit = sorted(words & _LIMIT_WORDS)
    if hit:
        reasons.append("it talks about a limit (" + ", ".join(hit) + ")")
    return reasons


# ---- limits and overlap --------------------------------------------------------------
def check_limit(side: str, amount: int, sealed: int) -> str:
    """'ok' when the offer stays inside the side's own sealed limit, else 'past_limit'.

    The agency sealed a floor, so an offer below it is past the limit.
    The client sealed a ceiling, so an offer above it is past the limit.
    """
    if side == "agency":
        return "past_limit" if amount < sealed else "ok"
    if side == "client":
        return "past_limit" if amount > sealed else "ok"
    raise ValueError(f"unknown side {side!r}")


def overlap(floor: int, ceiling: int) -> bool:
    """One bit: can a deal exist at all? Never reveals either number."""
    return floor <= ceiling
