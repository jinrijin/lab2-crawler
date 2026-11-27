# -*- coding: utf-8 -*-
"""查看 output 目录下的 CSV 文件（按显示宽度对齐，方便在终端里核对抓取结果）

用法：python show_csv.py [school.csv|news.csv] [显示条数]
"""
import csv
import os
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
NAME = sys.argv[1] if len(sys.argv) > 1 else "school.csv"
SHOW = int(sys.argv[2]) if len(sys.argv) > 2 else 10
PATH = os.path.join(BASE, "output", NAME)


def width(s):
    """按显示宽度计算（中文占 2 个字符位）"""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in str(s))


def pad(s, w, align="left"):
    space = max(0, w - width(s))
    return (" " * space + s) if align == "right" else (s + " " * space)


with open(PATH, encoding="utf-8-sig") as f:
    rows = list(csv.reader(f))

header, data = rows[0], rows[1:]
ncol = len(header)
widths = [max(width(r[i]) for r in rows if len(r) > i) for i in range(ncol)]
has_no = (header[0] == "序号")

print(f"文件：output\\{NAME}")
print(f"共 {len(data)} 条记录，下面显示前 {SHOW} 条：\n")

line = "  ".join(([] if has_no else [pad("序号", 4)]) +
                 [pad(h, widths[i]) for i, h in enumerate(header)])
print(line)
print("-" * width(line))
for idx, r in enumerate(data[:SHOW], 1):
    cells = []
    if not has_no:
        cells.append(pad(str(idx), 4, "right"))
    for i in range(ncol):
        val = str(r[i])
        numeric = val.replace(".", "").isdigit()
        cells.append(pad(val, widths[i], "right" if numeric else "left"))
    print("  ".join(cells))
