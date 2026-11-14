from mazegenerator import MazeGenerator
from eat_game import Game

maze = MazeGenerator(size=(15, 15), perfect=False, seed=42).maze
g = Game(maze)
print("start:", g.score, len(g.pacgums))

g.update(0.016)
print("after first frame:", g.score)

g.set_direction("RIGHT")
for _ in range(60):
    g.update(1 / 60)
print("after 1s right:", round(g.pacman_x, 2), g.score, len(g.pacgums))
