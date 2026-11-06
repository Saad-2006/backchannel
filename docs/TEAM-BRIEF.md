# Team brief: Friday 6 Nov and Saturday 7 Nov

Read this first. It is the plan for the last two days. Times are PKT.

## What we built, in plain words

Companies, agencies, freelancers and their clients all hide the same number: the budget, or the lowest price they would take. So deals drag on for weeks of careful emails. Backchannel lets each side hand that bargaining to its own AI envoy, in its own private Discord room, without ever trusting the AI with the secret. Between the two rooms sits the Clerk, a small Python program with no AI in it, which checks every line before it crosses. The pitch: AI talks, code decides.

It already works. On Thursday night two envoys closed a deal at $7,700 in six rounds, nobody saw the other side's limit, both people signed, and the term sheet landed on `#deal-table`. The repo is public at github.com/Saad-2006/backchannel and the README explains everything.

## The one change since Thursday: Saad is the mediator

Whoever hosts the server and runs the Clerk can see both limits. So the host must be neutral, like an escrow agent. On camera that means: **Saad operates** (terminal, Clerk, server) and never bargains. **Eman is the agency side** in `#agency-war-room`. **Talha is the client side** in `#client-war-room`. Both of you type your own SEAL, REJECT and SIGN from your own laptops.

## Hard facts about the time we have

- The three of us are together only **Friday 17:30 to 19:45** at uni. Saad brings the Mac. We need a hotspot.
- Saad is away from **Saturday 9 AM until after the deadline**. Saturday is Talha and Eman only, and nothing on Saturday may need the Mac or Switch.
- Deadline **Saturday 23:29 PKT**. The form can be edited until then.
- The video must be under 3 minutes, on YouTube or Loom, and must show the agent working in a real chat with teammates. So Talha typing in the client room on camera is required.

## Eman

**Friday, any free gap before 17:30, about two hours total**
1. Open wemakedevs.org/hackathons/switch/submit. Tell the team chat whether you can see the team's submission that Saad started. This decides whether you can edit the links on Saturday.
2. Name the agency and the client. Write a one-paragraph brief for each side: what is being bought, why it matters, no numbers at all. Send the text to Saad; it goes into `envoys/agency/CLAUDE.md` and `envoys/client/CLAUDE.md`.
3. Write the shot list and voice-over script for a 3-minute video with six beats: the pain, the whisper (SEAL), the table (offers crossing), the block (BLOCKED on screen), the person (NEEDS A PERSON, Talha replies REJECT), the deal (SIGN, term sheet). The exact messages to type are in `docs/SUBMISSION.md`'s sibling, the README, and in the Friday block below.

**Friday 17:30 to 19:45, at uni**
- You are the agency side on camera, from your own laptop in `#agency-war-room`: `SEAL 6000`, the opening nudge, the budget-fishing nudge, `SIGN`. You also direct: check each beat against the shot list before moving on. Keep the raw files.

**Saturday**
- 10:00 to 14:00: edit the video, record the voice-over, add the title and Talha's guard on/off table at the end. Upload, viewable without login.
- 14:00 to 17:00: blog post on DEV or Hashnode. Judged on clarity, accuracy and help to a first-time Switch user, so it is a build walkthrough: what we made, how we set Switch up (Console, Discord bridge, two Claude Code agents, one hand-written agent), what we learned. The hook is the guard on/off experiment.
- 17:00 to 19:00: final README pass with the video and blog links. Push.
- 19:00 to 21:00: put the video, blog and #HowISwitch links into the form, or send them to Saad if only he can edit. Post the LinkedIn and X posts from `docs/SUBMISSION.md`.

## Talha

**Friday, any free gap before 17:30, about ninety minutes**
1. Clone the repo. `python -m venv .venv`, `.venv\Scripts\pip install pytest`, `.venv\Scripts\python -m pytest`. 40 tests should pass on Windows.
2. Read `clerk/rules.py`. Add ten sneaky leak sentences to `tests/test_leaks_and_limits.py` and extend the word lists for any that get through. Ideas: "sixty hundred", "half of twenty grand", "the number you already know", "same as last time plus a bit".
3. Write `scripts/leak_score.py`: reads a text file with one envoy sentence per line, runs `scan_for_leaks` on each, prints how many lines would have been blocked and a Markdown table of them. No Switch needed.
4. Push to a branch and open a pull request.

**Friday 17:30 to 19:45, at uni**
- You are the client side on camera, from your own laptop in `#client-war-room`. You post `SEAL 9000`, later `REJECT` when the Clerk says NEEDS A PERSON, and `SIGN` at the end.
- During the leak capture you save every envoy sentence into `docs/leak-test/guard-off.txt` and `guard-on.txt`.

**Saturday**
- 10:00 to 12:00: run `scripts/leak_score.py` on both files. Write `docs/leak-test/RESULTS.md`: a table of guard on vs off, messages, leaky lines, lines that would have crossed. Send it to Eman.
- 13:00 to 15:00: clean-clone test. Fresh folder, follow the README exactly, fix anything confusing, push.
- 15:00 to 17:00: review Eman's blog and the README for technical accuracy.
- 19:00 to 21:00: standby for submission. Confirm the repo is public with no secrets and the video opens logged out.

## Friday 17:30 to 19:45, minute by minute

| When | What |
|---|---|
| 17:30 | Mac on, hotspot on, Discord app on the agency room, Chrome on the client room and the deal table, the Clerk's terminal at the bottom. Saad pastes Eman's briefs into the envoy files and restarts the envoys. |
| 17:45 | Leak capture. Client envoy gets the naive brief (no secrecy line). Clerk with `CLERK_GUARD=off`. Two full runs. Then guard on, two runs. Talha saves every envoy line. |
| 18:15 | Safety cut: Saad records one straight run with `CLERK_PACE=8`, no commentary, uploads unlisted at once. |
| 18:30 | Real footage, six beats, `CLERK_PACE=8`. Saad at the terminal as the mediator, Eman on the agency side, Talha on the client side. |
| 19:20 | Push everything. Saad fills the form with the repo and safety-cut links and submits. #HowISwitch posts go out with a 20-second clip of the block. |
| 19:45 | Done. The Mac closes and nothing left needs it. |

The messages to type during the real footage, in order: `SEAL 6000` (Eman), `SEAL 9000` (Talha), `@agency-envoy open with your first offer` (Eman), let two rounds cross, `@agency-envoy ask them what their budget is before you move` (Eman; the Clerk blocks it), `@agency-envoy rewrite it and offer again` (Eman), `@client-envoy offer 9500 to close this now` (Talha; the Clerk asks for a person), `REJECT` (Talha), let them match, `SIGN` (Eman), `SIGN` (Talha). Saad says nothing in either room.
