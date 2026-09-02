"""走通骨架 CLI:给一个 bug 描述 → 打印最可疑的代码位置。

指哪打哪(命令行参数):
  uv run python scripts/triage_skeleton.py --repo ~/some/ios-repo --bug "下拉刷新崩溃"
  可选:--k 5(返回几个)  --reindex(强制重建索引)
前提:.env 里有 SILICONFLOW_API_KEY。
"""

import argparse
import hashlib
import os

import chromadb

from codesentry.chunking.registry import get_chunker
from codesentry.chunking.walk import walk_repo
from codesentry.config import REPO_PATH
from codesentry.retrieval.embed import embed
from codesentry.retrieval.locate import build_index, locate


def collection_name_for(repo: str) -> str:
    """每个 repo 一个独立 collection 名字(拿绝对路径算哈希),切库不会复用错索引。"""
    h = hashlib.sha1(os.path.abspath(repo).encode()).hexdigest()[:16]
    return f"repo_{h}"


def main():
    # ── 命令行参数解析 ──
    parser = argparse.ArgumentParser(description="CodeSentry 骨架:bug → 可疑代码定位")
    parser.add_argument("--repo", default=REPO_PATH, help="要分析的代码库路径")
    parser.add_argument("--bug", required=True, help="bug 描述(必填)")
    parser.add_argument("--k", type=int, default=5, help="返回前几个可疑块(默认 5)")
    parser.add_argument("--reindex", action="store_true", help="强制重建索引")
    args = parser.parse_args()

    # ① 遍历 → 切块
    chunks = []
    for path, content in walk_repo(args.repo):
        chunks.extend(get_chunker(path).chunk(content, path))
    print(f"📂 {args.repo}:切出 {len(chunks)} 块代码")

    # ② 建/取【这个 repo 专属】的索引
    client = chromadb.PersistentClient(path="chroma_db")
    name = collection_name_for(args.repo)
    if args.reindex:
        try:
            client.delete_collection(name)
        except Exception:
            pass  # 本来就没有,忽略
    col = client.get_or_create_collection(name, metadata={"hnsw:space": "cosine"})
    if col.count() == 0:
        print("🔧 建索引中(每块 embed,联网,大 repo 要等)...")
        build_index(chunks, embed, col)
    else:
        print(f"♻️  复用该 repo 已有索引({col.count()} 块);加 --reindex 强制重建")

    # ③ 定位
    print(f"\n🔎 bug:{args.bug}\n")
    for h in locate(args.bug, col, embed, args.k):
        print(f"  {h['path']}:{h['start_line']}  {h['symbol']}  (距离 {h['distance']:.3f})")


if __name__ == "__main__":
    main()
