# Submission form answers (paste into wemakedevs.org/hackathons/switch/submit)

Editable until the deadline. Required fields are marked. Replace the bracketed links.

## Part 1: Project details

**Project title** (required)
Backchannel: AI talks, code decides

**Tracks** (required)
Best Business Workflow

**Project description** (required)
An agency and a client want to close a deal, but neither will say its limit: the agency has a floor, the client has a ceiling, and they circle for weeks. Backchannel gives each side its own AI envoy in a private Discord room. The envoys bargain for their people, but they never share a room. The only link between the two rooms is the Clerk, a small Python program with no AI in it. It reads every offer, blocks any line that could give away a limit (the only number allowed in an offer is the offer), holds an offer that crosses a side's own limit until a person on that side approves it, announces only whether a deal is possible, and writes the term sheet when a person on each side signs. The Clerk runs with a neutral notary, the way escrow works, so neither side has to trust the other side, the other side's host, or any AI. It is for any two teams who want AI to do the back-and-forth without trusting it with the secret.

**GitHub repository** (required)
[https://github.com/Saad-2006/backchannel]

**Demo video** (required, under 3 minutes)
[YouTube link]

**Live demo**
Leave blank.

## Part 2: Track details

**Blog post**
[DEV or Hashnode link]

**#HowISwitch post**
[X or LinkedIn link]

## Part 3: How you used Switch

**How did you use Switch in your project?** (required)
Agents: two Claude Code envoys created in Switch Console, each with its own working folder and brief, and one hand-written Python agent, the Clerk, registered through Switch's agent protocol (POST /agents, the event stream, heartbeats, list_rooms, post). Platform: Discord, bridged by Switch, with three private and public channels: #agency-war-room, #client-war-room and #deal-table. Real work: our teammates seal a limit, watch their envoy negotiate, approve or reject an offer that crosses the limit, and sign the result, all from Discord. Switch is the wall and the Clerk is the door, and both are run by a neutral notary, not by either party. Room membership is what keeps the two sides apart; the Clerk is the only member of both war rooms, and it is plain code. Take Switch away and there is no shared bus between a Python process, two Claude Code sessions and three people in Discord.

**What did you like about Switch, and what would you improve?** (required)
Liked: the agent protocol is small enough to speak from the Python standard library in an evening, and room membership doubles as an access-control model, which is the whole basis of our project. Console's Discord bridge meant our Windows teammates never touched the server. Got in the way: a hand-written agent's owner is the bootstrap account, so nobody can @mention it, and we had to design around that with command words; an all-scope stream reports zero rooms, so we had to call list_rooms; ops need a live connection id or return 409; and the message payload has fields the docs don't list yet (sender_kind, on_behalf_of). Next: a documented sender kind so an agent can tell a person from another agent without a name list, a way to transfer agent ownership, and a loop brake for agent-to-agent mentions.

## #HowISwitch post (X and LinkedIn, Friday night, with the 20-second block clip)
We let two AIs negotiate a deal on Switch and watched one try to leak its owner's floor. A 200-line Python Clerk with no AI in it caught the line before it crossed. The rule: the only number allowed in an offer is the offer. #HowISwitch #FlipTheSwitch [repo link]

## LinkedIn post (Saad, Friday night, with the block clip or the term sheet screenshot)
Most software companies and their clients, freelancers and the people who hire them, all hide the same number: the budget, or the lowest price they'd take. So deals drag on for weeks of careful emails.

For the Flip the Switch hackathon our team built Backchannel. Each side briefs its own AI envoy in a private Discord room. The envoys bargain for their people but never share a room. The only link between the rooms is the Clerk: a small Python program with no AI in it that checks every line before it crosses. It blocks anything that could give away a limit (the only number allowed in an offer is the offer), holds an offer that crosses your own limit until a person approves it, and writes the term sheet when both sides sign.

Switch is what made it possible: two Claude Code agents from Switch Console, one hand-written Python agent on the Switch agent protocol, and Discord rooms whose membership is the wall between the two sides. The first real run closed a deal in six rounds and about a minute, and neither side ever saw the other's number.

AI talks, code decides. Repo and video in the comments. #HowISwitch #FlipTheSwitch
