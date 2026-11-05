import pytest

from clerk.rules import check_limit, overlap, scan_for_leaks


@pytest.mark.parametrize("clean", [
    "Revision rounds and a kickoff call included.",
    "We can sign this week.",
    "That's our best and final.",
    "Includes a kickoff call and weekly updates.",
])
def test_clean_sentences_pass(clean):
    assert scan_for_leaks(clean) == []


@pytest.mark.parametrize("leaky", [
    "Honestly we can't go under 6k.",
    "Our floor is firm.",
    "We can't go below six thousand.",
    "Sixty hundred is where we stop.",
    "Anything under 6,0,0,0 is a no.",
    "Our budget caps out soon.",
    "That's the most we are authorised to pay.",
    "Just a grand more.",
    "We'd walk at that price.",
    "Nothing above 9000.",
])
def test_leaky_sentences_are_caught(leaky):
    assert scan_for_leaks(leaky), leaky


def test_reasons_are_readable():
    reasons = scan_for_leaks("Our floor is six thousand, or 6000.")
    assert any("second number" in r for r in reasons)
    assert any("spells out" in r for r in reasons)
    assert any("limit" in r for r in reasons)


def test_check_limit_agency_floor():
    assert check_limit("agency", 6000, 6000) == "ok"
    assert check_limit("agency", 6001, 6000) == "ok"
    assert check_limit("agency", 5999, 6000) == "past_limit"


def test_check_limit_client_ceiling():
    assert check_limit("client", 9000, 9000) == "ok"
    assert check_limit("client", 8999, 9000) == "ok"
    assert check_limit("client", 9001, 9000) == "past_limit"


def test_check_limit_unknown_side():
    with pytest.raises(ValueError):
        check_limit("table", 1, 1)


def test_overlap():
    assert overlap(6000, 9000)
    assert overlap(7000, 7000)
    assert not overlap(9001, 9000)
