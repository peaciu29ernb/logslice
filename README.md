# logslice

A CLI tool to filter and slice structured log files by time range or field patterns.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/youruser/logslice.git && cd logslice && pip install .
```

---

## Usage

```bash
# Filter logs by time range
logslice --file app.log --start "2024-01-15T08:00:00" --end "2024-01-15T09:00:00"

# Filter by field pattern
logslice --file app.log --match level=error

# Combine time range and field filter
logslice --file app.log --start "2024-01-15T08:00:00" --match service=api --output filtered.log
```

### Options

| Flag | Description |
|------|-------------|
| `--file` | Path to the structured log file (JSON, NDJSON) |
| `--start` | Start of the time range (ISO 8601) |
| `--end` | End of the time range (ISO 8601) |
| `--match` | Field pattern filter in `key=value` format |
| `--output` | Write results to a file instead of stdout |

---

## Requirements

- Python 3.8+

---

## License

This project is licensed under the [MIT License](LICENSE).