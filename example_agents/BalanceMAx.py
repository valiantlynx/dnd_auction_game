import random

from dnd_auction_game import AuctionGameClient


def auction_value_estimate(dice_size: int, num_rolls: int, bonus: int = 0) -> float:
    """
    Estimates the expected value of an auction based on the dice size, number of rolls, and bonus.
    Parameters:
    dice_size (int): The number of sides on the dice (e.g., 6 for D6, 20 for D20).
    num_rolls (int): The number of dice rolls for this auction.
    bonus (int): Any additional bonus points added to the roll (default is 0).
    Returns:
    float: The estimated value of the auction.
    """
    # The average value of a dice roll is (1 + dice_size) / 2
    average_roll_value = (1 + dice_size) / 2

    # Total value is the average value of a single roll multiplied by the number of rolls, plus any bonus
    estimated_value = (average_roll_value * num_rolls) + bonus

    return estimated_value


def balanceMax(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    die_sizes = [2, 3, 4, 6, 8, 10, 12, 20]

    agent_state = states[agent_id]
    current_gold = agent_state["gold"]

    # More aggressive in later rounds
    if 'round_counter' in states:
        round_counter = states['round_counter']
        max_gold_fraction = 0.20 if round_counter < 5 else 0.40
    else:
        max_gold_fraction = 0.20  # Early rounds spend only 20% of gold

    bids = {}

    for auction_id, auction_info in auctions.items():
        dice_type = auction_info.get('dice_type', 3)
        dice_size = die_sizes[dice_type]
        auction_value = auction_value_estimate(dice_size)

        bid = min(current_gold, int(auction_value / max(die_sizes) * current_gold * max_gold_fraction))
        bid = max(1, min(bid, current_gold))

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
        game.run(balanceMax)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")

    print("<game is done>")
