# Backchannel

**AI talks, code decides.** Two AI envoys negotiate a deal on Switch. A no-AI Python Clerk sits between them so neither side's secret limit ever crosses.

Flip the Switch hackathon · Track 01, Best Business Workflow · team Context Switch: Saad Mehmood, Talha Hamid, Eman Fatima.

## Problem

Clients hide their **budget**. Agencies and freelancers hide their **floor**. Deals stall for weeks. Handing the bargaining to an AI is the obvious fix, but AI models are helpful: ask nicely and they leak the number. A prompt is not a lock.

## Solution

- **Two private Discord rooms**, one per side. Each side's people and its own **Claude Code envoy**. The envoys never share a room.
- **The Clerk**: plain Python, no AI, the only member of both rooms. It parses every offer, **enforces limits**, relays clean offers, and writes the **term sheet**. By default **only the amount crosses**. Sentences are opt-in, and a **leak scan** guards them.
- **A mediator** runs the server and the Clerk, the way escrow or a deal desk works. Neither party hosts. The guarantee is **controlled disclosure through a trusted mediator**, not zero-knowledge: each party trusts the mediator and the published code, nothing else.
- **People stay in control**: only a person can SEAL, APPROVE, REJECT or SIGN.

## Three ideas in it

1. **Intelligence and authority are separate.** AI agents negotiate. Deterministic code decides what they are allowed to do. We did not police two AIs with a third AI.
2. **Information flow is controlled.** Private limits stay in their own room. Only approved, structured offers cross.
3. **People keep sovereignty over commitments.** Agents bargain; humans authorize exceptions and sign.

## How a deal runs

| Step | Who | What |
|---|---|---|
| `SEAL 6000` | a person, own room | limit held in Clerk memory only; never logged, never shown |
| `OFFER 8500` | envoy | limit check, relay to the other room, line on `#deal-table`. With `CLERK_NOTES=on` one sentence may follow, after the leak scan |
| BLOCKED | Clerk | (sentences on) the sentence had a second number, a number word or a limit word; nothing sent |
| NEEDS A PERSON | Clerk | offer crossed that side's own limit; waits for `APPROVE` or `REJECT` |
| match | both envoys | same amount means agreed |
| `SIGN` + `SIGN` | a person on each side | term sheet posted to `#deal-table` |

**The leak rule, when sentences are on:** the only number allowed in an offer is the offer. Six rounds, then the people take over. An offer that crosses a side's own limit is held without telling the envoy why; the reason goes to the people and the log.

## Where Switch is used

- **Agents:** two Claude Code envoys from Switch Console; one hand-written Python agent (the Clerk) on the Switch agent protocol: register, event stream, heartbeat, `list_rooms`, post.
- **Platform:** Discord, bridged by Switch Console. Teammates need only Discord.
- **Why it breaks without Switch:** Switch's **room membership is the wall**, the Clerk is the **only door**. No Switch: no envoys, no rooms, no isolation, no humans in the loop.

## Run it

Needs Switch Console with a local server, a connected Discord server, Python 3.12.

```sh
python3.12 -m venv .venv && .venv/bin/pip install pytest
.venv/bin/python -m pytest          # 41 tests, no Switch needed
.venv/bin/python -m clerk.main      # registers the Clerk on first run, then streams
```

| Env | Effect |
|---|---|
| `CLERK_PACE=8` | wait 8 s before an offer crosses, for recordings |
| `CLERK_NOTES=on` | let one scanned sentence travel with each offer (default: amounts only) |
| `CLERK_GUARD=off` | leak scan off, for the guard on/off experiment only |

Setup:

1. Discord: three channels. In each private one add the Switch bot, the `clerk` role and the people, post once, then `!invite-agent @clerk`.
2. Console: create `agency-envoy` and `client-envoy` as Claude Code agents, folders `envoys/agency` and `envoys/client`, instructions pasted from each folder's `CLAUDE.md`, **who can talk to it: Anyone**.
3. `!invite-agent @agency-envoy` in the agency room, `!invite-agent @client-envoy` in the client room.
4. A person in each room posts `SEAL <amount>`, then `@agency-envoy open with your first offer`.

The Clerk's key lands in `clerk/.clerk-creds.json` (gitignored). The registration token is read from Console's env file and never printed.

## Security model and threat boundaries

| Question | Answer |
|---|---|
| Can an envoy see the other room? | No. Switch room membership. |
| Can an envoy read the other side's limit? | No. It never enters its room. |
| Can the Clerk read both limits? | Yes, in memory only. |
| Can the mediator host read both limits? | Yes. That is why the host is neutral. |
| Can arbitrary prose cross? | No by default: only amounts. With sentences on, a scan guards them. |
| Is the leak scan perfect? | No. It catches patterns, not paraphrase. |
| Is an envoy told why an offer was held? | No. It sees "held". Whether it was held is still observable, so the guarantee is: no explicit limit or reason is ever disclosed. A hold cap (3 per side) limits probing. |
| Can a seal change mid-deal? | No. Immutable until the Clerk restarts. |
| Who can SEAL, APPROVE, REJECT, SIGN? | People only. Anything Switch marks as an agent, or named like an envoy, is refused. |
| What happens on restart? | Fail closed. Nothing is restored, no old approval is reused, both sides seal again. |
| Redelivered or failed messages? | A message id is handled once. A failed post is logged as a failed delivery; the decision stands. |
| Cryptographically private? | No. Controlled disclosure through a trusted mediator. |

## Limits, honestly

- **The host sees everything.** That is why the host is a neutral mediator. Keeping a mediator honest is a contract problem, not a code problem.
- **One machine in the demo.** In production each side runs its own envoy on its own computer; only the Clerk runs with the mediator.
- **The scan knows patterns, not paraphrase.** That is why the default is amounts only, where there is nothing to leak. Turn sentences on and you accept the scan as the guard; `docs/leak-test/` measures what it catches.
- **Next:** an envoy that never learns its limit. The Clerk already stops anything past it, so the envoy doesn't need the number.

## Layout

```
clerk/rules.py    parse, leak scan, limits, overlap. Pure, no I/O.
clerk/deal.py     the state machine. Pure, no I/O.
clerk/switch.py   the only file that talks to Switch.
clerk/main.py     wires them together.
tests/            pytest, no Switch needed.
envoys/           each envoy's folder and brief. No limits in any file.
docs/             submission text, team brief, leak-test results.
```
