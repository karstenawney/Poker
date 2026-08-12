from collections import Counter
import itertools
import random

# Define Suits and Ranks
SUITS = ["h", "d", "c", "s"]  # Hearts, Diamonds, Clubs, Spades
RANKS = list(range(2, 15))  # 2 to 14 (11: J, 12: Q, 13: K, 14: A)


def evaluate_5card_hand(hand):
    """Evaluates a strict 5-card hand and returns a ranking tuple for comparison."""
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
        hand_type = 7  # Four of a Kind
    elif frequencies == [3, 2]:
        hand_type = 6  # Full House
    elif is_flush:
        hand_type = 5  # Flush
    elif is_straight:
        hand_type = 4  # Straight
    elif frequencies == [3, 1, 1]:
        hand_type = 3  # Three of a Kind
    elif frequencies == [2, 2, 1]:
        hand_type = 2  # Two Pair
    elif frequencies == [2, 1, 1, 1]:
        hand_type = 1  # One Pair
    else:
        hand_type = 0  # High Card

    return (hand_type, value_order)


def evaluate_best_hand(cards):
    """Evaluates the best 5-card combination out of 5 to 7 available cards."""
    if len(cards) < 5:
        raise ValueError("Need at least 5 cards to evaluate a hand.")

    best_score = None
    for combo in itertools.combinations(cards, 5):
        score = evaluate_5card_hand(combo)
        if best_score is None or score > best_score:
            best_score = score
    return best_score


def simulate_poker_equity(
    hole_cards, community_cards, num_players, num_simulations=1000
):
    """Simulates games to calculate equity based on current hole/community cards."""
    known_cards = set(hole_cards + community_cards)
    full_deck = [(r, s) for r in RANKS for s in SUITS]
    remaining_deck = [card for card in full_deck if card not in known_cards]

    cards_needed_on_board = 5 - len(community_cards)
    num_opponents = num_players - 1
    
    # Check deck sufficiency (2 cards per opponent + missing board cards)
    total_needed = cards_needed_on_board + (num_opponents * 2)
    if len(remaining_deck) < total_needed:
        raise ValueError("Too many players for the remaining deck size.")

    wins = 0

    for _ in range(num_simulations):
        deck = remaining_deck.copy()
        random.shuffle(deck)

        # Deal missing community cards
        board = community_cards + [
            deck.pop() for _ in range(cards_needed_on_board)
        ]

        # Evaluate player hand
        my_score = evaluate_best_hand(hole_cards + board)

        # Deal opponent hands and evaluate
        opponents_best_score = None
        for _ in range(num_opponents):
            opp_hole = [deck.pop(), deck.pop()]
            opp_score = evaluate_best_hand(opp_hole + board)

            if (
                opponents_best_score is None
                or opp_score > opponents_best_score
            ):
                opponents_best_score = opp_score

        # Determine winner
        if my_score > opponents_best_score:
            wins += 1.0
        elif my_score == opponents_best_score:
            wins += 0.5  # Split pot

    return wins / num_simulations


def parse_card_input(prompt_text):
    """Helper to parse user input into card tuples, e.g., '14 s' or '10h'."""
    while True:
        raw = input(prompt_text).strip().lower().replace(",", " ")
        parts = raw.split()

        if len(parts) == 1 and len(parts[0]) >= 2:
            suit = parts[0][-1]
            rank_str = parts[0][:-1]
        elif len(parts) == 2:
            rank_str, suit = parts[0], parts[1]
        else:
            print("Invalid input format. Try '14 s' or 'Ah' or '10 h'.")
            continue

        rank_map = {"a": 14, "k": 13, "q": 12, "j": 11, "10": 10}
        rank = rank_map.get(rank_str, None)
        if rank is None:
            try:
                rank = int(rank_str)
            except ValueError:
                pass

        if rank in RANKS and suit in SUITS:
            return (rank, suit)
        else:
            print("Invalid card. Rank must be 2-14 (or A, K, Q, J) and suit h, d, c, s.")


def get_action_recommendation(equity, current_pot, call_amount):
    """Calculates Pot Odds, Expected Value (EV), and generates actions."""
    total_pot_if_called = current_pot + call_amount

    if call_amount == 0:
        pot_odds = 0.0
        # When calling $0, EV is simply winning your equity share of current pot
        ev = equity * current_pot
    else:
        pot_odds = call_amount / total_pot_if_called
        # Correct EV Formula: (Equity * Total Pot Won) - Call Amount
        ev = (equity * total_pot_if_called) - call_amount

    # Decision Matrix
    if call_amount == 0:
        if equity > 0.65:
            rec = "RAISE / VALUE BET"
            reason = f"Strong equity ({equity:.1%}). Build the pot."
        elif equity > 0.35:
            rec = "CHECK"
            reason = f"Moderate equity ({equity:.1%}). See free card."
        else:
            rec = "CHECK (or Fold to future bets)"
            reason = f"Weak equity ({equity:.1%}). Play cautiously."
    else:
        if equity > pot_odds + 0.15:
            rec = "RAISE"
            reason = f"Equity ({equity:.1%}) significantly exceeds Pot Odds ({pot_odds:.1%}). Positive EV: +${ev:.2f}"
        elif equity >= pot_odds:
            rec = "CALL"
            reason = f"Equity ({equity:.1%}) covers Pot Odds ({pot_odds:.1%}). Positive EV: +${ev:.2f}"
        else:
            rec = "FOLD"
            reason = f"Equity ({equity:.1%}) below Pot Odds ({pot_odds:.1%}). Negative EV: -${abs(ev):.2f}"

    return rec, reason, pot_odds, ev


def main():
    print("==================================================")
    print("     TEXAS HOLD'EM DECISION & EQUITY ENGINE       ")
    print("==================================================")

    # 1. Get Hole Cards (2 cards)
    print("\nEnter your 2 Hole Cards:")
    card1 = parse_card_input(" Card 1 (e.g. '14 s' or 'Ah'): ")
    card2 = parse_card_input(" Card 2 (e.g. '13 s' or 'Ks'): ")
    hole_cards = [card1, card2]

    # Map stage names to target total community cards
    stage_card_counts = {
        "Pre-Flop": 0,
        "Flop": 3,
        "Turn": 4,
        "River": 5,
    }
    
    community_cards = []
    rounds = ["Pre-Flop", "Flop", "Turn", "River"]
    round_idx = 0

    while round_idx < len(rounds):
        stage = rounds[round_idx]
        target_card_count = stage_card_counts[stage]
        
        # Trim community_cards if the user backed up a stage
        community_cards = community_cards[:target_card_count]

        print(f"\n--- CURRENT STAGE: {stage.upper()} ---")
        num_players = int(input("\nTotal players remaining at table (including you): "))

        # Prompt only for missing community cards
        cards_to_add = target_card_count - len(community_cards)
        if cards_to_add > 0:
            print(f"Enter {cards_to_add} community card(s):")
            for _ in range(cards_to_add):
                community_cards.append(parse_card_input(" Card: "))

        pot = float(input("\nCurrent total pot size ($): "))
        call_amount = float(input("Amount to call/bet to stay in ($0 if check): "))

        print("\nCalculating Equity (running 1,500 simulations)...")
        try:
            equity = simulate_poker_equity(
                hole_cards, community_cards, num_players, num_simulations=1500
            )
        except ValueError as e:
            print(f"Error during simulation: {e}")
            break

        rec, reason, pot_odds, ev = get_action_recommendation(
            equity, pot, call_amount
        )

        # Output Results
        print("\n" + "=" * 45)
        print(f"  Hand Equity:   {equity:.2%}")
        if call_amount > 0:
            print(f"  Pot Odds:      {pot_odds:.2%}")
            print(f"  Expected Value: ${ev:+.2f}")
        print(f"  RECOMMENDATION: {rec}")
        print(f"  REASON:         {reason}")
        print("=" * 45)

        if round_idx < len(rounds) - 1:
            cont = input("\nBetting over? (Y/n): ").strip().lower()
            if cont == "n":
                # Go back one stage
                round_idx = max(0, round_idx - 1)
                continue
        round_idx += 1


if __name__ == "__main__":
    main()