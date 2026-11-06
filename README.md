# Backchannel: AI talks, code decides

Two sides want to close a deal. Neither will say its limit. Each side briefs its own AI envoy in a private Discord room, and the envoys bargain for them. The only link between the two rooms is the **Clerk**: a small Python program with no AI in it. It reads every offer, blocks any line that could give away a limit, holds an offer that crosses a side's own limit until a person approves it, announces only whether a deal is possible, and writes the term sheet when a person on each side signs.

Built for the Flip the Switch hackathon (Track 01, Best Business Workflow) by team Context Switch: Saad Mehmood, Talha Hamid, Eman Fatima.

## The trust model: a notary, not a referee you have to trust

Whoever runs the Clerk can see both limits, because the Clerk holds them in memory. So the host must be a **neutral third party** that neither side is, the same way an escrow agent or a notary works. Each side trusts the notary and the code it runs, and nothing else: not the other side, and not any AI.

| Role | In production | In our demo |
|---|---|---|
| Notary | runs the Switch server, the Discord server and the Clerk; is in no deal and never bargains | Saad: operates the terminal, stays out of both war rooms on camera |
| Agency | its own people and its own envoy, in a room the client cannot see | Eman and `agency-envoy` |
| Client | its own people and its own envoy, in a room the agency cannot see | Talha and `client-envoy` |

What each party can see: its own room, and the public deal table. What the notary can see: everything, which is why the notary is a role you trust, not a party. The AI envoys see only their own room and know only their own side's limit, and the Clerk makes sure that limit never crosses.

## The rooms

| Room | Who is in it | What happens there |
|---|---|---|
| `#agency-war-room` (private) | the agency's people, `agency-envoy`, the Clerk | the agency seals its floor and briefs its envoy |
| `#client-war-room` (private) | the client's people, `client-envoy`, the Clerk | the client seals its ceiling and briefs its envoy |
| `#deal-table` (public) | everyone; only the Clerk posts | every cleared offer, then the term sheet |

The envoys never share a room. The Clerk is the only member of both war rooms, and it is plain code.

## How Switch is used

- **Agents:** two Claude Code envoys created in Switch Console, each with its own working folder and brief (`envoys/agency`, `envoys/client`), and one hand-written Python agent, the Clerk, that speaks Switch's agent protocol directly: `POST /agents` to register, the SSE event stream, heartbeats, `list_rooms`, and `POST /agents/{id}/message` to post.
- **Platform:** Discord, bridged by Switch Console. Teammates on Windows only need Discord.
- **Why it would not work without Switch:** room membership is the wall between the two sides, and the Clerk is the door. Switch gives a Python process, two Claude Code sessions and three people one shared, access-controlled bus. Take it away and there is no wall.

## The Clerk's rules (`clerk/rules.py`, `clerk/deal.py`)

Commands are one capital word at the start of a message. Only that first line is ever read.

| Command | Who | What the Clerk does |
|---|---|---|
| `SEAL <amount>` | a person | holds that side's limit in memory only, never on disk or in a log. After both seals it posts one bit to `#deal-table`: a deal is possible, or not. |
| `OFFER <amount> <one sentence>` | the envoy or a person | leak scan, then limit check, then relay to the other room mentioning that side's envoy, plus a line on `#deal-table`. A matching amount means agreed. |
| `APPROVE` / `REJECT` | a person | lets through or drops an offer that crossed that side's own limit |
| `SIGN` | a person | accepts the agreed price (or the other side's latest offer). Two signatures produce the term sheet. |

**Leak scan:** the only number allowed in an offer is the offer. Any other digits, any number word (six, thousand, grand, k, even two) or any limit word (floor, ceiling, minimum, budget, under, above, walk, ...) blocks the line, and nothing is sent. Strict on purpose, so a judge can read the whole rule in one breath.

Other guards: an envoy cannot SEAL, APPROVE, REJECT or SIGN; mentions inside a sentence are defused before it crosses; six rounds, then the people take over. Every decision is one JSON line in `logs/clerk.jsonl` with the time, room, command, decision and reason, and never a sealed value.

## Run it

Requirements: Switch Console running a local server, a Discord server connected to it, Python 3.12.

```sh
python3.12 -m venv .venv && .venv/bin/pip install pytest
.venv/bin/python -m pytest            # 40 tests, no Switch needed
.venv/bin/python -m clerk.main        # registers the Clerk on first run, then streams
```

Options: `CLERK_PACE=8` waits eight seconds before an offer crosses, so a recording can keep up. `CLERK_NOTES=off` lets only amounts cross, no sentences. `CLERK_GUARD=off` disables the leak scan (only for the guard on/off experiment).

Set-up in Discord and Console:

1. Create the three channels. For each private one: add the Switch bot, the `clerk` role and the people, post one message, then `!invite-agent @clerk`.
2. In Console, create `agency-envoy` and `client-envoy` as Claude Code agents, working folders `envoys/agency` and `envoys/client`, instructions pasted from each folder's `CLAUDE.md`, and "who can talk to your agent" set to Anyone (the Clerk is owned by Switch's bootstrap account, so it cannot address an owner-only agent).
3. `!invite-agent @agency-envoy` in the agency room, `!invite-agent @client-envoy` in the client room.
4. A person in each room posts `SEAL <amount>`, then `@agency-envoy open with your first offer`.

The Clerk's key is written to `clerk/.clerk-creds.json` (gitignored) the first time it runs; the registration token is read from Console's env file and never printed.

## Known limits, and what to do about each

- **The host sees everything.** The Discord owner reads every channel and the Clerk holds both limits. That is why the host is a neutral notary (see the trust model above). Keeping the notary honest is the same problem as keeping an escrow agent honest, and not one this project tries to solve with code.
- **One machine in the demo.** Both envoys and the Clerk run on the notary's Mac. Switch already supports agents on other machines, so in production each side runs its own envoy on its own computer and only the Clerk runs with the notary.
- **The leak scan catches patterns it knows.** Two answers. The guard on/off experiment in `docs/leak-test/` measures how much gets through without it. And `CLERK_NOTES=off` removes the risk entirely: only amounts cross, no sentence at all, so there is nothing to scan and nothing to leak. Sentences are a feature you turn on when you want persuasion and accept the scan as the guard.
- **Next step we did not build:** an envoy does not need to know its side's limit at all. The Clerk already stops any offer past it and asks a person. An envoy that never knows the number cannot leak it. We kept the limit in the envoy's briefing so the guard on/off experiment has something to measure.

## Layout

```
clerk/rules.py    pure rules: parse, leak scan, limits, overlap. No I/O.
clerk/deal.py     the state machine: what to post for each command. No I/O.
clerk/switch.py   the only file that talks to Switch.
clerk/main.py     wires the two together.
tests/            pytest, no Switch needed.
envoys/           each envoy's folder and brief. No limits in any file.
docs/             submission text, team brief, leak-test results.
```
