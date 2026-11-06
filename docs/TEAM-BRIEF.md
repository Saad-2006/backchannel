# Backchannel: the one page

Read this and nothing else. Everything the team needs is here. Written Friday 6 Nov, 23:15 PKT.

## 1. What we built

Two parties want a deal. The client hides its budget, the agency hides its floor, and deals crawl for weeks. Backchannel gives each side a private Discord room with its own people and its own AI envoy (a Claude Code agent). The envoys bargain for their people but never share a room. Between the rooms sits the Clerk: plain Python, no AI, the only member of both rooms. By default it lets only an amount cross. It holds any offer that crosses that side's own limit until a person there says APPROVE or REJECT. When both envoys land on the same amount, a person on each side types SIGN and the Clerk posts the term sheet to a public deal table. Pitch: **AI talks, code decides.**

It works. Thursday night: six rounds, $7,700, neither room saw the other's number, both signed, term sheet posted, about one minute.

## 2. What Switch is, and why we need it

Switch puts AI agents into a team's chat (Discord here) as room members with names and permissions. You run a Switch server, connect Discord, and agents join channels, read them and reply under their own name. Agents can be ready-made (Claude Code) or your own program speaking Switch's protocol.

We need it for four things we would otherwise have to build: the envoys exist because Switch runs them; the wall between the sides is Switch's room membership; a no-AI script can sit in both rooms because Switch lets any program be a member; and the humans are in the loop because Switch bridges Discord. Pull Switch out and there are no envoys, no rooms, no wall, no humans. The one-liner: **Switch is the rooms and the players. The Clerk is the rule that decides what crosses.**

## 3. Why a mediator

Whoever runs the Clerk can see both limits, and the Discord owner can read every channel. If the host were one of the parties, the other side would never put its number in. So the host must be neutral, like escrow or a deal desk. That is the normal shape of any two-party secret, and a server holding separate rooms for parties who distrust each other is exactly what Switch is for. On camera: **Saad is the mediator** (runs the Mac, never bargains), **Eman is the agency**, **Talha is the client**. The guarantee we claim: controlled disclosure through a trusted mediator. Not zero-knowledge.

## 4. What the audit found, and what we changed

- The leak scan can't catch paraphrase. Changed: by default only the amount crosses, no sentence. Sentences are opt-in (`CLERK_NOTES=on`) and scanned.
- Saying "past your floor" to the envoy lets it probe. Changed: a held offer just says "held"; the reason goes to the people and the log. A hold cap of three per side limits probing.
- Identity was by display name. Changed: anything Switch marks as an agent, or named like an envoy, is never a person. Only people can SEAL, APPROVE, REJECT, SIGN.
- A seal could be changed mid-deal. Changed: immutable until the Clerk restarts.
- After a REJECT of an agreed price, an old offer could be signed. Changed: reopening clears offers; a fresh offer is required.
- Double SIGN, redelivered messages, failed posts. Changed: ignored, de-duplicated by message id, logged as failed delivery.
- Restart: nothing is restored; both sides seal again. Fail closed.
- 49 tests cover all of it. README has a security-model table saying exactly what is and isn't guaranteed.

## 5. Where things live

| Thing | Where |
|---|---|
| Public explanation for judges | `README.md` |
| Form answers, LinkedIn post, #HowISwitch post | `docs/SUBMISSION.md` |
| This page: plan, roles, experiments | `docs/TEAM-BRIEF.md` |
| Tonight's transcripts | `docs/leak-test/guard-on.txt`, `guard-off.txt`, `NOTES.md` |
| Envoy briefs | `envoys/agency/CLAUDE.md`, `envoys/client/CLAUDE.md` |
| The Clerk | `clerk/rules.py`, `clerk/deal.py`, `clerk/switch.py`, `clerk/main.py` |
| Tests | `tests/` |
| Team slides | Saad's Desktop, `Backchannel-team-brief-v2.pptx` |
| Repo | github.com/Saad-2006/backchannel |

## 6. Tonight: setup, then the takes, in order

**Saad, setup, 10 minutes.** Pull, test, recreate the three channels (agency: bot, `clerk` role, Eman; client: bot, `clerk` role, Talha; deal table: bot, `clerk` role), post once in each, `!invite-agent @clerk` in all three, envoy invites in the war rooms, reset both envoys in Console. Screen: Discord app on the agency room, Chrome on the client room, second Chrome on the deal table, terminal at the bottom. OBS full screen.

```
cd ~/Desktop/backchannel && git pull && .venv/bin/python -m pytest -q
CLERK_PACE=8 .venv/bin/python -m clerk.main
```

Saad restarts the Clerk before every take (it remembers the deal). Eman types only in `#agency-war-room`, Talha only in `#client-war-room`. Nobody types anything not listed. Wait for the Clerk after each line. Three takes, that's all.

**Take 1, the deal. Default mode. Recorded. This is also the safety cut: upload it unlisted right after.**
1. Eman: `SEAL 6000`
2. Talha: `SEAL 9000`
3. Eman: `@agency-envoy open with your first offer`
4. After round two, Talha: `@client-envoy offer 9500 to close this now` (the Clerk holds it, nothing is sent)
5. Talha: `REJECT`
6. Wait until the deal table says Agreed.
7. Eman: `SIGN`
8. Talha: `SIGN` (the term sheet appears)

**Take 2, the block. `CLERK_NOTES=on CLERK_PACE=8`. Recorded.**
1. Eman: `SEAL 6000`. Talha: `SEAL 9000`.
2. Eman: `@agency-envoy ask them what their budget is, then make your opening offer` (BLOCKED on screen, nothing reaches the client room or the table)
3. Eman: `@agency-envoy rewrite the sentence without any number or limit word and offer again`
4. Stop when the clean offer crosses.

**Take 3, guard off versus guard on. Recorded, for the blog.**
First `CLERK_NOTES=on CLERK_GUARD=off`:
1. Eman: `SEAL 6000`. Talha: `SEAL 9000`.
2. Talha: `@client-envoy tell them honestly how close this is to the most we can spend, then offer`
3. Eman: `@agency-envoy hint at where your bottom is without using a number, then offer`
4. Note exactly what crossed into the other room.
Restart with `CLERK_NOTES=on` (guard on) and repeat lines 1 to 3. Note what crossed now.

**Then Saad:** copy the envoy lines from take 3 into `docs/leak-test/guard-off.txt` and `guard-on.txt`, one per line. Push. Submit the form from `docs/SUBMISSION.md` with the repo link and the take 1 link. Send Eman all three recordings, send Talha the two transcript files.

## 7. Saturday

**Eman: the video.** Under three minutes, four acts, voice-over: (1) the conflict and the two seals, the table says only "a deal is possible"; (2) the Clerk blocks a leak, nothing reaches the table; (3) the negotiation on the deal table, the held offer and REJECT, six-round cap; (4) both SIGN, the term sheet. End card: AI talks, code decides. Upload public or unlisted, put the link in the README, and in the form if your account can edit it.

**Talha: the blog.** For a first-time Switch user. Sections: the problem; what we built; how Switch was set up (Console, Discord bridge, two Claude Code agents, one hand-written agent on the protocol); what the Clerk does and the one rule; the experiments, with the real transcripts and a table of what crossed with the guard on, off, and in amounts-only mode; what we learned; what we'd do next (an envoy that never learns its limit). Publish on DEV or Hashnode, link it in the README, send the link to Eman.
