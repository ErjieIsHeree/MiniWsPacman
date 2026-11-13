# Tutorial de MLX (MiniLibX) con Python: de 0 a 100

Guía basada en los man files de MiniLibX y en el wrapper de Python que me pasaste.

## 1. Qué es MLX y cómo se piensa

MLX es una librería muy simple para abrir ventanas, dibujar y recibir eventos de teclado y ratón, sin saber nada de X11, Wayland o Vulkan. Todo gira en torno a cuatro ideas:

1. **Conexión** (`mlx_ptr`): lo primero que creas. Es tu enlace con el sistema gráfico. Casi todas las funciones la piden.
2. **Ventana** (`win_ptr`): un rectángulo en pantalla donde se muestra algo.
3. **Imagen** (`img_ptr`): un bloque de memoria con píxeles que dibujas tú y luego "pegas" en una ventana.
4. **Eventos y bucle**: registras funciones (hooks) y llamas a `mlx_loop`, que se queda esperando eventos y las invoca.

El flujo de cualquier programa MLX es siempre el mismo:

```a
init -> crear ventana -> (crear imagen) -> registrar hooks -> mlx_loop -> limpiar
```

Una idea clave: `mlx_ptr`, `win_ptr` e `img_ptr` son **identificadores opacos**. En Python son simplemente enteros (direcciones de memoria) que no tienes que interpretar, solo pasar de vuelta a las funciones. Si algo falla, la función devuelve `None` (el `NULL` de C).

## 2. Preparación

El wrapper carga `libmlx.so` desde su misma carpeta, así que necesitas:

```a
proyecto/
  mlx.py        <- el wrapper (clase Mlx)
  mlx.pyi       <- los typings
  libmlx.so     <- la librería compilada
  main.py       <- tu programa
```

Y en tu programa:

```python
from mlx import Mlx

m = Mlx()
```

Importante: todas las funciones son **métodos** de ese objeto (`m.mlx_init()`, `m.mlx_new_window(...)`), no funciones sueltas como en C.

## 3. Tu primera ventana

```python
from mlx import Mlx

m = Mlx()
mlx = m.mlx_init()
if mlx is None:
    raise SystemExit('No se pudo iniciar MLX')

win = m.mlx_new_window(mlx, 640, 480, 'Mi primera ventana')
if win is None:
    raise SystemExit('No se pudo crear la ventana')

m.mlx_loop(mlx)   # no vuelve hasta que se llame a mlx_loop_exit
```

Si lo ejecutas, aparece una ventana y el programa se queda esperando. Dos avisos que vienen del propio wrapper:

- Mientras `mlx_loop` corre, **Ctrl+C no funciona** desde Python. Para matar el programa usa **`Ctrl+\`**.
- Aún no hemos programado ninguna forma de cerrarla limpiamente; eso llega en la sección 7.

Puedes crear tantas ventanas como quieras, cada una con su `win_ptr`.

## 4. Coordenadas y colores

**Coordenadas:** el origen `(0, 0)` es la esquina **superior izquierda**. La x crece hacia la derecha y la y crece hacia **abajo**.

**Colores:** un color es un entero sin signo de 32 bits en formato **ARGB**:

```a
0xAARRGGBB
  AA = transparencia (0 transparente, 255 opaco)
  RR = rojo, GG = verde, BB = azul   (cada uno de 0 a 255)
```

Ejemplos: rojo opaco `0xFFFF0000`, verde `0xFF00FF00`, azul `0xFF0000FF`, blanco `0xFFFFFFFF`.

Una función cómoda para componer colores:

```python
def rgb(r, g, b, a=255):
    return (a << 24) | (r << 16) | (g << 8) | b
```

El man avisa de que al empaquetar los bytes hay que tener en cuenta el **endianness** (orden de los bytes en memoria). Lo veremos con las imágenes, que es donde importa.

## 5. Dibujar directamente: pixel_put y string_put

Lo más sencillo es dibujar sobre la ventana:

```python
m.mlx_pixel_put(mlx, win, 100, 100, 0xFFFF0000)            # un píxel rojo
m.mlx_string_put(mlx, win, 50, 50, 0xFFFFFFFF, 'Hola MLX') # texto
```

Funciona, pero el man avisa: **`mlx_pixel_put` es lento**, porque cada llamada va al sistema gráfico y descarta lo que cae fuera de la ventana. Para dibujar cosas de verdad, usa imágenes. Además `mlx_clear_window` borra la ventana (la pone en negro).

## 6. Imágenes: la forma correcta de dibujar

Una imagen es un array de bytes en memoria. Dibujas en él a tu ritmo (rápido) y después lo envías a la ventana de una vez.

### 6.1 Crear la imagen y obtener su memoria

```python
img = m.mlx_new_image(mlx, 640, 480)
data, bpp, line, fmt = m.mlx_get_data_addr(img)
```

`mlx_get_data_addr` en C devuelve un puntero y rellena tres variables. En el wrapper Python (marcado como "API break") devuelve una **tupla**:

- `data`: un `memoryview` **escribible** sobre la memoria de la imagen.
- `bpp` (bits per pixel): bits por píxel, normalmente 32.
- `line` (size_line): **bytes por línea**. Ojo: puede ser mayor que `ancho * 4` por alineación, así que úsalo siempre en vez de calcularlo tú.
- `fmt`: cómo se ordenan los canales. `0` = B8G8R8A8, `1` = A8R8G8B8.

### 6.2 Dónde está cada píxel

El píxel `(x, y)` empieza en el byte:

```a
offset = y * line + x * (bpp // 8)
```

Y ocupa `bpp // 8` bytes (4 normalmente).

### 6.3 Escribir un píxel respetando el formato

Aquí entra el endianness. Un color `0xAARRGGBB` guardado en memoria queda así:

- `fmt == 0` (B8G8R8A8): bytes en orden B, G, R, A, que equivale a escribir el entero en **little endian**.
- `fmt == 1` (A8R8G8B8): bytes en orden A, R, G, B, que equivale a **big endian**.

```python
def color_bytes(color, fmt):
    return color.to_bytes(4, 'little' if fmt == 0 else 'big')

def put_pixel(data, line, bpp, fmt, w, h, x, y, color):
    if 0 <= x < w and 0 <= y < h:           # evitar salirse de la imagen
        off = y * line + x * (bpp // 8)
        data[off:off + 4] = color_bytes(color, fmt)
```

Comprobar los límites es importante: escribir fuera de la imagen es escribir fuera de tu memoria.

### 6.4 Mostrar la imagen

```python
m.mlx_put_image_to_window(mlx, win, img, 0, 0)  # (x, y) = dónde se coloca en la ventana
```

Puedes llamarlo cuando quieras, las veces que quieras; cada llamada vuelca el contenido actual de la imagen.

### 6.5 Dibujar rápido en Python

Python es lento haciendo un bucle píxel a píxel. Aprovecha que `data` admite **slices**:

```python
# Rellenar toda la imagen de un color
pixel = color_bytes(0xFF202020, fmt)
for y in range(h):
    off = y * line
    data[off:off + w * 4] = pixel * w   # una línea entera de golpe

# Rectángulo
def rect(x0, y0, rw, rh, color):
    row = color_bytes(color, fmt) * rw
    for y in range(y0, y0 + rh):
        off = y * line + x0 * 4
        data[off:off + rw * 4] = row
```

(Asume que el rectángulo cabe en la imagen; recórtalo antes si no.)

### 6.6 Cargar imágenes de fichero

```python
img, w, h = m.mlx_png_file_to_image(mlx, 'sprite.png')
img, w, h = m.mlx_xpm_file_to_image(mlx, 'sprite.xpm')
if img is None:
    ...  # falló la carga
```

Devuelven una **tupla** `(img, ancho, alto)`. MLX tiene su propio lector, así que puede que no abra todos los PNG/XPM, pero sí maneja transparencia. La imagen resultante se usa igual que una creada con `mlx_new_image`.

### 6.7 Liberar

```python
m.mlx_destroy_image(mlx, img)
```

El wrapper lleva un registro interno de las alturas de las imágenes (lo necesita para calcular el tamaño del `memoryview`), por eso destruir una imagen que no creaste a través del wrapper lanza `KeyError`.

## 7. Eventos y el bucle principal

`mlx_loop` es un bucle infinito que espera eventos y llama a tus funciones. Tú solo **registras** qué función atiende cada evento antes de llamar al bucle.

### 7.1 Los hooks básicos

| Hook                             | Se dispara cuando...         | Firma de tu callback     |
| -------------------------------- | ---------------------------- | ------------------------ |
| `mlx_key_hook(win, f, param)`    | se **suelta** una tecla      | `f(keycode, param)`      |
| `mlx_mouse_hook(win, f, param)`  | se pulsa un botón del ratón  | `f(button, x, y, param)` |
| `mlx_expose_hook(win, f, param)` | hay que redibujar la ventana | `f(param)`               |
| `mlx_loop_hook(mlx, f, param)`   | **no ocurre ningún evento**  | `f(param)`               |

Detalles importantes:

- `param` es **cualquier objeto Python** que quieras que te devuelvan. MLX nunca lo toca. Es tu forma de compartir estado (mlx, win, imagen, posición del jugador...) con los callbacks.
- Cada ventana puede tener sus propias funciones para el mismo evento.
- `loop_hook` no está atado a una ventana (recibe `mlx_ptr`). Es el motor de las animaciones.
- El evento *expose* solo ocurre en X11; en Wayland o macOS nunca se dispara.
- Para quitar un hook, pásale `None` como callback.
- Los callbacks no devuelven nada (en el wrapper están definidos como `None`).

### 7.2 Salir limpiamente

```python
def on_key(keycode, s):
    print('tecla:', keycode)        # así descubres el código de cada tecla
    if keycode == 65307:            # ESC en Linux/X11; compruébalo imprimiéndolo
        s.m.mlx_loop_exit(s.mlx)    # hace que mlx_loop retorne
```

`mlx_loop_exit` provoca que `mlx_loop` termine y devuelva el control a tu código, donde puedes limpiar.

### 7.3 Hook genérico: mlx_hook

Para cualquier otro evento (tecla pulsada, movimiento del ratón, cerrar ventana) está `mlx_hook(win, evento, mascara, callback, param)`. Los números vienen del histórico fichero `X.h` de X11:

| Evento         | Nº  | Callback                 |
| -------------- | --- | ------------------------ |
| KeyPress       | 2   | `f(keycode, param)`      |
| KeyRelease     | 3   | `f(keycode, param)`      |
| ButtonPress    | 4   | `f(button, x, y, param)` |
| ButtonRelease  | 5   | `f(button, x, y, param)` |
| MotionNotify   | 6   | `f(x, y, param)`         |
| cualquier otro | n   | `f(param)`               |

La máscara también viene de `X.h` (por ejemplo `1` para KeyPress, `2` para KeyRelease) y en algunas configuraciones se ignora. Para el botón de cerrar la ventana se suele usar el evento `17` (DestroyNotify) con máscara `0`; esto depende del backend, así que pruébalo en el tuyo.

## 8. Animación: el patrón loop_hook + imagen

La receta clásica de un juego o animación:

1. Mantén el **estado** (posición, etc.) en un objeto.
2. En `loop_hook`: borra la imagen, dibuja el estado actual, vuelca la imagen a la ventana.
3. En los hooks de teclado: **solo modifica el estado**, sin dibujar.

Esa separación (estado / dibujo) evita parpadeos y te mantiene el código ordenado.

## 9. Programa completo: un cuadrado que se mueve

```python
from mlx import Mlx

W, H = 640, 480
SIZE = 50
SPEED = 5

class State:
    pass

def color_bytes(color, fmt):
    return color.to_bytes(4, 'little' if fmt == 0 else 'big')

def draw(s):
    # Fondo
    bg = color_bytes(0xFF202020, s.fmt) * W
    for y in range(H):
        off = y * s.line
        s.data[off:off + W * 4] = bg
    # Cuadrado
    row = color_bytes(0xFFFF4040, s.fmt) * SIZE
    for y in range(s.y, s.y + SIZE):
        off = y * s.line + s.x * 4
        s.data[off:off + SIZE * 4] = row

def on_loop(s):
    draw(s)
    s.m.mlx_put_image_to_window(s.mlx, s.win, s.img, 0, 0)

def on_key_press(keycode, s):
    print('keycode', keycode)
    if keycode == 65307:                       # ESC (X11)
        s.m.mlx_loop_exit(s.mlx)
    elif keycode in (65361, 97):               # flecha izq. / a
        s.x = max(0, s.x - SPEED)
    elif keycode in (65363, 100):              # flecha der. / d
        s.x = min(W - SIZE, s.x + SPEED)
    elif keycode in (65362, 119):              # flecha arriba / w
        s.y = max(0, s.y - SPEED)
    elif keycode in (65364, 115):              # flecha abajo / s
        s.y = min(H - SIZE, s.y + SPEED)

def on_close(s):
    s.m.mlx_loop_exit(s.mlx)

def main():
    s = State()
    s.m = Mlx()
    s.mlx = s.m.mlx_init()
    s.win = s.m.mlx_new_window(s.mlx, W, H, 'Cuadrado')
    s.img = s.m.mlx_new_image(s.mlx, W, H)
    s.data, s.bpp, s.line, s.fmt = s.m.mlx_get_data_addr(s.img)
    s.x, s.y = 100, 100

    s.m.mlx_hook(s.win, 2, 1, on_key_press, s)   # KeyPress
    s.m.mlx_hook(s.win, 17, 0, on_close, s)      # cerrar ventana
    s.m.mlx_loop_hook(s.mlx, on_loop, s)

    s.m.mlx_loop(s.mlx)

    # Limpieza (se llega aquí tras mlx_loop_exit)
    s.m.mlx_destroy_image(s.mlx, s.img)
    s.m.mlx_destroy_window(s.mlx, s.win)
    s.m.mlx_release(s.mlx)

main()
```

Los códigos de tecla de arriba son los de Linux/X11; si no responden, mira lo que imprime el `print('keycode', ...)` y ajústalos.

## 10. Funciones extra

### Ratón

```python
m.mlx_mouse_hide(mlx)               # ocultar el cursor
m.mlx_mouse_show(mlx)               # mostrarlo
m.mlx_mouse_move(mlx, 100, 100)     # colocarlo
ret, x, y = m.mlx_mouse_get_pos(mlx)  # leer su posición (devuelve tupla)
```

### Teclado

```python
m.mlx_do_key_autorepeatoff(mlx)  # sin repetición al mantener pulsada una tecla
m.mlx_do_key_autorepeaton(mlx)   # (por defecto está activada)
```

### Pantalla

```python
ret, w, h = m.mlx_get_screen_size(mlx)  # funciona incluso antes de crear ventanas
```

### Sincronización

- `mlx_do_sync(mlx)`: vacía los comandos pendientes hacia el sistema gráfico (sin garantía de que ya se hayan procesado).
- `mlx_sync(mlx, cmd, ptr)`: control fino con tres comandos: `Mlx.SYNC_IMAGE_WRITABLE` (`ptr` = imagen), `Mlx.SYNC_WIN_FLUSH` y `Mlx.SYNC_WIN_COMPLETED` (`ptr` = ventana).

## 11. Orden de limpieza

Al terminar, libera en orden inverso a la creación:

```a
mlx_destroy_image  ->  mlx_destroy_window  ->  mlx_release
```

## 12. Errores típicos y consejos

- **`None` inesperado:** `mlx_init`, `mlx_new_window`, `mlx_new_image` y las funciones de carga devuelven `None` si fallan. Compruébalo siempre.
- **Dibujar en el hook de teclado:** hazlo en `loop_hook`; en los hooks solo cambia estado.
- **Imagen torcida o desplazada:** estás usando `ancho * 4` en vez de `line`.
- **Colores raros (rojo y azul intercambiados):** ignoraste `fmt` al escribir los bytes.
- **Lentitud:** evita `mlx_pixel_put` y bucles píxel a píxel; escribe líneas enteras con slices.
- **Un hook no responde:** recuerda que `key_hook` solo salta al **soltar**; para pulsar usa `mlx_hook` con el evento 2.
- **El programa no se puede parar:** `Ctrl+\`, no Ctrl+C.
- **Estado compartido:** usa `param` (un objeto o una clase) en vez de variables globales.

## 13. Mapa mental final

```a
Mlx()  ->  mlx_init  ->  mlx_new_window ----------------+
                     \-> mlx_new_image -> get_data_addr  |
                              (dibujas en data)          |
                              put_image_to_window -------+
   hooks: key / mouse / expose / loop / mlx_hook
   mlx_loop  ->  (eventos llaman a tus callbacks)
   mlx_loop_exit -> destroy_image -> destroy_window -> release
```

Con esto tienes todo lo necesario para hacer desde una simple ventana hasta un juego 2D o un renderizador. El siguiente paso natural es practicar: un fractal, un Pong o un pequeño raycaster usando exactamente este patrón.
