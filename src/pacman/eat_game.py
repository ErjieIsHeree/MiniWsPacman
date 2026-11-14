SPEED = 4.0
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}


class Game:
    """Pac-Man position, pacgums and score."""

    def __init__(self, maze: list[list[int]]) -> None:
        """Start with pacman standing still and a pacgum in every cell."""
        self.maze = maze
        self.width = len(maze[0])
        self.height = len(maze)
        self.pacman_x = 3.0  # Initial position of pacman in maze cells
        self.pacman_y = 2.0
        self.dx = 0   # Horizontal direction: -1 left, 0 still, 1 right.
        self.dy = 0   # Vertical direction: -1 up, 0 still, 1 down.
        self.score = 0
        # Store pacgum positions as unique (x, y) coordinates.
        self.pacgums: set[tuple[int, int]] = set()  
        for y in range(self.height):  # Loop through each row.
            for x in range(self.width):  # Loop through each column.
                if maze[y][x] != 15:    # Skip cells with all four walls.
                    self.pacgums.add((x,y))  # Place a pacgum in this cell.


    def set_direction(self, name: str) -> None:
        """Change pacman's direction ("UP", "DOWN", "LEFT", "RIGHT")."""
        self.dx, self.dy = DIRECTIONS[name]


    def update(self, dt: float) -> None:
        """Move pacman, wrap around the edges, eat the pacgum under it."""
        self.pacman_x += self.dx * SPEED * dt
        self.pacman_y += self.dy * SPEED * dt

        if self.pacman_x > self.width:
            self.pacman_x = -1.0
        elif self.pacman_x < -1:
            self.pacman_x = float(self.width)
        if self.pacman_y > self.height:
            self.pacman_y = -1.0
        elif self.pacman_y < -1:
            self.pacman_y = float(self.height)

        # Convert the position to the nearest cell for non-negative coordinates.
        cell = (int(self.pacman_x + 0.5), int(self.pacman_y + 0.5))
        if cell in self.pacgums:
            self.pacgums.remove(cell)
            self.score += 10


    @property
    def won(self) -> bool:
        """True when every pacgum has been eaten."""
        return not self.pacgums