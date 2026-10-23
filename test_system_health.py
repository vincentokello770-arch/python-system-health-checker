import unittest
import platform
import shutil
import sys
from pathlib import Path

class TestSystemHealth(unittest.TestCase):

    def test_python_version_is_available(self):
        self.assertGreaterEqual(sys.version_info.major, 3)

    def test_operating_system_is_available(self):
        self.assertTrue(platform.system())

    def test_home_directory_exists(self):
        self.assertTrue(Path.home().is_dir())

    def test_disk_usage_is_valid(self):
        usage = shutil.disk_usage(Path.home().anchor or str(Path.home()))

        self.assertGreater(usage.total, 0)
        self.assertGreaterEqual(usage.free, 0)
        self.assertGreaterEqual(usage.used, 0)
        self.assertLessEqual(usage.used, usage.total)
        self.assertLessEqual(usage.free, usage.total)

if __name__ == "__main__":
    unittest.main()
