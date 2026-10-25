# Python System Health Checker

A lightweight Python utility that collects local system information, evaluates disk-space health against explicit thresholds, generates a readable health report, and returns a severity-based process exit code for automation.

## 1. Business Problem

Low disk space can cause failed application writes, interrupted jobs, unsuccessful software updates, and service degradation. Manually checking disk capacity is repetitive and does not provide a consistent result that scripts or CI/CD workflows can interpret.

This project demonstrates a small, testable approach to detecting disk-capacity risk and communicating the result to both people and automation.

## 2. Operational Requirements

The checker should:

- Collect operating system, architecture, and Python version information.
- Measure disk capacity, used space, and available space.
- Check whether common user directories exist.
- Classify disk health using explicit, configurable thresholds.
- Generate a readable report and save it to disk.
- Return an exit code that another program can interpret.
- Support automated tests without requiring the machine's real disk to be in a particular state.

## 3. Design Decisions

### Decision A: Use Python's standard library

The implementation uses modules such as `platform`, `shutil`, `sys`, and `pathlib`.

**Reason:** The initial scope does not justify external dependencies. This reduces installation overhead and dependency-management risk.

**Trade-off:** The tool has no third-party monitoring integrations, alert delivery, or centralized dashboard.

### Decision B: Separate severity classification from reporting

The `classify_disk_status()` function determines the severity independently of report formatting.

**Reason:** The classification logic can be tested directly, including exact threshold boundaries, without depending on the actual disk state.

**Trade-off:** The current design evaluates disk capacity only; it is not a comprehensive operating-system health monitor.

### Decision C: Inject disk measurements into report generation

The `generate_report()` function accepts an optional disk-usage object.

**Reason:** Tests can supply controlled measurements and reproduce an incident consistently instead of depending on the developer's available disk space.

**Trade-off:** This is a small testing seam, not a complete abstraction for monitoring multiple disks or remote hosts.

### Decision D: Use explicit severity thresholds and exit codes

| Free disk space | Severity | Exit code |
|---|---|---:|
| Above 10% | HEALTHY | 0 |
| Above 5% and up to 10% | WARNING | 1 |
| 5% or below | CRITICAL | 2 |
| Report cannot be saved | REPORT ERROR | 3 |
| Disk usage cannot be measured | MEASUREMENT ERROR | 4 |

The boundaries are intentional: exactly 10% is WARNING, and exactly 5% is CRITICAL.

These values are demonstration defaults, not universal production standards. A production deployment should set thresholds based on disk capacity, workload, growth rate, recovery time, and the consequences of a full disk.

**Reason:** Exit codes make the result usable by scheduled jobs, shell scripts, and future monitoring integrations.

**Trade-off:** A calling system must explicitly interpret the codes. Some automation platforms treat every nonzero exit code as a generic failure rather than distinguishing WARNING from CRITICAL.

## 4. How It Works

1. Determine the user's home drive.
2. Collect disk-usage measurements.
3. Calculate free disk space as a percentage of total capacity.
4. Classify the result as HEALTHY, WARNING, or CRITICAL.
5. Collect system information and check Desktop, Documents, and Downloads.
6. Print the report.
7. Return `4` with a diagnostic if disk measurement fails.
8. Save the report under `reports/`, then return the disk-severity exit code; return `3` if report saving fails.

## 5. Requirements

- Python 3.10 or later.
- Windows, Linux, or macOS with the standard Python library available.
- Permission to read disk-usage information and write the report directory.

The automated workflow currently tests Python 3.10, 3.11, and 3.12 on Ubuntu. The local development environment used for this project is Windows 10 with Python 3.10.6.

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

A report is printed to the terminal and saved under `reports/`. The generated report directory is intentionally excluded from version control.

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
- `3`: Report-saving failure; inspect the error printed to standard error.
- `4`: Disk-measurement failure; inspect the error printed to standard error.

Run the commands consecutively in the same PowerShell session so another command does not replace the exit-code value.

## 7. Run the Automated Tests

Run:

```bash
python -m unittest -v
```

The test suite covers:

- Basic runtime and operating-system information.
- Home-directory availability.
- Valid disk-usage measurements.
- Expected report sections.
- Report creation and file contents.
- Healthy, warning, and critical classification.
- Invalid percentage rejection.
- A simulated critical-disk report.
- Disk-measurement and report-saving failure handling.

The tests use controlled disk measurements to validate critical conditions without filling the real disk.

## 8. Validation Evidence

Latest local verification for this project revision:

- **14 automated tests passed.**
- The simulated disk scenario used a 100 GiB disk with 4 GiB free.
- The simulated scenario was correctly classified as CRITICAL.
- The live Windows run detected 12.55 GB free out of 476.73 GB, or 2.63%, and classified it as CRITICAL.
- The report was successfully written to the local `reports/` directory.

The live disk measurement is a point-in-time observation, not a permanent system characteristic. Results may differ on subsequent runs.

The latest local test result does not, by itself, establish that the modified code has passed the remote GitHub Actions workflow. That must be confirmed after pushing the changes.

## 9. Reliability, Security, and Cost

### Reliability

- Severity logic is isolated in a dedicated function.
- Controlled test inputs make threshold tests repeatable.
- Automated tests run through Python's built-in `unittest` framework.
- GitHub Actions is configured to run tests on pushes and pull requests to `main` across Python 3.10, 3.11, and 3.12.

The application catches `OSError` exceptions during disk measurement and report saving. Disk-measurement failures print a diagnostic to standard error and return exit code `4`; report-saving failures return exit code `3`. It does not retry failed operations. Structured logs and alert delivery are not implemented.

### Security

- The tool uses local system information and the Python standard library.
- It does not require cloud credentials, API keys, or external service connections.
- Generated reports are excluded from version control because they contain machine-specific operational information.

The reports are plain-text files and are not encrypted. Anyone with access to the local files may be able to read them.

### Cost

The project has no required paid service and no third-party Python dependency. GitHub Actions usage is subject to the applicable GitHub plan and usage limits.

### Scaling considerations

The current implementation checks one local drive and a few user directories. Monitoring multiple machines would require a collection mechanism, secure remote communication, centralized storage, alerting, and appropriate access controls.

A larger deployment should also consider absolute free-space thresholds, disk growth rate, workload-specific limits, and alert deduplication rather than relying on percentage thresholds alone.

## 10. Current Limitations

- Monitors one selected local drive rather than every mounted volume.
- Checks directory existence, not directory permissions or application functionality.
- Uses fixed severity thresholds in the current implementation.
- Does not send notifications or retain historical metrics in a structured database.
- Disk-measurement and report-saving failures are handled and tested. Failures during report generation are not yet explicitly handled.
- Does not implement a service, daemon, scheduler, or remote monitoring agent.

## 11. Planned Improvements

1. Add explicit handling and tests for report-generation failures.
2. Make severity thresholds configurable through command-line arguments or a configuration file.
3. Add machine-readable JSON output for integration with monitoring tools.
4. Add tests for process exit codes.
5. Expand disk selection and monitoring to multiple volumes.
6. Add structured logging and optional notifications.
7. Document and verify the CI results for every supported Python version.

Future improvements should be prioritized according to a defined operational need rather than added only to increase project complexity.

## 12. Repository Structure

```text
python-system-health-checker/
├── .github/
│   └── workflows/
│       └── python-tests.yml
├── reports/                 # Generated locally; ignored by Git
├── .gitignore
├── README.md
├── system_health.py
└── test_system_health.py
```

## 13. Engineering Summary

This project demonstrates standard-library Python development, separation of logic and presentation, deterministic unit testing, operational severity classification, report generation, process exit codes, Git-based version control, and a GitHub Actions CI workflow.

The focus is on making a small utility testable and automatable while documenting its assumptions, trade-offs, and limitations honestly.
