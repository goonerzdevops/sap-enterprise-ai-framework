#!/usr/bin/env python3
"""
Zero-Dependency Knowledge Base Folder Auditor & Index Generator
Part of skill: knowledge-file-curator
"""

import os
import sys
import argparse
import re
from pathlib import Path

def audit_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.splitlines()
    line_count = len(lines)
    
    has_frontmatter = content.startswith('---') and '---' in content[3:]
    has_toc = bool(re.search(r'#+\s*(?:📌\s*)?(?:daftar\s+isi|table\s+of\s+contents)', content, re.IGNORECASE))
    
    # Classify line count
    if line_count < 100:
        status = "UNDERSIZED (<100)"
    elif 150 <= line_count <= 450:
        status = "IDEAL (150-450)"
    elif line_count > 600:
        status = "OVERSIZED (>600)"
    else:
        status = "ACCEPTABLE"
        
    return {
        "filename": os.path.basename(filepath),
        "lines": line_count,
        "status": status,
        "frontmatter": has_frontmatter,
        "toc": has_toc
    }

def main():
    parser = argparse.ArgumentParser(description="Audit and curate knowledge base folders.")
    parser.add_argument("--dir", required=True, help="Target directory to audit")
    parser.add_argument("--generate-index", action="store_true", help="Generate draft 00_FOLDER_INDEX.md")
    args = parser.parse_args()
    
    target_dir = Path(args.dir)
    if not target_dir.is_dir():
        print(f"Error: {target_dir} is not a valid directory.")
        sys.exit(1)
        
    md_files = sorted([f for f in target_dir.iterdir() if f.is_file() and f.suffix.lower() == '.md'])
    
    print(f"\n=======================================================")
    print(f" KNOWLEDGE BASE AUDIT REPORT: {target_dir.name}")
    print(f"=======================================================")
    print(f"{'Filename':40} | {'Lines':>6} | {'Status':>16} | {'YAML':>5} | {'TOC':>5}")
    print("-" * 82)
    
    for f in md_files:
        res = audit_file(f)
        yaml_str = "YES" if res["frontmatter"] else "NO"
        toc_str = "YES" if res["toc"] else "NO"
        print(f"{res['filename']:40} | {res['lines']:6d} | {res['status']:>16} | {yaml_str:>5} | {toc_str:>5}")
    print("-" * 82)

if __name__ == "__main__":
    main()
