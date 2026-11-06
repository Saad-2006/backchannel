from clerk.deal import HOLD_CAP, Deal
from clerk.rules import parse_command


def go(deal, side, sender, text, person=None):
    if person is None:
        person = sender not in ("agency-envoy", "client-envoy")
    return deal.handle(side, sender, person, parse_command(text))


def sealed(notes=True):
    d = Deal(notes=notes)
    go(d, "agency", "Eman", "SEAL 6000")
    go(d, "client", "Talha", "SEAL 9000")
    return d


def test_seal_is_immutable_for_the_deal():
    d = sealed()
    out = go(d, "agency", "Eman", "SEAL 5000")
    assert "already sealed" in out[0].text and d.sealed["agency"] == 6000


def test_hold_cap_stops_boundary_probing():
    d = sealed()
    for i in range(HOLD_CAP):
        out = go(d, "agency", "agency-envoy", f"OFFER {5000 + i} probe.")
        assert "NEEDS A PERSON" in out[0].text
        go(d, "agency", "Eman", "REJECT")
    out = go(d, "agency", "agency-envoy", "OFFER 5900 probe.")
    assert "Too many held offers" in out[0].text and "agency" not in d.pending


def test_held_message_never_says_high_or_low():
    d = sealed()
    out = go(d, "agency", "agency-envoy", "OFFER 5000 x.")
    text = out[0].text.lower()
    for word in ("floor", "ceiling", "below", "above", "past", "low", "high"):
        assert word not in text


def test_reject_after_agreement_requires_fresh_offers_before_sign():
    d = sealed()
    go(d, "agency", "agency-envoy", "OFFER 8000 a.")
    go(d, "client", "client-envoy", "OFFER 8000 b.")
    assert d.agreed == 8000
    go(d, "agency", "Eman", "REJECT")
    assert d.agreed is None and d.last_offer == {} and d.signed == {}
    out = go(d, "client", "Talha", "SIGN")
    assert "no offer" in out[0].text and d.agreed is None


def test_sign_twice_is_ignored():
    d = sealed()
    go(d, "agency", "agency-envoy", "OFFER 8000 a.")
    go(d, "client", "client-envoy", "OFFER 8000 b.")
    go(d, "agency", "Eman", "SIGN")
    out = go(d, "agency", "Eman", "SIGN")
    assert "already signed" in out[0].text and not d.closed


def test_sixth_round_cannot_trigger_a_seventh():
    d = sealed()
    side = "agency"
    for i in range(6):
        go(d, side, f"{side}-envoy", f"OFFER {8000 - i} s.")
        side = "client" if side == "agency" else "agency"
    assert d.rounds == 6
    go(d, side, f"{side}-envoy", "OFFER 7000 s.")
    go(d, side, f"{side}-envoy", "OFFER 7001 s.")
    assert d.rounds == 6


def test_rejected_offer_never_reaches_the_table():
    d = sealed()
    go(d, "client", "client-envoy", "OFFER 9500 x.")
    out = go(d, "client", "Talha", "REJECT")
    assert all(a.to != "table" for a in out) and "client" not in d.last_offer


def test_agent_kind_sender_is_never_a_person():
    # main.py treats sender_kind == "agent" as not a person even with an unknown name; deal.py enforces the flag
    d = sealed()
    out = d.handle("agency", "some-other-agent", False, parse_command("SIGN"))
    assert "only a person" in out[0].text
