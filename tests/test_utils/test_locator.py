import unittest
from pathlib import Path
from vank.utils.locator import get_obj_file


class A:
    pass


fake1 = 1
fake2 = True


class TestLocator(unittest.TestCase):
    def test_get_obj_file(self):
        self.assertEqual(get_obj_file(fake1, project_dir=Path(__file__).parent), __file__)
        # because python cached small integer
        self.assertEqual(get_obj_file(1, project_dir=Path(__file__).parent), __file__)
        self.assertEqual(get_obj_file(fake2, project_dir=Path(__file__).parent), __file__)
        self.assertEqual(get_obj_file("2"), "Unknown")
        self.assertEqual(get_obj_file(A), __file__)
