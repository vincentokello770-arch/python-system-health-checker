import platform
import shutil
import sys
from pathlib import Path
from datetime import datetime

def main():
    home = Path.home()
    drive = home.anchor or str(home)
    disk = shutil.disk_usage(drive)

    print("=" * 45)
    print("       SYSTEM HEALTH CHECKER")
    print("=" * 45)
    print(f"Date and time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Operating sys : {platform.system()} {platform.release()}")
    print(f"Architecture  : {platform.machine()}")
    print(f"Python version: {sys.version.split()[0]}")
    print()
    print("DISK SPACE")
    print(f"Total         : {disk.total / (1024**3):.2f} GB")
    print(f"Used          : {disk.used / (1024**3):.2f} GB")
    print(f"Free          : {disk.free / (1024**3):.2f} GB")

    print()
    print("DIRECTORY CHECKS")
    directories = ["Desktop", "Documents", "Downloads"]
    for name in directories:
        path = home / name
        status = "OK" if path.is_dir() else "NOT FOUND"
        print(f"{name:12} : {status}")

    print()
    free_percent = disk.free / disk.total * 100
    if free_percent < 10:
        print("WARNING: Less than 10% disk space is free.")
    else:
        print("STATUS: Disk space is above the 10% warning threshold.")

    print("=" * 45)

if __name__ == "__main__":
    main()
