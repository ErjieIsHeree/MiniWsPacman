"""Main application: MLX window, event hooks and main loop."""
import time
from typing import Any

from mlx import Mlx
from pacman.maze_loader import load_maze
from pacman.renderer import YELLOW, Renderer

TILE = 32
FRAME_TIME = 1 / 60

KEY_ESC = 65307
EVENT_KEY_PRESS, MASK_KEY_PRESS = 2, 1
EVENT_CLOSE = 33


class App:
    """Owns the window, the renderer and the main loop"""
    def __init__(self) -> None:
        """Load the first maze and open the window"""
        self.grid = load_maze(15, 15, 42)  # TODO: read size and seed from config
        self.m = Mlx()
        self.mlx_ptr = self.m.mlx_init()
        if not self.mlx_ptr:
            raise RuntimeError("cannot connect to the display")

        width = self.grid.width * TILE
        height = self.grid.height * TILE
        self.win = self.m.mlx_new_window(self.mlx_ptr, width, height,
                                         "Pac-Man")
        if not self.win:
            self.m.mlx_release(self.mlx_ptr)
            raise RuntimeError("cannot open the window")
        self.renderer = Renderer(self.m, self.mlx_ptr, self.win, TILE)
        pacgums: set[tuple[int, int]] = set()
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if not self.grid.is_blocked(x, y):
                    pacgums.add((x, y))

        self.renderer.build_background(self.grid, pacgums, set())
        self.pacman_img = self.renderer.make_rect(TILE - 8, TILE - 8, YELLOW)
        self.last = time.monotonic()

    def on_key(self, keycode: int, parap: Any) -> None:
        """ESC quits."""
        if keycode == KEY_ESC:
            self.m.mlx_loop_exit(self.mlx_ptr)

    def on_close(self, param: Any) -> None:
        """windows close button quits"""
        self.m.mlx_loop_exit(self.mlx_ptr)

    def on_frame(self, param: Any) -> None:
        """Draw one frame, then wait so we run at about 60 fps."""
        now = time.monotonic()   # Current time in seconds (always increasing)
        dt = now - self.last   # Time elapsed since the previous frame
        self.last = now   # Remember this frame's time for the next frame

        self.renderer.draw_background()  # Draw the maze and pacgums; this also covers the previous frame
        self.renderer.draw_sprite(self.pacman_img, 7, 7)    # TODO: NEED TO CHANGE AFTER
        self.renderer.draw_text(10, 20, f"FPS: {1 / dt:.0f}" if dt else "")  # Show frames per second (skip if dt is 0 to avoid dividing by 0)

        spent = time.monotonic() - now    # Time spent on this frame so far
        if spent < FRAME_TIME:   # Frame finished early: sleep the rest to keep about 60 fps
            time.sleep(FRAME_TIME - spent)

    def run(self) -> None:
        """Register the hooks and run the main loop until the user quits."""
        self.m.mlx_hook(self.win, EVENT_KEY_PRESS, MASK_KEY_PRESS,
                        self.on_key, None)
        self.m.mlx_hook(self.win, EVENT_CLOSE, 0, self.on_close, None)
        self.m.mlx_loop_hook(self.mlx_ptr, self.on_frame, None)
        try:
            self.m.mlx_loop(self.mlx_ptr)
        finally:
            self.renderer.destroy()
            self.m.mlx_destroy_window(self.mlx_ptr, self.win)
            self.m.mlx_release(self.mlx_ptr)
