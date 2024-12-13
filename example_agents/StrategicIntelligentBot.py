import random
from math import exp
from dnd_auction_game import AuctionGameClient

############################################################################################
#
# Strategic Intelligent Bot
#   This bot uses the sigmoid interest rate to decide when to save and when to bid aggressively.
#   It considers the expected value of the auction and adjusts bids based on historical data.
#
############################################################################################

# Sigmoid function
def sigmoid(x):
    return 1 / (1 + exp(-x))

# Interest rate function based on the amount of gold
def interest_rate(g):
    return 1 + sigmoid(4 - g / 1000)

# Estimate auction value based on auction information
def auction_value_estimate(auction_info):
    """Estimate the expected auction value based on the auction info."""
    die = auction_info.get('die', 6)  # Default to 6-sided die
    num = auction_info.get('num', 1)
    bonus = auction_info.get('bonus', 0)
    expected_value = num * (1 + die) / 2 + bonus
    return expected_value

# Calculate optimal spending threshold based on interest and previous auction outcomes
def calculate_spending_threshold(current_gold, prev_auctions):
    interest = interest_rate(current_gold)
    
    # Consider historical auction rewards and bids to adjust spending dynamically
    historical_avg_reward = 0
    historical_avg_bid = 0
    num_auctions = 0

    for auction in prev_auctions.values():
        if 'reward' in auction:
            historical_avg_reward += auction['reward']
        if 'bids' in auction:
            historical_avg_bid += sum(auction['bids']) / len(auction['bids']) if auction['bids'] else 0
        num_auctions += 1

    # Avoid division by zero
    historical_avg_reward = historical_avg_reward / num_auctions if num_auctions > 0 else 10
    historical_avg_bid = historical_avg_bid / num_auctions if num_auctions > 0 else 10

    # Determine gold fraction based on interest and reward potential
    spending_factor = min(0.3, (interest - 1) * 0.2)  # Spend more when interest is high
    gold_to_spend = current_gold * spending_factor + historical_avg_reward - historical_avg_bid
    
    return min(current_gold, max(100, gold_to_spend))  # Ensure the bot always spends reasonably

# Bot logic
def StrategicIntelligentBot(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    agent_state = states[agent_id]
    current_gold = agent_state["gold"]
    bids = {}

    # Determine spending threshold based on interest rate and previous performance
    spending_threshold = calculate_spending_threshold(current_gold, prev_auctions)

    # Estimate values for all available auctions
    auction_estimates = {
        auction_id: auction_value_estimate(auction_info)
        for auction_id, auction_info in auctions.items()
    }

    # Sort auctions by estimated value in descending order
    sorted_auctions = sorted(auction_estimates.items(), key=lambda x: x[1], reverse=True)

    # Distribute spending threshold among the most valuable auctions
    total_estimated_value = sum([estimate for _, estimate in sorted_auctions])
    if total_estimated_value == 0:
        total_estimated_value = 1  # Prevent division by zero

    # Allocate bids proportionally based on estimated value
    for auction_id, estimated_value in sorted_auctions:
        if spending_threshold <= 0:
            break  # Stop when no more gold can be spent
        bid_fraction = estimated_value / total_estimated_value
        bid_amount = int(bid_fraction * spending_threshold)
        bid_amount = max(1, bid_amount)  # Minimum bid of 1
        bid_amount = min(bid_amount, spending_threshold)  # Cap bid at available spending threshold
        bids[auction_id] = bid_amount
        spending_threshold -= bid_amount

    return bids

if __name__ == "__main__":
    host = "localhost"
    agent_name = "StrategicIntelligentBot_{}".format(random.randint(1, 1000))
    player_id = "StrategicPlayer"
    port = 8001

    game = AuctionGameClient(
        host=host,
        agent_name=agent_name,
        player_id=player_id,
        port=port
    )

    try:
        game.run(StrategicIntelligentBot)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")

    print("<game is done>")
