import time
from typing import Any

from mlx import Mlx
from mazegenerator import MazeGenerator


# 0000 WSEN
TILE = 32  # Size of each maze cell in pixels (32 × 32)
WALL = 3   # Thickness of maze walls in pixels
maze = MazeGenerator(size=(15, 15), perfect=False, seed=42).maze
MAZE_W = len(maze[0])  # width of maze
MAZE_H = len(maze)     # lenth of maze
WIN_W = MAZE_W * TILE  # Window width in pixels
WIN_H = MAZE_H * TILE  # Window height in pixels
SIZE = 32       # the size of ghost
SPEED = 60.0    # Movement speed  in pixels pr second

# key_codes
KEY_ESC = 65307
KEY_LEFT, KEY_UP, KEY_RIGHT, KEY_DOWN = 65361, 65362, 65363, 65364
KEY_A, KEY_W, KEY_D, KEY_S = 97, 119, 100, 115

# Store the ghost's position, direction and last update time
ghost: dict[str, Any] = {
    "x": 100.0,
    "y": 80.0,
    "dx": 0.0,
    "dy": 0.0,
    "last": time.monotonic(),
}

# Initialize MLX and create a window
m = Mlx()
mlx_ptr = m.mlx_init()
win = m.mlx_new_window(mlx_ptr, WIN_W, WIN_H, "Ghost_Walk")


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


RED = bytes([0x00, 0x00, 0xFF, 0xFF])
BLUE = bytes([0xFF, 0x00, 0x00, 0xFF])

ghost_image = make_rect(SIZE, SIZE, RED)

DARK = bytes([0x60, 0x10, 0x10, 0xFF])
BLACK = bytes([0x00, 0x00, 0x00, 0xFF])


def make_background() -> Any:
    """Draw the whole maze once into one big image."""
    img = m.mlx_new_image(mlx_ptr, WIN_W, WIN_H)
    data, _, size_line, _ = m.mlx_get_data_addr(img)
    m.mlx_sync(mlx_ptr, Mlx.SYNC_IMAGE_WRITABLE, img)
    fill_rect(data, size_line, 0, 0, WIN_W, WIN_H, BLACK)
    for y in range(MAZE_H):
        for x in range(MAZE_W):
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
    return img


background = make_background()


# Update the ghost's position and redraw it every frame
def on_frame(param: Any) -> None:
    # Calculate the time since the last frame
    now = time.monotonic()
    dt = now - param["last"]
    param["last"] = now
    # Move the ghost based on its direction and speed
    param["x"] += param["dx"] * dt * SPEED
    param["y"] += param["dy"] * SPEED * dt
    # Make the ghost appear on the opposite side
    # when it moves outside the window
    if param["x"] > WIN_W:
        param["x"] = -SIZE
    elif param["x"] < -SIZE:
        param["x"] = WIN_W
    if param["y"] > WIN_H:
        param["y"] = -SIZE
    elif param["y"] < -SIZE:
        param["y"] = WIN_H
    m.mlx_put_image_to_window(mlx_ptr, win, background, 0, 0)
    m.mlx_put_image_to_window(mlx_ptr, win, ghost_image, int(param["x"]),
                              int(param["y"]))


# Handle keyboard input
def on_key(keycode: int, param: Any) -> None:
    # Exit the program when ESC is pressed
    if keycode == KEY_ESC:
        m.mlx_loop_exit(mlx_ptr)
    # Change the ghost's movement direction
    elif keycode in (KEY_A, KEY_LEFT):
        param["dx"], param["dy"] = -1, 0
    elif keycode in (KEY_D, KEY_RIGHT):
        param["dx"], param["dy"] = 1, 0
    elif keycode in (KEY_W, KEY_UP):
        param["dx"], param["dy"] = 0, -1
    elif keycode in (KEY_S, KEY_DOWN):
        param["dx"], param["dy"] = 0, 1


# Exit the program when the window is closed
def on_close(param: Any) -> None:
    m.mlx_loop_exit(mlx_ptr)


# Register the keyboard event hook
m.mlx_hook(win, 2, 1, on_key, ghost)
# Register the window close event hook
m.mlx_hook(win, 33, 1, on_close, None)


# Register the function called during the main loop
m.mlx_loop_hook(mlx_ptr, on_frame, ghost)
# Start the main event loop
m.mlx_loop(mlx_ptr)


# Clean up resources after the loop exits
m.mlx_destroy_image(mlx_ptr, ghost_image)
m.mlx_destroy_image(mlx_ptr, background)
m.mlx_destroy_window(mlx_ptr, win)
m.mlx_release(mlx_ptr)
print("bye")
