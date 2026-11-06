# Video edit script (Eman)

Three source files from Saad, all screen recordings of the same four-window layout: agency room top-left, deal table top-right, client room bottom-left, Clerk terminal bottom-right.

| File | Length | What it holds |
|---|---|---|
| `take2-deal.mov` | 2:11 | **The main one.** Seals, a leaky line BLOCKED, a clean line crossing, six rounds, agreed at $7,900, both SIGN, term sheet. |
| `take3-guard-off.mov` | 1:00 | Same leaky line with the guard off: it crosses into the client room and the deal table. |
| `take1-deal.mov` | 1:58 | Backup. A full deal at $8,200 in amounts-only mode. Use only if take 2 has a problem. |

No voice-over needed. Captions on screen carry the story. Target length: about 2:30. Keep the Discord text readable: crop to the window named in each clip when the caption says so.

## Timeline

Problem first, then the fix. Timestamps are positions inside the source file.

### Card 1, 0:00 to 0:08, black background, white text
Line 1 (big): **Backchannel**
Line 2: **AI talks. Code decides.**
Line 3 (small): Flip the Switch hackathon · Track 01 · team Context Switch

### Card 2, 0:08 to 0:18
Clients hide their budget. Agencies hide their floor. Deals crawl for weeks.
The obvious fix: let an AI bargain for each side. The obvious risk: AI models are helpful.

### Card 3, 5 seconds
**What happens if the two AIs just talk?**

### Clip 1, the leak. `take3-guard-off.mov` 0:02 to 0:28
Full layout. Both seals go in (0:02 to 0:08). Then the agency side sends "OFFER 8800 Honestly, we can't go under 6k" and it crosses: the client room and the deal table both show the sentence.
Caption at the seals: **Each side seals its limit in its own private room.**
Caption at the crossing: **One message, and the floor has leaked to the other side.**
Hold two seconds on the deal-table line "Honestly, we can't go under 6k".

### Card 4, 8 seconds
**So we put a Clerk between the rooms.**
Plain Python. No AI. The only member of both private rooms. Built on Switch.

### Clip 2, the seals. `take2-deal.mov` 0:02 to 0:14
Full layout. Caption: **Same deal, fresh start. Each side seals. The Clerk holds the limits in memory only.**
At 0:12 crop briefly to the deal table (top-right): "Both sides have sealed. A deal is possible. No numbers shown." Caption: **The public table learns one bit: a deal is possible.**

### Clip 3, the block. `take2-deal.mov` 0:20 to 0:36
Crop to the agency room (top-left). The same leaky line, "OFFER 8800 Honestly, we can't go under 6k". The Clerk answers BLOCKED with three reasons.
Caption: **The same line. The Clerk blocks it. Nothing reaches the other side.**
Hold two seconds on the Clerk's BLOCKED message.

### Clip 4, the clean line crosses. `take2-deal.mov` 0:36 to 0:50
Full layout. "OFFER 8800 Full scope with launch support included." crosses into the client room, "Round 1" appears on the deal table, the client's envoy answers.
Caption: **Same amount, clean sentence. It crosses. The client's envoy answers on its own.**

### Clip 5, the negotiation. `take2-deal.mov` 0:50 to 1:40, played at 2x speed
Full layout. Rounds 2 to 6 cross through the Clerk. The deal table counts them.
Caption: **The envoys bargain through the Clerk, round by round. Six rounds at most. Neither room can see the other. Switch's room membership is the wall; the Clerk is the only door.**
Drop back to normal speed when the deal table says "Agreed. Each side's person: reply SIGN." (source 1:39).

### Clip 6, the signatures. `take2-deal.mov` 1:55 to 2:10
Full layout, then crop to the deal table at the end. SIGN in the agency room, SIGN in the client room, the TERM SHEET appears.
Caption: **A person on each side signs. The Clerk writes the term sheet. Neither side ever saw the other's limit.**
Hold three seconds on the term sheet.

### Card 5, 8 seconds
**Switch keeps the sides apart.**
**The Clerk decides what crosses.**
**The AI never decides anything about the secret.**

### Card 6, 6 seconds
github.com/Saad-2006/backchannel
Built on Switch · Two Claude Code envoys · One Python Clerk, no AI · Discord
(small) The two human seats were operated by one teammate from two accounts during recording.

## Notes
- The term sheet shows the Discord usernames of the two accounts. That's fine; it's true.
- If any clip is too small to read, crop to the single window the caption talks about. The layout is a 2x2 grid, so each window is a clean quarter.
- Export 1080p, upload to YouTube as Unlisted or Public, open the link in a private window to confirm it plays, then put the link in the README under the title and send it to Saad before 7 PM.
