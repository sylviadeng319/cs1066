### m07/cards.py
import random

# Define card suits
C = '\u2663'
D = '\u2662'
H = '\u2661'
S = '\u2660'
suits = [C, D, H, S]

# Build a list of card ranks
ranks = [str(n) for n in range(2, 11)]
ranks += ['J', 'Q', 'K', 'A']

# A single wildcard; first character must not collide with 2-10, J, Q, K, or A
JOKER = '*'

def shuffle(mixup=True):
    '''Returns sorted or unsorted (i.e., mixed-up) deck of cards '''
    # Build a full deck of cards, plus one joker
    deck = [rank + suit for suit in suits for rank in ranks]
    deck.append(JOKER)

    if mixup:
        # Shuffle the deck
        random.shuffle(deck)

    return deck

def main():
    print('Sorted deck:')
    print(shuffle(False))
    
    print('Shuffled deck:')
    print(shuffle(True))

if __name__ == '__main__':
    main()
