import time
from typing import Any

from mlx import Mlx
from mazegenerator import MazeGenerator
from eat_game import Game


TILE = 32  # Size of each maze cell in pixels (32 × 32)
WALL = 3   # Thickness of maze walls in pixels
SIZE = TILE - 8  # Size of Pacman

# key_codes
KEY_ESC = 65307
KEY_LEFT, KEY_UP, KEY_RIGHT, KEY_DOWN = 65361, 65362, 65363, 65364
KEY_A, KEY_W, KEY_D, KEY_S = 97, 119, 100, 115

# Color of the game
YELLOW = bytes([0x00, 0xFF, 0xFF, 0xFF])
WHITE = bytes([0xFF, 0xFF, 0xFF, 0xFF])
BLUE = bytes([0xFF, 0x00, 0x00, 0xFF])
DARK = bytes([0x60, 0x10, 0x10, 0xFF])
BLACK = bytes([0x00, 0x00, 0x00, 0xFF])


KEY_TO_DIR = {
    KEY_LEFT: "LEFT", KEY_A: "LEFT",
    KEY_RIGHT: "RIGHT", KEY_D: "RIGHT",
    KEY_UP: "UP", KEY_W: "UP",
    KEY_DOWN: "DOWN", KEY_S: "DOWN",
}


maze = MazeGenerator(size=(15, 15), perfect=False, seed=42).maze
game = Game(maze)

m = Mlx()
mlx_ptr = m.mlx_init()
win = m.mlx_new_window(mlx_ptr, game.width * TILE, game.height * TILE,
                       "Eat test")


def make_rect(width: int, height: int, color: bytes) -> Any:
    """Create an MLX image filled with one color."""
    img = m.mlx_new_image(mlx_ptr, width, height)  # Create an image with the given dimensions
    data, bpp, size_line, _ = m.mlx_get_data_addr(img)  # Get the pixel buffer, bits per pixel, and bytes per row
    m.mlx_sync(mlx_ptr, Mlx.SYNC_IMAGE_WRITABLE, img)    # Wait until the image is ready for writing
    for y in range(height):
        start = y * size_line  # Calculate the starting byte offset of the current row
        data[start:start + width * 4] = color * width  # Fill the row with the given color (4 bytes per pixel)
    return img


def fill_rect(data: Any, size_line: int, x: int, y: int,
              width: int, height: int, color: bytes) -> None:
    """Paint a rectangle into an image's pixel buffer"""
    for row in range(y, y + height):
        start = row * size_line + x * 4
        data[start:start + width * 4] = color * width


def make_background() -> Any:
    """Draw the whole maze once into one big image."""
    img = m.mlx_new_image(mlx_ptr, game.width * TILE, game.height * TILE)
    data, _, size_line, _ = m.mlx_get_data_addr(img)
    m.mlx_sync(mlx_ptr, Mlx.SYNC_IMAGE_WRITABLE, img)
    fill_rect(data, size_line, 0, 0,
              game.width * TILE, game.height * TILE, BLACK)
    for y in range(game.height):
        for x in range(game.width):
            cell = maze[y][x]
            px = x * TILE
            py = y * TILE
            if cell == 15:                      # "42"
                fill_rect(data, size_line, px, py, TILE, TILE, DARK)
                continue
            if cell & 1:                        # N
                fill_rect(data, size_line, px, py, TILE, WALL, BLUE)
            if cell & 4:                        # S
                fill_rect(data, size_line, px, py + TILE - WALL,
                          TILE, WALL, BLUE)
            if cell & 8:                        # W
                fill_rect(data, size_line, px, py, WALL, TILE, BLUE)
            if cell & 2:                        # E
                fill_rect(data, size_line, px + TILE - WALL, py,
                          WALL, TILE, BLUE)
    # the pattern of pacgums(eg. 3*32->left, 96+16->half cell to right, 112-2->menos the left size of pacgums)
    for (gx, gy) in game.pacgums:
        fill_rect(data, size_line,
                  gx * TILE + TILE // 2 - 2, gy * TILE + TILE // 2 - 2,
                  4, 4, WHITE)
    return img


background = make_background()
bg_data, _, bg_line, _ = m.mlx_get_data_addr(background)
pacman_image = make_rect(SIZE, SIZE, YELLOW)
drawn: set[tuple[int, int]] = set(game.pacgums) # the set of the pacgums in the background

clock = {"last": time.monotonic()}


def on_key(keycode: int, param: Any) -> None:
    """ESC quits; arrows / WASD tell the game which way to go."""
    if keycode == KEY_ESC:
        m.mlx_loop_exit(mlx_ptr)
    elif keycode in KEY_TO_DIR:
        game.set_direction(KEY_TO_DIR[keycode])


def on_close(param: Any) -> None:
    """Window close button quits."""
    m.mlx_loop_exit(mlx_ptr)


def on_frame(param: Any) -> None:
    """Update the game and render one frame.

    Calculate elapsed time since the previous frame and update the game.
    Convert Pac-Man's position from maze cells to pixel coordinates.
    Erase newly eaten pacgums from the background and update their
    drawing records. Draw the background, Pac-Man, score, and victory
    message if all pacgums have been eaten.

    Sleep for any remaining frame time to limit updates to approximately
    60 frames per second."""
    now = time.monotonic()
    dt = now - clock["last"]  # how many second past
    clock["last"] = now  # record now as the last time

    game.update(dt) # update game status

    # Convert the position from maze cells to pixels.
    # Add 4 pixels to center the 24×24 sprite inside a 32×32 cell.
    px = int(game.pacman_x * TILE) + 4
    py = int(game.pacman_y * TILE) + 4

    # Find pacgums still drawn on the background but already eaten.
    eaten = drawn - game.pacgums
    if eaten:
        # Wait until the background image is ready for writing.
        m.mlx_sync(mlx_ptr, Mlx.SYNC_IMAGE_WRITABLE, background)
        for (gx, gy) in eaten:
            # Cover each eaten pacgum with a 4×4 black rectangle.
            fill_rect(bg_data, bg_line,
                      gx * TILE + TILE // 2 - 2, gy * TILE + TILE // 2 - 2,
                      4, 4, BLACK)
        drawn.difference_update(eaten)

    m.mlx_put_image_to_window(mlx_ptr, win, background, 0, 0)
    m.mlx_put_image_to_window(mlx_ptr, win, pacman_image, px, py)
    m.mlx_string_put(mlx_ptr, win, 10, 20, 0xFFFFFF,
                     f"SCORE: {game.score}")
    if game.won:
        m.mlx_string_put(mlx_ptr, win, 200, 240, 0xFFFF00, "YOU WIN!")
    spent = time.monotonic() - now
    if spent < 1 / 60:
        time.sleep(1 / 60 - spent)


m.mlx_hook(win, 2, 1, on_key, None)
m.mlx_hook(win, 33, 0, on_close, None)
m.mlx_loop_hook(mlx_ptr, on_frame, None)

try:
    m.mlx_loop(mlx_ptr)
finally:
    m.mlx_destroy_image(mlx_ptr, background)
    m.mlx_destroy_image(mlx_ptr, pacman_image)
    m.mlx_destroy_window(mlx_ptr, win)
    m.mlx_release(mlx_ptr)
