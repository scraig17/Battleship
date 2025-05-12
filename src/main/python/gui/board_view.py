import pygame

# Constants for drawing
GRID_SIZE = 40
HIT_COLOR = (255, 0, 0)     # Red
MISS_COLOR = (0, 0, 255)    # Blue
SHIP_COLOR = (0, 255, 0)    # Green
EMPTY_COLOR = (255, 255, 255)  # White
LINE_COLOR = (0, 0, 0)      # Black

class BoardView:
    def __init__(self, surface, client, is_player_board=True, top_left=(0, 0)):
        """
        Initialize a visual 10x10 board grid.
        :param surface: Pygame surface to draw on
        :param client: GameClient for sending attacks
        :param is_player_board: True for player board, False for opponent
        :param top_left: Top-left position (x, y) for drawing the board
        """
        self.surface = surface
        self.client = client
        self.is_player_board = is_player_board
        self.top_left = top_left  # Where to draw this board
        self.board = [["empty" for _ in range(10)] for _ in range(10)]
        self.ships = []

    def draw(self):
        """Draw the board with all states."""
        offset_x, offset_y = self.top_left
        for row in range(10):
            for col in range(10):
                cell = self.board[row][col]

                # Determine color
                if cell == "hit":
                    color = HIT_COLOR
                elif cell == "miss":
                    color = MISS_COLOR
                elif cell == "ship" and self.is_player_board:
                    color = SHIP_COLOR  # Only show ships on your own board
                else:
                    color = EMPTY_COLOR

                # Compute position and draw cell
                x = offset_x + col * GRID_SIZE
                y = offset_y + row * GRID_SIZE
                pygame.draw.rect(self.surface, color, pygame.Rect(x, y, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(self.surface, LINE_COLOR, pygame.Rect(x, y, GRID_SIZE, GRID_SIZE), 1)

    def handle_attack(self, row, col):
        """Send an attack to the server."""
        if not self.is_player_board:
            self.client.send_attack(row, col)

    def place_ship(self, ship):
        """Place a ship visually and track it."""
        row = ship['row']
        col = ship['col']
        size = ship['size']
        horizontal = ship['horizontal']

        # Ensure the ship fits on the board
        if horizontal and col + size > 10:
            print(f"Ship '{ship['name']}' doesn't fit horizontally at ({row},{col})")
            return
        if not horizontal and row + size > 10:
            print(f"Ship '{ship['name']}' doesn't fit vertically at ({row},{col})")
            return

        # Place the ship on the board
        for i in range(size):
            r = row
            c = col
            if horizontal:
                c += i
            else:
                r += i
            if 0 <= r < 10 and 0 <= c < 10:
                self.board[r][c] = "ship"

        self.ships.append(ship)
        print(f"Placed ship '{ship['name']}' on board at ({row},{col})")

    def update_cell(self, row, col, result):
        """Update a single cell based on attack result."""
        if result == "hit":
            self.board[row][col] = "hit"
        elif result == "miss":
            self.board[row][col] = "miss"

    def mark_attack(self, row, col, result):
        """Mark the result of an attack at (row, col)."""
        if result == "hit":
            self.board[row][col] = "hit"
        elif result == "miss":
            self.board[row][col] = "miss"
