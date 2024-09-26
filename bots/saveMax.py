import random
import os
from math import exp
from dnd_auction_game import AuctionGameClient


############################################################################################
#
# Sigmoid Interest Rate Bot
#   This bot saves its principal gold and spends only the interest generated once it reaches 15% interest.
#
############################################################################################


# Sigmoid function
def sigmoid(x):
    return 1 / (1 + exp(-x))

# Interest rate function based on gold
def interest_rate(g):
    return 1 + sigmoid(4 - g / 1000)

# Estimate auction value based on dice size
def auction_value_estimate(dice_size):
    """Estimate the expected auction value based on the dice size."""
    return (1 + dice_size) / 2

def InterestMax(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    # You can adjust these dice sizes based on your game rules
    die_sizes = [2, 3, 4, 6, 8, 10, 12, 20]

    agent_state = states[agent_id]
    current_gold = agent_state["gold"]

    # Target minimum interest rate (15% or 1.15)
    target_interest_rate = 1.15

    # Get the current interest rate based on the bot's gold
    current_interest_rate = interest_rate(current_gold)*2

    # If the interest rate is below the target, save gold and bid minimally
    if current_interest_rate < target_interest_rate:
        max_gold_fraction = 0.02  # Spend only 1% of current gold until interest rate is 15%
    else:
        # If the interest rate is 15% or more, spend based on the interest only
        interest_to_spend = (current_interest_rate - 1) * current_gold
        max_gold_fraction = min(interest_to_spend / current_gold, 0.25)  # Spend up to 25% of available interest

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
            bids[auction_id] = bid+1
            current_gold -= bid

    return bids


if __name__ == "__main__":

    host = "localhost"
    agent_name = "InterestMax_{}".format(random.randint(1, 1000))
    player_id = "InterestBasedPlayer"
    port = 8001

    game = AuctionGameClient(host=host,
                             agent_name=agent_name,
                             player_id=player_id,
                             port=port)
    try:
        game.run(InterestMax)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")

    print("<game is done>")
