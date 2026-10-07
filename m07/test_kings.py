import pytest

from cards import C, D, H, S, JOKER, shuffle
from kings import Hand, KingsGame, count_points, drop_3, drop_selected, three_match


def make_hand(cards):
    player = Hand("Test")
    for card in cards:
        player.append(card)
    return player


@pytest.mark.parametrize(
    "cards, expected_discard, expected_remaining",
    [
        # Three of a kind at the start after sorting
        (
            [f"7{C}", f"7{D}", f"7{H}", f"A{S}", f"K{C}"],
            f"7{H}",
            [f"A{S}", f"K{C}"],
        ),
        # Three of a kind at the end after sorting
        (
            [f"2{S}", f"5{C}", f"9{C}", f"9{D}", f"9{H}"],
            f"9{H}",
            [f"2{S}", f"5{C}"],
        ),
        # Pair, then three of a kind
        (
            [f"5{C}", f"5{S}", f"8{C}", f"8{D}", f"8{H}"],
            f"8{H}",
            [f"5{S}", f"5{C}"],
        ),
        # Three of a kind, then a pair
        (
            [f"5{C}", f"5{D}", f"5{H}", f"8{C}", f"8{S}"],
            f"5{H}",
            [f"8{S}", f"8{C}"],
        ),
        # Three 10s (rank is two characters; matching uses the first)
        (
            [f"10{C}", f"10{D}", f"10{H}", f"A{S}", f"2{C}"],
            f"10{H}",
            [f"2{C}", f"A{S}"],
        ),
        # Three face cards
        (
            [f"K{C}", f"K{D}", f"K{H}", f"3{S}", f"Q{C}"],
            f"K{H}",
            [f"3{S}", f"Q{C}"],
        ),
        # Four of a kind: discards the first three after sorting
        (
            [f"4{C}", f"4{D}", f"4{H}", f"4{S}", f"A{C}"],
            f"4{S}",
            [f"4{C}", f"A{C}"],
        ),
    ],
)
def test_drop_3_discards_three_matching_cards(cards, expected_discard, expected_remaining):
    player = make_hand(cards)

    discard = drop_3(player)

    assert discard == expected_discard
    assert len(player) == 2
    assert player.hand == expected_remaining


@pytest.mark.parametrize("size", [0, 1, 4, 6])
def test_drop_3_requires_exactly_five_cards(size):
    player = make_hand([f"A{S}"] * size)

    with pytest.raises(AssertionError, match="Called `drop_3` with fewer than 5 cards"):
        drop_3(player)


def test_drop_3_requires_three_matching_cards():
    player = make_hand([f"A{S}", f"2{C}", f"3{D}", f"4{H}", f"5{S}"])

    with pytest.raises(AssertionError, match="Called `drop_3` without 3 matching cards"):
        drop_3(player)


def test_drop_3_requires_three_matching_cards_with_only_pairs():
    player = make_hand([f"A{S}", f"A{C}", f"2{D}", f"2{H}", f"5{S}"])

    with pytest.raises(AssertionError, match="Called `drop_3` without 3 matching cards"):
        drop_3(player)


def test_drop_3_pair_plus_joker():
    player = make_hand([JOKER, f"A{S}", f"7{C}", f"7{D}", f"K{C}"])

    discard = drop_3(player)

    assert discard == JOKER
    assert len(player) == 2
    assert player.hand == [f"A{S}", f"K{C}"]


def test_drop_3_two_pairs_plus_joker_uses_first_pair():
    player = make_hand([JOKER, f"2{S}", f"2{C}", f"5{H}", f"5{D}"])

    discard = drop_3(player)

    assert discard == JOKER
    assert player.hand == [f"5{H}", f"5{D}"]


def test_drop_3_natural_three_preferred_over_joker():
    player = make_hand([JOKER, f"7{H}", f"7{D}", f"7{C}", f"A{S}"])

    discard = drop_3(player)

    assert discard == f"7{H}"
    assert player.hand == [JOKER, f"A{S}"]


def test_drop_3_joker_without_a_pair_raises():
    player = make_hand([JOKER, f"A{S}", f"2{C}", f"3{D}", f"4{H}"])

    with pytest.raises(AssertionError, match="Called `drop_3` without 3 matching cards"):
        drop_3(player)


def test_count_points_joker_is_ten():
    assert count_points([JOKER]) == 10
    assert count_points([JOKER, f"A{S}", f"K{C}"]) == 11


def test_deck_contains_one_joker():
    deck = shuffle(False)
    assert deck.count(JOKER) == 1
    assert len(deck) == 53


def test_three_match_natural_and_joker():
    assert three_match([f"7{C}", f"7{D}", f"7{H}"])
    assert three_match([JOKER, f"7{C}", f"7{D}"])
    assert three_match([f"10{C}", f"10{D}", f"10{H}"])
    assert not three_match([f"7{C}", f"8{D}", f"7{H}"])
    assert not three_match([JOKER, f"7{C}", f"8{D}"])


def test_drop_selected_removes_clicked_cards():
    player = make_hand([f"4{C}", f"4{D}", f"4{H}", f"4{S}", f"A{C}"])

    discard = drop_selected(player, [1, 2, 3])

    assert discard == f"4{D}"
    assert player.hand == [f"4{C}", f"A{C}"]


def test_web_game_drop_three_then_switches_player():
    game = KingsGame(vs_ai=False)
    game.player1.hand[:] = [f"7{C}", f"7{D}", f"7{H}", f"A{S}", f"K{C}"]
    state = game.drop_three('player1', [0, 1, 2])
    assert state['error'] is None
    assert state['player1']['count'] == 2
    if state['phase'] != 'over':
        assert state['turn'] == 'Player 2'


def test_web_game_stock_then_discard():
    game = KingsGame(vs_ai=True)
    assert game.state()['phase'] == 'choose'

    state = game.take_stock('player1')
    assert state['phase'] == 'discard'
    assert state['player1']['count'] == 6

    state = game.discard_card('player1', 0)
    assert state['error'] is None
    assert state['pending_ai'] or state['phase'] == 'over'

    if state['pending_ai']:
        state = game.play_ai()
        assert state['error'] is None
        assert state['turn'] == 'You' or state['phase'] == 'over'


def test_web_game_both_hands_marks_active_player():
    game = KingsGame(vs_ai=False)
    game.take_stock('player1')
    state = game.discard_card('player1', 0)
    if state['phase'] != 'over':
        assert state['turn'] == 'Player 2'
        assert state['player2']['active'] is True
        assert state['player1']['active'] is False
