import numpy as np

class BlackJack:
    
    deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]*4
    
    player_hand_sum = 0
    player_hand = []
    player_aces = 0
    
    dealer_card = 0
    dealer_hand = []
    dealer_hand_sum = 0
    
    states = []
    
    def start(self):
        
        np.random.shuffle(self.deck)
        
        draw = np.random.choice(self.deck, size = 4, replace = False)
        self.deck = np.delete(self.deck, range(4))
        
        self.player_hand = [draw[0], draw[1]]
        self.dealer_card = draw[2]
        self.dealer_hand = [draw[2], draw[3]]
        self.dealer_hand_sum = self._get_sum(self.dealer_hand)
        self.player_aces = sum(card == 11 for card in self.player_hand)
        self.player_hand_sum = self._get_sum(self.player_hand)
        
    def _get_sum(self, hand):
        
        sum_hand = sum(hand)
        
        if sum_hand > 21:
            for ace in filter(lambda x : x == 11, hand):
                sum_hand -= 10
                if sum_hand <= 21:
                    break
        return sum_hand
    
    def hit(self):
        
        draw = self.deck[0]
        self.player_hand.append(draw)
        self.deck = np.delete(self.deck, (0))
        self.player_hand_sum = self._get_sum(self.player_hand)
        self.player_aces += draw == 11
        
    def stand(self):
        self._dealer_turn()
        
    def _dealer_turn(self):
        while self.dealer_hand_sum < 17:
            self.dealer_hand.append(self.deck[0])
            self.deck = np.delete(self.deck, (0))
            self.dealer_hand_sum = self._get_sum(self.dealer_hand)
            
    def _get_states(self):
        states = []
        for i in range(len(self.deck)):
            for j in range(i):
                p_sum = self._get_sum([self.deck[i], self.deck[j]])
                n_aces = (self.deck[i] == 11) + (self.deck[j] == 11)
                states.extend([(p_sum, n_aces, d_card) for d_card in np.unique(self.deck)])
        return list(set(states))
    
    def __init__(self):
        print("Object created")
        self.states = self._get_states()
        self.start()