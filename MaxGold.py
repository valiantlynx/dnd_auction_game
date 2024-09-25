import random
import os
from math import exp
from dnd_auction_game import AuctionGameClient

############################################################################################
#
# Optimal Gold Management Bot
#   This bot maintains a capital of 4000 gold and spends excess gold (up to 3000 gold)
#   each round on the most valuable auctions.
#
############################################################################################

# Sigmoid function
def sigmoid(x):
    return 1 / (1 + exp(-x))

# Interest rate function based on gold
def interest_rate(g):
    return 1 + sigmoid(4 - g / 1000)

# Estimate auction value based on auction_info
def auction_value_estimate(auction_info):
    """Estimate the expected auction value based on the auction info."""
    die = auction_info.get('die', 6)  # Default to 6-sided die
    num = auction_info.get('num', 1)
    bonus = auction_info.get('bonus', 0)
    # Expected value of one die roll is (1 + die) / 2
    expected_value = num * (1 + die) / 2 + bonus
    return expected_value

def OptimalGoldBot(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    agent_state = states[agent_id]
    current_gold = agent_state["gold"]

    # Desired capital to maintain
    desired_capital = 4000

    # Calculate gold available to spend this round
    gold_to_spend = max(0, current_gold - desired_capital)
    gold_to_spend = min(gold_to_spend, 3000)  # Spend up to 3000 gold

    # Prepare to bid on auctions
    bids = {}

    # Estimate values for all available auctions
    auction_estimates = {}
    for auction_id, auction_info in auctions.items():
        estimated_value = auction_value_estimate(auction_info)
        auction_estimates[auction_id] = estimated_value

    # Sort auctions by estimated value in descending order
    sorted_auctions = sorted(auction_estimates.items(), key=lambda x: x[1], reverse=True)

    # Distribute gold_to_spend among the most valuable auctions
    total_estimated_value = sum([estimate for _, estimate in sorted_auctions])
    if total_estimated_value == 0:
        total_estimated_value = 1  # Prevent division by zero

    # Allocate bids proportionally based on estimated value
    for auction_id, estimated_value in sorted_auctions:
        if gold_to_spend <= 0:
            break  # No more gold to spend
        # Calculate bid proportionally
        bid_fraction = estimated_value / total_estimated_value
        bid_amount = int(bid_fraction * gold_to_spend)
        # Ensure at least a minimum bid of 1
        bid_amount = max(1, bid_amount)
        # Do not exceed the remaining gold to spend
        bid_amount = min(bid_amount, gold_to_spend)
        bids[auction_id] = bid_amount
        gold_to_spend -= bid_amount

    return bids

if __name__ == "__main__":
    host = "localhost"
    agent_name = "OptimalGoldBot_{}".format(random.randint(1, 1000))
    player_id = "OptimalGoldPlayer"
    port = 8001

    game = AuctionGameClient(host=host,
                             agent_name=agent_name,
                             player_id=player_id,
                             port=port)
    try:
        game.run(OptimalGoldBot)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")

    print("<game is done>")
