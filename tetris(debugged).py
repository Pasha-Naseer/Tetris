import json
import matplotlib.pyplot as plt
import pygame
import random
import os
import datetime
import tempfile

# Initialize Pygame
pygame.init()

# Screen size
WIDTH, HEIGHT = 300, 600
ROWS, COLS = 20, 10
BLOCK_SIZE = WIDTH // COLS

# Leaderboard file
RECORDS_FILE = "tetris-records.json"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (80, 80, 80)

# Tetromino shapes
SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
}

SHAPE_COLORS = {
    "I": CYAN,
    "O": YELLOW,
    "T": PURPLE,
    "S": GREEN,
    "Z": RED,
    "J": BLUE,
    "L": ORANGE,
}


def load_records(filename=RECORDS_FILE):
    """Load leaderboard records without crashing on missing or invalid files.

    Expected format:
    {
        "timestamp": {"player_name": score}
    }

    Invalid individual entries are ignored. If the whole JSON file is
    malformed, it is preserved under a .corrupt timestamped filename.
    """
    if not os.path.exists(filename):
        return {}

    try:
        with open(filename, "r", encoding="utf-8") as records_file:
            data = json.load(records_file)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        backup_name = (
            f"{filename}.corrupt-"
            f"{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )
        try:
            os.replace(filename, backup_name)
            print(
                f"Warning: leaderboard JSON was invalid ({error}). "
                f"The original file was preserved as '{backup_name}'. "
                "Starting with an empty leaderboard."
            )
        except OSError as backup_error:
            print(
                f"Warning: leaderboard JSON was invalid ({error}), and "
                f"the file could not be backed up ({backup_error}). "
                "Starting with an empty leaderboard without overwriting it."
            )
        return {}
    except OSError as error:
        print(f"Warning: could not read leaderboard: {error}")
        return {}

    if not isinstance(data, dict):
        print("Warning: leaderboard root must be a JSON object. Ignoring its contents.")
        return {}

    valid_records = {}
    for timestamp, player_data in data.items():
        if not isinstance(timestamp, str) or not isinstance(player_data, dict):
            continue

        valid_player_data = {}
        for player_name, score in player_data.items():
            if (
                isinstance(player_name, str)
                and player_name.strip()
                and isinstance(score, int)
                and not isinstance(score, bool)
                and score >= 0
            ):
                valid_player_data[player_name] = score

        if valid_player_data:
            valid_records[timestamp] = valid_player_data

    return valid_records


def save_records(data, filename=RECORDS_FILE):
    """Save records atomically so an interrupted write is less likely to
    leave a partially-written JSON file.
    """
    directory = os.path.dirname(os.path.abspath(filename))
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=directory,
            delete=False,
            suffix=".tmp",
        ) as temp_file:
            temp_path = temp_file.name
            json.dump(data, temp_file, indent=4, ensure_ascii=False)
            temp_file.flush()
            os.fsync(temp_file.fileno())

        os.replace(temp_path, filename)
        return True

    except (OSError, TypeError, ValueError) as error:
        print(f"Error: could not save leaderboard: {error}")
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        return False


def create_grid(locked_positions=None):
    if locked_positions is None:
        locked_positions = {}

    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLS):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid


class Tetromino:
    def __init__(self, shape):
        self.shape = shape
        self.color = SHAPE_COLORS[shape]
        self.rotation = 0
        self.x = COLS // 2 - len(SHAPES[shape][0]) // 2
        self.y = 0

    def image(self):
        return self.rotate(self.rotation)

    def rotate(self, rot):
        shape = SHAPES[self.shape]
        for _ in range(rot % 4):
            shape = [list(row) for row in zip(*shape[::-1])]
        return shape

    def get_cells(self):
        positions = []
        shape_matrix = self.image()
        for i, row in enumerate(shape_matrix):
            for j, val in enumerate(row):
                if val:
                    positions.append((self.x + j, self.y + i))
        return positions

    def valid_position(self, grid):
        for x, y in self.get_cells():
            if x < 0 or x >= COLS or y < 0 or y >= ROWS:
                return False
            if grid[y][x] != BLACK:
                return False
        return True

    def move(self, dx, dy, grid):
        self.x += dx
        self.y += dy
        if not self.valid_position(grid):
            self.x -= dx
            self.y -= dy
            return False
        return True


def clear_rows(grid, locked):
    full_rows = [y for y in range(ROWS) if BLACK not in grid[y]]

    for y in full_rows:
        for x in range(COLS):
            locked.pop((x, y), None)

    for key in sorted(list(locked.keys()), key=lambda position: position[1], reverse=True):
        x, y = key
        cleared_below = sum(1 for row in full_rows if row > y)
        if cleared_below > 0:
            locked[(x, y + cleared_below)] = locked.pop((x, y))

    return len(full_rows)


def calculate_score(lines_cleared):
    scores = {1: 100, 2: 300, 3: 500, 4: 800}
    return scores.get(lines_cleared, 0)


def draw_grid(screen, grid):
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(
                screen,
                grid[y][x],
                (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
            )

    for y in range(ROWS):
        pygame.draw.line(screen, WHITE, (0, y * BLOCK_SIZE), (WIDTH, y * BLOCK_SIZE))
    for x in range(COLS):
        pygame.draw.line(screen, WHITE, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, HEIGHT))


def draw_score(screen, score, player_name, font):
    score_text = font.render(f"{player_name} - Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))


def draw_pause(screen, font):
    pause_text = font.render("Paused", True, WHITE)
    pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(pause_text, pause_rect)


def get_player_name(screen, title_font, input_font):
    player_name = ""
    input_active = True

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if player_name.strip():
                        input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 12 and event.unicode.isprintable():
                    player_name += event.unicode

        screen.fill(BLACK)
        title_text = title_font.render("Enter Player Name", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        screen.blit(title_text, title_rect)

        input_box = pygame.Rect(40, HEIGHT // 2 - 10, WIDTH - 80, 40)
        pygame.draw.rect(screen, WHITE, input_box, 2)

        name_surface = input_font.render(player_name, True, WHITE)
        screen.blit(name_surface, (input_box.x + 10, input_box.y + 8))

        hint_text = input_font.render("Press Enter to start", True, GRAY)
        hint_rect = hint_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(hint_text, hint_rect)
        pygame.display.update()

    return player_name.strip()


def build_leaderboard(records):
    """Return each player's best score, sorted from highest to lowest."""
    best_scores = {}

    for player_data in records.values():
        for player_name, score in player_data.items():
            normalized_name = player_name.strip().lower()
            if not normalized_name:
                continue
            best_scores[normalized_name] = max(
                score, best_scores.get(normalized_name, 0)
            )

    return sorted(best_scores.items(), key=lambda item: item[1], reverse=True)


def show_leaderboard(records):
    leaderboard = build_leaderboard(records)
    if not leaderboard:
        print("No leaderboard records to display yet.")
        return

    names = [name for name, _ in leaderboard]
    scores = [score for _, score in leaderboard]

    print("Leaderboard:")
    for position, (name, score) in enumerate(leaderboard, start=1):
        print(f"{position}. {name} - {score}")

    fig, ax = plt.subplots()
    bars = ax.bar(names, scores)
    ax.bar_label(bars, fmt="%d")
    ax.set_ylabel("Scores")
    ax.set_title("All-time best players!")
    plt.tight_layout()
    plt.show()


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 24)
    title_font = pygame.font.SysFont("arial", 30)

    player_name = get_player_name(screen, title_font, font)
    if player_name is None:
        pygame.quit()
        return

    locked_positions = {}
    current_piece = Tetromino(random.choice(list(SHAPES.keys())))
    fall_time = 0
    fall_speed = 0.5
    score = 0
    paused = False

    running = True
    while running:
        clock.tick()
        grid = create_grid(locked_positions)

        if not paused:
            fall_time += clock.get_rawtime()

            if fall_time / 1000 >= fall_speed:
                fall_time = 0
                if not current_piece.move(0, 1, grid):
                    for x, y in current_piece.get_cells():
                        locked_positions[(x, y)] = current_piece.color
                    grid = create_grid(locked_positions)
                    lines_cleared = clear_rows(grid, locked_positions)
                    score += calculate_score(lines_cleared)
                    fall_speed = max(0.08, 0.5 - (score // 500) * 0.03)
                    grid = create_grid(locked_positions)
                    current_piece = Tetromino(random.choice(list(SHAPES.keys())))
                    if not current_piece.valid_position(grid):
                        running = False
        else:
            fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                elif not paused:
                    if event.key == pygame.K_LEFT:
                        current_piece.move(-1, 0, grid)
                    elif event.key == pygame.K_RIGHT:
                        current_piece.move(1, 0, grid)
                    elif event.key == pygame.K_DOWN:
                        current_piece.move(0, 1, grid)
                    elif event.key == pygame.K_UP:
                        current_piece.rotation += 1
                        if not current_piece.valid_position(grid):
                            current_piece.rotation -= 1
                    elif event.key == pygame.K_SPACE:
                        while current_piece.move(0, 1, grid):
                            pass

        screen.fill(BLACK)
        draw_grid(screen, grid)

        for x, y in current_piece.get_cells():
            pygame.draw.rect(
                screen,
                current_piece.color,
                (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
            )

        draw_score(screen, score, player_name, font)
        if paused:
            draw_pause(screen, font)

        pygame.display.update()

    # Save the final score while preserving all valid previous records.
    records = load_records()
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    records[timestamp] = {player_name: score}
    save_records(records)

    pygame.quit()
    show_leaderboard(load_records())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
