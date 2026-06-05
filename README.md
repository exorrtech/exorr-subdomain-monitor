# EXORR Subdomain Monitor

![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)
![MIT License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.0.0-orange)

**Continuous subdomain discovery and change tracking** by EXORR Security.

Monitor target domains for new and removed subdomains over time. Integrates subfinder for passive recon and built-in DNS enumeration as a fallback. Detects changes between runs and generates timestamped snapshots.

---

## Features

- **Multi-source discovery** — subfinder integration + DNS enumeration fallback
- **Change detection** — automatically diffs current results against last snapshot
- **Timestamped snapshots** — every run saved as JSON for historical tracking
- **New/removed alerts** — instantly see what subdomains appeared or disappeared
- **History view** — list all past scans with counts
- **Zero dependencies** — pure Python, no external packages required

---

## Installation

```bash
git clone https://github.com/exorrtech/exorr-subdomain-monitor.git
cd exorr-subdomain-monitor
pip install -e .
```

---

## Usage

### First scan (all subdomains are new)

```bash
exorr-subdomain-monitor example.com
```

### Second scan (detects changes)

```bash
exorr-subdomain-monitor example.com
```

Output shows new and removed subdomains since last run.

### Using only DNS enumeration (no subfinder)

```bash
exorr-subdomain-monitor example.com --tools dns
```

### View historical snapshots

```bash
exorr-subdomain-monitor example.com --history
```

### Save report

```bash
exorr-subdomain-monitor example.com -o report.md --format markdown
```

### Custom data directory

```bash
exorr-subdomain-monitor example.com -d /path/to/data
```

---

## Discovery Tools

| Tool | Method | Requirements |
|------|--------|-------------|
| `subfinder` | Passive subdomain enumeration | [subfinder](https://github.com/projectdiscovery/subfinder) installed |
| `dns` | Active DNS enumeration of 50+ common prefixes | `dig` (usually pre-installed) |

Tools run in sequence and results are merged. If subfinder is not found, DNS enumeration runs automatically.

---

## Snapshot Format

Each run saves a JSON snapshot:

```json
{
  "domain": "example.com",
  "timestamp": "2026-01-01T12:00:00+00:00",
  "count": 42,
  "subdomains": ["api.example.com", "www.example.com", ...]
}
```

Snapshots are stored in `./exorr-monitor-data/<domain>/` by default.

---

## Project Structure

```
exorr-subdomain-monitor/
  exorr_subdomain_monitor/
    __init__.py
    cli.py        # CLI interface
    monitor.py    # Core monitoring engine
    report.py     # Report generator
  tests/
    test_monitor.py
  pyproject.toml
  README.md
  LICENSE
```

---

## Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

---

*Walk with the void. EXORR Security*
