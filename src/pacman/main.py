from mazegenerator import MazeGenerator


g = MazeGenerator(size=(15, 15), seed=42)
g.generate()
print(g.maze)

# 0000 WSEN
