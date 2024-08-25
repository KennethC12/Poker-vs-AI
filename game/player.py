
class Player:
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.current_bet = 0
        self.has_folded = False
        self.has_acted = False 

    def bet(self, amount):
        if amount > self.chips:
            raise ValueError(f"{self.name} does not have enough chips to bet {amount}.")
        self.chips -= amount

    def check(self, current_game_bet):
        """Allow the player to check only if their bet matches the current game's bet."""
        if self.current_bet != current_game_bet:
            raise ValueError(f"{self.name} cannot check when their current bet is less than the game's current bet.")
        # No further action is needed for a check

    def fold(self):
        # The player folds and can no longer participate in this round.
        self.has_folded = True

    def reset_for_new_round(self):
        # Reset bet and folded status at the start of a new round.
        self.current_bet = 0
        self.has_folded = False
        self.has_acted = False 

    def is_all_in(self):
        # Returns True if the player has gone all in.
        return self.chips == 0

    def __str__(self):
        # A string representation for debugging or printing the player status.
        return f"Player: {self.name}, Chips: {self.chips}, Current Bet: {self.current_bet}, Folded: {self.has_folded}"