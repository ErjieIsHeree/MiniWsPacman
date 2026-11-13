"""Type stubs for the MLX Python wrapper around the MiniLibX C library.

Pointers returned by the C library (mlx, window and image identifiers) are
exposed by ctypes as plain ``int`` addresses, or ``None`` when the C function
returned NULL.
"""

from typing import Any, Callable, Optional, Tuple, TypeAlias

# --- Opaque handles --------------------------------------------------------
# ctypes converts a `c_void_p` return value to `int` (or `None` for NULL).
MlxPtr: TypeAlias = int
WinPtr: TypeAlias = int
ImgPtr: TypeAlias = int

# --- Hook callback signatures ---------------------------------------------
# `param` is the arbitrary Python object given when registering the hook.
ExposeCallback: TypeAlias = Callable[[Any], None]
LoopCallback: TypeAlias = Callable[[Any], None]
KeyCallback: TypeAlias = Callable[[int, Any], None]  # (keycode, param)
MouseCallback: TypeAlias = Callable[[int, int, int, Any], None]
# (button, x, y, param)
MotionCallback: TypeAlias = Callable[[int, int, Any], None]  # (x, y, param)

# Callback accepted by the generic `mlx_hook`, depending on `x_event`:
#   2, 3 (KeyPress / KeyRelease)       -> KeyCallback
#   4, 5 (ButtonPress / ButtonRelease) -> MouseCallback
#   6    (MotionNotify)                -> MotionCallback
#   any other event                    -> ExposeCallback-like (param)
HookCallback: TypeAlias = Callable[..., None]


class Mlx:
    # Values for the `cmd` argument of `mlx_sync`
    SYNC_IMAGE_WRITABLE: int  # 1 -> `img_or_win_ptr` is an image
    SYNC_WIN_FLUSH: int  # 2 -> `img_or_win_ptr` is a window
    SYNC_WIN_COMPLETED: int  # 3 -> `img_or_win_ptr` is a window

    so_file: str
    mlx_func: Any  # ctypes.CDLL

    def __init__(self) -> None: ...

    # --- Initialisation -----------------------------------------------------
    def mlx_init(self) -> Optional[MlxPtr]:
        """Connect to the graphic system. Returns None on failure."""
        ...

    def mlx_release(self, mlx_ptr: MlxPtr) -> int:
        """Disconnect from the graphic system and free resources."""
        ...

    # --- Windows ------------------------------------------------------------
    def mlx_new_window(
        self, mlx_ptr: MlxPtr, width: int, height: int, title: str
    ) -> Optional[WinPtr]:
        """Create a window. Returns None on failure."""
        ...

    def mlx_clear_window(self, mlx_ptr: MlxPtr, win_ptr: WinPtr) -> int:
        """Clear the window (in black)."""
        ...

    def mlx_pixel_put(
        self, mlx_ptr: MlxPtr, win_ptr: WinPtr, x: int, y: int, color: int
    ) -> int:
        """Draw one pixel. `color` is a 32-bit integer (ARGB, mind endianness).
        Slow: prefer images."""
        ...

    def mlx_destroy_window(self, mlx_ptr: MlxPtr, win_ptr: WinPtr) -> int: ...

    # --- Images -------------------------------------------------------------
    def mlx_new_image(
        self, mlx_ptr: MlxPtr, width: int, height: int
    ) -> Optional[ImgPtr]:
        """Create an in-memory image. Returns None on failure."""
        ...

    def mlx_get_data_addr(
            self, img_ptr: ImgPtr) -> Tuple[memoryview, int, int, int]:
        """API break: returns a tuple.

        Returns ``(data, bits_per_pixel, size_line, format)`` where:
          - data: writable byte view (``memoryview`` of format 'B') over the
            image buffer, ``height * size_line`` bytes long
          - bits_per_pixel: depth of the image
          - size_line: bytes per image line
          - format: 0 -> B8G8R8A8, 1 -> A8R8G8B8
        """
        ...

    def mlx_put_image_to_window(
        self, mlx_ptr: MlxPtr, win_ptr: WinPtr, img_ptr: ImgPtr, x: int, y: int
    ) -> int: ...

    def mlx_destroy_image(self, mlx_ptr: MlxPtr, img_ptr: ImgPtr) -> int:
        """Raises KeyError if `img_ptr` was not created through this wrapper.
        """
        ...

    # --- Events & main loop -------------------------------------------------
    def mlx_loop(self, mlx_ptr: MlxPtr) -> int:
        """Run the event loop; returns only after `mlx_loop_exit`."""
        ...

    def mlx_loop_exit(self, mlx_ptr: MlxPtr) -> int: ...

    def mlx_mouse_hook(
        self, win_ptr: WinPtr, callback: Optional[MouseCallback], param: Any
    ) -> int:
        """Callback signature: ``(button, x, y, param) -> None``.
        Pass a falsy callback to remove the hook."""
        ...

    def mlx_key_hook(
        self, win_ptr: WinPtr, callback: Optional[KeyCallback], param: Any
    ) -> int:
        """Callback signature: ``(keycode, param) -> None`` (key released).
        Pass a falsy callback to remove the hook."""
        ...

    def mlx_expose_hook(
        self, win_ptr: WinPtr, callback: Optional[ExposeCallback], param: Any
    ) -> int:
        """Callback signature: ``(param) -> None``.
        Pass a falsy callback to remove the hook."""
        ...

    def mlx_loop_hook(
        self, mlx_ptr: MlxPtr, callback: Optional[LoopCallback], param: Any
    ) -> int:
        """Callback signature: ``(param) -> None``, called when no
        event occurs. Pass a falsy callback to remove the hook."""
        ...

    def mlx_hook(
        self,
        win_ptr: WinPtr,
        x_event: int,
        x_mask: int,
        callback: Optional[HookCallback],
        param: Any,
    ) -> int:
        """Generic hook using X11 event/mask values (see X.h).

        Callback signature depends on `x_event`:
          - 2, 3: ``(keycode, param)``
          - 4, 5: ``(button, x, y, param)``
          - 6:    ``(x, y, param)``
          - other: ``(param)``
        Pass a falsy callback to remove the hook.
        """
        ...

    # --- Misc ---------------------------------------------------------------
    def mlx_string_put(
        self,
        mlx_ptr: MlxPtr,
        win_ptr: WinPtr,
        x: int,
        y: int,
        color: int,
        string: str,
    ) -> int: ...

    def mlx_xpm_file_to_image(
        self, mlx_ptr: MlxPtr, filename: str
    ) -> Tuple[Optional[ImgPtr], int, int]:
        """API break: returns ``(img_ptr, width, height)``. `img_ptr`
        is None on failure."""
        ...

    def mlx_png_file_to_image(
        self, mlx_ptr: MlxPtr, filename: str
    ) -> Tuple[Optional[ImgPtr], int, int]:
        """API break: returns ``(img_ptr, width, height)``. `img_ptr`
        is None on failure."""
        ...

    def mlx_mouse_hide(self, mlx_ptr: MlxPtr) -> int: ...
    def mlx_mouse_show(self, mlx_ptr: MlxPtr) -> int: ...
    def mlx_mouse_move(self, mlx_ptr: MlxPtr, x: int, y: int) -> int: ...

    def mlx_mouse_get_pos(self, mlx_ptr: MlxPtr) -> Tuple[int, int, int]:
        """API break: returns ``(ret, x, y)``."""
        ...

    def mlx_do_key_autorepeatoff(self, mlx_ptr: MlxPtr) -> int: ...

    def mlx_do_key_autorepeaton(self, mlx_ptr: MlxPtr) -> int: ...

    def mlx_get_screen_size(self, mlx_ptr: MlxPtr) -> Tuple[int, int, int]:
        """API break: returns ``(ret, width, height)``."""
        ...

    # --- Sync ---------------------------------------------------------------
    def mlx_do_sync(self, mlx_ptr: MlxPtr) -> int:
        """Flush pending commands to the graphic subsystem."""
        ...

    def mlx_sync(
        self, mlx_ptr: MlxPtr, cmd: int, img_or_win_ptr: int
    ) -> int:
        """`cmd` is one of SYNC_IMAGE_WRITABLE (param = image),
        SYNC_WIN_FLUSH or SYNC_WIN_COMPLETED (param = window)."""
        ...
