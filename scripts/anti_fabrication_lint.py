#!/usr/bin/env python3
"""反编造 lint —— initial-coverage-advanced skill 的交付前阻断门。

只兜机械可检的编造痕迹，命中即非零退出，逐条要求清除。
诚实声明：catch 不住"看起来合理的错数"（如 MAU 写错、目标价过时），
那一类只能靠异源验证和 _data 底稿核对，不是这个脚本的职责。

用法：
    python anti_fabrication_lint.py <路径> [<路径> ...]
    路径可以是图表构建脚本(.py)、_data 底稿、各阶段稿件(.md)、目录。
    传目录则递归扫其中的 .py / .md / .csv / .json / _data 文件。

退出码：有命中 = 1，干净 = 0。
"""

import os
import re
import sys

# 1) 合成数据迹象：图表构建代码里出现这些，基本就是在凑点
SYNTH_PATTERNS = [
    (r"\bnp\.interp\b", "np.interp 插值——缺数不许插值补点，留空或只画已知值"),
    (r"\bnp\.random\b", "np.random 随机——不许给数据加噪声/造点"),
    (r"\brandom\.(uniform|gauss|normal|randint|random)\b", "random 造数——不许合成数据点"),
    (r"噪声|加噪|jitter\b", "噪声/jitter——不许给真实序列叠造噪声"),
    (r"\bnp\.linspace\b.*#.*(股价|价格|指数|收盘)", "linspace 拼价格序列——价格必须用真实日频收盘"),
]

# 2) 把编造合法化的免责标签，贴在数据系列/数值上
DISCLAIMER_PATTERNS = [
    (r"示意(?!图标题)", "“示意”——不得用于标注不存在的数据，缺数就留空或标“未获取”"),
    (r"approx|placeholder|dummy|fake|mock", "approx/placeholder 等——疑似占位/编造数据"),
    (r"假设值|估计值|凑数|大致(?:画|给)|随便给", "假设值/凑数——图表数值必须有来源，不许估着填"),
]

# 3) 缺一手结算源的迹象：声称是现价/收盘，但没有日 K 原始序列落盘
PRICE_WORDS = re.compile(r"现价|收盘价|最新价|股价图|指数线|日\s*K|日频")
RAW_SERIES_HINT = re.compile(r"_data|日K|daily|close.*csv|push2his|序列.*csv|\.csv")

# 4) 用涨幅反推收盘的迹象（应当反过来：close 来自结算源，涨幅是核出来的）
REVERSE_DERIVE = re.compile(
    r"close\s*=\s*[\w.]+\s*\*\s*\(\s*1\s*\+|收盘\s*=\s*[\w.]+\s*[×*]\s*\(\s*1\s*[+＋]"
)

SCAN_EXTS = (".py", ".md", ".csv", ".json", ".txt")


def iter_files(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in files:
                    if f.endswith(SCAN_EXTS):
                        yield os.path.join(root, f)
        elif os.path.isfile(p):
            yield p
        else:
            print(f"[warn] 路径不存在，跳过：{p}", file=sys.stderr)


def scan_file(path):
    hits = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError as e:
        print(f"[warn] 读不了 {path}: {e}", file=sys.stderr)
        return hits

    is_code = path.endswith(".py")
    text = "".join(lines)

    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("#"):
            continue  # 注释行（含“正当插值已说明”的澄清）不算
        for pat, msg in SYNTH_PATTERNS:
            if is_code and re.search(pat, line):
                hits.append((i, "合成", msg, line.strip()))
        for pat, msg in DISCLAIMER_PATTERNS:
            if re.search(pat, line):
                hits.append((i, "免责标签", msg, line.strip()))
        if REVERSE_DERIVE.search(line):
            hits.append((i, "反推", "疑似用涨幅反推收盘——收盘必须取结算源本身", line.strip()))

    # 文件级：提了价格/收盘，却全文没有日 K 原始序列的迹象
    if PRICE_WORDS.search(text) and not RAW_SERIES_HINT.search(text):
        hits.append((0, "缺一手源", "提到现价/收盘/股价图，但没看到日 K 原始序列落盘的迹象", ""))

    return hits


def main(argv):
    paths = argv[1:]
    if not paths:
        print(__doc__)
        return 2

    total = 0
    for path in iter_files(paths):
        hits = scan_file(path)
        if not hits:
            continue
        total += len(hits)
        print(f"\n● {path}")
        for lineno, kind, msg, snippet in hits:
            loc = f"L{lineno}" if lineno else "(全文)"
            print(f"  [{kind}] {loc}  {msg}")
            if snippet:
                print(f"      > {snippet}")

    print("\n" + "=" * 60)
    if total:
        print(f"反编造 lint 命中 {total} 处。逐条清除——要么指到 _data 底稿的真实来源，")
        print("要么删掉该数据/系列；正当插值（如真日 K 重采样）在该行加注释说明即可。")
        print("清不掉不交付。")
        return 1
    print("反编造 lint 通过：未发现机械可检的编造痕迹。")
    print("注意：这不证明数字都对——看起来合理的错数靠异源验证和 _data 底稿核对。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
