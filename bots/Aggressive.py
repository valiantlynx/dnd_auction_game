def aggressive_bid(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    die_sizes = [2, 3, 4, 6, 8, 10, 12, 20]

    def auction_value_estimate(dice_size):
        """Estimate the expected auction value based on the dice size."""
        # The average value for any dice is (1 + max_value) / 2
        return (1 + dice_size) / 2
    agent_state = states[agent_id]
    current_gold = agent_state["gold"]

    max_gold_fraction = 0.50  # Aggressive bot spends 50% of gold each round

    bids = {}

    for auction_id, auction_info in auctions.items():
        dice_type = auction_info.get('dice_type', 3)
        dice_size = die_sizes[dice_type]
        auction_value = auction_value_estimate(dice_size)

        bid = min(current_gold, int(auction_value / max(die_sizes) * current_gold * max_gold_fraction))
        bid = max(1, min(bid, current_gold))

        if bid <= current_gold:
            bids[auction_id] = bid
            current_gold -= bid

    return bids
