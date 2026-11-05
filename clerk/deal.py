"""The deal state machine. Pure: it takes commands and returns what to post. No I/O.

Sealed limits live only inside a Deal object in the Clerk's memory. They are never returned
in an Action and never written anywhere.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from clerk import rules
from clerk.rules import Command

SIDES = ("agency", "client")
OTHER = {"agency": "client", "client": "agency"}
LIMIT_NAME = {"agency": "floor", "client": "ceiling"}
ENVOY = {"agency": "agency-envoy", "client": "client-envoy"}
ROUND_CAP = 6
REPLY_HINT = "Reply in this room with one line: OFFER <amount> <one short sentence>"


@dataclass(frozen=True)
class Action:
    to: str      # "agency", "client" or "table"
    text: str


@dataclass
class Deal:
    guard: bool = True                         # False only for the guard-off leak test
    sealed: dict[str, int] = field(default_factory=dict)
    rounds: int = 0
    last_offer: dict[str, int] = field(default_factory=dict)
    pending: dict[str, Command] = field(default_factory=dict)   # side -> offer awaiting a person
    agreed: int | None = None
    signed: dict[str, str] = field(default_factory=dict)        # side -> who signed
    closed: bool = False
    log: list[tuple[str, str, str]] = field(default_factory=list)  # (command, decision, reason)

    # ---- entry point -------------------------------------------------------------------
    def handle(self, side: str, sender: str, is_person: bool, cmd: Command) -> list[Action]:
        if cmd.error:
            return self._note(cmd.word, "bounced", "could not parse", [Action(side, f"Clerk: {cmd.error}")])
        if self.closed:
            return self._note(cmd.word, "ignored", "deal closed", [Action(side, "Clerk: this deal is closed and signed.")])
        if cmd.word == "OFFER":
            return self._offer(side, cmd)
        if not is_person:
            return self._note(cmd.word, "refused", "only a person may do this",
                              [Action(side, f"Clerk: only a person may {cmd.word}. {ENVOY[side]} cannot.")])
        if cmd.word == "SEAL":
            return self._seal(side, cmd)
        if cmd.word == "APPROVE":
            return self._approve(side)
        if cmd.word == "REJECT":
            return self._reject(side)
        if cmd.word == "SIGN":
            return self._sign(side, sender)
        return []

    # ---- commands ----------------------------------------------------------------------
    def _seal(self, side: str, cmd: Command) -> list[Action]:
        self.sealed[side] = cmd.amount
        out = [Action(side, f"Clerk: sealed. I hold the {side}'s {LIMIT_NAME[side]} in memory only. "
                            "It is never written down or shown.")]
        if len(self.sealed) == 2:
            possible = rules.overlap(self.sealed["agency"], self.sealed["client"])
            verdict = "A deal is possible." if possible else "No deal is possible at these limits."
            out.append(Action("table", f"Both sides have sealed. {verdict} No numbers shown."))
        return self._note("SEAL", "sealed", f"{side} {LIMIT_NAME[side]} held in memory", out)

    def _offer(self, side: str, cmd: Command) -> list[Action]:
        if side not in self.sealed:
            return self._note("OFFER", "held", "side has not sealed",
                              [Action(side, f"Clerk: a person must SEAL the {side}'s {LIMIT_NAME[side]} before any offer.")])
        if self.agreed is not None:
            return self._note("OFFER", "held", "a price is agreed",
                              [Action(side, f"Clerk: a price is already agreed at {rules.money(self.agreed)}. "
                                            "A person replies SIGN to confirm or REJECT to reopen.")])
        if side in self.pending:
            return self._note("OFFER", "held", "an offer awaits a person",
                              [Action(side, "Clerk: an earlier offer is waiting for APPROVE or REJECT from a person here.")])
        if self.rounds >= ROUND_CAP:
            return self._note("OFFER", "stopped", f"round cap {ROUND_CAP} reached",
                              [Action(side, f"Clerk: round cap of {ROUND_CAP} reached. The people take it from here: SIGN or walk.")])
        if self.guard:
            reasons = rules.scan_for_leaks(cmd.note)
            if reasons:
                return self._note("OFFER", "blocked", "; ".join(reasons),
                                  [Action(side, "Clerk: BLOCKED. Nothing was sent. The sentence can't travel because "
                                                + "; ".join(reasons) + ". The only number allowed in an offer is the offer. "
                                                + "Rewrite the sentence and OFFER again.")])
        if rules.check_limit(side, cmd.amount, self.sealed[side]) == "past_limit":
            self.pending[side] = cmd
            return self._note("OFFER", "needs a person", f"past the {side}'s {LIMIT_NAME[side]}",
                              [Action(side, f"Clerk: NEEDS A PERSON. {rules.money(cmd.amount)} is past the {side}'s "
                                            f"{LIMIT_NAME[side]}. Nothing was sent. A person here replies APPROVE or REJECT.")])
        return self._relay(side, cmd, "relayed")

    def _approve(self, side: str) -> list[Action]:
        cmd = self.pending.pop(side, None)
        if cmd is None:
            return self._note("APPROVE", "ignored", "nothing pending", [Action(side, "Clerk: nothing is waiting for approval.")])
        return self._relay(side, cmd, "approved by a person and relayed")

    def _reject(self, side: str) -> list[Action]:
        if side in self.pending:
            self.pending.pop(side)
            return self._note("REJECT", "dropped", "person rejected the overrun",
                              [Action(side, f"Clerk: dropped. Nothing was sent. @{ENVOY[side]} make a different offer.")])
        if self.agreed is not None:
            self.agreed, self.signed = None, {}
            return self._note("REJECT", "reopened", "person rejected the agreed price",
                              [Action(side, f"Clerk: the agreed price is withdrawn. @{ENVOY[side]} continue."),
                               Action(OTHER[side], f"Clerk: the {side} withdrew from the agreed price. @{ENVOY[OTHER[side]]} continue."),
                               Action("table", f"The {side} withdrew. Negotiation reopened.")])
        return self._note("REJECT", "ignored", "nothing to reject", [Action(side, "Clerk: nothing is waiting to be rejected.")])

    def _sign(self, side: str, sender: str) -> list[Action]:
        if self.agreed is None:
            other_offer = self.last_offer.get(OTHER[side])
            if other_offer is None:
                return self._note("SIGN", "ignored", "no offer to accept", [Action(side, "Clerk: there is no offer from the other side to sign yet.")])
            self.agreed = other_offer
        self.signed[side] = sender
        if len(self.signed) == 2:
            self.closed = True
            return self._note("SIGN", "closed", f"both sides signed at {self.agreed}", [Action("table", self.term_sheet())]
                              + [Action(s, f"Clerk: signed by both sides at {rules.money(self.agreed)}. The term sheet is on #deal-table.") for s in SIDES])
        other = OTHER[side]
        return self._note("SIGN", "signed", f"{side} signed, waiting for {other}",
                          [Action(side, f"Clerk: the {side} has signed at {rules.money(self.agreed)}. Waiting for the {other}."),
                           Action(other, f"Clerk: the {side} accepts {rules.money(self.agreed)} and has signed. A person here replies SIGN to close, or REJECT."),
                           Action("table", f"The {side} signed at {rules.money(self.agreed)}. Waiting for the {other}.")])

    # ---- helpers -----------------------------------------------------------------------
    def _relay(self, side: str, cmd: Command, decision: str) -> list[Action]:
        self.rounds += 1
        self.last_offer[side] = cmd.amount
        other = OTHER[side]
        note = f' "{cmd.note}"' if cmd.note else ""
        out = [Action(other, f"@{ENVOY[other]} Offer from the {side}, round {self.rounds} of {ROUND_CAP}: "
                             f"{rules.money(cmd.amount)}.{note}\n{REPLY_HINT}"),
               Action("table", f"Round {self.rounds}: the {side} offers {rules.money(cmd.amount)}.{note}")]
        if self.last_offer.get(other) == cmd.amount:
            self.agreed = cmd.amount
            out = [Action("table", f"Round {self.rounds}: the {side} matches at {rules.money(cmd.amount)}. "
                                   "Agreed. Each side's person: reply SIGN.")]
            out += [Action(s, f"Clerk: both envoys are at {rules.money(cmd.amount)}. A person here replies SIGN to confirm, or REJECT.") for s in SIDES]
            return self._note("OFFER", "agreed", f"both at {cmd.amount} after round {self.rounds}", out)
        return self._note("OFFER", decision, f"round {self.rounds} of {ROUND_CAP}, {side} -> {other}", out)

    def _note(self, command: str, decision: str, reason: str, actions: list[Action]) -> list[Action]:
        self.log.append((command, decision, reason))
        return actions

    def term_sheet(self) -> str:
        who = ", ".join(f"{self.signed[s]} for the {s}" for s in SIDES if s in self.signed)
        return ("**TERM SHEET**\n"
                f"Price: {rules.money(self.agreed)}\n"
                f"Rounds: {self.rounds} of {ROUND_CAP}\n"
                f"Signed by: {who}\n"
                "Neither side's limit was disclosed. Every line that crossed was checked by the Clerk, "
                "plain code with no AI in it.")
