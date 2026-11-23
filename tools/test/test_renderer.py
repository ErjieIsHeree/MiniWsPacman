"""Open a window and draw the maze with Renderer."""
from typing import Any

from mlx import Mlx

from pacman.maze_loader import load_maze
from pacman.renderer import YELLOW, Renderer

TILE = 32
KEY_ESC = 65307

grid = load_maze(15, 15, 42)

pacgums: set[tuple[int, int]] = set()
for y in range(grid.height):
    for x in range(grid.width):
        if not grid.is_blocked(x, y):
            pacgums.add((x, y))

corners = {(0, 0), (grid.width - 1, 0),
           (0, grid.height - 1), (grid.width - 1, grid.height - 1)}

m = Mlx()
mlx_ptr = m.mlx_init()
win = m.mlx_new_window(mlx_ptr, grid.width * TILE, grid.height * TILE,
                       "Renderer test")
renderer = Renderer(m, mlx_ptr, win, TILE)
renderer.build_background(grid, pacgums - corners, corners)
pacman_img = renderer.make_rect(TILE - 8, TILE - 8, YELLOW)


def on_frame(param: Any) -> None:
    """Draw background, pacman and text."""
    renderer.draw_background()
    renderer.draw_sprite(pacman_img, 7, 7)
    renderer.draw_text(10, 20, "SCORE: 0")


def on_key(keycode: int, param: Any) -> None:
    """ESC quits."""
    if keycode == KEY_ESC:
        m.mlx_loop_exit(mlx_ptr)


def on_close(param: Any) -> None:
    """Close button quits."""
    m.mlx_loop_exit(mlx_ptr)


m.mlx_hook(win, 2, 1, on_key, None)
m.mlx_hook(win, 33, 0, on_close, None)
m.mlx_loop_hook(mlx_ptr, on_frame, None)
try:
    m.mlx_loop(mlx_ptr)
finally:
    renderer.destroy()
    m.mlx_destroy_window(mlx_ptr, win)
    m.mlx_release(mlx_ptr)