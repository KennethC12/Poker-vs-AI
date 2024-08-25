from player import *
from game_state import *
import random


class CFRBot(Player):
    def __init__(self, name, chips):
        super().__init__(name, chips)
        self.actions = ['fold', 'call', 'bet', 'check']
        self.regret_sum = {action: 0 for action in self.actions}
        self.strategy = {action: 1.0 / len(self.actions) for action in self.actions}
        self.strategy_sum = {action: 0 for action in self.actions}
        self.num_actions = len(self.actions)

    def get_strategy(self):
        """
        Get the current strategy based on the regret-matching approach.
        """
        total_positive_regret = sum(max(0, self.regret_sum[a]) for a in self.actions)
        
        # If there is any positive regret, we update the strategy based on regret values
        if total_positive_regret > 0:
            for action in self.actions:
                self.strategy[action] = max(0, self.regret_sum[action]) / total_positive_regret
        else:
            # If no regret, choose actions uniformly
            self.strategy = {a: 1.0 / self.num_actions for a in self.actions}
        
        # Sum up strategy for future regret-matching updates
        for action in self.actions:
            self.strategy_sum[action] += self.strategy[action]

        return self.strategy


    def choose_action(self, game_state):
        """Choose an action based on the current strategy, but filter out illegal actions."""
        strategy = self.get_strategy()

        # List valid actions
        valid_actions = self.get_valid_actions(game_state)
        if not valid_actions:
            return 'fold'

        # Filter strategy to include only valid actions
        actions = list(strategy.keys())
        probabilities = [strategy[action] if action in valid_actions else 0 for action in actions]

        total_prob = sum(probabilities)
        if total_prob > 0:
            probabilities = [p / total_prob for p in probabilities]
        else:
            probabilities = [1.0 / len(valid_actions)] * len(actions)

        return random.choices(actions, probabilities)[0]

    def get_valid_actions(self, game_state):
        valid_actions = []
        current_bet = self.current_bet
        game_current_bet = game_state.current_bet

        # Can check if the player's current bet equals the game's current bet
        if current_bet == game_current_bet:
            valid_actions.append('check')
        
        # The player can fold at any time
        valid_actions.append('fold')
        
        # If the current bet is less than the game's current bet and the player has enough chips, they can call
        if current_bet < game_current_bet and self.chips >= (game_current_bet - current_bet):
            valid_actions.append('call')
        
        # If the player still has chips, they can always bet
        if self.chips > 0:
            valid_actions.append('bet')

        return valid_actions


    def act(self, game_state, deck, chat_log):
        action = self.choose_action(game_state)  # The bot chooses an action

        if action == 'fold' and self.current_bet < game_state.current_bet:
            if self.chips >= (game_state.current_bet - self.current_bet):
                print(f"{self.name} avoided folding and will call.")
                action = 'call'

        if action == 'fold':
            game_state.handle_fold(self, chat_log)  # Pass 'self' which refers to the Player (CFRBot)

        elif action == 'call':
            amount_to_call = game_state.current_bet - self.current_bet
            if amount_to_call > 0:
                game_state.handle_bet(self, amount_to_call, chat_log)  # Pass 'self' which refers to the Player (CFRBot)
        
        elif action == 'bet':
            # Ensure the bot bets at least the minimum required
            bet_amount = max(game_state.current_bet, 20)  # Set a minimum bet of 20 or the current bet
            bet_amount = min(bet_amount, self.chips)  # Make sure the bet doesn't exceed the bot's available chips
            game_state.handle_bet(self, bet_amount, chat_log)  # Pass 'self' which refers to the Player (CFRBot)
        
        elif action == 'check':
            if self.current_bet == game_state.current_bet:  # Ensure the bot can check only if bets are equal
                game_state.handle_check(self, chat_log)  # Pass 'self' which refers to the Player (CFRBot)

        # Log the bot's action in the chat log
        chat_log.add_message(f"{self.name} chose to {action}")



    def update_regret(self, action_taken, action_value, baseline_value):
        """
        Update the regret for each action based on the outcome of the action taken.
        action_value: the utility gained by the action taken.
        baseline_value: the baseline utility (for comparison).
        """
        for action in self.actions:
            if action == action_taken:
                regret = 0  # No regret for the action that was taken
            else:
                # Regret is the difference between the utility for not taking the action and the utility gained
                regret = action_value - baseline_value
            
            # Add regret to regret_sum
            self.regret_sum[action] += regret


    def get_average_strategy(self):
        total_strategy_sum = sum(self.strategy_sum[action] for action in self.actions)
        if total_strategy_sum > 0:
            return {action: self.strategy_sum[action] / total_strategy_sum for action in self.actions}
        else:
            return {action: 1.0 / self.num_actions for action in self.actions}
