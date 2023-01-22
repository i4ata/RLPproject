import numpy as np
import random

class BlackJack:
    
    deck = []
    
    # variables for the game
    player_hand_sum = 0
    player_hand = []
    has_ace = False
        
    dealer_card = 0
    dealer_hand = []
    dealer_hand_sum = 0
    dealer_has_ace = False
    
    # save all states here
    states = []
    
    # keep track of these
    wins = 0
    losses = 0
    draws = 0
    
    reward_multiplier = 1
    
    def start_from_state(self, state): # simulate a game with a hardcoded initial state
        # <player hand value, player has usable ace, dealer visible card value>
        
        # reset everything
        self.reward_multiplier = 1
        self.deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 1]*4
        np.random.shuffle(self.deck)
        
        # generate dealer hand
        self.dealer_card = state[2]
        dealer_other = random.choice(self.deck)
        self.dealer_hand = [state[2], dealer_other]
        
        # remove dealer hand from deck
        self.deck.remove(dealer_other)
        self.deck.remove(state[2])
        
        # generate player hand and remove it from the deck
        # 1) player has an ace
        if state[1]:
            self.player_hand = [1, state[0] - 11]
            self.deck.remove(1)
            self.deck.remove(state[0] - 11)
        # 2) player doesn't have an ace
        else:
            c1 = random.randint(max(2, state[0] - 10), 10)
            c2 = state[0] - c1
            self.player_hand = [c1, c2]
            self.deck.remove(c1)
            self.deck.remove(c2)
            
        # compute the sums and update has_ace variables
        self.player_hand_sum = self._get_sum_player()
        self.dealer_hand_sum = self._get_sum_dealer()
        
        # if the dealer has 21, it's an auto win for them so we reset
        # nothing to learn in that case
        if self.dealer_hand_sum == 21:
            self.start_from_state(state)
        
    
    def start(self): # simulate a normal game
        
        # reset everything
        self.reward_multiplier = 1
        self.deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 1]*4
        np.random.shuffle(self.deck)
        
        # draw 4 cards and delete them from the deck
        draw = self.deck[:4]
        self.deck = np.delete(self.deck, range(4))
        
        # deal them to player and dealer
        self.player_hand = [draw[0], draw[1]]
        self.dealer_hand = [draw[2], draw[3]]
        
        self.dealer_card = draw[2]
        
        # compute sums and update has_ace variables
        self.dealer_hand_sum = self._get_sum_dealer()
        self.player_hand_sum = self._get_sum_player()
        
        # check if someone has 21, then the round is over and we start again
        if self.player_hand_sum == 21 and self.dealer_hand_sum != 21:
            self.wins += 1
            self.start()
        elif self.player_hand_sum != 21 and self.dealer_hand_sum == 21:
            self.losses += 1
            self.start()
        elif self.player_hand_sum == 21 and self.dealer_hand_sum == 21:
            self.draws += 1
            self.start()
        
        # get the player to a point where they need to make a choice
        # if the sum of cards < 12, then there is no point in not hitting, since there is no way that you bust
        while self.player_hand_sum < 12:
            self.hit()
        
    def _get_sum_player(self): # compute the sum of the player's hand
        
        sum_hand = sum(self.player_hand)
        
        # if they have an ace and they can count it as 11 instead of 1 without busting
        if sum_hand <= 11 and any(card == 1 for card in self.player_hand):
            sum_hand += 10
            self.has_ace = True
        else:
            self.has_ace = False
            
        return sum_hand
    
    def _get_sum_dealer(self): # comopute the sum of the player's hand
        
        sum_hand = sum(self.dealer_hand)
        
        # if they have an ace and they can count it as 11 instead of 1 without busting
        if sum_hand <= 11 and any(card == 1 for card in self.dealer_hand):
            sum_hand += 10
            self.dealer_has_ace = True
        else:
            self.dealer_has_ace = False
        
        return sum_hand
    
    # perform "double". That is, "hit" and then "stand". The reward at the end is doubled
    def double(self):
        self.hit()
        if self.player_hand_sum < 21:
            self.stand()
        self.reward_multiplier = 2
    
    # perform "hit". That is, draw a card from the deck.
    def hit(self):
        
        draw = self.deck[0]
        self.player_hand.append(draw)
        self.deck = np.delete(self.deck, (0))
        self.has_ace = self.has_ace or draw == 1 # this line is probably pointless
        self.player_hand_sum = self._get_sum_player()
        
        if self.player_hand_sum == 21: # if the sum is now 21, we enter a terminal state. The player auto stands
            self.stand()
        
    # perform "stand". Basically, the dealer takes their turn.
    def stand(self):
        self._dealer_turn()
        
    # the dealer's turn. They hit until they reach a hand sum of 17
    def _dealer_turn(self):
        while self.dealer_hand_sum < 17:
            self.dealer_hand.append(self.deck[0])
            self.deck = np.delete(self.deck, (0))
            self.dealer_hand_sum = self._get_sum_dealer()
            
    # return the current state of the game
    def get_current_state(self):
        return (self.player_hand_sum, self.has_ace, self.dealer_card)
    
    # generate all possible states
    def _get_states(self):
        states = []
        self.deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 1]*4
        for i in range(len(self.deck)):
            for j in range(i):
                
                self.player_hand = [self.deck[i], self.deck[j]]
                self.has_ace = any(card == 1 for card in self.player_hand)
                
                p_sum = self._get_sum_player()
                
                if p_sum == 21 or p_sum < 12: # sum 21 and sum < 12 are not included
                    continue
                
                states.extend([(p_sum, self.has_ace, d_card) for d_card in np.unique(self.deck)])
        return list(set(states))
    
    # get the reward, call that after a game is over.
    def get_reward(self):
        if self.player_hand_sum > 21: # we bust = we lose
            self.losses += 1
            return -1 * self.reward_multiplier
        if self.dealer_hand_sum > 21 or self.dealer_hand_sum < self.player_hand_sum: # dealer busted or we got more and didn't bust = we win
            self.wins += 1
            return 1 * self.reward_multiplier
        if self.dealer_hand_sum > self.player_hand_sum: # if we both don't bust and dealer got more = we lose
            self.losses += 1
            return -1 * self.reward_multiplier
        # it's a draw
        self.draws += 1
        return 0
    
    # print a summary of a game
    def get_stats(self):
        all_outcomes = self.wins + self.losses + self.draws
        print("Winrate: " + str(self.wins / all_outcomes))
        print("Drawrate: " + str(self.draws / all_outcomes))
        print("Loserate: " + str(self.losses / all_outcomes))
        print("Ws: " + str(self.wins) + "; Ls: " + str(self.losses) + "; Draws: " + str(self.draws))
              
    # test a deterministic policy "pi" for "iterations" of simulated games.
    def test_policy(self, pi, iterations):
        rewards = [0]*iterations
        self.wins = self.losses = self.draws = 0
        self.reward_multiplier = 1
        for i in range(iterations):

            self.start()

            while self.player_hand_sum < 21: # while the player hasn't busted

                state = self.get_current_state()

                action = pi[state]

                if action == "hit":
                    self.hit()
                elif action == "stand":
                    self.stand() # if we stand, the round ends
                    break
                elif action == "double":
                    self.double()
                    break
            rewards[i] = self.get_reward()
        self.get_stats()
        print("Profit: " + str(sum(rewards)))
        double_won, double_lost = len(list(filter(lambda x: x == 2, rewards))), len(list(filter(lambda x: x == -2, rewards)))
        print("Wins after doubling: " + str(double_won) + "; Losses after doubling: " + str(double_lost))

    # constructor: creates the states
    def __init__(self):
        print("New BlackJack game created")
        self.states = self._get_states()