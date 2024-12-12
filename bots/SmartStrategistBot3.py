import os
from math import exp
from dnd_auction_game import AuctionGameClient
import plotly.graph_objects as go
import random
import threading
import time

# Sigmoid function for calculating interest rate
def sigmoid(x):
    return 1 / (1 + exp(-x))

# Function to calculate the interest rate based on available gold
def interest_rate(g):
    return 1 + sigmoid(4 - g / 1000)

# Function to estimate the expected value of an auction based on dice rolls and bonuses
def auction_value_estimate(auction_info):
    die = auction_info.get('die', 6)  # Default to 6-sided die
    num = auction_info.get('num', 1)
    bonus = auction_info.get('bonus', 0)
    expected_value = num * (1 + die) / 2 + bonus
    return expected_value

# Function to estimate OptimalGoldBot's bid based on auction values and total gold
def estimate_optimal_gold_bot_bid(auction_estimates, total_gold_to_spend):
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

# Function to calculate the risk-reward ratio based on bids and estimated auction value
def risk_reward_ratio(bid_amount, estimated_value, competition):
    reward = estimated_value - bid_amount
    risk = bid_amount * (1 + competition)
    return reward / risk if risk > 0 else 0

# Combined Bot Function with strategic bidding and counter tactics
def CombinedStrategistCounterBot(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    agent_state = states[agent_id]
    current_gold = agent_state["gold"]

    # Set desired capital to maintain, dynamically adjusted based on game progress
    rounds_left = len(auctions)
    desired_capital = max(2000, current_gold // 2) if rounds_left < 5 else 5000  # Aggressive capital retention
    gold_to_spend = max(0, current_gold - desired_capital)

    # Prepare to bid on auctions
    bids = {}
    auction_estimates = {}

    # Estimate the value of each auction
    for auction_id, auction_info in auctions.items():
        estimated_value = auction_value_estimate(auction_info)
        auction_estimates[auction_id] = estimated_value

    # Estimate OptimalGoldBot's bids for counter strategy
    optimal_bot_gold_to_spend = 3000  # OptimalGoldBot spends up to 3000 gold
    optimal_bot_bids = estimate_optimal_gold_bot_bid(auction_estimates, optimal_bot_gold_to_spend)

    # Assess competition based on previous round's bids
    competition_scores = {auction_id: len(prev_auctions.get(auction_id, {}).get("bids", [])) for auction_id in auction_estimates}

    # Calculate total estimated value for all auctions
    total_estimated_value = sum(auction_estimates.values())
    if total_estimated_value == 0:
        total_estimated_value = 1  # Prevent division by zero

    # Prioritize auctions based on risk-reward and counter OptimalGoldBot's bids
    for auction_id, estimated_value in sorted(auction_estimates.items(), key=lambda x: x[1], reverse=True):
        if gold_to_spend <= 0:
            break  # No more gold to spend

        # Initial bid calculation based on value estimate
        bid_fraction = estimated_value / total_estimated_value
        initial_bid = int(bid_fraction * gold_to_spend)

        # Adjust bid based on risk-reward ratio and competition
        competition = competition_scores.get(auction_id, 0)
        rr_ratio = risk_reward_ratio(initial_bid, estimated_value, competition)
        bid_multiplier = 1.0 + rr_ratio * 0.5 if rr_ratio > 1.0 else 0.8  # Scale bid based on risk-reward ratio
        bid_amount = int(initial_bid * bid_multiplier)

        # Counter OptimalGoldBot by overbidding
        optimal_bot_bid = optimal_bot_bids.get(auction_id, 1)
        counter_bid = max(int(optimal_bot_bid * 1.05), optimal_bot_bid + 1)  # Overbid by 5% or at least 1 gold
        bid_amount = max(bid_amount, counter_bid)

        # Ensure the bid is within the remaining gold limits and worth competing
        bid_amount = min(bid_amount, current_gold)
        if bid_amount > 0 and (competition < 3 or rr_ratio > 0.75):
            bids[auction_id] = bid_amount
            gold_to_spend -= bid_amount
    return bids

# Synchronous run function
def run_auction_bot(host, agent_name, player_id, port):
    game = AuctionGameClient(
        host=host,
        agent_name=agent_name,
        player_id=player_id,
        port=port
    )
    game.run(CombinedStrategistCounterBot)  # Use a synchronous call

# Function to handle threading
def run_bot_thread(host, agent_name, player_id, port):
    run_auction_bot(host, agent_name, player_id, port)

if __name__ == "__main__":
    host = "localhost"
    agent_name = "Stonks_3000_{}".format(random.randint(1, 1000))
    player_id = "Stonks_3000"
    port = 8001

    # Start the auction bot in a separate thread
    auction_bot_thread = threading.Thread(target=run_bot_thread, args=(host, agent_name, player_id, port))
    auction_bot_thread.start()
