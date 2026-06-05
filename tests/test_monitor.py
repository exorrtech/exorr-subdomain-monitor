"""Tests for the subdomain monitor."""
import json
import tempfile
from pathlib import Path

from exorr_subdomain_monitor.monitor import SubdomainMonitor


def test_snapshot_save_and_load():
    """Snapshots should be saved and loadable."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monitor = SubdomainMonitor(
            domain="test.com",
            data_dir=tmpdir,
            tools=["dns"],
        )
        test_subs = {"www.test.com", "api.test.com", "mail.test.com"}
        path = monitor._save_snapshot(test_subs)
        assert path.exists()

        loaded = monitor._get_latest_snapshot()
        assert loaded == test_subs


def test_diff_detection():
    """Monitor should detect new and removed subdomains."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monitor = SubdomainMonitor(
            domain="test.com",
            data_dir=tmpdir,
            tools=["dns"],
        )
        # Save initial snapshot
        monitor._save_snapshot({"www.test.com", "api.test.com"})

        # Override discover to return a different set
        monitor.discover = lambda: {"www.test.com", "mail.test.com", "new.test.com"}

        result = monitor.run()
        assert "new.test.com" in result["new_subdomains"]
        assert "mail.test.com" in result["new_subdomains"]
        assert "api.test.com" in result["removed_subdomains"]


def test_history():
    """History should list all snapshots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monitor = SubdomainMonitor(
            domain="test.com",
            data_dir=tmpdir,
            tools=["dns"],
        )
        monitor._save_snapshot({"a.test.com"})
        monitor._save_snapshot({"a.test.com", "b.test.com"})
        history = monitor.history()
        assert len(history) == 2
        assert history[0]["count"] == 1
        assert history[1]["count"] == 2


def test_no_previous_snapshot():
    """First run should treat all subdomains as new."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monitor = SubdomainMonitor(
            domain="fresh.com",
            data_dir=tmpdir,
            tools=["dns"],
        )
        monitor.discover = lambda: {"a.fresh.com", "b.fresh.com"}
        result = monitor.run()
        assert result["previous_count"] == 0
        assert len(result["new_subdomains"]) == 2
        assert len(result["removed_subdomains"]) == 0


def test_unchanged_detection():
    """Monitor should correctly count unchanged subdomains."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monitor = SubdomainMonitor(
            domain="stable.com",
            data_dir=tmpdir,
            tools=["dns"],
        )
        monitor._save_snapshot({"a.stable.com", "b.stable.com"})
        monitor.discover = lambda: {"a.stable.com", "b.stable.com"}
        result = monitor.run()
        assert result["unchanged_count"] == 2
        assert len(result["new_subdomains"]) == 0
        assert len(result["removed_subdomains"]) == 0
