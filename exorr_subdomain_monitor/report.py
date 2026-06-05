"""Report generator for subdomain monitor results."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


class MonitorReportGenerator:
    """Generate reports from monitoring results."""

    def __init__(self, result: Dict[str, Any], format: str = "json"):
        self.result = result
        self.format = format

    def _to_json(self) -> str:
        return json.dumps({
            "scanner": "exorr-subdomain-monitor",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": self.result,
        }, indent=2, default=str)

    def _to_markdown(self) -> str:
        r = self.result
        lines = [
            "# EXORR Subdomain Monitor Report",
            "",
            f"**Domain:** `{r['domain']}`  ",
            f"**Date:** {r['timestamp']}  ",
            "",
            "## Summary",
            "",
            f"- **Current:** {r['current_count']} subdomains",
            f"- **Previous:** {r['previous_count']} subdomains",
            f"- **New:** {len(r['new_subdomains'])}",
            f"- **Removed:** {len(r['removed_subdomains'])}",
            "",
        ]
        if r["new_subdomains"]:
            lines.append("## New Subdomains")
            for s in r["new_subdomains"]:
                lines.append(f"- `{s}`")
            lines.append("")
        if r["removed_subdomains"]:
            lines.append("## Removed Subdomains")
            for s in r["removed_subdomains"]:
                lines.append(f"- ~~`{s}`~~")
            lines.append("")
        lines.append("---")
        lines.append("*Walk with the void. EXORR Security*")
        return "\n".join(lines)

    def save(self, path: str) -> None:
        content = self._to_json() if self.format == "json" else self._to_markdown()
        Path(path).write_text(content, encoding="utf-8")
