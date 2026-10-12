#!/usr/bin/env python3
"""
prune_versions.py - Reusable Multi-Version Pruning & Deduplication Engine.
Designed for SAP Second Brain Project Onboarding SOP.
Uses Python Standard Library ONLY.

Rule: Retain at most the LAST 2 VERSIONS (Latest + 1 Prior Baseline).
Purges older obsolete versions (e.g. v0.1, v0.2, v0.3 when v0.4 & v0.5 exist).
"""

import os
import sys
import re
import argparse
from pathlib import Path
from collections import defaultdict

# Force UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Regex to capture version string: e.g., _v.0.5, - V1.2, _v0.10_id.md
VERSION_PATTERN = re.compile(
    r'^(.*?)(?:[_\-\. ]+v(?:er)?\.?\s*(\d+(?:\.\d+)*))(.*?)$',
    re.IGNORECASE
)

def parse_version_tuple(v_str):
    """Convert version string '0.10' -> (0, 10) for proper integer ordering."""
    try:
        return tuple(int(x) for x in v_str.split('.'))
    except ValueError:
        return (0,)

def find_version_groups(target_dir):
    """Group files by (parent_dir, base_name, extension)."""
    groups = defaultdict(list)
    root = Path(target_dir).resolve()
    
    for p in root.rglob('*'):
        if not p.is_file():
            continue
        m = VERSION_PATTERN.match(p.name)
        if m:
            base_name = m.group(1).lower().rstrip('_- ')
            suffix = m.group(3).lower()
            v_str = m.group(2)
            v_tuple = parse_version_tuple(v_str)
            key = (str(p.parent), base_name, suffix)
            groups[key].append((v_tuple, v_str, p))

    return groups

def scan_and_prune(target_dir, keep_count=2, apply=False):
    groups = find_version_groups(target_dir)
    multi_groups = {k: v for k, v in groups.items() if len(v) > keep_count}

    print(f"Directory: {target_dir}")
    print(f"Total versioned file groups found: {len(groups)}")
    print(f"Groups exceeding {keep_count} versions: {len(multi_groups)}")
    print("=" * 70)

    total_to_delete = 0
    total_bytes_saved = 0

    for (parent, base_name, suffix), file_list in sorted(multi_groups.items()):
        # Sort by version tuple ascending: e.g. (0,1), (0,2), (0,3), (0,4), (0,5)
        file_list.sort(key=lambda x: x[0])
        keep_files = file_list[-keep_count:]
        purge_files = file_list[:-keep_count]

        rel_parent = os.path.relpath(parent, target_dir)
        print(f"\n📂 [{rel_parent}] {base_name} {suffix}")
        print(f"   🟢 KEEP ({len(keep_files)} latest):")
        for v_tuple, v_str, p in keep_files:
            print(f"      ✔ v{v_str}: {p.name}")

        print(f"   🔴 PURGE ({len(purge_files)} obsolete):")
        for v_tuple, v_str, p in purge_files:
            size_kb = p.stat().st_size / 1024
            total_bytes_saved += p.stat().st_size
            total_to_delete += 1
            if apply:
                try:
                    p.unlink()
                    print(f"      ❌ DELETED v{v_str}: {p.name} ({size_kb:.1f} KB)")
                except Exception as e:
                    print(f"      ⚠ ERROR deleting {p.name}: {e}")
            else:
                print(f"      [Candidate] v{v_str}: {p.name} ({size_kb:.1f} KB)")

    print("\n" + "=" * 70)
    print(f"Summary: {total_to_delete} obsolete files flagged.")
    print(f"Potential Storage Saved: {total_bytes_saved / 1024:.1f} KB ({total_bytes_saved / (1024*1024):.2f} MB)")
    if apply:
        print("Status: All obsolete files successfully DELETED.")
    else:
        print("Status: DRY RUN ONLY. Run with --apply to execute deletion.")

def main():
    parser = argparse.ArgumentParser(description="Prune obsolete document versions keeping only the latest N versions.")
    parser.add_argument("--dir", "-d", required=True, help="Directory to scan")
    parser.add_argument("--keep", "-k", type=int, default=2, help="Number of latest versions to keep (default: 2)")
    parser.add_argument("--apply", action="store_true", help="Apply deletion (default is dry-run)")

    args = parser.parse_args()
    scan_and_prune(args.dir, keep_count=args.keep, apply=args.apply)

if __name__ == "__main__":
    main()
