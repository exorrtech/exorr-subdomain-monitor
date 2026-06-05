#!/usr/bin/env python3
"""EXORR Subdomain Monitor — Track subdomain changes over time."""

import argparse
import json
import sys
from typing import Optional

from .monitor import SubdomainMonitor
from .report import MonitorReportGenerator


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="exorr-subdomain-monitor",
        description="EXORR Subdomain Monitor — continuous subdomain discovery and change tracking",
        epilog="Walk with the void. EXORR Security",
    )
    p.add_argument("domain", nargs="?", help="Target domain to monitor")
    p.add_argument("-d", "--data-dir", default="./exorr-monitor-data", help="Data directory (default: ./exorr-monitor-data)")
    p.add_argument("--tools", default="subfinder,dns", help="Comma-separated discovery tools (default: subfinder,dns)")
    p.add_argument("--history", action="store_true", help="Show historical snapshots")
    p.add_argument("-o", "--output", default=None, help="Output file path")
    p.add_argument("--format", choices=["json", "markdown"], default="json", help="Report format")
    p.add_argument("--verbose", action="store_true", help="Verbose output")
    p.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    return p.parse_args(argv)


def main(argv: Optional[list] = None) -> int:
    args = parse_args(argv)

    if not args.domain and not args.history:
        print("[!] Provide a domain to monitor, or use --history to view past runs", file=sys.stderr)
        return 1

    if args.domain:
        tools = [t.strip() for t in args.tools.split(",")]
        monitor = SubdomainMonitor(
            domain=args.domain,
            data_dir=args.data_dir,
            tools=tools,
            verbose=args.verbose,
        )

        print(f"\n  EXORR Subdomain Monitor v1.0.0")
        print(f"  ==============================")
        print(f"  Domain: {args.domain}")
        print(f"  Tools:  {', '.join(tools)}")
        print()

        result = monitor.run()

        print(f"  ==============================")
        print(f"  Current subdomains:  {result['current_count']}")
        print(f"  Previous subdomains: {result['previous_count']}")
        print(f"  New:                 {len(result['new_subdomains'])}")
        print(f"  Removed:            {len(result['removed_subdomains'])}")

        if result["new_subdomains"]:
            print(f"\n  NEW SUBDOMAINS:")
            for s in result["new_subdomains"]:
                print(f"    + {s}")

        if result["removed_subdomains"]:
            print(f"\n  REMOVED SUBDOMAINS:")
            for s in result["removed_subdomains"]:
                print(f"    - {s}")

        print(f"\n  Snapshot saved: {result['snapshot_path']}")
        print()

        if args.output:
            reporter = MonitorReportGenerator(result, format=args.format)
            reporter.save(args.output)
            print(f"  Report saved: {args.output}")

    if args.history:
        if not args.domain:
            print("[!] --history requires a domain", file=sys.stderr)
            return 1
        monitor = SubdomainMonitor(domain=args.domain, data_dir=args.data_dir)
        snapshots = monitor.history()
        if snapshots:
            print(f"\n  Snapshot History for {args.domain}:")
            for s in snapshots:
                print(f"    {s['timestamp']} - {s['count']} subdomains")
            print()
        else:
            print(f"\n  No snapshots found for {args.domain}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
