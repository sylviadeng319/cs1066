### m06/kings.py
from cards import JOKER, shuffle

class Hand(object):
    '''Simple class that defines a player's hand'''
    def __init__(self, name):
        self.name = name
        self.hand = []     # will be a list of cards

    def __iadd__(self, other):
        self.hand += other
        return self

    def __iter__(self):
        return self.hand.__iter__()

    def __len__(self):
        return len(self.hand)

    def __str__(self):
        # Creates a string of the hand list
        return self.hand.__str__()

    def append(self, card):
        # Adds card to the end of the hand list
        self.hand.append(card)

    def pop(self, i):
        # Removes card at index i in hand
        return self.hand.pop(i)

rules = '''The object of this game is to be the first to have 5 or fewer points
in your hand. The point values for each card are as follows:

  * Aces are 1 point.
  * Numbered cards have their face value in points.
  * Jacks and Queens are 10 points.
  * Kings are 0 points.

There are two players in the game, and each is dealt 5 cards.
The remaining cards form the stock pile. The top card on the
stock pile is turned over to create the discard pile.

The first player begins by choosing to pick up the top card
on the stock or discard pile. They then select a card from
their hand to discard, and they place it face-up on the
discard pile.

If at the start of a player's turn, the player has three
cards in their hand with the same face value, they may skip
taking a new card and directly discard the three matching
cards. This play will leave them with just two cards,
instead of five, in their hand.

At the end of a player's turn, if the point value of a
player's hand is 5 or less, they shout "I am King" and
the game is over.
'''

###
# Functions called by `main`
###

def print_directions():
    print('### WELCOME TO THE KINGS CARD GAME ###')
    print()
    print(rules)

def winner(p1, p2):
    '''Determines which player won. If no winner yet, returns False.'''
    p1_points = count_points(p1)
    p2_points = count_points(p2)

    if p1_points > 5 and p2_points > 5:
        # No winner yet
        return False

    # Figure out which player won
    if p1_points == p2_points:
        print('GAME OVER: shuffle produced a tie!')
    elif p1_points > p2_points:
        print(f'GAME OVER: With {p2_points} points, {p2.name} is KING!')
    else:
        print(f'GAME OVER: With {p1_points} points, {p1.name} is KING!')
    return True

def take_turn(player, deck, discard):
    '''Mostly the logic for a human player, but it does call `ai`
       if it's an AI's turn.'''
    print()
    if player.name == 'AI':
        return ai(player, deck, discard)

    # Otherwise, it's a human player's turn
    print(f"{player.name}'s turn ... Press return when ready", end=' ')
    input()
    print(f'Your hand: {player}')
    print(f'Discard: {discard}')
    print()

    # Ask for and validate the player's next move
    while True:
        move = input('What do you want to do: s, d, 3? ')
        if move in ['s', 'd', '3']:
            break
        else:
            print('You must choose:')
            print('  * take from [s]tock pile')
            print('  * take from [d]iscard pile')
            print('  * discard [3] cards')

    # Update the player's hand if they've chosen to draw a card
    if move == 's':
        player.append(deck.pop(0))
        print(f'Your updated hand is: {player}')
    elif move == 'd':
        player.append(discard)
        print(f'Your updated hand is: {player}')

    # Update the player's hand based on their discard choice
    if move == '3':
        discard = drop_3(player)
    else:
        index = select_card(player)
        discard = player.pop(index)

    print(f'Your updated hand is: {player}')

    return discard

##
# Helper functions for `take_turn` and `winner`
##

def ai(player, deck, discard):
    ''' Very dumb AI'''
    # Used by AI to sort its hand
    def my_key(item):
        return count_points([item])

    # Dumb AI: it always takes a stock card
    player.append(deck.pop(0))

    # Sort the cards by rank and discards the highest ranked card
    player.hand.sort(key=my_key)
    discard = player.pop(5)

    print(f'AI took from the stock pile and discarded a {discard}')

    return discard

def count_points(player_hand):
    ''' Given a player's hand (i.e., a list of cards), returns
        the point total.'''
    points = 0
    for card in player_hand:
        if card == JOKER:
            points += 10
            continue
        rank = card[0]
        if rank == 'A':
            points += 1
        elif rank == 'Q' or rank == 'J' or rank == '1':
            points += 10
        elif rank == 'K':
            pass
        else:
            points += int(rank)
    return points

def drop_3(player):
    ''' Given a hand with 5 cards, drop the three that match and
        return the last of the three matching as the discard card. '''
    assert len(player) == 5, 'Called `drop_3` with fewer than 5 cards'

    player.hand.sort()
    cards_by_rank = {}
    for card in player:
        if card != JOKER:
            cards_by_rank.setdefault(card[0], []).append(card)

    matching_cards = None
    for cards_of_rank in cards_by_rank.values():
        if len(cards_of_rank) >= 3:
            matching_cards = cards_of_rank[:3]
            break

    if matching_cards is None and JOKER in player.hand:
        for cards_of_rank in cards_by_rank.values():
            if len(cards_of_rank) >= 2:
                matching_cards = cards_of_rank[:2] + [JOKER]
                break

    if matching_cards is None:
        assert False, 'Called `drop_3` without 3 matching cards'

    for card in matching_cards:
        player.hand.remove(card)
    return matching_cards[0]

def select_card(player):
    '''Asks player for the rank of a card to discard and
       verifies the response. Returns the index of the first
       card in the player's hand with that rank.'''
    while True:
        rank = input('What is the rank of the card you want to discard? ')
        if rank != '10' and rank not in 'A23456789JQK':
            print('Bad card rank. Try again ...')
            continue

        for i, card in enumerate(player):
            if card[0] == rank[0]:
                return i
        else:
            print('Card rank not in hand. Try again ...')
            continue

def main():
    ans = input('Do you need directions? ')
    if ans != '' and ans.lower()[0] == 'y':
        print_directions()

    # Create players
    player1 = Hand('Human')   # always a human

    ans = input('Do you want to play against an AI? ')
    if ans != '' and ans.lower()[0] == 'y':
        player2 = Hand('AI')
    else:
        player2 = Hand('Other Human')

    # Create the deck and shuffle it
    deck = shuffle()

    # Deal cards to the two players
    for _ in range(5):
        player1.append(deck.pop(0))
        player2.append(deck.pop(0))

    # Create discard pile. We keep only the top card
    # on the discard pile.
    discard = deck.pop(0)

    # Set game loop to start with player1
    turn = player1

    while not winner(player1, player2):             # game loop
        # Game ends in a tie when we run out of stock cards
        if len(deck) == 0:
            print('No more cards. No winner. :-(')

        # The next player takes their turn
        discard = take_turn(turn, deck, discard)

        # Switch to the other player
        if turn == player1:
            turn = player2
        else:
            turn = player1

if __name__ == '__main__':
    main()
