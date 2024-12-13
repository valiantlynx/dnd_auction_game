import os
import random

from dnd_auction_game import AuctionGameClient


def save_and_spend_later_bid(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    agent_state = states[agent_id]
    current_gold = agent_state["gold"]
    total_rounds = states.get('num_rounds_in_game')
    round_counter = states.get('round_counter', 1)
    num_auctions = len(auctions)

    # Early phase: Spend only 1% of current gold on each auction
    if round_counter <= total_rounds // 2:
        spend_percentage = 0.01  # Spend 1% of gold
        total_gold_to_spend = current_gold * spend_percentage
    else:
        # Later phase: Spend all remaining gold evenly across remaining rounds and auctions
        rounds_left = total_rounds - round_counter + 1  # +1 to include the current round
        auctions_left = num_auctions * rounds_left  # Total auctions left across all rounds
        total_gold_to_spend = current_gold*2  # We want to spend all remaining gold by the end

    # Calculate the gold per auction for this round
    gold_per_auction = total_gold_to_spend / num_auctions

    bids = {}
    for auction_id in auctions.keys():
        # Ensure we spend all remaining gold, by setting a floor of 1 gold for each auction
        bid = max(1, int(gold_per_auction))

        # Place the bid if there is enough gold remaining
        if bid <= current_gold:
            bids[auction_id] = bid
            current_gold -= bid

    # Final check to spend all remaining gold in the last round if any remains
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
        game.run(save_and_spend_later_bid)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")

    print("<game is done>")
