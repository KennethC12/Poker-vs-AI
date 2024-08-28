import pygame
import os
from evaluator import *
from player import *
from game_state import *

# Initialize Pygame
pygame.init()

# Initialize the font module
pygame.font.init()

clock = pygame.time.Clock()


chat_font = pygame.font.Font(None, 20)
chat_log = ChatLog(chat_font, max_messages=10)

# Now, you can use `chat_log` in other modules


WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Poker by Kenneth Chen")

# Load and convert the background image
BACKGROUND_ORIG = pygame.image.load("images/poker-table.png").convert_alpha()


def scale_background():
    return pygame.transform.scale(
        BACKGROUND_ORIG, (WIDTH, HEIGHT)
    )  # Scale based on new window dimensions


# Initial scaling of the background image
BACKGROUND = scale_background()


def draw_bg():
    WIN.blit(BACKGROUND, (0, 0))


def resize_window(width, height):
    global WIN, WIDTH, HEIGHT, BACKGROUND
    WIDTH, HEIGHT = width, height
    WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    BACKGROUND = scale_background()  # Rescale background

    # Update button positions based on the new window dimensions
    for button in buttons:
        button.update_position(WIDTH, HEIGHT)

    bet_text_box.update_position(WIDTH, HEIGHT)


def load_card_images():
    card_images = {}
    suits = ["hearts", "diamonds", "clubs", "spades"]
    ranks = [
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "Jack",
        "Queen",
        "King",
        "Ace",
    ]

    for suit in suits:
        for rank in ranks:
            card_name = f"{rank}_of_{suit}.png"
            image_path = os.path.join("cards", card_name)
            print(f"Loading image: {image_path}")  # Debug information
            if not os.path.exists(image_path):
                print(f"File not found: {image_path}")  # Debug information
            else:
                try:
                    card_images[(rank, suit)] = pygame.image.load(
                        image_path
                    ).convert_alpha()
                except pygame.error as e:
                    print(f"Error loading image: {image_path} - {e}")

    # Load the card back image
    card_images["back"] = pygame.image.load(
        os.path.join("cards", "card_back.png")
    ).convert_alpha()

    return card_images


card_images = load_card_images()


class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, screen, font):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False


class TextBox:
    def __init__(self, x_percent, y_percent, w_percent, h_percent, font):
        # Store position and size as percentages
        self.x_percent = x_percent
        self.y_percent = y_percent
        self.w_percent = w_percent
        self.h_percent = h_percent
        self.rect = pygame.Rect(0, 0, 0, 0)  # Initial placeholder rect
        self.color = pygame.Color("black")
        self.text = ""
        self.font = font
        self.txt_surface = font.render(self.text, True, self.color)
        self.active = False

    def update_position(self, width, height):
        """Update the TextBox position and size based on window dimensions."""
        self.rect = pygame.Rect(
            int(self.x_percent * width),
            int(self.y_percent * height),
            int(self.w_percent * width),
            int(self.h_percent * height),
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = pygame.Color("black") if self.active else pygame.Color("black")
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)
        if event.type == pygame.MOUSEWHEEL:
            chat_log.handle_scroll(event.y)

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


# Main loop
running = True

clock = pygame.time.Clock()
FPS = 60


def draw_pot(screen, pot, font):
    """Displays the total pot amount on the screen."""
    pot_text = font.render(
        f"Total Pot: {pot} chips", True, (255, 255, 255)
    )  # White text color
    pot_rect = pot_text.get_rect(
        center=(screen.get_width() // 2, 160)
    )  # Display at the top center of the screen
    screen.blit(pot_text, pot_rect)


def draw_cards(screen, cards, stage):
    card_width = 70
    card_height = 100
    spacing = 20
    start_x = (screen.get_width() - (card_width + spacing) * len(cards)) // 2
    y = screen.get_height() // 2 - card_height // 2

    # Map ranks and suits to their display names for image filenames
    rank_map = {
        "02": "02",
        "03": "03",
        "04": "04",
        "05": "05",
        "06": "06",
        "07": "07",
        "08": "08",
        "09": "09",
        "10": "10",
        "J": "Jack",
        "Q": "Queen",
        "K": "King",
        "A": "Ace",
    }
    suit_map = {"C": "clubs", "D": "diamonds", "H": "hearts", "S": "spades"}

    # Display only the number of cards appropriate for the current stage
    if stage == PRE_FLOP:
        cards_to_display = 0
    elif stage == FLOP:
        cards_to_display = 3
    elif stage == TURN:
        cards_to_display = 4
    elif stage == RIVER:
        cards_to_display = 5

    # Loop through the community cards and display them on the screen
    for i, card in enumerate(cards[:cards_to_display]):
        rank = rank_map.get(card[:-1], card[:-1])  # Extract rank from the card string
        suit = suit_map.get(card[-1], card[-1])  # Extract suit from the card string
        card_key = (rank, suit)

        if card_key in card_images:
            card_image = card_images[card_key]
            x = start_x + i * (card_width + spacing)
            screen.blit(card_image, (x, y))
        else:
            print(f"Card image for {card_key} not found.")


# Font for buttons
font = pygame.font.Font(None, 36)

# Assign blinds at the start of the round
assign_blinds(chat_log)

# Create the TextBox instance
bet_text_box = TextBox(0.63125, 0.8333, 0.175, 0.0533, font)

# Define button actions


def fold_action(chat_log):
    current_player = game_state.players[game_state.current_player_index]
    try:
        game_state.handle_fold(current_player, chat_log)  # Added chat_log
        print(f"{current_player.name} has folded.")
        game_state.next_player(deck, chat_log)  # Pass both deck and chat_log
    except ValueError as e:
        chat_log.add_message(f"Error: {str(e)}")


def call_action(chat_log):
    current_player = game_state.players[game_state.current_player_index]
    try:
        amount_to_call = game_state.current_bet - current_player.current_bet
        if amount_to_call > 0:
            game_state.handle_bet(current_player, amount_to_call, chat_log)
            chat_log.add_message(
                f"{current_player.name} has called with {amount_to_call} chips. Pot is now {game_state.pot} chips."
            )
        else:
            chat_log.add_message(f"{current_player.name} has checked.")

        # Check if all players have acted (use updated check)
        if game_state.all_players_have_acted():
            game_state.advance_stage(deck, chat_log)  # Pass chat_log here
        else:
            game_state.next_player(deck, chat_log)  # Pass chat_log here as well
    except ValueError as e:
        chat_log.add_message(f"Error: {str(e)}")


def bet_any_amount_action(chat_log):
    current_player = game_state.players[game_state.current_player_index]
    try:
        amount_to_bet = int(
            bet_text_box.text
        )  # This can raise an error if bet_text_box.text is empty or invalid
        game_state.handle_bet(current_player, amount_to_bet, chat_log)  # Added chat_log
        chat_log.add_message(f"{current_player.name} has bet {amount_to_bet} chips.")
        game_state.next_player(
            deck, chat_log
        )  # Pass the deck and chat_log as arguments
    except ValueError as e:
        chat_log.add_message(f"Error: {str(e)}")


def check_action(chat_log):
    """Handles the check action and advances the stage if all players have checked."""
    current_player = game_state.players[game_state.current_player_index]

    try:
        game_state.handle_check(current_player, chat_log)  # Pass chat_log here
        chat_log.add_message(f"{current_player.name} has checked.")

        # Move to the next player or advance the stage if all players have acted
        if game_state.all_players_have_acted():
            game_state.advance_stage(deck, chat_log)
        else:
            game_state.next_player(deck, chat_log)
    except ValueError as e:
        chat_log.add_message(f"Error: {str(e)}")


def display_cards(screen, players):
    """Displays player cards on the screen."""
    rank_map = {
        "02": "02",
        "03": "03",
        "04": "04",
        "05": "05",
        "06": "06",
        "07": "07",
        "08": "08",
        "09": "09",
        "10": "10",
        "J": "jack",
        "Q": "queen",
        "K": "king",
        "A": "ace",
    }
    suit_map = {"C": "clubs", "D": "diamonds", "H": "hearts", "S": "spades"}

    # Define positions for Player 1 (bottom-center) and Player 2 (top-center)
    card_width = 70
    spacing = -20
    num_cards = 2  # Each player has 2 cards

    screen_width = screen.get_width()

    # Calculate horizontal starting positions to center the cards
    player1_start_x = (
        screen_width - (num_cards * (card_width + spacing) - spacing)
    ) // 2  # Centered bottom
    player2_start_x = (
        screen_width - (num_cards * (card_width + spacing) - spacing)
    ) // 2  # Centered top

    player_positions = [
        (player1_start_x, screen.get_height() - 140),  # Player 1 (center-bottom)
        (player2_start_x, 40),  # Player 2 (center-top)
    ]

    # Loop through players and display their cards at specific positions
    for i, player in enumerate(players):
        player_pos_x, player_pos_y = player_positions[
            i
        ]  # Get the x and y coordinates for the player's cards

        for j in range(num_cards):
            if i == 1:  # Player 2, opponent
                # Show the card back for the opponent
                card_image = card_images["back"]
            else:
                # Show the actual card for Player 1 (bottom)
                card = player.hand[j]
                if len(card) < 2:
                    print(f"Error: Unexpected card format: {card}")
                    continue

                rank = rank_map.get(card[:-1])
                if rank is None:
                    print(f"Error: Rank '{card[:-1]}' not found in rank_map.")
                    continue

                suit = suit_map.get(card[-1])
                if suit is None:
                    print(f"Error: Suit '{card[-1]}' not found in suit_map.")
                    continue

                card_filename = f"{rank}_of_{suit}.png"
                card_path = os.path.join("cards", card_filename)
                if not os.path.isfile(card_path):
                    print(f"Error: File '{card_path}' not found.")
                    continue

                card_image = pygame.image.load(card_path)

            # Display the card (or card back) with spacing between them
            screen.blit(
                card_image, (player_pos_x + j * (card_width + spacing), player_pos_y)
            )


def display_chip_count(screen, players, player_positions):
    """
    Displays player chip counts on the screen, positioned based on player_positions.
    player_positions: List of tuples, where each tuple contains the (x, y) position for each player's chip count.
    """
    font = pygame.font.Font(None, 36)

    # Loop through players and display their chips at specific positions
    for i, player in enumerate(players):
        chip_text = font.render(
            f"{player.name}: {player.chips} chips", True, (255, 255, 255)
        )  # White text color

        # Get the x and y position for the player from player_positions
        chip_x, chip_y = player_positions[i]

        # Display the chip count at the specified position
        screen.blit(chip_text, (chip_x, chip_y))


def draw_game_state(screen, players):
    # Define player chip positions
    player_positions = [
        (50, HEIGHT - 100),  # Adjust based on the new height
        (50, 50),  # Player 2 chip position (top-left)
    ]

    # Display player chips using the defined positions
    display_chip_count(screen, players, player_positions)

    # (You can also call display_cards() or other functions here)
    display_cards(screen, players)


# Function to distribute the pot to the winner
def distribute_pot_to_winner(winner):
    winner.chips += game_state.pot
    game_state.pot = 0


def simulate_game_utility(bot, game_state):
    # Example of calculating utility based on chips won/lost
    initial_chips = bot.chips
    current_chips = (
        bot.chips
    )  # At the end of the round, update this with the final chip count
    return current_chips - initial_chips  # The


class Button:
    def __init__(
        self,
        text,
        x_percent,
        y_percent,
        width_percent,
        height_percent,
        color,
        hover_color,
        action=None,
    ):
        self.text = text  # Store the button label
        self.x_percent = x_percent
        self.y_percent = y_percent
        self.width_percent = width_percent
        self.height_percent = height_percent
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.rect = pygame.Rect(0, 0, 0, 0)  # Placeholder, updated in the resize method

    def update_position(self, width, height):
        """Update the button position and size based on the current window size."""
        self.rect = pygame.Rect(
            int(self.x_percent * width),  # X position
            int(self.y_percent * height),  # Y position
            int(self.width_percent * width),  # Button width
            int(self.height_percent * height),  # Button height
        )

    def draw(self, screen, font):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        text_surface = font.render(
            self.text, True, (0, 0, 0)
        )  # Render the button label
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False


# Create buttons using percentage positions and sizes based on the initial window size (800x600)
buttons = [
    Button(
        "Fold",
        0.0625,
        0.9166,
        0.125,
        0.083,
        (200, 0, 0),
        (255, 0, 0),
        lambda: fold_action(chat_log),
    ),  # 50/800, 550/600, 100/800, 50/600
    Button(
        "Call",
        0.4375,
        0.9166,
        0.125,
        0.083,
        (0, 0, 200),
        (0, 0, 255),
        lambda: call_action(chat_log),
    ),  # 350/800, 550/600, 100/800, 50/600
    Button(
        "Bet",
        0.6250,
        0.9166,
        0.1875,
        0.083,
        (200, 200, 0),
        (255, 255, 0),
        lambda: bet_any_amount_action(chat_log),
    ),  # 500/800, 550/600, 150/800, 50/600
    Button(
        "Check",
        0.8750,
        0.9166,
        0.125,
        0.083,
        (200, 200, 200),
        (255, 255, 255),
        lambda: check_action(chat_log),
    ),  # 700/800, 550/600, 100/800, 50/600
]


# In the main game loop, handle the CFR bot's actions and regret updates


def main():
    global WIN, clock, game_state, deck

    # Initial button position setup
    for button in buttons:
        button.update_position(WIDTH, HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                resize_window(event.w, event.h)

            # Human player actions
            if game_state.players[game_state.current_player_index].name == "Player 1":
                for button in buttons:
                    button.is_clicked(event)
                bet_text_box.handle_event(event)

        # CFRBot takes action automatically when it's Player 2's turn
        if game_state.players[game_state.current_player_index].name == "CFR Bot":
            bot = game_state.players[game_state.current_player_index]
            action = bot.choose_action(game_state)
            bot.act(game_state, deck, chat_log)

            # Simulate the outcome of the game and calculate utility
            game_utility = simulate_game_utility(bot, game_state)

            # Update regrets after the action is taken
            bot.update_regret(action, game_utility, baseline_value=0)

            # Move to the next player or advance stage if all have acted
            if game_state.all_players_have_acted():
                game_state.advance_stage(deck, chat_log)
            else:
                game_state.next_player(deck, chat_log)

        # Draw the game state (background, players, chips, etc.)
        draw_bg()
        draw_game_state(WIN, game_state.players)

        # Draw the community cards based on the current stage
        draw_cards(WIN, game_state.community_cards, game_state.stage)

        # Draw the buttons (for human player)
        for button in buttons:
            button.draw(WIN, font)

        # Draw the total pot amount on the screen
        draw_pot(WIN, game_state.pot, font)

        chat_log.draw(WIN)

        # Draw the text box (for human player)
        bet_text_box.draw(WIN)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()


# Call the main game loop
if __name__ == "__main__":
    main()
