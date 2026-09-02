import uuid

import chromadb

from codesentry.chunking.base import CodeChunk
from codesentry.retrieval.locate import build_index, locate


def _fake_embed(text: str) -> list[float]:
    # 含 "refresh" 的偏向量 A,否则偏向量 B —— 让检索能区分开
    return [1.0, 0.0] if "refresh" in text.lower() else [0.0, 1.0]


def _new_collection():
    return chromadb.EphemeralClient().create_collection(
        f"test_{uuid.uuid4().hex}", metadata={"hnsw:space": "cosine"}
    )


def test_locate_ranks_relevant_first():
    col = _new_collection()
    chunks = [
        CodeChunk("Refresh.swift", 10, 20, "refresh()", "func", None, "func refresh(){}", "swift"),
        CodeChunk("Other.swift", 1, 5, "other()", "func", None, "func other(){}", "swift"),
    ]
    build_index(chunks, _fake_embed, col)

    hits = locate("下拉 refresh 偶发崩溃", col, _fake_embed, k=2)
    assert hits[0]["path"] == "Refresh.swift"        # 最相关的排第一
    assert hits[0]["start_line"] == 10               # 带回了定位信息
    assert "refresh" in hits[0]["code"]              # 带回了代码
    assert "distance" in hits[0]                     # 带回了距离
