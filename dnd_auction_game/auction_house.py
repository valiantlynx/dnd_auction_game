
from typing import List, Dict, Union
import random
from collections import defaultdict
import json
import math
import os

class AuctionHouse:
    def __init__(self, game_token:str, play_token:str, save_logs=False):
        self.is_done = False
        self.is_active = False
        
        self.log_player_id_file = None
        self.log_file = None
        self.game_token = game_token
        self.play_token = play_token
        self.save_logs = save_logs
        self.gold_income = 1000
        
        self.agents = {}
        self.names = {}
        
        self.bank_interest_rate = 1.10
        self.auctions_per_agent = 1.5
        self.gold_back_fraction = 0.6
        
        self.die_sizes = [2,   3,  4,  6,   8, 10,  12,   20,  20]
        self.die_prob =  [8,   8,  9,  8,   6,  6,   5,    2,   1]
        self.max_n_die = [5,   7, 10,  2,   3,  3,   6,    2,   4]
        self.max_bonus = [10,  2, 16,  8,  21,  2,   5,    7,   3] 
        self.min_bonus = [-2, -8, -5, -5, -10, -4,  -5,  -4,  -4]

        self.round_counter = 0
        self.auction_counter = 1
        self.current_auctions = {}
        self.current_rolls = {} 
        self.current_bids = defaultdict(list)
        self.num_rounds_in_game = 10
        
        # set the logfile
        self._find_log_file()

        print("logging to: '{}'".format(self.log_file))

    
    def _find_log_file(self):
        if self.log_file is None:            
            i = 1

            f = "./auction_house_log_{}.jsonln".format(i)         
            f_player_id = "./auction_house_log_player_id_{}.jsonln".format(i)   
            while os.path.isfile(f):
                f = "./auction_house_log_{}.jsonln".format(i)
                f_player_id = "./auction_house_log_player_id_{}.jsonln".format(i)   
                i += 1

            self.log_file = f
            self.log_player_id_file = f_player_id

    def reset(self):
        self.is_done = False
        self.agents = {}
        self.names = {}
        self.current_auctions = {}
        self.current_rolls = {} 
        self.current_bids = defaultdict(list)
        self.round_counter = 0
        self.auction_counter = 1
        self.num_rounds_in_game = 10
        
    
    def add_agent(self, name:str, a_id:str, player_id:str):
        if a_id in self.agents:
            print("Agent {}  id:{} reconnected".format(name, a_id))
            return

        with open(self.log_player_id_file, 'a') as fp:
            pid = {"player_id": player_id, "agent_id": a_id, "name": name}
            fp.write("{}\n".format(json.dumps(pid)))
                    
        self.agents[a_id] = {"gold": 0, "points": 0}
        self.names[a_id] = name
    
    
    def prepare_auction(self):        
        prev_auctions = self.current_auctions
        prev_bids = self.current_bids
        prev_rolls = self.current_rolls
        
        self.current_bids = defaultdict(list)
        self.current_auctions, self.current_rolls = self._generate_auctions()        
        
        # update gold for agents
        for agent in self.agents.values():

            # bank of Braavos gives interest on stored gold
            agent["gold"] = int(agent["gold"] * self.bank_interest_rate)
            agent["gold"] += self.gold_income
                
                
        out_prev_state = {}
        for auction_id, info in prev_auctions.items():
            out_prev_state[auction_id] = {}
            out_prev_state[auction_id].update(info)            
            out_prev_state[auction_id]["reward"] = prev_rolls[auction_id]
            
            prev_bids[auction_id].sort(key=lambda x:x[1], reverse=True)            
            out_prev_state[auction_id]["bids"] = [{"a_id": a_id, "gold": g} for a_id, g in prev_bids[auction_id]]

        state = {
            "round": self.round_counter,
            "states": self.agents,
            "auctions": self.current_auctions,
            "prev_auctions": out_prev_state
        }

        if self.save_logs and self.log_file is not None:
            with open(self.log_file, "a") as fp:
                fp.write("{}\n".format(json.dumps(state)))
        
        self.round_counter += 1
        return state
        
  
    def _generate_auctions(self) -> Dict[str, dict]:
        auctions = {}
        rolls = {} # the amount rolled - hidden for agents
        
        indices = list(range(len(self.die_sizes)))
                
        n_auctions = int(math.ceil(self.auctions_per_agent*len(self.agents)))
                
        for _ in range(n_auctions):
            i = random.choices(indices, weights=self.die_prob, k=1)[0]            
            die = self.die_sizes[i]
            n_dices = random.randint(1, self.max_n_die[i])
            bonus = random.randint(self.min_bonus[i], self.max_bonus[i])
                                    
            auction_id = "a{}".format(self.auction_counter)
            a = {"die": die, "num": n_dices, "bonus": bonus}
            auctions[auction_id] = a
            self.auction_counter += 1
            
            points = sum( (random.randint(1, a["die"]) for _ in range(a["num"])) )
            points += a["bonus"]
            rolls[auction_id] = points
                    
        return auctions, rolls
    
    def register_bid(self, a_id:str, auction_id:str, gold:int):        
        if auction_id not in self.current_auctions:
            return
        
        gold = int(gold)
        if gold < 1:
            return
                
        if self.agents[a_id]["gold"] < gold:
            return
                
        self.current_bids[auction_id].append( (a_id, gold) )
        self.agents[a_id]["gold"] -= gold
    
    def process_all_bids(self):        
        
        for auction_id, bids in self.current_bids.items():
            win_amount = max(bids, key=lambda x:x[1])[1]
            for a_id, bid in bids:
                if bid == win_amount:
                    self.agents[a_id]["points"] += self.current_rolls[auction_id]
                
                else:
                    # cashback
                    back_value = int(bid * self.gold_back_fraction)
                    self.agents[a_id]["gold"] += back_value
            
        