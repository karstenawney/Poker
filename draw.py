import random
from collections import Counter

# Define Suits and Ranks
SUITS = ["h", "d", "c", "s"]
RANKS = list(range(2, 15))  # 2 to 14 (where 14 is Ace)


def evaluate_5card_hand(hand):
    """Evaluates a 5-card hand and returns a tuple that can be used for direct comparison.

    Higher tuples indicate stronger hands.
    """
    ranks = sorted([card[0] for card in hand], reverse=True)
    suits = [card[1] for card in hand]

    is_flush = len(set(suits)) == 1
    # Check for straight (including A-2-3-4-5 low straight)
    is_straight = len(set(ranks)) == 5 and (max(ranks) - min(ranks) == 4)
    if ranks == [14, 5, 4, 3, 2]:
        is_straight = True
        ranks = [5, 4, 3, 2, 1]  # Re-rank Ace as low

    counts = Counter(ranks)
    # Sort counts by frequency first, then by rank value
    sorted_counts = sorted(
        counts.items(), key=lambda x: (x[1], x[0]), reverse=True
    )

    frequencies = [item[1] for item in sorted_counts]
    value_order = [item[0] for item in sorted_counts]

    # Hand Categories (8: Straight Flush down to 0: High Card)
    if is_straight and is_flush:
        hand_type = 8
    elif frequencies == [4, 1]:
        hand_type = 7  # Four of a kind
    elif frequencies == [3, 2]:
        hand_type = 6  # Full House
    elif is_flush:
        hand_type = 5  # Flush
    elif is_straight:
        hand_type = 4  # Straight
    elif frequencies == [3, 1, 1]:
        hand_type = 3  # Three of a kind
    elif frequencies == [2, 2, 1]:
        hand_type = 2  # Two Pair
    elif frequencies == [2, 1, 1, 1]:
        hand_type = 1  # One Pair
    else:
        hand_type = 0  # High Card

    return (hand_type, value_order)


def simulate_poker_win_rate(my_hand, num_players, num_simulations=1000):
    """Simulates 5-card poker games to calculate win probability.

    :param my_hand: List of 5 tuples, e.g., [(14, 's'), (13, 's'), (12, 's'),
    (11, 's'), (10, 's')]
    :param num_players: Total number of players at the table (including yourself)
    :param num_simulations: Number of games to simulate (default 1000)
    :return: Float representing probability of winning (0.0 to 1.0)
    """
    # Create a full deck of 52 cards
    full_deck = [(r, s) for r in RANKS for s in SUITS]

    # Remove cards already in hand
    remaining_deck = [card for card in full_deck if card not in my_hand]

    my_score = evaluate_5card_hand(my_hand)
    wins = 0

    for _ in range(num_simulations):
        # Shuffle remaining cards for this trial
        deck = remaining_deck.copy()
        random.shuffle(deck)

        # Deal 5 cards to each opponent
        num_opponents = num_players - 1
        opponents_best_score = None

        for _ in range(num_opponents):
            opponent_hand = [deck.pop() for _ in range(5)]
            opponent_score = evaluate_5card_hand(opponent_hand)

            if (
                opponents_best_score is None
                or opponent_score > opponents_best_score
            ):
                opponents_best_score = opponent_score

        # Check if user's hand beats all opponents
        if my_score > opponents_best_score:
            wins += 1
        elif my_score == opponents_best_score:
            wins += 0.5  # Split pot / Tie handling

    return wins / num_simulations

hand = []
for i in range(5):
    number = int(input("Card Number (2-14): "))
    suit = input("Card Suit (h, d, c, s): ")
    hand.append((number, suit))
cont = "y"
while cont == "y":
    players = int(input("Number of players (Including yourself): "))
    pot = float(input("Value of the pot: "))
    share = float(input("Value of your share of the pot: "))
    p_win = simulate_poker_win_rate(hand, players)
    outcome = p_win * (pot + share) - share
    print (outcome)
    if outcome < 0:
        print ("Recommend Folding")
    else:
        print ("Recommend Checking")
    cont = input("Another Betting Round? (Y/n): ").lower()