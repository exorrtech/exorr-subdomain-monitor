"""Core monitoring engine — discover, diff, and track subdomain changes."""

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class SubdomainMonitor:
    """Monitor a domain for subdomain changes over time."""

    def __init__(
        self,
        domain: str,
        data_dir: str = "./exorr-monitor-data",
        tools: Optional[List[str]] = None,
        verbose: bool = False,
    ):
        self.domain = domain
        self.data_dir = Path(data_dir) / domain
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tools = tools or ["subfinder", "dns"]
        self.verbose = verbose

    def _run_cmd(self, cmd: List[str], timeout: int = 120) -> str:
        """Run a shell command and return stdout."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ""

    def _discover_subfinder(self) -> Set[str]:
        """Discover subdomains using subfinder."""
        output = self._run_cmd(["subfinder", "-d", self.domain, "-silent"])
        if not output:
            return set()
        return {s.strip().lower() for s in output.splitlines() if s.strip()}

    def _discover_dns(self) -> Set[str]:
        """Discover subdomains using DNS enumeration (fallback)."""
        common_prefixes = [
            "www", "mail", "ftp", "webmail", "smtp", "pop",
            "ns1", "ns2", "dns", "dns1", "dns2", "mx", "mx1", "mx2",
            "api", "dev", "staging", "test", "prod", "production",
            "app", "portal", "admin", "dashboard", "panel",
            "git", "github", "ci", "cd", "jenkins", "build",
            "blog", "docs", "wiki", "help", "support", "kb",
            "shop", "store", "pay", "billing", "account",
            "cdn", "static", "assets", "media", "img", "images",
            "vpn", "remote", "ssh", "rdp", "terminal",
            "db", "database", "mysql", "postgres", "redis", "mongo",
            "auth", "login", "sso", "oauth", "idp",
            "status", "monitor", "health", "ping",
            "internal", "intranet", "extranet", "corp",
        ]
        found = set()
        for prefix in common_prefixes:
            subdomain = f"{prefix}.{self.domain}"
            result = self._run_cmd(["dig", "+short", subdomain, "A"])
            if result and result.strip():
                found.add(subdomain)
        return found

    def discover(self) -> Set[str]:
        """Run all enabled discovery tools and merge results."""
        all_subs: Set[str] = set()

        if "subfinder" in self.tools:
            if self.verbose:
                print(f"  Running subfinder for {self.domain}...")
            subs = self._discover_subfinder()
            all_subs.update(subs)
            if self.verbose:
                print(f"    subfinder found {len(subs)} subdomains")

        if "dns" in self.tools:
            if self.verbose:
                print(f"  Running DNS enumeration for {self.domain}...")
            subs = self._discover_dns()
            all_subs.update(subs)
            if self.verbose:
                print(f"    DNS enum found {len(subs)} subdomains")

        return all_subs

    def _get_latest_snapshot(self) -> Optional[Set[str]]:
        """Load the most recent snapshot."""
        snapshots = sorted(self.data_dir.glob("snapshot_*.json"))
        if not snapshots:
            return None
        with open(snapshots[-1], "r") as f:
            data = json.load(f)
        return set(data.get("subdomains", []))

    def _save_snapshot(self, subdomains: Set[str]) -> Path:
        """Save current subdomains as a timestamped snapshot."""
        ts = datetime.now(timezone.utc)
        timestamp = ts.strftime("%Y%m%d-%H%M%S") + f"-{ts.microsecond}"
        path = self.data_dir / f"snapshot_{timestamp}.json"
        data = {
            "domain": self.domain,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "count": len(subdomains),
            "subdomains": sorted(subdomains),
        }
        path.write_text(json.dumps(data, indent=2))
        return path

    def run(self) -> Dict[str, Any]:
        """Run a full discovery cycle and compare with last snapshot."""
        current = self.discover()
        previous = self._get_latest_snapshot()

        # Save snapshot
        snapshot_path = self._save_snapshot(current)

        # Calculate diff
        if previous is not None:
            new = current - previous
            removed = previous - current
            unchanged = current & previous
        else:
            new = current
            removed = set()
            unchanged = set()

        result = {
            "domain": self.domain,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_count": len(current),
            "previous_count": len(previous) if previous else 0,
            "new_subdomains": sorted(new),
            "removed_subdomains": sorted(removed),
            "unchanged_count": len(unchanged),
            "snapshot_path": str(snapshot_path),
        }

        return result

    def history(self) -> List[Dict[str, Any]]:
        """Return all historical snapshots."""
        snapshots = []
        for path in sorted(self.data_dir.glob("snapshot_*.json")):
            with open(path, "r") as f:
                data = json.load(f)
            snapshots.append({
                "timestamp": data.get("timestamp", ""),
                "count": data.get("count", 0),
                "path": str(path),
            })
        return snapshots
