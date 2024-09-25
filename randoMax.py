import random

from dnd_auction_game import AuctionGameClient


def randoMax(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    agent_state = states[agent_id]
    current_gold = agent_state["gold"]

    bids = {}

    for auction_id in auctions.keys():
        bid = random.randint(1, current_gold // 2)  # Random bid between 1 and half of the current gold

        if bid <= current_gold:
            bids[auction_id] = bid
            current_gold -= bid

    return bids


if __name__ == "__main__":

    host = "localhost"
    agent_name = "RandoMax{}".format( random.randint(1, 1000))
    player_id = "id_of_human_player"
    port = 8001

    game = AuctionGameClient(host=host,
                             agent_name=agent_name,
                             player_id=player_id,
                             port=port)
    try:
        game.run(randoMax)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")

    print("<game is done>")
