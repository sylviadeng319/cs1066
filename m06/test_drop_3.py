import pytest

from cards import C, D, H, JOKER, S, shuffle
from kings import Hand, count_points, drop_3


@pytest.mark.parametrize(
    ("cards_in_hand", "expected_discard", "expected_hand"),
    [
        (
            [f"4{H}", f"2{D}", f"3{C}", f"2{S}", f"2{H}"],
            f"2{S}",
            [f"3{C}", f"4{H}"],
        ),
        (
            [f"10{D}", f"4{H}", f"10{S}", f"3{C}", f"10{H}"],
            f"10{S}",
            [f"3{C}", f"4{H}"],
        ),
        (
            [f"Q{C}", f"Q{D}", f"4{H}", f"Q{H}", f"Q{S}"],
            f"Q{S}",
            [f"4{H}", f"Q{C}"],
        ),
    ],
)
def test_drop_3_discards_a_matching_triple(
    cards_in_hand, expected_discard, expected_hand
):
    hand = Hand("Test")
    hand += cards_in_hand

    discarded = drop_3(hand)

    assert discarded == expected_discard
    assert sorted(hand) == sorted(expected_hand)


@pytest.mark.parametrize(
    "cards_in_hand",
    [
        [f"2{C}", f"4{D}", f"6{H}", f"8{S}", f"10{C}"],
        [f"2{C}", f"2{D}", f"4{H}", f"6{S}", f"8{C}"],
    ],
)
def test_drop_3_requires_three_matching_cards(cards_in_hand):
    hand = Hand("Test")
    hand += cards_in_hand

    with pytest.raises(AssertionError):
        drop_3(hand)


@pytest.mark.parametrize(
    "cards_in_hand",
    [
        [f"2{C}", f"3{D}", f"4{H}", f"5{S}"],
        [f"2{C}", f"3{D}", f"4{H}", f"5{S}", f"6{C}", f"7{D}"],
    ],
)
def test_drop_3_requires_five_cards(cards_in_hand):
    hand = Hand("Test")
    hand += cards_in_hand

    with pytest.raises(AssertionError):
        drop_3(hand)


def test_deck_contains_one_joker():
    deck = shuffle(mixup=False)

    assert len(deck) == 53
    assert deck.count(JOKER) == 1


def test_joker_is_worth_ten_points():
    assert count_points([JOKER]) == 10


def test_drop_3_uses_joker_with_a_pair():
    hand = Hand("Test")
    hand += [f"3{C}", f"4{D}", JOKER, f"3{S}", f"5{H}"]

    discarded = drop_3(hand)

    assert discarded in [f"3{C}", f"3{S}", JOKER]
    assert sorted(hand) == sorted([f"4{D}", f"5{H}"])


def test_drop_3_prefers_a_natural_triple_over_joker_match():
    hand = Hand("Test")
    hand += [f"2{C}", f"2{D}", f"2{H}", f"2{S}", JOKER]

    discarded = drop_3(hand)

    assert discarded in [f"2{C}", f"2{D}", f"2{H}", f"2{S}"]
    assert sorted(hand) == sorted([f"2{C}", JOKER])