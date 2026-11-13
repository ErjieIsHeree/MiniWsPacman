from mlx import Mlx


def game_test(WIN_W: int = 700, WIN_H: int = 700) -> None:
    m = Mlx()

    mlx_ptr = m.mlx_init()

    if not mlx_ptr:
        raise()

    win = m.mlx_new_window(mlx_ptr, WIN_W, WIN_H, "Ghost_Walk")


if __name__ == "__main__":
    game_test()
