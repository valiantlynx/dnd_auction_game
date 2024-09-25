import random
import os
from dnd_auction_game import AuctionGameClient

############################################################################################
#
# optimal_bid
#   Bids strategically based on expected value of auctions and previous auction outcomes
#
############################################################################################

def auction_value_estimate(dice_size):
    """Estimate the expected auction value based on the dice size."""
    # The average value for any dice is (1 + max_value) / 2
    return (1 + dice_size) / 2


def ConservativeMax(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    # You can adjust these dice sizes based on your game rules
    die_sizes = [2, 3, 4, 6, 8, 10, 12, 20]

    agent_state = states[agent_id]
    current_gold = agent_state["gold"]

    max_gold_fraction = 0.25  # The fraction of available gold to spend per round (can be tweaked)

    # Calculate expected value for each auction
    bids = {}

    for auction_id, auction_info in auctions.items():
        # Extract the dice size for this auction (assuming auction_info contains a dice_type index)
        dice_type = auction_info.get('dice_type', 3)  # Default to 6-sided die (D6) if type is missing
        dice_size = die_sizes[dice_type]  # Get the dice size from the list

        # Estimate the auction value based on the dice size
        auction_value = auction_value_estimate(dice_size)

        # Calculate how much gold to bid, scaling with the estimated auction value
        bid = min(current_gold, int(auction_value / max(die_sizes) * current_gold * max_gold_fraction))  # Scale bid

        # Ensure the bot doesn't bid zero and doesn't overbid
        bid = max(1, min(bid, current_gold))

        # Place the bid if enough gold is available
        if bid <= current_gold:
            bids[auction_id] = bid
            current_gold -= bid

    return bids


if __name__ == "__main__":

    host = "localhost"
    agent_name = "ConservaativeMax"
    player_id = "Conservative"
    port = 8001

    game = AuctionGameClient(host=host,
                             agent_name=agent_name,
                             player_id=player_id,
                             port=port)
    try:
        game.run(ConservativeMax)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")

    print("<game is done>")
