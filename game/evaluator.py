from collections import Counter

# Define hand rankings
HAND_RANKINGS = {
    "High Card": 1,
    "One Pair": 2,
    "Two Pair": 3,
    "Three of a Kind": 4,
    "Straight": 5,
    "Flush": 6,
    "Full House": 7,
    "Four of a Kind": 8,
    "Straight Flush": 9,
    "Royal Flush": 10,
}


def evaluate_hand(hand):
    rank_map = {
        "02": 2,
        "03": 3,
        "04": 4,
        "05": 5,
        "06": 6,
        "07": 7,
        "08": 8,
        "09": 9,
        "10": 10,
        "J": 11,
        "Q": 12,
        "K": 13,
        "A": 14,
    }

    # Extract ranks and suits from the string-based cards (e.g., '2H', 'AS')
    ranks = [
        rank_map[card[:-1]] for card in hand
    ]  # Rank is everything except the last character
    suits = [card[-1] for card in hand]  # Suit is the last character

    sorted_ranks = sorted(ranks)

    # Handle low-Ace straight (A, 2, 3, 4, 5)
    if sorted_ranks == [2, 3, 4, 5, 14]:
        sorted_ranks = [1, 2, 3, 4, 5]  # Treat Ace as 1 for this straight

    is_straight = all(
        sorted_ranks[i] + 1 == sorted_ranks[i + 1] for i in range(len(sorted_ranks) - 1)
    )
    rank_counts = Counter(ranks)
    is_flush = len(set(suits)) == 1

    if is_straight and is_flush:
        return (HAND_RANKINGS["Straight Flush"], sorted_ranks[-1])
    if 4 in rank_counts.values():
        return (HAND_RANKINGS["Four of a Kind"], max(rank_counts, key=rank_counts.get))
    if 3 in rank_counts.values() and 2 in rank_counts.values():
        return (HAND_RANKINGS["Full House"], max(rank_counts, key=rank_counts.get))
    if is_flush:
        return (HAND_RANKINGS["Flush"], sorted_ranks[-1])
    if is_straight:
        return (HAND_RANKINGS["Straight"], sorted_ranks[-1])
    if 3 in rank_counts.values():
        return (HAND_RANKINGS["Three of a Kind"], max(rank_counts, key=rank_counts.get))
    if list(rank_counts.values()).count(2) == 2:
        return (HAND_RANKINGS["Two Pair"], max(rank_counts, key=rank_counts.get))
    if 2 in rank_counts.values():
        return (HAND_RANKINGS["One Pair"], max(rank_counts, key=rank_counts.get))
    return (HAND_RANKINGS["High Card"], sorted_ranks[-1])


def compare_hands(hand1, hand2):
    rank1, high_card1 = evaluate_hand(hand1)
    rank2, high_card2 = evaluate_hand(hand2)

    if rank1 > rank2:
        return 1
    elif rank1 < rank2:
        return -1
    else:
        # Tie-breaking by high card
        if high_card1 > high_card2:
            return 1
        elif high_card1 < high_card2:
            return -1
        else:
            # Additional tie-breaking for more complex cases
            sorted_hand1 = sorted([card[:-1] for card in hand1], reverse=True)
            sorted_hand2 = sorted([card[:-1] for card in hand2], reverse=True)
            for card1, card2 in zip(sorted_hand1, sorted_hand2):
                if card1 != card2:
                    return 1 if card1 > card2 else -1
            return 0  # Hands are identical


def determine_winner(players, community_cards):
    best_hand = None
    winners = []

    for player in players:
        hand = player.hand + community_cards
        if best_hand is None:
            best_hand = hand
            winners = [player]
        else:
            comparison = compare_hands(hand, best_hand)
            if comparison > 0:
                best_hand = hand
                winners = [player]
            elif comparison == 0:
                winners.append(player)

    if len(winners) == 1:
        return winners[0]
    return winners  # Return all winners in case of a tie
