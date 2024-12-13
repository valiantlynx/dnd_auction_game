import random
from dnd_auction_game import AuctionGameClient

############################################################################################
#
# SpreadBidder Bot
#   This bot aims to win as many auctions as possible with minimal bids by spreading 
#   its gold thinly across multiple auctions.
#
############################################################################################

# Bid just above the average expected minimum to increase chances of winning
def calculate_minimal_bid(auction_info, average_bid):
    """Calculate a low but potentially winning bid amount."""
    die = auction_info.get('die', 6)
    num = auction_info.get('num', 1)
    bonus = auction_info.get('bonus', 0)
    expected_value = num * (1 + die) / 2 + bonus

    # Determine a bid that is slightly above the historical average bid but conservative
    minimal_bid = max(1, int(average_bid * 0.9))  # 90% of the average bid as a safe threshold
    return minimal_bid

# Analyze previous bids to identify patterns and set lower bounds for current bids
def analyze_previous_bids(prev_auctions):
    """Analyze previous bids to gather average winning bids."""
    total_bids = []
    for auction_info in prev_auctions.values():
        bids = auction_info.get('bids', [])
        if bids:
            total_bids.extend(bids)

    average_bid = sum(total_bids) / len(total_bids) if total_bids else 10  # Default average bid if no data
    return average_bid

def SpreadBidder(agent_id: str, states: dict, auctions: dict, prev_auctions: dict):
    agent_state = states[agent_id]
    current_gold = agent_state["gold"]

    # Analyze previous auctions to determine average bid patterns
    average_bid = analyze_previous_bids(prev_auctions)

    # Split available gold evenly across all auctions
    available_gold_per_auction = current_gold / len(auctions)

    # Place small, strategic bids on each auction
    bids = {}
    for auction_id, auction_info in auctions.items():
        # Calculate the minimal bid to stay competitive without overspending
        bid_amount = calculate_minimal_bid(auction_info, average_bid)

        # Adjust bid amount based on the available gold per auction
        bid_amount = min(bid_amount, available_gold_per_auction)

        # Ensure bids are at least 1 gold
        bid_amount = max(1, int(bid_amount))

        # Place bid
        bids[auction_id] = bid_amount

    return bids

if __name__ == "__main__":
    host = "localhost"
    agent_name = "SpreadBidder_{}".format(random.randint(1, 1000))
    player_id = "SpreadBidderPlayer"
    port = 8001

    game = AuctionGameClient(
        host=host,
        agent_name=agent_name,
        player_id=player_id,
        port=port
    )
    try:
        game.run(SpreadBidder)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")

    print("<game is done>")
