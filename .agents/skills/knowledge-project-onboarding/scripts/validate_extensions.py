#!/usr/bin/env python3
"""
validate_extensions.py - Zero-Dependency Fast OOXML File Extension Integrity Scanner & Fixer.
Part of Knowledge Project Onboarding SOP (Second Brain Architecture).
Uses Python Standard Library ONLY (zipfile, pathlib, argparse, time).

Performs ultra-fast (<2ms/file) OOXML package inspection via:
1. Magic Bytes Check (PK\x03\x04)
2. ZIP Central Directory Entry Check
3. Authoritative [Content_Types].xml MIME Schema verification:
   - wordprocessingml -> .docx
   - spreadsheetml    -> .xlsx
   - presentationml   -> .pptx
"""

import os
import sys
import time
import zipfile
import argparse
from pathlib import Path

# Force UTF-8 on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Target formats supported
OOXML_EXTENSIONS = {'.docx', '.xlsx', '.pptx'}

# Magic byte signatures
ZIP_MAGIC = b'PK\x03\x04'
OLE2_MAGIC = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'  # Legacy MS Office 97-2003 (.doc, .xls, .ppt)

def inspect_ooxml_file(file_path):
    """
    Inspects a single file to determine its true OOXML type based on XML schema.
    Returns:
        dict: {
            'path': Path,
            'current_ext': str,
            'detected_type': str or None ('docx', 'xlsx', 'pptx', 'legacy_office', 'not_ooxml', 'corrupt'),
            'recommended_ext': str or None,
            'is_match': bool,
            'schema_evidence': str,
            'duration_ms': float,
            'error': str or None
        }
    """
    t0 = time.perf_counter()
    p = Path(file_path).resolve()
    current_ext = p.suffix.lower()

    result = {
        'path': p,
        'current_ext': current_ext,
        'detected_type': None,
        'recommended_ext': None,
        'is_match': True,
        'schema_evidence': '',
        'duration_ms': 0.0,
        'error': None
    }

    if not p.is_file():
        result['error'] = 'File not found'
        result['duration_ms'] = (time.perf_counter() - t0) * 1000
        return result

    # 1. Magic Bytes Filter (<0.01ms)
    try:
        with open(p, 'rb') as f:
            header = f.read(8)
    except Exception as e:
        result['error'] = f'Cannot read header: {e}'
        result['duration_ms'] = (time.perf_counter() - t0) * 1000
        return result

    if header[:4] != ZIP_MAGIC:
        if header[:8] == OLE2_MAGIC:
            result['detected_type'] = 'legacy_office'
            result['schema_evidence'] = 'OLE2 Compound Document (MS Office 97-2003 binary format)'
            result['is_match'] = False
            result['recommended_ext'] = '.doc' if current_ext == '.docx' else ('.xls' if current_ext == '.xlsx' else '.ppt')
        else:
            result['detected_type'] = 'not_ooxml'
            result['schema_evidence'] = f'Header bytes: {header[:4].hex()}'
            result['is_match'] = False
        result['duration_ms'] = (time.perf_counter() - t0) * 1000
        return result

    # 2 & 3. Zip Inspection & [Content_Types].xml Schema Check (<1ms)
    try:
        with zipfile.ZipFile(p, 'r') as z:
            namelist = set(z.namelist())
            
            # Read authoritative [Content_Types].xml
            if '[Content_Types].xml' not in namelist:
                result['detected_type'] = 'corrupt'
                result['error'] = 'Valid ZIP but missing [Content_Types].xml (Non-OOXML package)'
                result['is_match'] = False
                result['duration_ms'] = (time.perf_counter() - t0) * 1000
                return result

            content_types_raw = z.read('[Content_Types].xml').lower()

            # Schema evaluation:
            if b'wordprocessingml' in content_types_raw or 'word/document.xml' in namelist:
                result['detected_type'] = 'docx'
                result['recommended_ext'] = '.docx'
                result['schema_evidence'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml'
            elif b'spreadsheetml' in content_types_raw or 'xl/workbook.xml' in namelist:
                result['detected_type'] = 'xlsx'
                result['recommended_ext'] = '.xlsx'
                result['schema_evidence'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml'
            elif b'presentationml' in content_types_raw or 'ppt/presentation.xml' in namelist:
                result['detected_type'] = 'pptx'
                result['recommended_ext'] = '.pptx'
                result['schema_evidence'] = 'application/vnd.openxmlformats-officedocument.presentationml'
            else:
                result['detected_type'] = 'unknown_ooxml'
                result['schema_evidence'] = 'Unrecognized OOXML schema part'
                result['is_match'] = False

    except zipfile.BadZipFile:
        result['detected_type'] = 'corrupt'
        result['error'] = 'Corrupted ZIP archive'
        result['is_match'] = False
    except Exception as e:
        result['detected_type'] = 'error'
        result['error'] = str(e)
        result['is_match'] = False

    # Check match with current extension
    if result['recommended_ext']:
        result['is_match'] = (current_ext == result['recommended_ext'])

    result['duration_ms'] = (time.perf_counter() - t0) * 1000
    return result

def scan_directory(target_dir, recursive=True, apply_fix=False):
    """
    Scans a directory for OOXML files, checks for extension mismatches,
    and optionally renames mismatched files.
    """
    root = Path(target_dir).resolve()
    if not root.exists():
        print(f"❌ Error: Target path '{target_dir}' does not exist.")
        return 1

    files_to_check = []
    if root.is_file():
        files_to_check.append(root)
    else:
        glob_func = root.rglob if recursive else root.glob
        for p in glob_func('*'):
            if p.is_file() and p.suffix.lower() in OOXML_EXTENSIONS:
                files_to_check.append(p)

    total_scanned = len(files_to_check)
    print("=" * 80)
    print(f"🔍 OOXML Extension Integrity Scanner")
    print(f"📁 Target Directory : {root}")
    print(f"📦 Files to inspect  : {total_scanned} files (filter: {', '.join(sorted(OOXML_EXTENSIONS))})")
    print(f"⚡ Mode              : {'AUTO-FIX (--apply)' if apply_fix else 'DRY RUN (Audit Only)'}")
    print("=" * 80)

    if total_scanned == 0:
        print("ℹ️  No OOXML files found matching target extensions.")
        return 0

    mismatches = []
    errors = []
    matches = 0
    total_time_ms = 0.0

    for file_path in files_to_check:
        res = inspect_ooxml_file(file_path)
        total_time_ms += res['duration_ms']
        rel_path = file_path.relative_to(root) if root.is_dir() else file_path.name

        if res['error']:
            errors.append(res)
            print(f"⚠️  [ERROR] {rel_path} -> {res['error']} ({res['duration_ms']:.2f}ms)")
        elif not res['is_match']:
            mismatches.append(res)
            print(f"🔴 [MISMATCH] {rel_path}")
            print(f"   ├─ Nama Saat Ini : {res['current_ext']}")
            print(f"   ├─ Skema Asli    : {res['detected_type'].upper()} ({res['schema_evidence']})")
            print(f"   └─ Rekomendasi   : Rename ke {res['recommended_ext']} ({res['duration_ms']:.2f}ms)")
        else:
            matches += 1

    avg_speed = total_time_ms / total_scanned if total_scanned > 0 else 0

    print("\n" + "=" * 80)
    print("📊 RINGKASAN AUDIT INTEGRITAS EKSTENSI")
    print("=" * 80)
    print(f"Total File Diperiksa  : {total_scanned}")
    print(f"🟢 Sesuai (Valid)     : {matches}")
    print(f"🔴 Salah Ekstensi     : {len(mismatches)}")
    print(f"⚠️  Error / Korup     : {len(errors)}")
    print(f"⏱️  Total Durasi Scan : {total_time_ms:.2f} ms (Rata-rata: {avg_speed:.2f} ms/file)")
    print("=" * 80)

    # Auto-Fix Execution
    if mismatches and apply_fix:
        print("\n🔧 MENJALANKAN AUTO-FIX RENAMING:")
        for item in mismatches:
            p = item['path']
            rec_ext = item['recommended_ext']
            if not rec_ext:
                print(f"   ⚠️  Dilewati (Tidak ada rekomendasi ekstensi valid): {p.name}")
                continue
            
            new_path = p.with_suffix(rec_ext)
            if new_path.exists():
                print(f"   ⚠️  Gagal Rename: Target file '{new_path.name}' sudah ada!")
                continue

            try:
                p.rename(new_path)
                print(f"   ✔ Berhasil di-rename: {p.name} ➔ {new_path.name}")
            except Exception as e:
                print(f"   ❌ Gagal rename {p.name}: {e}")
        print("\n✔ Auto-fix selesai.")
    elif mismatches and not apply_fix:
        print("\n💡 Petunjuk: Jalankan dengan argumen '--apply' untuk memperbaiki ekstensi yang salah secara otomatis.")

    return 1 if mismatches or errors else 0

def main():
    parser = argparse.ArgumentParser(
        description="Fast OOXML File Extension Integrity Scanner (<2ms/file) using XML Schema validation."
    )
    parser.add_argument(
        "--dir", "-d",
        type=str,
        default=".",
        help="Target folder to scan (default: current directory)."
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        default=None,
        help="Single file to inspect."
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Disable recursive subfolder scan."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply auto-rename fix to mismatched files."
    )

    args = parser.parse_args()

    target = args.file if args.file else args.dir
    return scan_directory(target, recursive=not args.no_recursive, apply_fix=args.apply)

if __name__ == "__main__":
    sys.exit(main())
