import os

from dnd_auction_game import AuctionGameClient

from main import AuctionAgent


def opportunistMax(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    die_sizes = [2, 3, 4, 6, 8, 10, 12, 20]

    agent_state = states[agent_id]
    current_gold = agent_state["gold"]

    max_gold_fraction = 0.20  # Default conservative spending

    if prev_auctions and any(agent_id in prev_bids for prev_bids in prev_auctions.values()):
        # If the bot won an auction in the previous round, it bids more aggressively
        max_gold_fraction = 0.40

    bids = {}

    for auction_id, auction_info in auctions.items():
        dice_type = auction_info.get('dice_type', 3)
        dice_size = die_sizes[dice_type]
        auction_value = auctions.auction_value_estimate(dice_size)

        bid = min(current_gold, int(auction_value / max(die_sizes) * current_gold * max_gold_fraction))
        bid = max(1, min(bid, current_gold))

        if bid > current_gold:
            bids[auction_id] = bid
            current_gold -= bid

    return bids

if __name__ == "__main__":

    host = "localhost"
    agent_name = "OppertunistMax"
    player_id = "Conservative"
    port = 8001

    game = AuctionGameClient(host=host,
                             agent_name=agent_name,
                             player_id=player_id,
                             port=port)
    try:
        game.run(opportunistMax)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")

    print("<game is done>")
