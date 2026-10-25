import unittest
import platform
import shutil
import sys
import tempfile
from collections import namedtuple
from pathlib import Path

from system_health import (
    classify_disk_status,
    generate_report,
    save_report,
)


DiskUsage = namedtuple("DiskUsage", ["total", "used", "free"])


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
        self.assertIn("Severity", report)

    def test_report_is_saved_to_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = save_report(
                "Test health report",
                output_dir=Path(temp_dir),
                timestamp="test_run",
            )
            self.assertTrue(report_path.is_file())
            self.assertEqual(
                report_path.read_text(encoding="utf-8").strip(),
                "Test health report",
            )

    def test_healthy_disk_status(self):
        self.assertEqual(classify_disk_status(50.0), "HEALTHY")
        self.assertEqual(classify_disk_status(10.01), "HEALTHY")

    def test_warning_disk_status(self):
        self.assertEqual(classify_disk_status(10.0), "WARNING")
        self.assertEqual(classify_disk_status(7.5), "WARNING")
        self.assertEqual(classify_disk_status(5.01), "WARNING")

    def test_critical_disk_status(self):
        self.assertEqual(classify_disk_status(5.0), "CRITICAL")
        self.assertEqual(classify_disk_status(1.0), "CRITICAL")
        self.assertEqual(classify_disk_status(0.0), "CRITICAL")

    def test_invalid_disk_percentage_is_rejected(self):
        for value in (-1.0, 100.1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    classify_disk_status(value)

    def test_simulated_critical_disk_appears_in_report(self):
        # Simulate a 100 GB disk with only 4 GB free.
        simulated_disk = DiskUsage(
            total=100 * 1024**3,
            used=96 * 1024**3,
            free=4 * 1024**3,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            report = generate_report(
                disk_usage=simulated_disk,
                home=Path(temp_dir),
            )

        self.assertIn("Free space    : 4.00%", report)
        self.assertIn("Severity      : CRITICAL", report)


if __name__ == "__main__":
    unittest.main()
