class Player:
    # The Player class represents a player in the game.
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.current_bet = 0
        self.has_folded = False
        self.has_acted = False

    # Define player bet actions
    def bet(self, amount):
        if amount > self.chips:
            raise ValueError(f"{self.name} does not have enough chips to bet {amount}.")
        self.chips -= amount

    # Define player check action
    def check(self, current_game_bet):
        """Allow the player to check only if their bet matches the current game's bet."""
        if self.current_bet != current_game_bet:
            raise ValueError(
                f"{self.name} cannot check when their current bet is less than the game's current bet."
            )
        # No further action is needed for a check

    # Define player fold action
    def fold(self):
        # The player folds and can no longer participate in this round.
        self.has_folded = True

    # Function to reset the player's status for a new round
    def reset_for_new_round(self):
        # Reset bet and folded status at the start of a new round.
        self.current_bet = 0
        self.has_folded = False
        self.has_acted = False

    # Function to check if the player has gone all in
    def is_all_in(self):
        # Returns True if the player has gone all in.
        return self.chips == 0

    # Function to print the player's current status
    def __str__(self):
        # A string representation for debugging or printing the player status.
        return f"Player: {self.name}, Chips: {self.chips}, Current Bet: {self.current_bet}, Folded: {self.has_folded}"
