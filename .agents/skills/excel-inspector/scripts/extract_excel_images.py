# -*- coding: utf-8 -*-
"""
Zero-Dependency Excel (.xlsx) Image & Diagram Extractor
Mengekstrak gambar dan screenshot yang ditempel di lembar kerja Excel secara berurutan
berdasarkan koordinat baris (row) pada DrawingML OpenXML.

Penggunaan CLI:
    python extract_excel_images.py --file <path_to_excel.xlsx> [--output <output_dir>] [--prefix <img_prefix>]

Dependensi: 100% Python Standard Library (zipfile, xml.etree.ElementTree, shutil, argparse).
"""

import sys
import os
import zipfile
import shutil
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


NAMESPACES = {
    'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}


def extract_images_from_xlsx(excel_path: str, output_dir: str = None, prefix: str = "img") -> list:
    """
    Mengekstrak seluruh gambar embedded dari berkas .xlsx dan mengurutkannya
    berdasarkan posisi baris (top-to-bottom).
    """
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"File tidak ditemukan: {excel_path}")

    excel_file = Path(excel_path)
    if output_dir is None:
        output_dir = excel_file.parent / f"{excel_file.stem}_assets"

    os.makedirs(output_dir, exist_ok=True)
    extracted_files = []

    with zipfile.ZipFile(excel_path, 'r') as z:
        # Cari seluruh drawing XML
        drawing_files = [n for n in z.namelist() if n.startswith('xl/drawings/drawing') and n.endswith('.xml')]
        
        items = []
        for d in drawing_files:
            rels_path = d.replace('drawings/', 'drawings/_rels/') + '.rels'
            if rels_path not in z.namelist():
                continue

            root = ET.fromstring(z.read(d))
            rels_root = ET.fromstring(z.read(rels_path))
            rid_map = {r.get('Id'): r.get('Target') for r in rels_root}

            for anc in root:
                # Periksa anchor (oneCellAnchor / twoCellAnchor)
                fr = anc.find('xdr:from', NAMESPACES)
                blip = anc.find('.//a:blip', NAMESPACES)
                if fr is None or blip is None:
                    continue

                row_el = fr.find('xdr:row', NAMESPACES)
                col_el = fr.find('xdr:col', NAMESPACES)
                row = int(row_el.text) if row_el is not None and row_el.text else 0
                col = int(col_el.text) if col_el is not None and col_el.text else 0

                embed_id = blip.get(f"{{{NAMESPACES['r']}}}embed")
                if embed_id in rid_map:
                    target = rid_map[embed_id].replace('../', 'xl/')
                    items.append((row, col, target))

        # Sort berdasarkan baris lalu kolom
        items.sort(key=lambda x: (x[0], x[1]))

        for n, (row, col, tgt) in enumerate(items, 1):
            ext = os.path.splitext(tgt)[1].lower() or '.png'
            out_filename = f"{prefix}{n:02d}{ext}"
            out_filepath = os.path.join(output_dir, out_filename)

            try:
                with z.open(tgt) as src, open(out_filepath, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                extracted_files.append({
                    "index": n,
                    "filename": out_filename,
                    "path": str(out_filepath),
                    "row": row + 1,
                    "col": col + 1,
                    "source_archive": tgt
                })
                print(f"[OK] {out_filename} (Baris {row + 1}, Kolom {col + 1}) -> {out_filepath}")
            except KeyError:
                print(f"[WARN] Target media tidak ditemukan di arsip zip: {tgt}")

    return extracted_files


def main():
    parser = argparse.ArgumentParser(description="Zero-dependency Excel (.xlsx) Image & Diagram Extractor")
    parser.add_argument("--file", "-f", required=True, help="Path ke berkas .xlsx")
    parser.add_argument("--output", "-o", help="Folder tujuan penyimpanan gambar (default: <file>_assets/)")
    parser.add_argument("--prefix", "-p", default="img", help="Prefix nama file gambar (default: 'img')")

    args = parser.parse_args()
    results = extract_images_from_xlsx(args.file, args.output, args.prefix)
    print(f"\nSelesai: {len(results)} gambar berhasil diekstrak.")


if __name__ == "__main__":
    main()
