"""All MLX drawing for the game"""
from typing import Any

from mlx import Mlx

from pacman.maze_loader import (WALL_E, WALL_N, WALL_S, WALL_W,
                                Grid)

# the color of the maze and the wall thickness in pixels
BLACK = bytes([0x00, 0x00, 0x00, 0xFF])
BLUE = bytes([0xFF, 0x00, 0x00, 0xFF])
DARK = bytes([0x60, 0x10, 0x10, 0xFF])
WHITE = bytes([0xFF, 0xFF, 0xFF, 0xFF])
YELLOW = bytes([0x00, 0xFF, 0xFF, 0xFF])
WALL = 3


def fill_rect(data: Any, size_line: int, x: int, y: int,
              width: int, height: int, color: bytes) -> None:
    """Paint a rectangle into an image's pixel buffer"""
    for row in range(y, y + height):
        start = row * size_line + x * 4
        data[start:start + width * 4] = color * width


class Renderer:
    """Owns every MLX image and draws them on the window."""

    def __init__(self, m: Mlx, mlx_ptr: Any, win: Any, tile: int) -> None:
        """Keep the MLX handles and the cell size in pixels."""
        self.m = m
        self.mlx_ptr = mlx_ptr
        self.win = win
        self.tile = tile
        self.images: list[Any] = []
        self.background: Any = None
        self.bg_data: Any = None
        self.bg_line = 0

    def make_rect(self, width: int, height: int, color: bytes) -> Any:
        """Create an MLX image filled with one color."""
        img = self.m.mlx_new_image(self.mlx_ptr, width, height)
        data, _, size_line, _ = self.m.mlx_get_data_addr(img)
        self.m.mlx_sync(self.mlx_ptr, Mlx.SYNC_IMAGE_WRITABLE, img)
        fill_rect(data, size_line, 0, 0, width, height, color)
        self.images.append(img)
        return img

    def build_background(self, grid: Grid,
                         pacgums: set[tuple[int, int]],
                         super_pacgums: set[tuple[int, int]]) -> None:
        """Draw the maze, pacgums and super-pacgums into one image."""
        t = self.tile
        width, height = grid.width * t, grid.height * t

        if self.background is not None:
            self.m.mlx_destroy_image(self.mlx_ptr, self.background)
        img = self.m.mlx_new_image(self.mlx_ptr, width, height)
        data, _, size_line, _ = self.m.mlx_get_data_addr(img)
        self.m.mlx_sync(self.mlx_ptr, Mlx.SYNC_IMAGE_WRITABLE, img)
        fill_rect(data, size_line, 0, 0, width, height, BLACK)
        for y in range(grid.height):
            for x in range(grid.width):
                px, py = x * t, y * t
                if grid.is_blocked(x, y):
                    fill_rect(data, size_line, px, py, t, t, DARK)
                    continue
                if grid.has_wall(x, y, WALL_N):
                    fill_rect(data, size_line, px, py, t, WALL, BLUE)
                if grid.has_wall(x, y, WALL_S):
                    fill_rect(data, size_line, px, py + t - WALL,
                              t, WALL, BLUE)
                if grid.has_wall(x, y, WALL_W):
                    fill_rect(data, size_line, px, py, WALL, t, BLUE)
                if grid.has_wall(x, y, WALL_E):
                    fill_rect(data, size_line, px + t - WALL, py,
                              WALL, t, BLUE)
        for (gx, gy) in pacgums:
            self._paint_dot(data, size_line, gx, gy, 4, WHITE)
        for (gx, gy) in super_pacgums:
            self._paint_dot(data, size_line, gx, gy, 16, WHITE)

        self.background = img
        self.bg_data = data
        self.bg_line = size_line

    def _paint_dot(self, data: Any, size_line: int, gx: int, gy: int,
                   size: int, color: bytes) -> None:
        """Paint a size x size square centered in cell (gx, gy)."""
        x = gx * self.tile + self.tile // 2 - size // 2
        y = gy * self.tile + self.tile // 2 - size // 2
        fill_rect(data, size_line, x, y, size, size, color)

    def erase_dot(self, gx: int, gy: int) -> None:
        """Erase the pacgum or super-pacgum drawn in cell (gx, gy)."""
        self.m.mlx_sync(self.mlx_ptr, Mlx.SYNC_IMAGE_WRITABLE,
                        self.background)
        self._paint_dot(self.bg_data, self.bg_line, gx, gy, 16, BLACK)

    def destroy(self) -> None:
        """Free every image. Call before destroying the window."""
        for img in self.images:
            self.m.mlx_destroy_image(self.mlx_ptr, img)
        self.images.clear()
        if self.background is not None:
            self.m.mlx_destroy_image(self.mlx_ptr, self.background)
            self.background = None


