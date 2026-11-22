"""Adapter around the assigned A-Maze-ing package.""" 
from mazegenerator import MazeGenerator


WALL_N, WALL_E, WALL_S, WALL_W = 1, 2, 4, 8
BLOCKED = 15


class MazeLoadError(Exception):
    """Raised when the maze generator fails."""


class Grid:
    "The maze as our own class: cells[y][x] is a 4-bit wall mask."
    def __init__(self, cells: list[list[int]]) -> None:
        """Store the cells and the size of the maze.""" 
        self.cells = cells
        self.width = len(cells[0])
        self.height = len(cells)

    def is_blocked(self, x: int, y: int):
        """Return True if (x, y) is a cell of the '42' pattern."""
        return self.cells[y][x] == BLOCKED

    def has_wall(self, x: int, y: int, wall: int) -> bool:
        """Return True if cell (x, y) has the given wall (WALL_N...)."""
        return self.cells[y][x] & wall != 0

def load_maze(width: int, height: int, seed: int) -> Grid:
    """Generate a Pac-Man compatible maze. seed=0 means random."""
    try:
        gen = MazeGenerator(size=(width, height), perfect=False, seed=seed)
        cells = gen.maze
    except Exception as e:
        raise MazeLoadError(f"maze generator failed: {e}") from e
    return Grid(cells)
