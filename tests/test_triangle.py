import os
import sys
import unittest
from src.triangle import process_triangle, _parse_side, _classify, _build_coords

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))




class TestParseSide(unittest.TestCase):
    """Парсинг и валидация одной стороны."""

    def test_valid_integer_string_returns_float(self):
        self.assertEqual(_parse_side("5", "A"), 5.0)

    def test_valid_float_string_with_dot_returns_float(self):
        self.assertAlmostEqual(_parse_side("3.5", "A"), 3.5)

    def test_string_with_spaces_is_trimmed(self):
        self.assertEqual(_parse_side("  4  ", "A"), 4.0)

    def test_non_numeric_string_returns_none(self):
        self.assertIsNone(_parse_side("abc", "A"))

    def test_empty_string_returns_none(self):
        self.assertIsNone(_parse_side("", "A"))

    def test_negative_number_returns_none(self):
        self.assertIsNone(_parse_side("-3", "A"))

    def test_zero_returns_none(self):
        self.assertIsNone(_parse_side("0", "A"))

    def test_infinity_returns_none(self):
        self.assertIsNone(_parse_side("inf", "A"))

    def test_nan_returns_none(self):
        self.assertIsNone(_parse_side("nan", "A"))


class TestClassify(unittest.TestCase):
    """Определение вида треугольника."""

    def test_equilateral_all_sides_equal(self):
        self.assertEqual(_classify(3, 3, 3), "равносторонний")

    def test_isosceles_two_equal_sides(self):
        self.assertEqual(_classify(3, 3, 4), "равнобедренный")

    def test_isosceles_another_combination(self):
        self.assertEqual(_classify(4, 5, 4), "равнобедренный")

    def test_scalene_all_sides_different(self):
        self.assertEqual(_classify(3, 4, 5), "разносторонний")

    def test_not_triangle_when_sum_less(self):
        self.assertEqual(_classify(1, 2, 10), "не треугольник")

    def test_not_triangle_when_sum_equal_degenerate(self):
        self.assertEqual(_classify(1, 2, 3), "не треугольник")

    def test_not_triangle_float_sides(self):
        self.assertEqual(_classify(0.5, 0.5, 1.5), "не треугольник")


class TestBuildCoords(unittest.TestCase):
    """Расчёт координат вершин в поле 100x100."""

    def test_coords_count_is_three(self):
        coords = _build_coords(3, 4, 5)
        self.assertEqual(len(coords), 3)

    def test_coords_are_int_tuples(self):
        for x, y in _build_coords(3, 4, 5):
            self.assertIsInstance(x, int)
            self.assertIsInstance(y, int)

    def test_coords_within_field(self):
        for x, y in _build_coords(3, 4, 5):
            self.assertTrue(0 <= x <= 100, f"x={x} вне поля")
            self.assertTrue(0 <= y <= 100, f"y={y} вне поля")

    def test_coords_respect_margin(self):
        for x, y in _build_coords(3, 4, 5):
            self.assertGreaterEqual(x, 5)
            self.assertLessEqual(x, 95)
            self.assertGreaterEqual(y, 5)
            self.assertLessEqual(y, 95)

    def test_equilateral_is_symmetric(self):
        """У равностороннего треугольника две нижние вершины на одной высоте."""
        coords = _build_coords(5, 5, 5)
        ys = sorted(p[1] for p in coords)
        # Две НИЖНИЕ точки (наименьшие Y) должны быть равны
        self.assertEqual(ys[0], ys[1])

    def test_right_triangle_has_expected_shape(self):
        coords = _build_coords(3, 4, 5)
        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]
        self.assertGreater(max(xs) - min(xs), 0)
        self.assertGreater(max(ys) - min(ys), 0)


class TestProcessTriangle(unittest.TestCase):
    """Полный пайплайн."""

    def test_equilateral_returns_correct_kind(self):
        kind, _ = process_triangle("3", "3", "3")
        self.assertEqual(kind, "равносторонний")

    def test_isosceles_returns_correct_kind(self):
        kind, _ = process_triangle("3", "3", "4")
        self.assertEqual(kind, "равнобедренный")

    def test_scalene_returns_correct_kind(self):
        kind, _ = process_triangle("3", "4", "5")
        self.assertEqual(kind, "разносторонний")

    def test_not_triangle_returns_minus_one_coords(self):
        kind, coords = process_triangle("1", "2", "10")
        self.assertEqual(kind, "не треугольник")
        self.assertEqual(coords, [(-1, -1)] * 3)

    def test_non_numeric_returns_empty_kind_and_minus_two_coords(self):
        kind, coords = process_triangle("abc", "2", "3")
        self.assertEqual(kind, "")
        self.assertEqual(coords, [(-2, -2)] * 3)

    def test_negative_side_returns_empty_kind(self):
        kind, coords = process_triangle("-3", "4", "5")
        self.assertEqual(kind, "")
        self.assertEqual(coords, [(-2, -2)] * 3)

    def test_zero_side_returns_empty_kind(self):
        kind, _ = process_triangle("0", "4", "5")
        self.assertEqual(kind, "")

    def test_float_sides_produce_valid_triangle(self):
        kind, coords = process_triangle("3.5", "4.5", "5.5")
        self.assertEqual(kind, "разносторонний")
        for x, y in coords:
            self.assertTrue(0 <= x <= 100 and 0 <= y <= 100)

    def test_only_first_side_invalid_returns_empty_kind(self):
        kind, coords = process_triangle("xyz", "4", "5")
        self.assertEqual(kind, "")
        self.assertEqual(coords, [(-2, -2)] * 3)

    def test_only_third_side_invalid_returns_empty_kind(self):
        kind, coords = process_triangle("3", "4", "???")
        self.assertEqual(kind, "")
        self.assertEqual(coords, [(-2, -2)] * 3)


if __name__ == "__main__":
    unittest.main()