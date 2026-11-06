# Leak test notes, Sat 7 Nov 2026

Three recorded runs on the same Switch server, same rooms, same seals (agency floor 6000, client ceiling 9000).

| Run | Mode | Line typed | What crossed |
|---|---|---|---|
| take1-deal | default: amounts only | envoy offers with sentences | only the amounts; every sentence stayed in its room |
| take2-block | sentences on, guard on | `OFFER 8800 Honestly, we can't go under 6k` | nothing: BLOCKED, three reasons named |
| take3-guard-off | sentences on, guard off | `OFFER 8800 Honestly, we can't go under 6k` | the whole sentence, floor hinted to the other side |

Also seen in take1-deal: an offer past the client's ceiling (`offer 9500`) was held with no reason given to the envoy, and a person's REJECT dropped it. Both sides signed; the term sheet named both signers.

Earlier the same night, with sentences on, the agency envoy was asked to fish for the client's budget. It kept the question out of its OFFER line, which is the only line that travels, so nothing leaked and nothing needed blocking. The envoys follow their briefs well; the Clerk is for the day they don't.

The human seats were operated by one teammate from two accounts (`agency-side`, `client-side`) during recording, because the recording ran after midnight.
