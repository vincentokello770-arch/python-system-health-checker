
# Python System Health Checker

A lightweight Python utility that collects local system information, evaluates disk-space health against explicit thresholds, generates a readable health report, records diagnostic events in a persistent log, and returns severity-based process exit codes for automation.

## 1. Business Problem

Low disk space can cause failed application writes, interrupted jobs, unsuccessful software updates, and service degradation. Manually checking disk capacity is repetitive and does not provide a consistent result that scripts or CI/CD workflows can interpret.

This project demonstrates a small, testable approach to detecting disk-capacity risk and communicating the result to people and automation.

## 2. Operational Requirements

The checker should:

- Collect operating system, architecture, and Python version information.
- Measure disk capacity, used space, and available space.
- Check whether common user directories exist.
- Classify disk health using explicit severity thresholds.
- Generate a readable report and save it to disk.
- Record diagnostic events in a persistent log file.
- Return exit codes that other programs can interpret.
- Support automated tests without depending on the machine's actual disk state.
- Continue operating when logging setup fails, provided the core operation can proceed.

## 3. Design Decisions

### Decision A: Use Python's standard library

The implementation uses modules such as `platform`, `shutil`, `sys`, `pathlib`, and `logging`.

**Reason:** The initial scope does not justify external dependencies. This reduces installation overhead and dependency-management risk.

**Trade-off:** The tool has no third-party monitoring integrations, alert delivery, or centralized dashboard.

### Decision B: Separate severity classification from reporting

The `classify_disk_status()` function determines severity independently of report formatting.

**Reason:** Classification logic can be tested directly, including exact threshold boundaries, without depending on the actual disk state.

**Trade-off:** The current design evaluates disk capacity only; it is not a comprehensive operating-system health monitor.

### Decision C: Inject disk measurements into report generation

The `generate_report()` function accepts an optional disk-usage object.

**Reason:** Tests can supply controlled measurements and reproduce an incident consistently instead of depending on the developer's available disk space.

**Trade-off:** This is a testing seam, not a complete abstraction for monitoring multiple disks or remote hosts.

### Decision D: Use explicit severity thresholds and exit codes

| Free disk space | Severity | Exit code |
|---|---|---:|
| Above 10% | HEALTHY | 0 |
| Above 5% and up to 10% | WARNING | 1 |
| 5% or below | CRITICAL | 2 |
| Report cannot be saved | REPORT ERROR | 3 |
| Disk usage cannot be measured | MEASUREMENT ERROR | 4 |

The boundaries are intentional: exactly 10% is WARNING, and exactly 5% is CRITICAL.

These are demonstration defaults, not universal production standards. Production thresholds should account for disk capacity, workload, growth rate, recovery time, and the consequences of a full disk.

**Reason:** Exit codes allow scheduled jobs, shell scripts, and monitoring integrations to interpret the result.

**Trade-off:** Calling systems must explicitly interpret the codes. Some automation platforms treat all nonzero exit codes as generic failures.

### Decision E: Use persistent application logging

The `configure_logging()` function configures Python's built-in logging system to write diagnostic messages to `logs/system_health.log`.

Log entries include a timestamp, severity level, logger name, and message.

The application records:

- Disk-measurement failures.
- Report-saving failures.
- Successful health-check completion, including disk severity and free-space percentage.

Logging setup failure is handled without preventing the health check from proceeding. The application also retains its existing terminal error messages.

**Trade-off:** Logs are local plain-text files. The current implementation does not provide log rotation, centralized collection, notifications, or guaranteed persistence if the operating system or storage device fails.

## 4. How It Works

1. Determine the user's home drive.
2. Configure application logging.
3. Collect disk-usage measurements.
4. Calculate free disk space as a percentage of total capacity.
5. Classify the result as HEALTHY, WARNING, or CRITICAL.
6. Collect system information and check Desktop, Documents, and Downloads.
7. Print the report.
8. Save the report under `reports/`.
9. Record the health-check outcome in the application log.
10. Return the corresponding severity exit code, or an error code if disk measurement or report saving fails.

## 5. Requirements

- Python 3.10 or later.
- Windows, Linux, or macOS with the standard Python library available.
- Permission to read disk-usage information and write output files.

The configured GitHub Actions workflow tests Python 3.10, 3.11, and 3.12 on Ubuntu. The local development environment used for this project is Windows 10 with Python 3.10.6.

## 6. Run the Project

Clone the repository and enter its directory:

```bash
git clone https://github.com/vincentokello770-arch/python-system-health-checker.git
cd python-system-health-checker
```

Run the checker:

```bash
python system_health.py
```

The report is printed to the terminal and saved under `reports/`. Diagnostic events are written to `logs/system_health.log`.

Both generated directories are excluded from version control.

### Interpret the exit code

In PowerShell, run:

```powershell
python .\system_health.py
$LASTEXITCODE
```

The second command displays the exit code from the Python process.

- `0`: HEALTHY
- `1`: WARNING
- `2`: CRITICAL
- `3`: Report-saving failure.
- `4`: Disk-measurement failure.

Run the commands consecutively in the same PowerShell session so another command does not replace the exit-code value.

### Inspect the application log

In PowerShell:

```powershell
Get-Content .\logs\system_health.log -Tail 20
```

This displays the most recent 20 log lines.

The log file is created when logging is successfully configured. If logging setup fails, the application continues without persistent file logging.

## 7. Run the Automated Tests

Run:

```bash
python -m unittest -v
```

The suite currently contains 16 tests covering:

- Basic runtime and operating-system information.
- Home-directory availability.
- Valid disk-usage measurements.
- Expected report sections.
- Report creation and file contents.
- Healthy, warning, and critical classification.
- Invalid percentage rejection.
- Simulated critical-disk reporting.
- Disk-measurement and report-saving failure handling.
- Persistent log-file creation and diagnostic message writing.
- Logging setup failure handling.

The tests use controlled disk measurements to validate critical conditions without filling the real disk. Logging tests use temporary directories and clean up their handlers.

## 8. Validation Evidence

Latest local verification for the logging revision:

- **16 automated tests passed.**
- Python syntax compilation completed without errors.
- A simulated disk with 100 GiB total capacity and 4 GiB free was correctly classified as CRITICAL.
- Logging tests verified that diagnostic messages can be written to a file.
- A simulated logging setup failure was handled without raising an exception from `configure_logging()`.
- A live Windows run successfully generated a report, wrote a log entry, and returned exit code `2` because free disk space was below the critical threshold.

The live run reported 13.27 GB free out of 476.73 GB, or 2.78%. This is a point-in-time measurement and may change.

The local test result does not establish that the latest revision has passed GitHub Actions. That must be verified after the changes are committed and pushed.

## 9. Reliability, Security, and Cost

### Reliability

- Severity logic is isolated in a dedicated function.
- Controlled test inputs make threshold tests repeatable.
- Automated tests use Python's built-in `unittest` framework.
- Disk-measurement and report-saving failures are handled explicitly.
- Diagnostic events are recorded in a local log when logging is configured.
- GitHub Actions is configured to run tests on pushes and pull requests to `main` across Python 3.10, 3.11, and 3.12.

The application does not retry failed operations. Report-generation failures are not yet explicitly handled by `main()`.

### Security

- The tool uses local system information and the Python standard library.
- It does not require cloud credentials, API keys, or external service connections.
- Generated reports and logs are excluded from version control because they contain machine-specific operational information.

Reports and logs are plain-text files and are not encrypted. Anyone with access to the local files may be able to read them. Production deployments should define appropriate filesystem permissions and retention policies.

### Cost

The project has no required paid service and no third-party Python dependency. GitHub Actions usage is subject to the applicable GitHub plan and usage limits.

### Scaling considerations

The current implementation checks one selected local drive and a few user directories. Monitoring multiple machines would require a collection mechanism, secure remote communication, centralized storage, alerting, and appropriate access controls.

A larger deployment should also consider absolute free-space thresholds, disk growth rate, workload-specific limits, log rotation, and alert deduplication rather than relying on percentage thresholds alone.

## 10. Current Limitations

- Monitors one selected local drive rather than every mounted volume.
- Checks directory existence, not directory permissions or application functionality.
- Uses fixed severity thresholds.
- Writes logs locally without rotation or centralized collection.
- Does not send notifications or retain historical metrics in a structured database.
- Handles disk-measurement and report-saving failures, but report-generation failures are not explicitly handled by `main()`.
- Does not implement a service, daemon, scheduler, or remote monitoring agent.

## 11. Planned Improvements

1. Add explicit handling and tests for report-generation failures.
2. Make severity thresholds configurable through command-line arguments or a configuration file.
3. Add machine-readable JSON output for monitoring integrations.
4. Add tests for process exit codes.
5. Expand disk selection and monitoring to multiple volumes.
6. Add log rotation and configurable logging destinations.
7. Document and verify CI results for every supported Python version.

Improvements should be prioritized according to operational requirements rather than added only to increase project complexity.

## 12. Repository Structure

```text
python-system-health-checker/
├── .github/
│   └── workflows/
│       └── python-tests.yml
├── reports/                 # Generated locally; ignored by Git
├── logs/                    # Generated locally; ignored by Git
├── .gitignore
├── README.md
├── system_health.py
└── test_system_health.py
```

## 13. Engineering Summary

This project demonstrates standard-library Python development, separation of logic and presentation, deterministic unit testing, operational severity classification, report generation, process exit codes, persistent logging, Git-based version control, and a GitHub Actions CI workflow.

The focus is on making a small utility testable and automatable while documenting its assumptions, trade-offs, and limitations honestly.
