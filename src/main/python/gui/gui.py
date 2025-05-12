import pygame

from .client import GameClient
from .command_buttons import GRID_SIZE, CommandButtons
from .event_handler import GameEventHandler
from .event_view import EventView
from .board_view import BoardView

# UI layout
DISPLAY_SIZE = (1000, 600)
FRAME_RATE = 30
WINDOW_BG_COLOR = "lightgray"
WINDOW_FG_COLOR = "darkgreen"
WINDOW_TITLE = "Battleship"

# Board drawing offset
PLAYER_BOARD_POS = (40, 80)
OPPONENT_BOARD_POS = (520, 80)


class GUI:
    def __init__(self, client: GameClient, event_handler: GameEventHandler, player_name: str):
        self.client = client
        self.event_handler = event_handler
        self.player_name = player_name
        self.is_placing_ships = True
        self.next_ship_index = 0
        self.ship_types = [
            {"name": "Destroyer", "size": 2},
            {"name": "Submarine", "size": 3},
            {"name": "Cruiser", "size": 3},
            {"name": "Battleship", "size": 4},
            {"name": "Carrier", "size": 5},
        ]
        self.status_message = []

    def run(self):
        
        pygame.init()
        window = pygame.display.set_mode(DISPLAY_SIZE)
        pygame.display.set_caption(f"{self.player_name} @ {WINDOW_TITLE}")

        # Components
        event_view = EventView(window, color=WINDOW_FG_COLOR)
        command_buttons = CommandButtons(window, client=self.client)

        # Boards
        self.player_board = BoardView(window, self.client, is_player_board=True, top_left=PLAYER_BOARD_POS)
        self.opponent_board = BoardView(window, self.client, is_player_board=False, top_left=OPPONENT_BOARD_POS)

        clock = pygame.time.Clock()
        done = False

        while not done:
            for pending_event in self.event_handler.pending_events():
                print(f"[DEBUG] Received event object: {pending_event} ({type(pending_event)})")
                msg = str(pending_event)
                self.status_message.append(msg)
                if len(self.status_message) > 3:
                    self.status_message.pop(0)

                if pending_event.get("event") == "AttackEvent":
                    msg = pending_event.get("message", "")
                    coords = self._parse_attack_coords(msg)
                    if coords:
                        row, col = coords
                        attacker = msg.split(" ")[0]  # First word is attacker name
                        result = "hit" if "hit" in msg else "miss"

                        if attacker == self.player_name:
                            # You made the attack, update opponent board
                            self.opponent_board.board[row][col] = result
                        else:
                            # You were attacked, update your own board
                            self.player_board.board[row][col] = result

                if pending_event.get("event") == "GameOverEvent":
                    winner = pending_event.get("winner_id", "Unknown")
                    print(f"[DEBUG GUI] Extracted winner_id: {winner}")
                    self._show_game_over_screen(winner)
                    done = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()

                    if self.is_placing_ships:
                        # Check if click is within player board
                        grid_x, grid_y = PLAYER_BOARD_POS
                        col = (x - grid_x) // GRID_SIZE
                        row = (y - grid_y) // GRID_SIZE

                        if 0 <= row < 10 and 0 <= col < 10:
                            if self.next_ship_index < len(self.ship_types):
                                ship_type = self.ship_types[self.next_ship_index]
                                ship = {
                                    "name": ship_type["name"],
                                    "size": ship_type["size"],
                                    "row": row,
                                    "col": col,
                                    "horizontal": True  # Hardcoded, could be toggleable later
                                }
                                self.player_board.place_ship(ship)
                                print(f"Placed {ship['name']} at ({row},{col})")
                                self.next_ship_index += 1
                                if self.next_ship_index == len(self.ship_types):
                                    self.finish_ship_placement()
                    else:
                        # Handle attacks on opponent board
                        grid_x, grid_y = OPPONENT_BOARD_POS
                        col = (x - grid_x) // GRID_SIZE
                        row = (y - grid_y) // GRID_SIZE
                        if 0 <= row < 10 and 0 <= col < 10:
                            self.opponent_board.handle_attack(row, col)

                else:
                    command_buttons.consume_ui_event(event)

            window.fill(WINDOW_BG_COLOR)
            self.player_board.draw()
            self.opponent_board.draw()
            event_view.draw()
            command_buttons.draw()
            font = pygame.font.SysFont(None, 20)
            y = 20
            for msg in self.status_message:
                status_surface = font.render(msg, True, (0, 100, 0))
                window.blit(status_surface, (20, y))
                y += 22 
            pygame.display.flip()
            clock.tick(FRAME_RATE)

        pygame.quit()

    def finish_ship_placement(self):
        ships = self.player_board.ships
        self.client.send_place_ships(ships)
        print("Finished placing ships and sent to server.")
        self.is_placing_ships = False


    def _parse_attack_coords(self, message: str):
        try:
            if "attacked" not in message:
                return None
            coord_part = message.split("attacked")[1].split("-")[0].strip()
            coord_str = coord_part.strip("() ")
            row, col = map(int, coord_str.split(","))
            return row, col
        except Exception as e:
            print(f"[ERROR] Failed to parse attack coords from message '{message}': {e}")
            return None

    def _show_game_over_screen(self, winner_id):
        result_text = f"Game Over!"
        font = pygame.font.SysFont(None, 80)
        small_font = pygame.font.SysFont(None, 40)

        screen = pygame.display.get_surface()
        screen.fill("black")
        text = font.render(result_text, True, (255, 255, 255))
        winner_label = f"Winner: {winner_id}" if winner_id else "Winner: Unknown"
        winnertext = font.render(winner_label, True, (255, 255, 255))      
        subtext = small_font.render("Press any key to exit", True, (200, 200, 200))

        screen.blit(text, ((DISPLAY_SIZE[0] - text.get_width()) // 2, 200))
        screen.blit(winnertext, ((DISPLAY_SIZE[0] - winnertext.get_width()) // 2, 300))
        screen.blit(subtext, ((DISPLAY_SIZE[0] - subtext.get_width()) // 2, 400))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
