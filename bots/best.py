import random
import os
from math import exp
from dnd_auction_game import AuctionGameClient

############################################################################################
#
# Counter Bot
#   This bot estimates the OptimalGoldBot's bids and overbids on key auctions to win them.
#   It maintains a higher capital to have more gold available for bidding.
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

def estimate_optimal_gold_bot_bid(auction_estimates, total_gold_to_spend):
    """Estimate the bids that the OptimalGoldBot would place."""
    total_estimated_value = sum(auction_estimates.values())
    if total_estimated_value == 0:
        total_estimated_value = 1  # Prevent division by zero

    estimated_bids = {}
    for auction_id, estimated_value in auction_estimates.items():
        bid_fraction = estimated_value / total_estimated_value
        bid_amount = int(bid_fraction * total_gold_to_spend)
        bid_amount = max(1, bid_amount)
        estimated_bids[auction_id] = bid_amount
    return estimated_bids

def CounterBot(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    agent_state = states[agent_id]
    current_gold = agent_state["gold"]

    # Desired capital to maintain (higher than OptimalGoldBot's capital)
    desired_capital = 3800  # Increase capital to have more gold available

    # Calculate gold available to spend this round
    gold_to_spend = max(0, current_gold - desired_capital)
    # Willing to spend more than OptimalGoldBot
    gold_to_spend = min(gold_to_spend, 4000)  # Spend up to 4000 gold

    # Prepare to bid on auctions
    bids = {}

    # Estimate values for all available auctions
    auction_estimates = {}
    for auction_id, auction_info in auctions.items():
        estimated_value = auction_value_estimate(auction_info)
        auction_estimates[auction_id] = estimated_value

    # Estimate OptimalGoldBot's bids
    optimal_bot_gold_to_spend = 10000  # OptimalGoldBot spends up to 3000 gold
    optimal_bot_bids = estimate_optimal_gold_bot_bid(auction_estimates, optimal_bot_gold_to_spend)

    # Sort auctions by estimated value in descending order
    sorted_auctions = sorted(auction_estimates.items(), key=lambda x: x[1], reverse=True)

    # Overbid OptimalGoldBot on key auctions
    for auction_id, estimated_value in sorted_auctions:
        if gold_to_spend <= 0:
            break  # No more gold to spend

        # Estimate OptimalGoldBot's bid for this auction
        optimal_bot_bid = optimal_bot_bids.get(auction_id, 1)

        # Decide to overbid on this auction
        # Overbid by a small margin (e.g., 1% to 5% more)
        overbid_amount = int(optimal_bot_bid * 1.7)  # Overbid by 5%
        overbid_amount = max(overbid_amount, optimal_bot_bid + 200)  # Ensure at least 1 gold more

        # Do not exceed the remaining gold to spend
        bid_amount = min(overbid_amount, gold_to_spend)
        bids[auction_id] = bid_amount
        gold_to_spend -= bid_amount

    return bids

if __name__ == "__main__":
    host = "88.90.236.106"
    agent_name = "Stonks_3000".format(random.randint(1, 1000))
    player_id = "Stonks_3000"
    port = 8095

    game = AuctionGameClient(host=host,
                             agent_name=agent_name,
                             player_id=player_id,
                             port=port)
    try:
        game.run(CounterBot)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")

    print("<game is done>")
