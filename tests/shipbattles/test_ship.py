import unittest
from shipbattles import entity


class TestShip(unittest.TestCase):
    def test_intersects(self):
        cases = [
            {
                'ship_position': entity.Coordinates(1, 1),
                'shot_position': entity.Coordinates(1, 1),
                'size': 1,
                'orientation': entity.Orientation.vertical,
                'intersects': True
            },
            {
                'ship_position': entity.Coordinates(1, 1),
                'shot_position': entity.Coordinates(2, 1),
                'size': 1,
                'orientation': entity.Orientation.vertical,
                'intersects': False
            },
            {
                'ship_position': entity.Coordinates(1, 1),
                'shot_position': entity.Coordinates(1, 2),
                'size': 1,
                'orientation': entity.Orientation.vertical,
                'intersects': False
            },
            {
                'ship_position': entity.Coordinates(1, 1),
                'shot_position': entity.Coordinates(1, 2),
                'size': 2,
                'orientation': entity.Orientation.vertical,
                'intersects': True
            },
            {
                'ship_position': entity.Coordinates(1, 1),
                'shot_position': entity.Coordinates(2, 1),
                'size': 2,
                'orientation': entity.Orientation.horizontal,
                'intersects': True
            },
            {
                'ship_position': entity.Coordinates(1, 1),
                'shot_position': entity.Coordinates(1, 3),
                'size': 2,
                'orientation': entity.Orientation.vertical,
                'intersects': False
            },
            {
                'ship_position': entity.Coordinates(1, 1),
                'shot_position': entity.Coordinates(3, 1),
                'size': 2,
                'orientation': entity.Orientation.horizontal,
                'intersects': False
            }
        ]

        for case in cases:
            ship = entity.Ship(
                'id:1',
                case['ship_position'],
                case['size'],
                case['orientation']
                )
            self.assertEqual(
                case['intersects'], ship.intersects(case['shot_position']))
