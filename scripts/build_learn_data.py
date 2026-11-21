#!/usr/bin/env python3
"""从中文语料统计词级 bigram，生成 liu_user_predict.txt

输出格式：上文\t接续\t次数\t时间戳（与 liu_user_predict.lua 的存储格式一致）
只保留 1-4 字的纯汉字词，避免把标点、数字、英文记进去。
"""
import argparse
import os
import re
import sys
import time
from collections import Counter, defaultdict

import jieba

CJK_RE = re.compile(r"^[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]{1,4}$")
MAX_DOC_CHARS = 2000


def iter_docs(limit):
    """流式读取中文维基语料，不落盘。"""
    from datasets import load_dataset

    ds = load_dataset(
        "pleisto/wikipedia-cn-20230720-filtered",
        split="train",
        streaming=True,
    )
    n = 0
    for row in ds:
        if n >= limit:
            break
        n += 1
        text = row.get("completion") or row.get("text") or ""
        if not text:
            continue
        yield text[:MAX_DOC_CHARS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-docs", type=int, default=80000)
    ap.add_argument("--min-pair", type=int, default=3)
    ap.add_argument("--top-prev", type=int, default=15000)
    ap.add_argument("--per-key", type=int, default=8)
    ap.add_argument("--out", default="out/liu_user_predict.txt")
    args = ap.parse_args()

    stats = defaultdict(Counter)
    docs = 0
    started = time.time()

    for text in iter_docs(args.max_docs):
        docs += 1
        toks = [w for w in jieba.lcut(text) if CJK_RE.match(w)]
        for a, b in zip(toks, toks[1:]):
            stats[a][b] += 1
        if docs % 10000 == 0:
            elapsed = time.time() - started
            print(
                f"docs={docs} keys={len(stats)} elapsed={elapsed:.0f}s",
                flush=True,
            )

    print(f"done parsing: docs={docs} keys={len(stats)}", flush=True)

    rows = []
    dropped = 0
    for prev, cnt in stats.items():
        items = [(w, c) for w, c in cnt.items() if c >= args.min_pair]
        if not items:
            dropped += 1
            continue
        items.sort(key=lambda x: (-x[1], x[0]))
        rows.append((sum(c for _, c in items), prev, items[: args.per_key]))

    rows.sort(key=lambda x: (-x[0], x[1]))
    kept = rows[: args.top_prev]

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    now_ms = int(time.time() * 1000)
    pairs = 0
    with open(args.out, "w", encoding="utf-8") as f:
        for _total, prev, items in kept:
            for w, c in items:
                f.write(f"{prev}\t{w}\t{c}\t{now_ms}\n")
                pairs += 1

    print(
        f"wrote pairs={pairs} keys={len(kept)} dropped_keys={dropped} -> {args.out}",
        flush=True,
    )
    print(f"file size: {os.path.getsize(args.out)} bytes", flush=True)


if __name__ == "__main__":
    sys.exit(main())
