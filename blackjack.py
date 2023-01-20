import numpy as np

class BlackJack:
    
    deck = []
    
    player_hand_sum = 0
    player_hand = []
    has_ace = False
        
    dealer_card = 0
    dealer_hand = []
    dealer_hand_sum = 0
    dealer_has_ace = False
    
    states = []
    
    wins = 0
    losses = 0
    draws = 0
    blackjacks = 0 
    
    def start(self):
        
        self.deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 1]*4 # intialize the deck
        np.random.shuffle(self.deck) # shuffle it
        
        draw = self.deck[:4] # get the top 4 cards
        self.deck = np.delete(self.deck, range(4)) # delete the top 4 cards
        
        self.player_hand = [draw[0], draw[1]]
        self.dealer_hand = [draw[2], draw[3]]
        
        self.dealer_card = draw[2]
        self.dealer_hand_sum = self._get_sum_dealer()
        
        self.has_ace = any(card == 1 for card in self.player_hand)
        self.dealer_has_ace = any(card == 1 for card in self.dealer_hand)
        
        self.player_hand_sum = self._get_sum_player()
        
        if self.player_hand_sum == 21:
            self.blackjacks += 1
            self.start()
        
        while self.player_hand_sum < 12:
            self.hit()
        
    def _get_sum_player(self):
        
        sum_hand = sum(self.player_hand)
        
        if sum_hand <= 11 and any(card == 1 for card in self.player_hand):
            sum_hand += 10
            self.has_ace = True
            
        return sum_hand
    
    def _get_sum_dealer(self):
        
        sum_hand = sum(self.dealer_hand)
        
        if sum_hand <= 11 and any(card == 1 for card in self.dealer_hand):
            sum_hand += 10
            self.dealer_has_ace = True
        
        return sum_hand
    
    def hit(self):
        
        draw = self.deck[0]
        self.player_hand.append(draw)
        self.deck = np.delete(self.deck, (0))
        self.has_ace = self.has_ace or draw == 1
        self.player_hand_sum = self._get_sum_player()
        
        if self.player_hand_sum == 21:
            self.stand()
        
    def stand(self):
        self._dealer_turn()
        
    def _dealer_turn(self):
        while self.dealer_hand_sum < 17:
            self.dealer_hand.append(self.deck[0])
            self.deck = np.delete(self.deck, (0))
            self.dealer_hand_sum = self._get_sum_dealer()
            
    def get_current_state(self):
        return (self.player_hand_sum, self.has_ace, self.dealer_card)
    
    def _get_states(self):
        states = []
        self.deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 1]*4
        for i in range(len(self.deck)):
            for j in range(i):
                
                self.player_hand = [self.deck[i], self.deck[j]]
                self.has_ace = any(card == 1 for card in self.player_hand)
                
                p_sum = self._get_sum_player()
                
                if p_sum == 21 or p_sum < 12: # 21 is a terminal state
                    continue
                
                states.extend([(p_sum, self.has_ace, d_card) for d_card in np.unique(self.deck)])
        return list(set(states))
    
    def get_reward(self):
        if self.player_hand_sum > 21: # we bust = we lose
            self.losses += 1
            return -1
        if self.dealer_hand_sum > 21 or self.dealer_hand_sum < self.player_hand_sum: # dealer busted or we got more and didn't bust = we win
            self.wins += 1
            return 1
        if self.dealer_hand_sum > self.player_hand_sum: # if we both don't bust and dealer got more = we lose
            self.losses += 1
            return -1
        self.draws += 1
        return 0
    
    def __init__(self):
        print("Object created")
        self.states = self._get_states()