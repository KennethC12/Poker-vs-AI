from CFRBot import CFRBot
from player import *
from evaluator import *
import pygame
import random


PRE_FLOP = "pre-flop"
FLOP = "flop"
TURN = "turn"
RIVER = "river"


class ChatLog:
    def __init__(self, font, max_messages=10):
        self.messages = []  # List to store chat messages
        self.font = font  # Font for rendering the messages
        self.max_messages = max_messages  # Max number of messages to display at once
        self.scroll_offset = 0  # To track scrolling position

    def add_message(self, message):
        """Add a new message to the chat log and automatically scroll to the bottom."""
        self.messages.append(message)
        # Automatically scroll to the bottom when a new message is added
        if len(self.messages) > self.max_messages:
            self.scroll_offset = len(self.messages) - self.max_messages
        else:
            self.scroll_offset = (
                0  # No need to scroll if there aren't enough messages yet
            )

    def handle_scroll(self, direction):
        """Handle scrolling by adjusting the scroll offset."""
        # Scroll up (positive direction) or down (negative direction)
        if direction > 0 and self.scroll_offset > 0:
            self.scroll_offset -= 1  # Scroll up
        elif (
            direction < 0
            and self.scroll_offset < len(self.messages) - self.max_messages
        ):
            self.scroll_offset += 1  # Scroll down

    def draw(self, screen):
        """Draw the chat log on the screen with scrolling support."""
        y_offset = 10  # Start 10 pixels from the top
        window_width = screen.get_width()  # Get current window width

        # Only draw the visible messages based on the scroll offset
        visible_messages = self.messages[
            self.scroll_offset : self.scroll_offset + self.max_messages
        ]

        for message in visible_messages:
            text_surface = self.font.render(
                message, True, (255, 255, 255)
            )  # White text
            text_width = text_surface.get_width()
            x_position = window_width - text_width - 10  # Position for top-right corner
            screen.blit(
                text_surface, (x_position, y_offset)
            )  # Draw message at (x_position, y_offset)
            y_offset += 20  # Move down for the next message


def setup_chat_log(chat_font):
    global chat_log
    chat_log = ChatLog(chat_font, max_messages=10)


class GameState:
    def __init__(self):
        self.pot = 0
        self.current_bet = 0
        self.players = []
        self.current_player_index = 0
        self.small_blind_index = 0
        self.community_cards = []
        self.stage = PRE_FLOP
        self.players_must_act = True

    def rotate_blinds(self):
        """Rotate the small and big blinds to the next players."""
        # Increment the small blind index to the next player
        self.small_blind_index = (self.small_blind_index + 1) % len(self.players)

    def add_player(self, player):
        self.players.append(player)

    def handle_bet(self, player, amount, chat_log):
        """Handle the bet action from a player."""

        # Ensure that the player object has a 'has_folded' attribute (i.e., it's a Player object).
        if player.has_folded:
            raise ValueError(f"{player.name} has folded and cannot bet.")

        if amount > player.chips:
            raise ValueError(
                f"{player.name} does not have enough chips to bet {amount}."
            )

        # Deduct chips and update the current bet.
        player.chips -= amount
        player.current_bet += amount
        self.pot += amount
        self.current_bet = max(self.current_bet, player.current_bet)
        player.has_acted = True  # Mark the player as having acted.

        # Log the bet in the chat.
        chat_log.add_message(
            f"{player.name} has bet {amount} chips. Pot is now {self.pot} chips."
        )

    def handle_check(self, player, chat_log):
        """Handle the check action from a player."""
        try:
            # Call the check method on the Player object, not on GameState
            player.check(self.current_bet)
            chat_log.add_message(f"{player.name} checks.")
        except ValueError as e:
            chat_log.add_message(str(e))

    def handle_fold(self, player, chat_log):
        """Handle the fold action from a player."""
        try:
            player.fold()  # The player folds
            chat_log.add_message(f"{player.name} has folded.")

            # Check if only one player is left (this would end the round)
            if self.only_one_player_left():
                winner = next(p for p in self.players if not p.has_folded)
                chat_log.add_message(
                    f"{winner.name} wins the pot of {self.pot} chips by default!"
                )
                self.distribute_pot_to_winner(winner)

                pygame.time.delay(
                    2000
                )  # Short delay before resetting for the new round
                self.reset_for_new_round(deck, chat_log)  # Pass both deck and chat_log
        except AttributeError as e:
            chat_log.add_message(f"Error: {e}")

    def only_one_player_left(self):
        """Returns True if only one player is left in the game."""
        active_players = [player for player in self.players if not player.has_folded]
        return len(active_players) == 1

    def next_player(self, deck, chat_log):
        """Moves to the next active player and logs actions."""

        # Move to the next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

        # Skip folded players
        while self.players[self.current_player_index].has_folded:
            self.current_player_index = (self.current_player_index + 1) % len(
                self.players
            )

        # Check if all players have acted before moving to the next stage
        if self.all_players_have_acted():
            self.advance_stage(deck, chat_log)  # Pass both deck and chat_log
        else:
            chat_log.add_message(
                f"Next player is {self.players[self.current_player_index].name}"
            )
            print(f"Next player is {self.players[self.current_player_index].name}")

    def reset_for_new_round(self, deck, chat_log):
        """Resets the game state for a new round."""
        pygame.time.delay(2000)  # Delay before resetting for the next round
        deck[:] = create_deck()  # Reset and shuffle the deck
        self.pot = 0  # Reset the pot for the new round
        self.community_cards = []
        self.stage = PRE_FLOP
        self.players_must_act = True  # Players must act in the new round

        # Rotate the blinds to the next players
        self.rotate_blinds()

        # Reset players for the new round, but retain their blinds bet
        for player in self.players:
            player.reset_for_new_round()

        # Deal new cards to the players for the next round
        hands = deal_cards(deck, len(self.players), 2)
        for player, hand in zip(self.players, hands):
            player.hand = hand

        chat_log.add_message("New round starts!")
        print("New round starts!")

        # Post blinds after resetting (this is where current_bet is set to big blind)
        self.post_blinds()

        # Important: Do not reset players' current_bet here, since they should retain their blinds

    def post_blinds(self):
        """Posts the small and big blinds and sets the current bet to the big blind."""
        small_blind_player = self.players[self.small_blind_index]
        big_blind_player = self.players[
            (self.small_blind_index + 1) % len(self.players)
        ]

        # Deduct blinds from players' chips
        small_blind_player.chips -= SMALL_BLIND
        big_blind_player.chips -= BIG_BLIND

        # Set the players' current_bet to reflect the blinds they posted
        small_blind_player.current_bet = SMALL_BLIND
        big_blind_player.current_bet = BIG_BLIND

        # Add blinds to the pot
        self.pot += SMALL_BLIND + BIG_BLIND

        # Set the game's current bet to the big blind
        self.current_bet = BIG_BLIND
        print(f"Blinds posted - Current bet set to: {self.current_bet}")
        print(
            f"{small_blind_player.name}'s current bet: {small_blind_player.current_bet}"
        )
        print(f"{big_blind_player.name}'s current bet: {big_blind_player.current_bet}")
        print(f"Game's current bet: {self.current_bet}")

        # Set the current player to the first one to act (next after big blind)
        self.current_player_index = (self.small_blind_index + 2) % len(self.players)

    def all_players_folded(self):
        return all(player.has_folded for player in self.players)

    def should_end_round(self):
        active_players = [player for player in self.players if not player.has_folded]
        if len(active_players) <= 1:
            return True
        return all(player.current_bet == self.current_bet for player in active_players)

    def all_bets_equal(self):
        active_players = [player for player in self.players if not player.has_folded]
        if not active_players:
            return True
        return all(player.current_bet == self.current_bet for player in active_players)

    def advance_stage(self, deck, chat_log):
        """Advances the stage and deals the community cards for the next stage."""

        print(f"Advancing stage: {self.stage}, Current bet: {self.current_bet}")
        chat_log.add_message(
            f"Advancing stage: {self.stage}, Current bet: {self.current_bet}"
        )

        if self.stage == PRE_FLOP:
            # Do not reset current_bet here during pre-flop; it should remain as the big blind
            self.stage = FLOP
            self.community_cards = deck[:3]  # Deal the Flop (3 community cards)
            del deck[:3]
            print("Dealt the Flop.")
            chat_log.add_message("Dealt the Flop.")

            # Reset current_bet after the pre-flop stage is complete
            self.current_bet = 0
            print(
                f"Game's current bet reset to {self.current_bet} for the new stage: {self.stage}"
            )
            chat_log.add_message(
                f"Game's current bet reset to {self.current_bet} for the new stage: {self.stage}"
            )

        elif self.stage == FLOP:
            self.stage = TURN
            self.community_cards.append(deck[0])  # Deal the Turn (4th community card)
            del deck[0]
            print("Dealt the Turn.")
            chat_log.add_message("Dealt the Turn.")

            self.current_bet = 0  # Reset game’s bet for the new stage
            print(
                f"Game's current bet reset to {self.current_bet} for the new stage: {self.stage}"
            )
            chat_log.add_message(
                f"Game's current bet reset to {self.current_bet} for the new stage: {self.stage}"
            )

        elif self.stage == TURN:
            self.stage = RIVER
            self.community_cards.append(deck[0])  # Deal the River (5th community card)
            del deck[0]
            print("Dealt the River.")
            chat_log.add_message("Dealt the River.")

            self.current_bet = 0  # Reset game’s bet for the new stage
            print(
                f"Game's current bet reset to {self.current_bet} for the new stage: {self.stage}"
            )
            chat_log.add_message(
                f"Game's current bet reset to {self.current_bet} for the new stage: {self.stage}"
            )

        elif self.stage == RIVER:
            chat_log.add_message(
                "All community cards have been dealt. Determining the winner..."
            )
            print("All community cards have been dealt. Determining the winner...")
            winners = determine_winner(self.players, self.community_cards)

            if isinstance(winners, list) and len(winners) > 1:
                winner_names = ", ".join([winner.name for winner in winners])
                chat_log.add_message(f"It's a tie! The winners are: {winner_names}.")
                print(f"It's a tie! The winners are: {winner_names}.")

            else:
                chat_log.add_message(
                    f"{winners.name} wins the pot of {self.pot} chips!"
                )
                print(f"{winners.name} wins the pot of {self.pot} chips!")

            self.distribute_pot_to_winner(winners)
            self.reset_for_new_round(deck)

        # Reset players' bets and allow them to act again for the new stage (but not during pre-flop)
        if self.stage != PRE_FLOP:  # Only reset bets after the pre-flop stage
            for player in self.players:
                player.current_bet = 0  # Reset their bet for the new stage
                player.has_acted = False  # Reset their has_acted flag for the new stage
                print(f"{player.name}'s bet reset to {player.current_bet}.")
                chat_log.add_message(
                    f"{player.name}'s bet reset to {player.current_bet}."
                )

    def distribute_pot_to_winner(self, winners):
        """Distributes the pot to the winner or splits it among multiple winners."""
        if isinstance(winners, list):  # If there are multiple winners (tie)
            split_pot = self.pot // len(winners)
            for winner in winners:
                winner.chips += split_pot
                print(f"{winner.name} wins {split_pot} chips (split pot).")
        else:
            winners.chips += self.pot
            print(f"{winners.name} wins the pot of {self.pot} chips!")

        self.pot = 0  # Reset the pot after distribution

    def evaluate_hands(self):
        player_hands = {
            player: player.hand + self.community_cards for player in self.players
        }
        evaluated_hands = {
            player: evaluate_hand(hand) for player, hand in player_hands.items()
        }
        return evaluated_hands

    def determine_winner(self):
        """Determine the winner of the round."""
        # Pass the players and community cards to the determine_winner function
        winner = determine_winner(self.players, self.community_cards)
        return winner

    def all_players_have_acted(self):
        """Checks if all active players (who haven't folded) have either called, checked, or folded."""
        active_players = [player for player in self.players if not player.has_folded]

        # Ensure all active players have acted
        return all(player.has_acted for player in active_players)


def handle_player_action(action, deck):
    current_player = game_state.players[game_state.current_player_index]

    print(
        f"Before action: {current_player.name}'s current bet: {current_player.current_bet}, Game's current bet: {game_state.current_bet}"
    )

    if action == "call":
        amount_to_call = game_state.current_bet - current_player.current_bet
        if amount_to_call > 0:
            game_state.handle_bet(current_player, amount_to_call)
            print(f"{current_player.name} has called with {amount_to_call} chips.")
        else:
            print(f"{current_player.name} has already matched the current bet.")

    elif action == "check":
        try:
            game_state.handle_check(current_player)
        except ValueError as e:
            print(e)  # If the player can't check, display an error

    elif action == "fold":
        game_state.handle_fold(current_player)
        print(f"{current_player.name} has folded.")

    # After the action, check if all players have acted and advance to the next stage if necessary
    if game_state.all_players_have_acted():
        game_state.advance_stage(deck)  # Move to the next stage
    else:
        game_state.next_player(deck)

    print(
        f"After action: {current_player.name}'s current bet: {current_player.current_bet}, Game's current bet: {game_state.current_bet}"
    )


# Define blinds
SMALL_BLIND = 10
BIG_BLIND = 20


def rotate_blinds(self):
    """Rotate the small and big blinds to the next players."""
    self.current_player_index = (self.current_player_index + 1) % len(self.players)


def assign_blinds(chat_log):
    small_blind_player = game_state.players[game_state.current_player_index]
    big_blind_player = game_state.players[
        (game_state.current_player_index + 1) % len(game_state.players)
    ]

    # Deduct blinds from players' chips and add to the pot
    small_blind_player.chips -= SMALL_BLIND
    big_blind_player.chips -= BIG_BLIND
    game_state.pot += SMALL_BLIND + BIG_BLIND

    # Set the current bet to the big blind amount
    game_state.current_bet = BIG_BLIND

    # Update players' current bets
    small_blind_player.current_bet = SMALL_BLIND
    big_blind_player.current_bet = BIG_BLIND

    # Use the chat log to display messages
    chat_log.add_message(
        f"{small_blind_player.name} posts the small blind of {SMALL_BLIND} chips."
    )
    chat_log.add_message(
        f"{big_blind_player.name} posts the big blind of {BIG_BLIND} chips."
    )

    # Move the current player index to the next player after the big blind
    game_state.current_player_index = (game_state.current_player_index + 1) % len(
        game_state.players
    )


def reset_game_state():
    global game_state, players, deck
    # Create a new game state
    game_state = GameState()

    # Preserve the existing players and their chip counts
    for player in players:
        game_state.add_player(player)
        player.reset_for_new_round()  # Reset only the player's bet and fold status, not their chips

    # Deal new cards to the players
    deck = create_deck()
    hands = deal_cards(deck, len(players), 2)
    for player, hand in zip(players, hands):
        player.hand = hand

    # Rotate the blinds at the start of the new round
    rotate_blinds()

    # Assign blinds based on the new rotation
    assign_blinds(chat_log)

    # Reset the stage and community cards
    game_state.community_cards = []
    game_state.stage = "pre-flop"

    chat_log.add_message("New round starts!")


# Create and shuffle deck
def create_deck():
    ranks = ["02", "03", "04", "05", "06", "07", "08", "09", "10", "J", "Q", "K", "A"]
    suits = ["C", "D", "H", "S"]
    deck = [rank + suit for rank in ranks for suit in suits]
    random.shuffle(deck)
    return deck


# Deal cards to players
def deal_cards(deck, num_players, cards_per_player):
    hands = []
    for _ in range(num_players):
        hand = [deck.pop() for _ in range(cards_per_player)]
        hands.append(hand)
    return hands


game_state = GameState()

# Initialize players (one human player and one CFR bot)
players = [Player("Player 1", 1000), CFRBot("CFR Bot", 1000)]

# Deal cards to players
deck = create_deck()
hands = deal_cards(deck, len(players), 2)
for player, hand in zip(players, hands):
    player.hand = hand

# Add players to the game state
for player in players:
    game_state.add_player(player)
