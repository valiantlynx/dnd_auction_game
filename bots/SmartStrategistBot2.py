import random
from math import exp
import json
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dnd_auction_game import AuctionGameClient

# Sigmoid function for interest rate calculation
def sigmoid(x):
    return 1 / (1 + exp(-x))

# Calculate expected value of an auction based on dice rolls and bonuses
def auction_value_estimate(auction_info):
    die = auction_info.get('die', 6)
    num = auction_info.get('num', 1)
    bonus = auction_info.get('bonus', 0)
    expected_value = num * (1 + die) / 2 + bonus
    return expected_value

# Main bot function
def SmartStrategistBot(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    agent_state = states[agent_id]
    current_gold = agent_state["gold"]

    # Adjust desired capital dynamically based on game progress
    rounds_left = len(auctions)
    desired_capital = max(1000, min(2000, current_gold // 2)) if rounds_left < 5 else 2000
    gold_to_spend = max(0, current_gold - desired_capital)

    bids = {}
    auction_estimates = {}

    # Estimate the value of each auction
    for auction_id, auction_info in auctions.items():
        estimated_value = auction_value_estimate(auction_info)
        auction_estimates[auction_id] = estimated_value

    # Record the highest estimated value auction for the last bid
    best_auction_id = max(auction_estimates, key=auction_estimates.get, default=None)

    # Regular bidding strategy
    for auction_id, estimated_value in auction_estimates.items():
        if gold_to_spend <= 0:
            break
        
        bid_fraction = estimated_value / sum(auction_estimates.values()) if sum(auction_estimates.values()) > 0 else 1
        initial_bid = int(bid_fraction * gold_to_spend)
        bid_amount = max(1, min(initial_bid, current_gold))

        bids[auction_id] = bid_amount
        gold_to_spend -= bid_amount

    # Last bid: spend all remaining gold on the highest estimated auction
    if best_auction_id is not None and gold_to_spend > 0:
        bids[best_auction_id] = gold_to_spend
        print(f"Bidding all remaining gold on auction {best_auction_id}")

    return bids

# Visualization Setup
app = Dash(__name__)

# Dummy data for visualization (replace with actual data)
rounds = [0, 1, 2, 3]  # Example rounds
gold_data = [1000, 900, 850, 800]  # Example gold data over rounds
points_data = [0, 10, 20, 30]  # Example points data over rounds
gold_bid_data = [50, 150, 100, 200]  # Example gold bid amounts
expected_values = [75, 200, 150, 250]  # Expected auction values
bids_over_time = [2, 3, 1, 4]  # Number of bids per round
successful_bids = [1, 2, 0, 3]  # Successful bids per round
unsuccessful_bids = [1, 1, 1, 1]  # Unsuccessful bids per round

app.layout = html.Div([
    html.H1("Auction Bot Performance"),
    
    # Gold Over Time
    dcc.Graph(
        id='gold-over-time',
        figure={
            'data': [
                go.Scatter(x=rounds, y=gold_data, mode='lines+markers', name='Gold Over Time')
            ],
            'layout': go.Layout(title='Gold Over Time', xaxis={'title': 'Rounds'}, yaxis={'title': 'Gold'})
        }
    ),
    
    # Points Over Time
    dcc.Graph(
        id='points-over-time',
        figure={
            'data': [
                go.Scatter(x=rounds, y=points_data, mode='lines+markers', name='Points Over Time')
            ],
            'layout': go.Layout(title='Points Over Time', xaxis={'title': 'Rounds'}, yaxis={'title': 'Points'})
        }
    ),

    # Gold Bid vs Expected Value
    dcc.Graph(
        id='gold-bid-vs-expected-value',
        figure={
            'data': [
                go.Scatter(x=expected_values, y=gold_bid_data, mode='markers', name='Gold Bid vs Expected Value')
            ],
            'layout': go.Layout(title='Gold Bid vs Expected Value', xaxis={'title': 'Expected Value'}, yaxis={'title': 'Gold Bid'})
        }
    ),

    # Scatter Plot: Bids vs Returns
    dcc.Graph(
        id='bids-vs-returns',
        figure={
            'data': [
                go.Scatter(x=expected_values, y=gold_bid_data, mode='markers', name='Bids vs Returns')
            ],
            'layout': go.Layout(title='Bids vs Returns', xaxis={'title': 'Expected Value'}, yaxis={'title': 'Bid Amount'})
        }
    ),

    # Bids Over Time
    dcc.Graph(
        id='bids-over-time',
        figure={
            'data': [
                go.Bar(x=rounds, y=bids_over_time, name='Bids Per Round')
            ],
            'layout': go.Layout(title='Number of Bids Over Time', xaxis={'title': 'Rounds'}, yaxis={'title': 'Number of Bids'})
        }
    ),

    # Successful vs Unsuccessful Bids
    dcc.Graph(
        id='successful-vs-unsuccessful-bids',
        figure={
            'data': [
                go.Bar(x=rounds, y=successful_bids, name='Successful Bids', marker_color='green'),
                go.Bar(x=rounds, y=unsuccessful_bids, name='Unsuccessful Bids', marker_color='red')
            ],
            'layout': go.Layout(title='Successful vs Unsuccessful Bids', barmode='group', xaxis={'title': 'Rounds'}, yaxis={'title': 'Number of Bids'})
        }
    ),
    
    # Add more graphs as needed...
])

if __name__ == "__main__":
    host = "localhost"
    agent_name = "SmartStrategistBot2_{}".format(random.randint(1, 1000))
    player_id = "SmartStrategist2"
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
    
    app.run_server(debug=True)
