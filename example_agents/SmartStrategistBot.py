import random
from math import exp
from dnd_auction_game import AuctionGameClient

# Sigmoid function for interest rate calculation
def sigmoid(x):
    return 1 / (1 + exp(-x))

# Interest rate function based on available gold
def interest_rate(g):
    return 1 + sigmoid(4 - g / 1000)

# Calculate expected value of an auction based on dice rolls and bonuses
def auction_value_estimate(auction_info):
    die = auction_info.get('die', 6)
    num = auction_info.get('num', 1)
    bonus = auction_info.get('bonus', 0)
    # Expected value calculation
    expected_value = num * (1 + die) / 2 + bonus
    return expected_value

# Calculate risk-reward ratio based on bids and estimated auction value
def risk_reward_ratio(bid_amount, estimated_value, competition):
    # Simple reward calculation factoring in estimated value and bid
    reward = estimated_value - bid_amount
    # Risk is modeled as a function of the competition
    risk = bid_amount * (1 + competition)
    return reward / risk if risk > 0 else 0

# Main bot function
def SmartStrategistBot(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    agent_state = states[agent_id]
    current_gold = agent_state["gold"]

    # Adjust desired capital dynamically based on game progress
    rounds_left = len(auctions)
    desired_capital = max(1000, min(2000, current_gold // 2)) if rounds_left < 5 else 2000
    gold_to_spend = max(0, current_gold - desired_capital)

    # Prepare to bid on auctions
    bids = {}
    auction_estimates = {}

    # Estimate the value of each auction
    for auction_id, auction_info in auctions.items():
        estimated_value = auction_value_estimate(auction_info)
        auction_estimates[auction_id] = estimated_value

    # Assess competition for each auction based on previous round's bids
    competition_scores = {}
    for auction_id, _ in auction_estimates.items():
        if auction_id in prev_auctions:
            bids_on_auction = prev_auctions[auction_id].get("bids", [])
            competition_scores[auction_id] = len(bids_on_auction)
        else:
            competition_scores[auction_id] = 0

    # Dynamic bid adjustment based on past success and competition level
    total_estimated_value = sum(auction_estimates.values())
    if total_estimated_value == 0:
        total_estimated_value = 1  # Prevent division by zero

    # Prioritize auctions based on risk-reward and adjust bids accordingly
    for auction_id, estimated_value in sorted(auction_estimates.items(), key=lambda x: x[1], reverse=True):
        if gold_to_spend <= 0:
            break
        
        # Basic proportion of gold to bid based on value estimate
        bid_fraction = estimated_value / total_estimated_value
        initial_bid = int(bid_fraction * gold_to_spend)

        # Adjust bid based on risk-reward ratio
        competition = competition_scores.get(auction_id, 0)
        rr_ratio = risk_reward_ratio(initial_bid, estimated_value, competition)

        # Encourage aggressive bidding on auctions with good risk-reward
        bid_multiplier = 1.0 + rr_ratio * 0.5 if rr_ratio > 1.0 else 0.8  # Scales up or down based on ratio
        bid_amount = int(initial_bid * bid_multiplier)

        # Ensure the bid is within current gold limits and worth competing
        bid_amount = max(1, min(bid_amount, current_gold))
        if bid_amount > 0 and (competition < 3 or rr_ratio > 0.75):
            bids[auction_id] = bid_amount
            gold_to_spend -= bid_amount

    return bids

# Running the bot
if __name__ == "__main__":
    host = "localhost"
    agent_name = "SmartStrategistBot_{}".format(random.randint(1, 1000))
    player_id = "SmartStrategist"
    port = 8001

    game = AuctionGameClient(
        host=host,
        agent_name=agent_name,
        player_id=player_id,
        port=port
    )
    try:
        game.run(SmartStrategistBot)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")

    print("<game is done>")
