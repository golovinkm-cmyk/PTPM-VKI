import os
import sys
import unittest

#sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.delivery import calculate_delivery_cost



class TestValidation(unittest.TestCase):
    """Проверка входных данных."""

    def test_weight_below_minimum_returns_error(self):
        cost, date = calculate_delivery_cost(weight=0.05, distance=100, package_type="обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_weight_above_maximum_returns_error(self):
        cost, date = calculate_delivery_cost(weight=51, distance=100, package_type="обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_weight_exactly_minimum_is_valid(self):
        cost, _ = calculate_delivery_cost(weight=0.1, distance=100, package_type="обычный")
        self.assertNotEqual(cost, -1)

    def test_weight_exactly_maximum_is_valid(self):
        cost, _ = calculate_delivery_cost(weight=50.0, distance=100, package_type="обычный")
        self.assertNotEqual(cost, -1)

    def test_distance_below_minimum_returns_error(self):
        cost, date = calculate_delivery_cost(weight=1, distance=0, package_type="обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_distance_above_maximum_returns_error(self):
        cost, date = calculate_delivery_cost(weight=1, distance=5001, package_type="обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_distance_exactly_minimum_is_valid(self):
        cost, _ = calculate_delivery_cost(weight=1, distance=1, package_type="обычный")
        self.assertNotEqual(cost, -1)

    def test_distance_exactly_maximum_is_valid(self):
        cost, _ = calculate_delivery_cost(weight=1, distance=5000, package_type="обычный")
        self.assertNotEqual(cost, -1)

    def test_invalid_package_type_returns_error(self):
        cost, date = calculate_delivery_cost(weight=1, distance=100, package_type="жидкий")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_empty_package_type_returns_error(self):
        cost, _ = calculate_delivery_cost(weight=1, distance=100, package_type="")
        self.assertEqual(cost, -1)


class TestBaseCost(unittest.TestCase):
    """Базовая формула и весовые коэффициенты."""

    def test_base_cost_for_light_package(self):
        cost, _ = calculate_delivery_cost(weight=1, distance=1, package_type="обычный")
        self.assertEqual(cost, 205)

    def test_cost_grows_with_distance(self):
        c1, _ = calculate_delivery_cost(weight=1, distance=100, package_type="обычный")
        c2, _ = calculate_delivery_cost(weight=1, distance=200, package_type="обычный")
        self.assertGreater(c2, c1)

    def test_medium_weight_applies_1_2_multiplier(self):
        cost, _ = calculate_delivery_cost(weight=10, distance=200, package_type="обычный")
        self.assertEqual(cost, int((200 + 200 * 5) * 1.2))

    def test_heavy_weight_applies_1_5_multiplier(self):
        cost, _ = calculate_delivery_cost(weight=25, distance=200, package_type="обычный")
        self.assertEqual(cost, int((200 + 200 * 5) * 1.5))


class TestPackageType(unittest.TestCase):
    """Надбавки за тип посылки."""

    def test_fragile_adds_300(self):
        base, _ = calculate_delivery_cost(weight=1, distance=100, package_type="обычный")
        fragile, _ = calculate_delivery_cost(weight=1, distance=100, package_type="хрупкий")
        self.assertEqual(fragile - base, 300)

    def test_dangerous_adds_1000(self):
        base, _ = calculate_delivery_cost(weight=1, distance=100, package_type="обычный")
        dangerous, _ = calculate_delivery_cost(weight=1, distance=100, package_type="опасный")
        self.assertEqual(dangerous - base, 1000)

    def test_dangerous_more_expensive_than_fragile(self):
        fragile, _ = calculate_delivery_cost(weight=1, distance=100, package_type="хрупкий")
        dangerous, _ = calculate_delivery_cost(weight=1, distance=100, package_type="опасный")
        self.assertGreater(dangerous, fragile)


class TestExpressDelivery(unittest.TestCase):
    """Экспресс-доставка. Часть тестов падает — это найденные баги."""

    def test_express_should_cost_more_than_standard(self):
        standard, _ = calculate_delivery_cost(weight=1, distance=100, package_type="обычный", is_express=False)
        express, _ = calculate_delivery_cost(weight=1, distance=100, package_type="обычный", is_express=True)
        self.assertGreater(express, standard,
                           f"Экспресс ({express}) должен быть дороже обычной ({standard})")

    def test_express_should_not_be_cheaper_than_standard(self):
        standard, _ = calculate_delivery_cost(weight=10, distance=1000, package_type="обычный")
        express, _ = calculate_delivery_cost(weight=10, distance=1000, package_type="обычный", is_express=True)
        self.assertGreaterEqual(express, standard)

    def test_express_delivery_faster_for_long_distance(self):
        _, std_date = calculate_delivery_cost(weight=1, distance=5000, package_type="обычный")
        _, exp_date = calculate_delivery_cost(weight=1, distance=5000, package_type="обычный", is_express=True)
        self.assertLess(exp_date, std_date)

    def test_express_short_distance_takes_one_day(self):
        _, exp_date = calculate_delivery_cost(weight=1, distance=400, package_type="обычный", is_express=True)
        _, std_date = calculate_delivery_cost(weight=1, distance=400, package_type="обычный")
        self.assertLess(exp_date, std_date,
                        f"Экспресс ({exp_date}) должен быть раньше стандарта ({std_date})")


class TestDeliveryDate(unittest.TestCase):
    """Дата доставки. Один тест падает — фиксированная дата отправки."""

    def test_standard_delivery_returns_valid_date_format(self):
        _, date = calculate_delivery_cost(weight=1, distance=100, package_type="обычный")
        self.assertRegex(date, r"^\d{4}-\d{2}-\d{2}$")

    def test_delivery_date_is_in_the_future(self):
        _, date = calculate_delivery_cost(weight=1, distance=100, package_type="обычный")
        self.assertGreater(date, "2026-10-07",
                           f"Дата доставки {date} не должна быть в прошлом")

    def test_far_distance_takes_more_days(self):
        _, near = calculate_delivery_cost(weight=1, distance=100, package_type="обычный")
        _, far = calculate_delivery_cost(weight=1, distance=4000, package_type="обычный")
        self.assertLess(near, far)

    def test_minimum_delivery_time_is_one_day(self):
        _, date = calculate_delivery_cost(weight=1, distance=1, package_type="обычный")
        self.assertEqual(date, "2026-09-04")


class TestRounding(unittest.TestCase):
    """Округление цены. Тест падает — int() вместо round()."""

    def test_price_is_rounded_not_truncated(self):
        # (200 + 5) * 1.5 = 307.5 → int() даст 307, round() даст 308
        cost, _ = calculate_delivery_cost(weight=21, distance=1, package_type="обычный")
        self.assertEqual(cost, round(307.5),
                         f"Цена {cost} должна быть округлена, а не отброшена")


if __name__ == "__main__":
    unittest.main()