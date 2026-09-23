import logging
import math
from typing import List, Optional, Tuple

logger = logging.getLogger("PTPM-VKI")

FIELD_SIZE = 100   # поле отрисовки 100x100 px
MARGIN = 5         # отступ от краёв поля




def _parse_side(raw: str, name: str) -> Optional[float]:
    """Возвращает положительное конечное float или None при ошибке."""
    try:
        value = float(raw.strip())
    except (ValueError, AttributeError):
        logger.warning(f"Сторона {name}: нечисловое значение '{raw}'")
        return None
    if value <= 0 or not math.isfinite(value):
        logger.warning(f"Сторона {name}: не положительное конечное число ({value})")
        return None
    return value


def _classify(a: float, b: float, c: float) -> str:
    """Определяет вид треугольника по трём сторонам."""
    if a + b <= c or a + c <= b or b + c <= a:
        return "не треугольник"
    if a == b == c:
        return "равносторонний"
    if a == b or b == c or a == c:
        return "равнобедренный"
    return "разносторонний"


# ---------- расчёт координат ----------

def _build_coords(a: float, b: float, c: float) -> List[Tuple[int, int]]:
    """
    Считает координаты 3 вершин и вписывает треугольник в поле 100x100.
    Самая длинная сторона кладётся горизонтально как основание.
    """
    sides = sorted([a, b, c])   # [малая, средняя, большая]
    base = sides[2]             # основание (горизонтально)
    r_left = sides[1]           # радиус из P1
    r_right = sides[0]          # радиус из P2

    # Пересечение двух окружностей радиуса r_left (из P1) и r_right (из P2)
    x3 = (base ** 2 + r_left ** 2 - r_right ** 2) / (2 * base)
    y3 = math.sqrt(max(r_left ** 2 - x3 ** 2, 0.0))

    raw = [(0.0, 0.0), (base, 0.0), (x3, y3)]

    xs = [p[0] for p in raw]
    ys = [p[1] for p in raw]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)

    inner = FIELD_SIZE - 2 * MARGIN
    scale = inner / max(width, height) if max(width, height) > 0 else 1.0

    # Масштаб + сдвиг в положительную зону
    scaled = [((x - min(xs)) * scale, (y - min(ys)) * scale) for x, y in raw]

    sw = max(p[0] for p in scaled)
    sh = max(p[1] for p in scaled)
    offset_x = MARGIN + (inner - sw) / 2
    offset_y = MARGIN + (inner - sh) / 2

    return [
        (int(round(x + offset_x)), int(round(y + offset_y)))
        for x, y in scaled
    ]


# ---------- основной метод ----------

def process_triangle(raw_a: str, raw_b: str, raw_c: str):
    """
    Возвращает (вид: str, координаты: List[(int,int)]).

    Вид:
        'равносторонний' | 'равнобедренный' | 'разносторонний'
        | 'не треугольник' | '' (пустая строка для нечисловых данных)

    Координаты:
        [(-1, -1)] * 3 — при числовых, но некорректных данных (не треугольник)
        [(-2, -2)] * 3 — при невалидных (нечисловых) данных
    """
    logger.info(f"Запрос: A='{raw_a}', B='{raw_b}', C='{raw_c}'")

    try:
        a = _parse_side(raw_a, "A")
        b = _parse_side(raw_b, "B")
        c = _parse_side(raw_c, "C")

        if a is None or b is None or c is None:
            logger.warning(
                "Невалидные данные — координаты (-2, -2), вид = ''"
            )
            return "", [(-2, -2)] * 3

        kind = _classify(a, b, c)

        if kind == "не треугольник":
            logger.warning(
                f"Треугольник не существует: A={a}, B={b}, C={c}"
            )
            return kind, [(-1, -1)] * 3

        coords = _build_coords(a, b, c)
        logger.info(f"Успех: вид='{kind}', координаты={coords}")
        return kind, coords

    except Exception:
        logger.exception("Непредвиденная ошибка при обработке треугольника")
        return "", [(-2, -2)] * 3