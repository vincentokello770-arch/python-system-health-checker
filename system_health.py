import platform
import shutil
import sys
from datetime import datetime
from pathlib import Path


def generate_report():
    """Collect system information and return a formatted report."""
    home = Path.home()
    drive = home.anchor or str(home)
    disk = shutil.disk_usage(drive)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    free_percent = disk.free / disk.total * 100

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
        status = "OK" if (home / name).is_dir() else "NOT FOUND"
        lines.append(f"{name:12} : {status}")

    lines.extend([
        "",
        "DISK STATUS",
        (
            "WARNING: Less than 10% disk space is free."
            if free_percent < 10
            else "STATUS: Disk space is above the 10% warning threshold."
        ),
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
    report = generate_report()
    print(report)

    report_path = save_report(report)
    print(f"\nReport saved to: {report_path.resolve()}")


if __name__ == "__main__":
    main()
