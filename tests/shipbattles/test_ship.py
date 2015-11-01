import unittest
from shipbattles import entity


class TestShip(unittest.TestCase):
    def test_intersects(self):
        cases = {
            'fire exacly at 1-size ship': {
                'ship_position': entity.Coordinates(1, 1),
                'shot_position': entity.Coordinates(1, 1),
                'size': 1,
                'orientation': entity.Orientation.vertical,
                'intersects': True
            },
            'fire next to 1-size ship': {
                'ship_position': entity.Coordinates(1, 1),
                'shot_position': entity.Coordinates(2, 1),
                'size': 1,
                'orientation': entity.Orientation.vertical,
                'intersects': False
            },
            'fire below 1-size ship': {
                'ship_position': entity.Coordinates(1, 1),
                'shot_position': entity.Coordinates(1, 2),
                'size': 1,
                'orientation': entity.Orientation.vertical,
                'intersects': False
            },
            'fire at bottom of vertical 2-size ship': {
                'ship_position': entity.Coordinates(1, 1),
                'shot_position': entity.Coordinates(1, 2),
                'size': 2,
                'orientation': entity.Orientation.vertical,
                'intersects': True
            },
            'fire at right-corner of 2-size horizontal ship': {
                'ship_position': entity.Coordinates(1, 1),
                'shot_position': entity.Coordinates(2, 1),
                'size': 2,
                'orientation': entity.Orientation.horizontal,
                'intersects': True
            },
            'fire below 2-size vertical ship': {
                'ship_position': entity.Coordinates(1, 1),
                'shot_position': entity.Coordinates(1, 3),
                'size': 2,
                'orientation': entity.Orientation.vertical,
                'intersects': False
            },
            'fire next to 2-size horizontal ship': {
                'ship_position': entity.Coordinates(1, 1),
                'shot_position': entity.Coordinates(3, 1),
                'size': 2,
                'orientation': entity.Orientation.horizontal,
                'intersects': False
            }
        }

        for case in cases.values():
            ship = entity.Ship(
                'id:1',
                case['ship_position'],
                case['size'],
                case['orientation']
                )
            self.assertEqual(
                case['intersects'], ship.intersects(case['shot_position']))

    def test_fire_1_size_ship(self):
        ship = entity.Ship(
            'id:1', entity.Coordinates(1, 1), 1, entity.Orientation.horizontal)
        self.assertEqual(entity.FireResult.sunken, ship.fire())

    def test_fire_2_size_ship(self):
        ship = entity.Ship(
            'id:1', entity.Coordinates(1, 1), 2, entity.Orientation.horizontal)
        self.assertEqual(entity.FireResult.hit, ship.fire())
        self.assertEqual(entity.FireResult.sunken, ship.fire())
