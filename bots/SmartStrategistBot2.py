import os
from math import exp
from dnd_auction_game import AuctionGameClient
import plotly.graph_objects as go
from dash import Dash, dcc, html, Output, Input
import random
import threading
import time

# Create a directory for saving plots
os.makedirs('plots', exist_ok=True)

# Global state to hold data
global_state = {
    'rounds': [],
    'gold_data': [],
    'points_data': [],
    'gold_bid_data': [],
    'expected_values': [],
    'bids_over_time': [],
    'successful_bids': [],
    'unsuccessful_bids': []
}

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
    expected_value = num * (1 + die) / 2 + bonus
    return expected_value

# Calculate risk-reward ratio based on bids and estimated auction value
def risk_reward_ratio(bid_amount, estimated_value, competition):
    reward = estimated_value - bid_amount
    risk = bid_amount * (1 + competition)
    return reward / risk if risk > 0 else 0

# Main bot function
def SmartStrategistBot(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    agent_state = states[agent_id]
    current_gold = agent_state["gold"]
    
    # Update global state with current gold
    global_state['gold_data'].append(current_gold)
    global_state['rounds'].append(len(global_state['rounds']) + 1)  # Increment round

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
        total_estimated_value = 1

    # Prioritize auctions based on risk-reward and adjust bids accordingly
    for auction_id, estimated_value in sorted(auction_estimates.items(), key=lambda x: x[1], reverse=True):
        if gold_to_spend <= 0:
            break
        
        bid_fraction = estimated_value / total_estimated_value
        initial_bid = int(bid_fraction * gold_to_spend)

        competition = competition_scores.get(auction_id, 0)
        rr_ratio = risk_reward_ratio(initial_bid, estimated_value, competition)

        bid_multiplier = 1.0 + rr_ratio * 0.5 if rr_ratio > 1.0 else 0.8
        bid_amount = int(initial_bid * bid_multiplier)

        bid_amount = max(1, min(bid_amount, current_gold))
        if bid_amount > 0 and (competition < 3 or rr_ratio > 0.75):
            bids[auction_id] = bid_amount
            gold_to_spend -= bid_amount

    # Update global state with bids data
    global_state['gold_bid_data'].append(sum(bids.values()))  # Store total bid amount
    global_state['expected_values'].append(sum(auction_estimates.values()))  # Store total expected value
    global_state['bids_over_time'].append(len(bids))  # Store number of bids in the round

    successful_bids_count = sum(1 for bid in bids.values() if bid > 0)
    unsuccessful_bids_count = len(bids) - successful_bids_count
    global_state['successful_bids'].append(successful_bids_count)
    global_state['unsuccessful_bids'].append(unsuccessful_bids_count)

    return bids


# Visualization Setup
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Auction Bot Performance"),
    
    # Gold Over Time
    dcc.Graph(id='gold-over-time'),
    
    # Points Over Time
    dcc.Graph(id='points-over-time'),

    # Gold Bid vs Expected Value
    dcc.Graph(id='gold-bid-vs-expected-value'),

    # Scatter Plot: Bids vs Returns
    dcc.Graph(id='bids-vs-returns'),

    # Bids Over Time
    dcc.Graph(id='bids-over-time'),

    # Successful vs Unsuccessful Bids
    dcc.Graph(id='successful-vs-unsuccessful-bids'),
    
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)  # Update every second
])

@app.callback(
    [Output('gold-over-time', 'figure'),
     Output('points-over-time', 'figure'),
     Output('gold-bid-vs-expected-value', 'figure'),
     Output('bids-vs-returns', 'figure'),
     Output('bids-over-time', 'figure'),
     Output('successful-vs-unsuccessful-bids', 'figure')],
    Input('interval-component', 'n_intervals')
)
def update_graphs(n):
    # Create figures from the global state
    figures = []

    # Gold Over Time
    figures.append(go.Figure(data=[go.Scatter(x=global_state['rounds'], y=global_state['gold_data'], mode='lines+markers', name='Gold Over Time')])
                     .update_layout(title='Gold Over Time', xaxis_title='Rounds', yaxis_title='Gold'))

    # Points Over Time
    figures.append(go.Figure(data=[go.Scatter(x=global_state['rounds'], y=global_state['points_data'], mode='lines+markers', name='Points Over Time')])
                     .update_layout(title='Points Over Time', xaxis_title='Rounds', yaxis_title='Points'))

    # Gold Bid vs Expected Value
    figures.append(go.Figure(data=[go.Scatter(x=global_state['expected_values'], y=global_state['gold_bid_data'], mode='markers', name='Gold Bid vs Expected Value')])
                     .update_layout(title='Gold Bid vs Expected Value', xaxis_title='Expected Value', yaxis_title='Gold Bid'))

    # Scatter Plot: Bids vs Returns
    figures.append(go.Figure(data=[go.Scatter(x=global_state['expected_values'], y=global_state['gold_bid_data'], mode='markers', name='Bids vs Returns')])
                     .update_layout(title='Bids vs Returns', xaxis_title='Expected Value', yaxis_title='Bid Amount'))

    # Bids Over Time
    figures.append(go.Figure(data=[go.Bar(x=global_state['rounds'], y=global_state['bids_over_time'], name='Bids Per Round')])
                     .update_layout(title='Number of Bids Over Time', xaxis_title='Rounds', yaxis_title='Number of Bids'))

    # Successful vs Unsuccessful Bids
    figures.append(go.Figure(data=[
        go.Bar(x=global_state['rounds'], y=global_state['successful_bids'], name='Successful Bids', marker_color='green'),
        go.Bar(x=global_state['rounds'], y=global_state['unsuccessful_bids'], name='Unsuccessful Bids', marker_color='red')
    ]).update_layout(title='Successful vs Unsuccessful Bids', barmode='group', xaxis_title='Rounds', yaxis_title='Number of Bids'))

    return figures

def save_plots():
    # Save each figure as an image file
    for key, value in global_state.items():
        if key in ['gold_data', 'points_data', 'gold_bid_data', 'expected_values', 'bids_over_time', 'successful_bids', 'unsuccessful_bids']:
            fig = go.Figure(data=[go.Scatter(y=value)])
            fig.update_layout(title=key.replace('_', ' ').title(), yaxis_title=key.title())
            fig.write_image(f'plots/{key}.png')

def run_auction_bot(host, agent_name, player_id, port):
    game = AuctionGameClient(
        host=host,
        agent_name=agent_name,
        player_id=player_id,
        port=port
    )
    game.run(SmartStrategistBot)

if __name__ == "__main__":
    host = "localhost"
    agent_name = "SmartStrategistBot2_{}".format(random.randint(1, 1000))
    player_id = "SmartStrategistBot2"
    port = 8001

    # Start the auction bot in a separate thread
    auction_bot_thread = threading.Thread(target=run_auction_bot, args=(host, agent_name, player_id, port))
    auction_bot_thread.start()

    # Start the Dash app
    app.run_server(debug=True, use_reloader=False)

    # Save plots periodically
    while True:
        time.sleep(10)  # Save every 10 seconds
        save_plots()
