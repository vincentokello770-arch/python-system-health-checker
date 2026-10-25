
import io
import platform
import shutil
import sys
import tempfile
import unittest
from collections import namedtuple
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from system_health import (
    LOGGER,
    classify_disk_status,
    configure_logging,
    generate_report,
    main,
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
        usage = shutil.disk_usage(
            Path.home().anchor or str(Path.home())
        )
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

    def test_save_report_rejects_file_as_output_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            blocker = Path(temp_dir) / "not_a_directory"
            blocker.write_text("blocking file", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                save_report(
                    "Test report",
                    output_dir=blocker,
                    timestamp="failure_test",
                )

    def test_main_returns_3_when_report_saving_fails(self):
        simulated_disk = DiskUsage(
            total=100 * 1024**3,
            used=40 * 1024**3,
            free=60 * 1024**3,
        )
        stderr = io.StringIO()
        stdout = io.StringIO()

        with (
            patch(
                "system_health.shutil.disk_usage",
                return_value=simulated_disk,
            ),
            patch(
                "system_health.generate_report",
                return_value="Simulated health report",
            ),
            patch(
                "system_health.save_report",
                side_effect=OSError("simulated disk write failure"),
            ),
            redirect_stderr(stderr),
            redirect_stdout(stdout),
        ):
            exit_code = main()

        self.assertEqual(exit_code, 3)
        self.assertIn(
            "ERROR: Unable to save health report",
            stderr.getvalue(),
        )
        self.assertIn(
            "simulated disk write failure",
            stderr.getvalue(),
        )
        self.assertIn(
            "Simulated health report",
            stdout.getvalue(),
        )
        self.assertNotIn("Report saved to:", stdout.getvalue())

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

    def test_main_returns_4_when_disk_measurement_fails(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        with (
            patch(
                "system_health.shutil.disk_usage",
                side_effect=OSError(
                    "simulated disk measurement failure"
                ),
            ),
            patch("system_health.generate_report") as generate_report_mock,
            patch("system_health.save_report") as save_report_mock,
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            exit_code = main()

        self.assertEqual(exit_code, 4)
        self.assertIn(
            "ERROR: Unable to measure disk usage",
            stderr.getvalue(),
        )
        self.assertIn(
            "simulated disk measurement failure",
            stderr.getvalue(),
        )
        self.assertEqual(stdout.getvalue(), "")
        generate_report_mock.assert_not_called()
        save_report_mock.assert_not_called()

    def test_configure_logging_writes_to_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir)

            try:
                self.assertTrue(configure_logging(log_dir))

                LOGGER.error("Test diagnostic message")

                for handler in LOGGER.handlers:
                    handler.flush()

                log_file = log_dir / "system_health.log"

                self.assertTrue(log_file.is_file())
                self.assertIn(
                    "Test diagnostic message",
                    log_file.read_text(encoding="utf-8"),
                )
            finally:
                for handler in LOGGER.handlers[:]:
                    LOGGER.removeHandler(handler)
                    handler.close()

    def test_logging_setup_failure_does_not_crash(self):
        with patch(
            "system_health.Path.mkdir",
            side_effect=OSError("simulated logging setup failure"),
        ):
            result = configure_logging(Path("unavailable_logs"))

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
