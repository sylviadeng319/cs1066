### m07/kings.py
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
  * Jacks, Queens, and the Joker are 10 points.
  * Kings are 0 points.

There are two players in the game, and each is dealt 5 cards.
The remaining cards form the stock pile. The top card on the
stock pile is turned over to create the discard pile.

The first player begins by choosing to pick up the top card
on the stock or discard pile. They then select a card from
their hand to discard, and they place it face-up on the
discard pile.

If at the start of a player's turn, the player has three
cards in their hand with the same face value (the Joker may
count as any rank), they may skip taking a new card and
directly discard the three matching cards. This play will
leave them with just two cards, instead of five, in their
hand.

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

def ai(player, deck, discard, verbose=True):
    ''' Very dumb AI'''
    # Used by AI to sort its hand
    def my_key(item):
        return count_points([item])

    # Dumb AI: it always takes a stock card
    player.append(deck.pop(0))

    # Sort the cards by rank and discards the highest ranked card
    player.hand.sort(key=my_key)
    discard = player.pop(5)

    if verbose:
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

# def count_points(player_hand):
#     ''' Given a player's hand (i.e., a list of cards), returns
#         the point total.'''
#     points = 0
#     for card in player_hand:
#         rank = card[0]
#         if rank == 'K':
#             pass
#         elif rank == 'A':
#             points += 1
#         elif rank in '23456789':
#             points += int(rank)
#         else:
#             points += 10
#     return points

def drop_3(player):
    ''' Given a hand with 5 cards, drop the three that match and
        return the last of the three matching as the discard card.
        The joker is a wildcard and can match any rank. '''
    assert len(player) == 5, 'Called `drop_3` with fewer than 5 cards'

    # Sort the hand to make it easy to find the three matching cards
    player.hand.sort()

    indices = _matching_three_indices(player)
    assert indices is not None, 'Called `drop_3` without 3 matching cards'

    # Remove highest index first so the remaining cards keep their order
    discard = None
    for i in sorted(indices, reverse=True):
        discard = player.pop(i)
    return discard


def _matching_three_indices(player):
    '''Return indices of three matching cards, or None.

    Prefers a natural three-of-a-kind. Otherwise a pair plus the joker.
    '''
    last_card_rank = '0'
    count = 0
    run_start = 0
    first_pair = None

    for i, card in enumerate(player):
        if card == JOKER:
            last_card_rank = '0'
            count = 0
            continue

        if card[0] == last_card_rank:
            count += 1
            if count == 2 and first_pair is None:
                first_pair = [run_start, i]
            if count == 3:
                return [run_start, run_start + 1, run_start + 2]
        else:
            last_card_rank = card[0]
            count = 1
            run_start = i

    joker_at = next((i for i, card in enumerate(player) if card == JOKER), None)
    if first_pair is not None and joker_at is not None:
        return first_pair + [joker_at]
    return None


def three_match(cards):
    '''True if three cards share a rank. The joker matches any rank.'''
    if len(cards) != 3:
        return False
    ranks = [card[0] for card in cards if card != JOKER]
    if not ranks:
        return True
    return all(rank == ranks[0] for rank in ranks)


def drop_selected(player, indices):
    '''Drop three matching cards chosen by index; return the discard card.'''
    assert len(player) == 5, 'Called `drop_3` with fewer than 5 cards'
    unique = sorted(set(indices))
    assert len(unique) == 3, 'Called `drop_3` without 3 matching cards'
    assert all(0 <= i < len(player) for i in unique), 'Called `drop_3` without 3 matching cards'
    cards = [player.hand[i] for i in unique]
    assert three_match(cards), 'Called `drop_3` without 3 matching cards'

    discard = None
    for i in sorted(unique, reverse=True):
        discard = player.pop(i)
    return discard

def select_card(player):
    '''Asks player for the rank of a card to discard and
       verifies the response. Returns the index of the first
       card in the player's hand with that rank.'''
    while True:
        rank = input('What is the rank of the card you want to discard? ')
        if rank.lower() in ('*', 'joker'):
            for i, card in enumerate(player):
                if card == JOKER:
                    return i
            print('Card rank not in hand. Try again ...')
            continue

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

class KingsGame:
    '''Browser-playable Kings game. Actions are clicks on piles or cards.'''

    def __init__(self, vs_ai=True):
        self.vs_ai = vs_ai
        self.player1 = Hand('You' if vs_ai else 'Player 1')
        self.player2 = Hand('AI' if vs_ai else 'Player 2')
        self.deck = shuffle()
        for _ in range(5):
            self.player1.append(self.deck.pop(0))
            self.player2.append(self.deck.pop(0))
        self.discard = self.deck.pop(0)
        self.turn = self.player1
        self.phase = 'choose'   # choose | discard | over
        self.pending_ai = False
        self.last_ai = None
        self.winner_text = None
        self._set_choose_message()
        self._check_winner()

    def _set_choose_message(self):
        self.message = (
            f"{self.turn.name}'s turn: click the stock or discard pile, "
            'or click three matching cards to drop them.'
        )

    def _pack_hand(self, player, hide=False):
        return {
            'name': player.name,
            'hand': (['back'] * len(player)) if hide else list(player.hand),
            'count': len(player),
            'points': None if hide else count_points(player),
            'active': player is self.turn and self.phase != 'over',
        }

    def state(self, error=None):
        hide_ai = self.vs_ai and self.phase != 'over'
        return {
            'vs_ai': self.vs_ai,
            'phase': self.phase,
            'turn': self.turn.name,
            'player1': self._pack_hand(self.player1),
            'player2': self._pack_hand(self.player2, hide=hide_ai),
            'stock_count': len(self.deck),
            'discard': self.discard,
            'message': self.message,
            'winner': self.winner_text,
            'error': error,
            'last_ai': self.last_ai,
            'pending_ai': self.pending_ai,
        }

    def _current_is(self, player_key):
        if player_key == 'player1':
            return self.turn is self.player1
        if player_key == 'player2':
            return self.turn is self.player2
        return False

    def take_stock(self, player_key):
        if self.phase != 'choose' or self.pending_ai:
            return self.state('It is not time to take a card.')
        if not self._current_is(player_key):
            return self.state("It is not that player's turn.")
        if not self.deck:
            return self.state('The stock pile is empty.')
        self.turn.append(self.deck.pop(0))
        self.phase = 'discard'
        self.message = f"{self.turn.name}: click a card to discard."
        return self.state()

    def take_discard(self, player_key):
        if self.phase != 'choose' or self.pending_ai:
            return self.state('It is not time to take a card.')
        if not self._current_is(player_key):
            return self.state("It is not that player's turn.")
        if self.discard is None:
            return self.state('The discard pile is empty.')
        self.turn.append(self.discard)
        self.discard = None
        self.phase = 'discard'
        self.message = f"{self.turn.name}: click a card to discard."
        return self.state()

    def drop_three(self, player_key, indices):
        if self.phase != 'choose' or self.pending_ai:
            return self.state('It is not time to drop three cards.')
        if not self._current_is(player_key):
            return self.state("It is not that player's turn.")
        try:
            indices = [int(i) for i in indices]
            self.discard = drop_selected(self.turn, indices)
        except AssertionError as exc:
            msg = str(exc)
            if 'fewer than 5' in msg:
                return self.state('You need five cards to drop three.')
            return self.state('Those three cards do not match in rank.')
        except (TypeError, IndexError, ValueError):
            return self.state('Select three matching cards.')
        return self._end_turn()

    def discard_card(self, player_key, index):
        if self.phase != 'discard' or self.pending_ai:
            return self.state('It is not time to discard a card.')
        if not self._current_is(player_key):
            return self.state("It is not that player's turn.")
        try:
            index = int(index)
        except (TypeError, ValueError):
            return self.state('Click a card in your hand to discard it.')
        if index < 0 or index >= len(self.turn):
            return self.state('Click a card in your hand to discard it.')
        self.discard = self.turn.pop(index)
        return self._end_turn()

    def _end_turn(self):
        if self._check_winner():
            return self.state()

        self.turn = self.player2 if self.turn is self.player1 else self.player1
        self.phase = 'choose'
        self.last_ai = None

        if self.vs_ai and self.turn is self.player2:
            self.pending_ai = True
            self.message = 'AI is taking a turn...'
            return self.state()

        self._set_choose_message()
        return self.state()

    def play_ai(self):
        if not self.pending_ai or self.turn is not self.player2:
            return self.state('The AI is not waiting to play.')

        self.pending_ai = False
        if len(self.deck) == 0:
            self.phase = 'over'
            self.winner_text = 'No more cards. No winner.'
            self.message = self.winner_text
            return self.state()

        self.discard = ai(self.player2, self.deck, self.discard, verbose=False)
        self.last_ai = f'AI took from the stock pile and discarded {self.discard}'

        if self._check_winner():
            return self.state()

        self.turn = self.player1
        self.phase = 'choose'
        self._set_choose_message()
        return self.state()

    def _check_winner(self):
        p1_points = count_points(self.player1)
        p2_points = count_points(self.player2)
        if p1_points > 5 and p2_points > 5:
            return False

        self.phase = 'over'
        self.pending_ai = False
        if p1_points == p2_points:
            self.winner_text = 'GAME OVER: shuffle produced a tie!'
        elif p1_points > p2_points:
            self.winner_text = (
                f'GAME OVER: With {p2_points} points, {self.player2.name} is KING!'
            )
        else:
            self.winner_text = (
                f'GAME OVER: With {p1_points} points, {self.player1.name} is KING!'
            )
        self.message = self.winner_text
        return True


if __name__ == '__main__':
    import sys
    if '--web' in sys.argv:
        from web_kings import run_server
        run_server()
    else:
        main()
