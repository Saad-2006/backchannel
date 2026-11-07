# We let two AIs negotiate a deal on Switch, then stopped one from leaking the number

*Built in 48 hours for the Flip the Switch hackathon by team Context Switch. Repo: https://github.com/Saad-2006/backchannel. Demo: https://youtu.be/8SV46XGqTIU*

## The problem

Every agency hides its floor. Every client hides its budget. Both sides know the other has a number, and neither will say it first, so deals crawl through weeks of careful emails. The obvious fix is to let an AI agent do the bargaining for each side. The obvious risk is that AI models are built to be helpful. Ask one nicely what its owner's floor is and it may tell you, hint at it, or write "we can't go under 6k" while trying to sound firm. A prompt that says "keep this secret" is a suggestion, not a lock.

## What we built

Backchannel gives each side its own AI envoy, a Claude Code agent, in its own private Discord room. The envoys bargain for their people but never share a room. Between the rooms sits the **Clerk**: plain Python, no AI, the only member of both rooms. It parses every offer, enforces each side's sealed limit, decides what crosses, and writes the term sheet when a person on each side signs.

The pitch in four words: **AI talks, code decides.**

## How Switch made it possible

Switch puts agents into the chat a team already uses, as room members with names and permissions. We used it three ways:

1. **Two Claude Code envoys** created in Switch Console, each with its own working folder and a brief, each invited into exactly one private room with `!invite-agent`.
2. **One hand-written agent**, the Clerk, speaking Switch's agent protocol from the Python standard library: `POST /agents` to register, an SSE event stream, a heartbeat every two seconds, `list_rooms`, and `POST /agents/{id}/message` to post.
3. **Discord**, bridged by Switch Console, so teammates on Windows only needed Discord.

Switch's room membership is the wall between the two sides. The Clerk is the only door. Pull Switch out and there are no envoys, no rooms, no isolation and no humans in the loop.

## Setting it up, for a first-time Switch user

- Install Switch Console, run a local server, connect your Discord with a bot token and the server id.
- Create three channels. In each private one add the Switch bot, the agent role and the people, post one message, then `!invite-agent @clerk`.
- In Console, add two Claude Code agents. Set a working folder for each, paste the brief as instructions, and set "who can talk to your agent" to **Anyone**. A freshly registered agent answers only its owner; our Clerk is owned by Switch's bootstrap account, so without Anyone the envoys refuse every offer it relays.
- Register the Clerk on `POST /agents` with an integration profile, stream its events, post back.

Two things that bit us: an all-scope event stream reports zero rooms, so call `list_rooms`; and that op needs the connection id of a live stream or it returns 409. Deleted Discord channels also linger as rooms with the same name, so our Clerk posts into the room it last heard a person in.

## What the Clerk does

Commands are one capital word at the start of a message. Only the first line is ever read.

- `SEAL 6000`: a person seals their side's limit. Held in memory only, never logged, never shown. After both seals the Clerk posts one bit to the public table: a deal is possible, or not.
- `OFFER 8800 one sentence`: the envoy's move. Limit check, then relay to the other room mentioning that side's envoy, plus a line on the deal table. A matching amount means agreed.
- `NEEDS A PERSON`: the offer crossed that side's own limit. Nothing is sent until a person types `APPROVE` or `REJECT`. The envoy is not told why.
- `SIGN` from a person on each side: the Clerk writes the term sheet.

Only people may SEAL, APPROVE, REJECT or SIGN. An envoy that tries is refused.

**The one rule:** the only number allowed in an offer is the offer. By default the Clerk strips every sentence and lets only the amount cross. Turn sentences on and a scan blocks any other digit, any number word (six, thousand, grand, k) and any limit word (floor, ceiling, budget, under, above).

## The experiment

Same server, same rooms, same seals: floor 6000, ceiling 9000. We typed the same leaky line three ways.

| Mode | Line | What crossed |
|---|---|---|
| Amounts only (default) | envoys' offers with sentences | only the amounts; every sentence stayed in its room |
| Sentences on, guard on | `OFFER 8800 Honestly, we can't go under 6k` | nothing: BLOCKED, three reasons named |
| Sentences on, guard off | `OFFER 8800 Honestly, we can't go under 6k` | the whole sentence; the floor hinted to the other side in one message |

With the guard on, the envoys then negotiated six rounds through the Clerk, matched at $7,900, a person on each side signed, and the term sheet landed on the deal table. The whole run took about two minutes.

We also asked an envoy to fish for the other side's budget. It kept the question out of its OFFER line, which is the only line that travels, so nothing leaked. The envoys follow their briefs well. The Clerk is for the day they don't.

## What we learned

- **A prompt is not a lock.** Confidentiality has to come from structure: what is allowed to cross, not what the model is asked to avoid.
- **Separate intelligence from authority.** The AI negotiates. Deterministic, tested code decides what it may do. We did not police two AIs with a third AI.
- **Whoever hosts sees everything.** The Clerk holds both limits in memory, so the host must be a neutral mediator, like escrow. We say so in the README instead of pretending otherwise.

## What's next

An envoy that never learns its own limit. The Clerk already stops anything past it and asks a person, so the envoy doesn't need the number, and an envoy that doesn't know a number can't leak it. And each side running its envoy on its own machine, with only the Clerk at the mediator.

Code, tests and transcripts: https://github.com/Saad-2006/backchannel
