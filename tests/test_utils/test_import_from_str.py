import unittest
from vank.utils.load_module import import_from_str
import vank.core


class TestLoad(unittest.TestCase):
    def test_bad_import_grammar(self):
        with self.assertRaises(ValueError):
            import_from_str("a.b.c.")
        with self.assertRaises(ValueError):
            import_from_str(".a.b")
        with self.assertRaises(ValueError):
            import_from_str(".a.b")
        with self.assertRaises(ValueError):
            import_from_str("a.b.c:")
        with self.assertRaises(ValueError):
            import_from_str("a.b.c:a.")
        with self.assertRaises(ValueError):
            import_from_str("a.b.c.:a")
        with self.assertRaises(ValueError):
            import_from_str(".a.b.c:a")

    def test_good_import_grammar(self):
        self.assertEqual(import_from_str("vank.core"), vank.core)
        with self.assertRaises(ImportError):
            import_from_str("vank.fake.module")
        with self.assertRaises(ImportError):
            import_from_str("vank.core.application.asgi:fake_object")
