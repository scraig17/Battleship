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

PLAYER_BOARD_POS = (40, 80)
OPPONENT_BOARD_POS = (520, 80)


class GUI:
    def __init__(self, client: GameClient, event_handler: GameEventHandler, player_name: str):
        self.client = client
        self.event_handler = event_handler
        self.player_name = player_name
        self.is_placing_ships = True
        self.next_ship_index = 0
        self.chat_input = ""
        self.chat_history = []
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

        event_view = EventView(window, color=WINDOW_FG_COLOR)
        command_buttons = CommandButtons(window, client=self.client)
        self.player_board = BoardView(window, self.client, is_player_board=True, top_left=PLAYER_BOARD_POS)
        self.opponent_board = BoardView(window, self.client, is_player_board=False, top_left=OPPONENT_BOARD_POS)

        clock = pygame.time.Clock()
        done = False

        while not done:
            for pending_event in self.event_handler.pending_events():
                print(f"[DEBUG] Received event: {pending_event}")
                msg = str(pending_event)
                self.status_message.append(msg)
                if len(self.status_message) > 3:
                    self.status_message.pop(0)

                event_type = pending_event.get("event")
                if event_type == "ChatEvent":
                    chat_msg = pending_event.get("message", "")
                    if isinstance(chat_msg, str):
                        self.chat_history.append(chat_msg)
                        if len(self.chat_history) > 6:
                            self.chat_history.pop(0)

                elif event_type == "AttackEvent":
                    msg = pending_event.get("message", "")
                    coords = self._parse_attack_coords(msg)
                    if coords:
                        row, col = coords
                        attacker = msg.split(" ")[0]
                        result = "hit" if "hit" in msg else "miss"
                        if attacker == self.player_name:
                            self.opponent_board.board[row][col] = result
                        else:
                            self.player_board.board[row][col] = result

                elif event_type == "GameOverEvent":
                    winner = pending_event.get("winner_id", "Unknown")
                    self._show_game_over_screen(winner)
                    done = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.chat_input.strip():
                            try:
                                self.client.send_chat(self.chat_input.strip())
                                # Also append to local chat history
                                self.chat_history.append(f"{self.player_name}: {self.chat_input.strip()}")
                                if len(self.chat_history) > 5:
                                    self.chat_history.pop(0)
                            except Exception as e:
                                print(f"[ERROR] Failed to send chat message: {e}")
                            self.chat_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.chat_input = self.chat_input[:-1]
                    else:
                        self.chat_input += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if self.is_placing_ships:
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
                                    "horizontal": True
                                }
                                self.player_board.place_ship(ship)
                                self.next_ship_index += 1
                                if self.next_ship_index == len(self.ship_types):
                                    self.finish_ship_placement()
                    else:
                        grid_x, grid_y = OPPONENT_BOARD_POS
                        col = (x - grid_x) // GRID_SIZE
                        row = (y - grid_y) // GRID_SIZE
                        if 0 <= row < 10 and 0 <= col < 10:
                            self.opponent_board.handle_attack(row, col)
                else:
                    command_buttons.consume_ui_event(event)

            window.fill(WINDOW_BG_COLOR)

            # Draw chat first to avoid it being covered
            chat_font = pygame.font.SysFont(None, 24)
            input_y = DISPLAY_SIZE[1] - 30
            history_y = input_y - 120

            input_surf = chat_font.render("> " + self.chat_input, True, (0, 0, 0))
            window.blit(input_surf, (20, input_y))

            y = history_y
            for line in self.chat_history[-6:]:
                line_surf = chat_font.render(line, True, (0, 0, 0))
                window.blit(line_surf, (20, y))
                y += 20

            self.player_board.draw()
            self.opponent_board.draw()
            event_view.draw()
            command_buttons.draw()

            # Draw status
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
            print(f"[ERROR] Failed to parse coords: {e}")
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
                if event.type in [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    waiting = False
