import platform
import shutil
import sys
from datetime import datetime
from pathlib import Path


WARNING_THRESHOLD = 10.0
CRITICAL_THRESHOLD = 5.0


def classify_disk_status(free_percent):
    """Classify disk health using explicit operational thresholds."""
    if not 0 <= free_percent <= 100:
        raise ValueError("Free disk percentage must be between 0 and 100.")

    if free_percent <= CRITICAL_THRESHOLD:
        return "CRITICAL"
    if free_percent <= WARNING_THRESHOLD:
        return "WARNING"
    return "HEALTHY"


def generate_report(disk_usage=None, home=None):
    """Collect system information and return a formatted health report."""
    home = Path(home) if home is not None else Path.home()
    drive = home.anchor or str(home)

    # Allow controlled disk measurements in automated tests.
    disk = disk_usage if disk_usage is not None else shutil.disk_usage(drive)

    if disk.total <= 0:
        raise ValueError("Total disk capacity must be greater than zero.")

    free_percent = disk.free / disk.total * 100
    status = classify_disk_status(free_percent)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "=" * 45,
        "       SYSTEM HEALTH CHECKER",
        "=" * 45,
        f"Date and time : {now}",
        f"Operating sys : {platform.system()} {platform.release()}",
        f"Architecture  : {platform.machine()}",
        f"Python version: {sys.version.split()[0]}",
        "",
        "DISK SPACE",
        f"Total         : {disk.total / (1024**3):.2f} GB",
        f"Used          : {disk.used / (1024**3):.2f} GB",
        f"Free          : {disk.free / (1024**3):.2f} GB",
        f"Free space    : {free_percent:.2f}%",
        "",
        "DIRECTORY CHECKS",
    ]

    for name in ["Desktop", "Documents", "Downloads"]:
        directory_status = (
            "OK" if (home / name).is_dir() else "NOT FOUND"
        )
        lines.append(f"{name:12} : {directory_status}")

    lines.extend([
        "",
        "DISK STATUS",
        f"Severity      : {status}",
        f"Warning limit : {WARNING_THRESHOLD:.1f}%",
        f"Critical limit: {CRITICAL_THRESHOLD:.1f}%",
        "=" * 45,
    ])

    return "\n".join(lines)


def save_report(report, output_dir=Path("reports"), timestamp=None):
    """Save a report and return the path of the created file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_path = output_dir / f"health_report_{timestamp}.txt"
    report_path.write_text(report + "\n", encoding="utf-8")

    return report_path


def main():
    home = Path.home()
    drive = home.anchor or str(home)
    try:
        disk = shutil.disk_usage(drive)
    except OSError as error:
        print(
            f"ERROR: Unable to measure disk usage for {drive}: {error}",
            file=sys.stderr,
        )
        return 4

    report = generate_report(disk_usage=disk, home=home)
    print(report)

    try:
        report_path = save_report(report)
    except OSError as error:
        print(
            f"\nERROR: Unable to save health report: {error}",
            file=sys.stderr,
        )
        return 3

    print(f"\nReport saved to: {report_path.resolve()}")

    free_percent = disk.free / disk.total * 100
    status = classify_disk_status(free_percent)

    return {"HEALTHY": 0, "WARNING": 1, "CRITICAL": 2}[status]


if __name__ == "__main__":
    sys.exit(main())
