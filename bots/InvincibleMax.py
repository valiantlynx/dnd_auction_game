import random
from dnd_auction_game import AuctionGameClient

def calculate_risk_factor(current_gold, round_num, total_rounds):
    """Dynamically adjust the risk factor based on the round number."""
    # Increase the bid aggressiveness as the game progresses
    if round_num / total_rounds > 0.75:
        return 0.8  # Be more aggressive in the last quarter of the game
    elif round_num / total_rounds > 0.5:
        return 0.30  # Medium aggressiveness in the middle of the game
    else:
        return 0.10  # Be conservative in the early game


def optimal_bid2(agent_id: str, states: dict, auctions: dict, prev_auctions: dict, round_num, total_rounds):
    """Optimal bid strategy with added risk management and adaptive bidding."""

    # Agent state and available gold
    agent_state = states[agent_id]
    current_gold = agent_state["gold"]

    # Risk factor adjustment
    max_gold_fraction = calculate_risk_factor(current_gold, round_num, total_rounds)

    bids = {}

    for auction_id, auction_info in auctions.items():
        # Extract dice parameters for this auction
        dice_size = auction_info.get('die', 6)  # Default to D6 if dice size is missing
        num_rolls = auction_info.get('num', 1)  # Number of dice rolls
        bonus = auction_info.get('bonus', 0)  # Flat bonus for the auction

        # Estimate the auction value based on dice size and rolls
        auction_value = auction_value_estimate(dice_size, num_rolls, bonus)

        # Calculate how much gold to bid based on estimated auction value and risk factor
        bid = min(current_gold, int(auction_value / (dice_size * num_rolls) * current_gold * max_gold_fraction))

        # Ensure the bot doesn't bid zero and avoids overbidding
        bid = max(1, min(bid, current_gold))

        # Place the bid if enough gold is available
        if bid <= current_gold:
            bids[auction_id] = bid
            current_gold -= bid

    return bids


if __name__ == "__main__":

    host = "localhost"
    agent_name = ("InvincibleMax{}".format(random.randint(1,100)))
    player_id = "Invincible_001"
    port = 8001

    game = AuctionGameClient(host=host,
                             agent_name=agent_name,
                             player_id=player_id,
                             port=port)

    total_rounds = 100  # Assuming a 12-round game, can be adjusted based on the server settings

    try:
        # Use a loop to run the bot for each round
        for round_num in range(1, total_rounds + 1):
            game.run(optimal_bid2)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")

    print("<game is done>")
