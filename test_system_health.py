import unittest
import platform
import shutil
import sys
import tempfile
from pathlib import Path

from system_health import generate_report, save_report


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

    def test_report_contains_system_information(self):
        report = generate_report()
        self.assertIn("SYSTEM HEALTH CHECKER", report)
        self.assertIn("DISK SPACE", report)
        self.assertIn("DIRECTORY CHECKS", report)

    def test_report_is_saved_to_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = save_report(
                "Test health report",
                output_dir=Path(temp_dir),
                timestamp="test_run"
            )
            self.assertTrue(report_path.is_file())
            self.assertEqual(
                report_path.read_text(encoding="utf-8").strip(),
                "Test health report"
            )


if __name__ == "__main__":
    unittest.main()
