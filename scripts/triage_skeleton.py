"""走通骨架 CLI:给一个 bug 描述 → 打印最可疑的代码位置。

运行:uv run python scripts/triage_skeleton.py
前提:.env 里要有 SILICONFLOW_API_KEY(embed 用);REPO_PATH 默认指向 tests/fixtures/repo。
把 7 个模块串起来:walk_repo → get_chunker.chunk → build_index → locate。
"""

import chromadb

from codesentry.chunking.registry import get_chunker
from codesentry.chunking.walk import walk_repo
from codesentry.config import REPO_PATH
from codesentry.retrieval.embed import embed
from codesentry.retrieval.locate import build_index, locate

# 骨架期:硬编码一个 bug 描述(以后从 ClickUp 拉)
BUG = "下拉刷新时偶发崩溃"


def main():
    # ① 遍历 repo → 切块(walk_repo 拉一个,get_chunker 挑切块器,chunk 切)
    chunks = []
    for path, content in walk_repo(REPO_PATH):
        chunks.extend(get_chunker(path).chunk(content, path))
    print(f"📂 {REPO_PATH}:切出 {len(chunks)} 块代码")

    # ② 建/取索引(持久化到 chroma_db/,已 gitignore)
    col = chromadb.PersistentClient(path="chroma_db").get_or_create_collection(
        "codesentry", metadata={"hnsw:space": "cosine"}
    )
    if col.count() == 0:
        print("🔧 建索引中(每块 embed,联网,大 repo 要等)...")
        build_index(chunks, embed, col)
    else:
        print(f"♻️  复用已有索引({col.count()} 块);想重建就删掉 chroma_db/ 再跑")

    # ③ 定位:按 bug 查最可疑的 5 块
    print(f"\n🔎 bug:{BUG}\n")
    hits = locate(BUG, col, embed, k=5)
    for h in hits:
        print(f"  {h['path']}:{h['start_line']}  {h['symbol']}  (距离 {h['distance']:.3f})")


if __name__ == "__main__":
    main()
