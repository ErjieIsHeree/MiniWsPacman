import time
from typing import Any

from mlx import Mlx


WIN_W, WIN_H = 640, 200  # the size of window
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

# Create a 32x32 image for the ghost
ghost_image = m.mlx_new_image(mlx_ptr, SIZE, SIZE)

# Get access to the image's pixel data
data, bpp, size_line, _ = m.mlx_get_data_addr(ghost_image)
m.mlx_sync(mlx_ptr, Mlx.SYNC_IMAGE_WRITABLE, ghost_image)

# Fill the image with red pixels
red = bytes([0x00, 0x00, 0xFF, 0xFF])
for y in range(SIZE):
    start = y * size_line
    data[start:start + SIZE * 4] = red * SIZE


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
    # Clear the window and draw the ghost at its new position
    m.mlx_clear_window(mlx_ptr, win)
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
m.mlx_destroy_window(mlx_ptr, win)
m.mlx_release(mlx_ptr)
print("bye")
