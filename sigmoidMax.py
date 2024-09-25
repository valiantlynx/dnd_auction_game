import os
import random
from math import exp, log10

from dnd_auction_game import AuctionGameClient


# Sigmoid function
def sigmoid(x):
    return 1 / (1 + exp(-x))

# Interest rate function based on gold
def interest_rate(g):
    return 1 + sigmoid(4 - g / 1000)

def sigmoid_saving_bid(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    agent_state = states[agent_id]
    current_gold = agent_state["gold"]
    total_rounds = 1000
    round_counter = states.get('round_counter', 1)
    num_auctions = len(auctions)

    # Calculate the interest rate based on current gold amount
    current_interest_rate = interest_rate(current_gold)

    # Determine the number of digits in the current gold amount to adjust spend percentage
    def get_spend_percentage(gold):
        num_digits = int(log10(gold)) if gold > 0 else 0  # log10 gives number of digits-1
        # Spend more based on how many digits are in the gold amount
        return min(0.01 + 0.01 * (num_digits - 2), 1.0)  # Start at 1%, max 100% spend

    # Adjust the spend percentage based on the interest rate
    spend_percentage = get_spend_percentage(current_gold) * current_interest_rate

    # Spend only a percentage of current gold during early rounds
    if round_counter <= total_rounds // 2:
        total_gold_to_spend = current_gold * spend_percentage
    else:
        # Spend all remaining gold during the later rounds
        rounds_left = total_rounds - round_counter + 1  # +1 to include the current round
        auctions_left = num_auctions * rounds_left  # Total auctions left across all rounds
        total_gold_to_spend = current_gold  # Spend everything by the end

    # Calculate the gold per auction for this round
    gold_per_auction = total_gold_to_spend / num_auctions

    bids = {}
    for auction_id in auctions.keys():
        # Ensure we spend all remaining gold, with a minimum of 1 gold per auction
        bid = max(1, int(gold_per_auction))

        # Place the bid if there is enough gold remaining
        if bid <= current_gold:
            bids[auction_id] = bid
            current_gold -= bid

    # If it's the last round and there is still gold left, spend the rest
    if round_counter == total_rounds and current_gold > 0:
        remaining_gold_per_auction = current_gold // num_auctions
        for auction_id in auctions.keys():
            bids[auction_id] += remaining_gold_per_auction
            current_gold -= remaining_gold_per_auction

    return bids


if __name__ == "__main__":

    host = "localhost"
    agent_name = "{}_{}".format(os.path.basename(__file__), random.randint(1, 1000))
    player_id = "id_of_human_player"
    port = 8001

    game = AuctionGameClient(host=host,
                             agent_name=agent_name,
                             player_id=player_id,
                             port=port)
    try:
        game.run(sigmoid_saving_bid)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")

    print("<game is done>")
