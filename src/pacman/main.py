from mazegenerator import MazeGenerator

g = MazeGenerator(size=(5, 5), seed=1)
g.generate()
for row in g.maze:
    print(" ".join(f"{c:04b}" for c in row))
