#!/usr/bin/env python3
"""把 liu_user_predict 的 TSV 转成 build_predict 的输入格式。

输入：上文\t接续\t次数\t时间戳
输出：上文 接续 权重（空白分隔，每行一个候选）

build_predict 用 std::cin >> 逐个 token 读取，所以任何字段都不能含空白。
"""
import sys

src = sys.argv[1] if len(sys.argv) > 1 else "out/liu_user_predict.txt"

dropped = 0
written = 0
with open(src, encoding="utf-8") as f, open("out/predict_input.txt", "w", encoding="utf-8") as out:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 3:
            dropped += 1
            continue
        prev, word, count = parts[0], parts[1], parts[2]
        if not prev or not word or any(c.isspace() for c in prev + word):
            dropped += 1
            continue
        try:
            w = float(count)
        except ValueError:
            dropped += 1
            continue
        out.write(f"{prev} {word} {w:g}\n")
        written += 1

print(f"written={written} dropped={dropped}")
