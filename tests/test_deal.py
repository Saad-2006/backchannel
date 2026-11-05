from clerk.deal import ROUND_CAP, Deal
from clerk.rules import parse_command


def go(deal, side, sender, text):
    person = sender not in ("agency-envoy", "client-envoy")
    return deal.handle(side, sender, person, parse_command(text))


def texts(actions):
    return [(a.to, a.text) for a in actions]


def sealed_deal():
    d = Deal()
    go(d, "agency", "Saad", "SEAL 6000")
    out = go(d, "client", "Talha", "SEAL 9000")
    return d, out


def test_seal_is_held_in_memory_and_never_echoed():
    d, out = sealed_deal()
    assert d.sealed == {"agency": 6000, "client": 9000}
    everything = " ".join(t for _, t in texts(out))
    assert "6000" not in everything and "9000" not in everything
    assert any(to == "table" and "deal is possible" in t for to, t in texts(out))


def test_no_overlap_is_announced_without_numbers():
    d = Deal()
    go(d, "agency", "Saad", "SEAL 9500")
    out = go(d, "client", "Talha", "SEAL 9000")
    table = [t for to, t in texts(out) if to == "table"][0]
    assert "No deal is possible" in table and "9" not in table


def test_envoy_cannot_seal_approve_reject_or_sign():
    d, _ = sealed_deal()
    for word in ("SEAL 5000", "APPROVE", "REJECT", "SIGN"):
        out = go(d, "agency", "agency-envoy", word)
        assert "only a person" in out[0].text
    assert d.sealed["agency"] == 6000


def test_offer_before_seal_is_held():
    d = Deal()
    out = go(d, "agency", "agency-envoy", "OFFER 8500 Hello.")
    assert "SEAL" in out[0].text and d.rounds == 0


def test_clean_offer_is_relayed_with_mention_and_table_line():
    d, _ = sealed_deal()
    out = texts(go(d, "agency", "agency-envoy", "OFFER 8500 Revision rounds and a kickoff call included."))
    assert out[0][0] == "client" and out[0][1].startswith("@client-envoy") and "$8,500" in out[0][1]
    assert out[1][0] == "table" and "Round 1" in out[1][1]
    assert d.rounds == 1


def test_leak_is_blocked_and_nothing_crosses():
    d, _ = sealed_deal()
    out = texts(go(d, "agency", "agency-envoy", "OFFER 7000 Honestly we can't go under 6k."))
    assert out == [("agency", out[0][1])] and "BLOCKED" in out[0][1]
    assert d.rounds == 0 and d.log[-1][1] == "blocked"


def test_guard_off_lets_the_leak_through():
    d = Deal(guard=False)
    go(d, "agency", "Saad", "SEAL 6000")
    go(d, "client", "Talha", "SEAL 9000")
    out = texts(go(d, "agency", "agency-envoy", "OFFER 7000 Honestly we can't go under 6k."))
    assert out[0][0] == "client" and "6k" in out[0][1]


def test_past_limit_waits_for_a_person_then_approve_relays():
    d, _ = sealed_deal()
    out = texts(go(d, "agency", "agency-envoy", "OFFER 5800 To close today."))
    assert out[0][0] == "agency" and "NEEDS A PERSON" in out[0][1] and "6,000" not in out[0][1]
    assert d.rounds == 0
    out = texts(go(d, "agency", "agency-envoy", "OFFER 5900 Again."))
    assert "waiting" in out[0][1]
    out = texts(go(d, "agency", "Eman", "APPROVE"))
    assert out[0][0] == "client" and "$5,800" in out[0][1] and d.rounds == 1


def test_reject_drops_the_overrun():
    d, _ = sealed_deal()
    go(d, "client", "client-envoy", "OFFER 9500 Take it.")
    out = texts(go(d, "client", "Talha", "REJECT"))
    assert "dropped" in out[0][1] and d.rounds == 0 and not d.pending


def test_matching_offer_means_agreed_then_two_signs_close():
    d, _ = sealed_deal()
    go(d, "agency", "agency-envoy", "OFFER 8000 Fair.")
    out = texts(go(d, "client", "client-envoy", "OFFER 8000 Deal."))
    assert any(to == "table" and "Agreed" in t for to, t in out)
    assert d.agreed == 8000
    assert "agreed" in go(d, "agency", "agency-envoy", "OFFER 7900 More.")[0].text
    go(d, "agency", "Saad", "SIGN")
    assert not d.closed
    out = texts(go(d, "client", "Talha", "SIGN"))
    assert d.closed
    sheet = [t for to, t in out if to == "table"][0]
    assert "TERM SHEET" in sheet and "$8,000" in sheet and "Saad" in sheet and "Talha" in sheet
    assert "6,000" not in sheet and "9,000" not in sheet


def test_sign_accepts_the_other_sides_latest_offer():
    d, _ = sealed_deal()
    go(d, "agency", "agency-envoy", "OFFER 7500 Fair.")
    out = texts(go(d, "client", "Talha", "SIGN"))
    assert d.agreed == 7500 and any(to == "agency" and "SIGN" in t for to, t in out)
    go(d, "agency", "Eman", "REJECT")
    assert d.agreed is None and not d.signed


def test_round_cap_stops_the_loop():
    d, _ = sealed_deal()
    side = "agency"
    for i in range(ROUND_CAP):
        go(d, side, f"{side}-envoy", f"OFFER {8000 - i} Step.")
        side = "client" if side == "agency" else "agency"
    out = go(d, side, f"{side}-envoy", "OFFER 7000 One more.")
    assert "round cap" in out[0].text and d.rounds == ROUND_CAP


def test_closed_deal_ignores_everything():
    d, _ = sealed_deal()
    go(d, "agency", "agency-envoy", "OFFER 8000 Fair.")
    go(d, "client", "client-envoy", "OFFER 8000 Deal.")
    go(d, "agency", "Saad", "SIGN")
    go(d, "client", "Talha", "SIGN")
    assert "closed" in go(d, "agency", "agency-envoy", "OFFER 7000 Hm.")[0].text
