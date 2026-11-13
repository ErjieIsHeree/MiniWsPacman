from mlx import Mlx


def rgb(r: int, g: int, b: int, a: int = 255):
    """This function works for turning 0-255 value on ARGB into its hex value
    """
    return (a << 24) | (r << 16) | (g << 8) | b


def get_offset(x: int, y: int, line: int, bpp: int) -> int:
    return y * line + x * (bpp // 8)


def color_bytes(color, fmt):
    return color.to_bytes(4, "little" if fmt == 0 else "big")


def put_pixel(data, line, bpp, fmt, w, h, x, y, color):
    if 0 <= x < w and 0 <= y < h:
        off = get_offset(x, y, line, bpp)
        data[off:off + 4] = color_bytes(color, fmt)


def game_test(
        WIN_W: int = 640,
        WIN_H: int = 480
        ) -> None:
    """Testing mlx"""
    m = Mlx()

    # Sync with graphic system
    mlx_ptr = m.mlx_init()

    if mlx_ptr is None:
        raise SystemExit("[ERROR]: Failure initializing MLX")

    # Create a window  and receive its pointer
    win_ptr = m.mlx_new_window(mlx_ptr, WIN_W, WIN_H, "Hello, window!")
    if win_ptr is None:
        raise SystemExit("[ERROR]: Failure creating the window")

    # Creates a image and get its memory
    img_w, img_h = 320, 240
    img = m.mlx_new_image(mlx_ptr, img_w, img_h)
    if img is None:
        raise SystemExit("[ERROR]: Failure creating the image")

    # Edit the image
    data, bpp, line, fmt = m.mlx_get_data_addr(img)
    put_pixel(data, line, bpp, fmt, img_w, img_h, 50, 50, rgb(255, 0, 0))

    # Showing image
    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img, 50, 50)

    m.mlx_loop(mlx_ptr)


if __name__ == "__main__":
    game_test()
