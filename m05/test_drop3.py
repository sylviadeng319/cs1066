### m05/test_drop3.py

import cards
from kings import Hand, drop_3
import pytest


def equal_hands(hand1, hand2):
    ''' Returns True if the two hands are equal, False otherwise. '''
    if len(hand1) != len(hand2):
        return False
    for card in hand1:
        if card not in hand2:
            return False
    return True


def test_drop_3_normal():
    #
    # Test case 1: Three matching cards
    #
    # Setup a hand and the expected outputs
    hand = Hand('Test1')
    hand += [f'2{cards.H}', f'2{cards.D}', f'2{cards.S}', f'3{cards.C}', f'4{cards.H}']
    expected_hand = [f'3{cards.C}', f'4{cards.H}']

    # Run the function under the test inputs
    top_discard = drop_3(hand)

    # Check the results
    assert(top_discard == f'2{cards.S}')
    assert equal_hands(hand, expected_hand), f"Expected {expected_hand}, but got {hand}"


def test_drop_3_exceptional():
    #
    # Test case 2: No matching cards
    #
    # Setup a hand; expected result is an exception
    hand = Hand('Test2')
    hand += [f'5{cards.H}', f'6{cards.D}', f'7{cards.S}', f'8{cards.C}', f'9{cards.H}']

    # Run the function under the test inputs and check the result
    with pytest.raises(AssertionError):
        drop_3(hand)


def test_drop_3_edge():
    #
    # Test case 3: Two matching cards
    #
    hand = Hand('Test3')
    hand += [f'10{cards.H}', f'10{cards.D}', f'A{cards.S}', f'2{cards.C}', f'J{cards.H}']
    # Run the function under the test inputs and check the result
    with pytest.raises(AssertionError):
        drop_3(hand)


    #
    # Test case 4: Four matching cards
    #
    hand = Hand('Test4')
    hand += [f'10{cards.H}', f'10{cards.D}', f'10{cards.S}', f'10{cards.C}', f'J{cards.H}']
    expected_hand = [f'10{cards.C}', f'J{cards.H}']
    top_discard = drop_3(hand)
    assert(top_discard == f'10{cards.S}')
    assert equal_hands(hand, expected_hand), f"Expected {expected_hand}, but got {hand}"
