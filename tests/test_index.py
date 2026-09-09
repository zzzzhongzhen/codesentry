import uuid

import chromadb

from codesentry.chunking.base import CodeChunk
from codesentry.retrieval.locate import build_index


def _fake_embed(text: str) -> list[float]:
    # 假 embedder:确定性、不联网。真向量维度无所谓,能存进去就行。
    return [float(len(text)), 1.0, 0.0]


def _new_collection():
    # 唯一名字:EphemeralClient 是共享的,同名会"已存在"报错,每个测试用独立名字隔离
    return chromadb.EphemeralClient().create_collection(
        f"test_{uuid.uuid4().hex}", metadata={"hnsw:space": "cosine"}
    )


def test_build_index_adds_all_chunks():
    col = _new_collection()
    chunks = [
        CodeChunk("A.swift", 1, 3, "foo()", "function", None, "func foo(){}", "swift"),
        CodeChunk("B.swift", 1, 2, "bar()", "function", None, "func bar(){}", "swift"),
    ]
    build_index(chunks, _fake_embed, col)
    assert col.count() == 2


def test_build_index_handles_large_repo_over_chroma_limit():
    # 复现大 repo 崩溃:Chroma 一次 add 上限 5461,超了必须分批
    col = _new_collection()
    chunks = [
        CodeChunk(f"F{i}.swift", 1, 2, f"f{i}", "func", None, f"code{i}", "swift")
        for i in range(6000)
    ]
    build_index(chunks, _fake_embed, col)   # 不分批的话这里会崩
    assert col.count() == 6000


def test_build_index_stores_path_metadata():
    col = _new_collection()
    chunks = [CodeChunk("Login.swift", 42, 50, "submit()", "func", None, "code", "swift")]
    build_index(chunks, _fake_embed, col)
    got = col.get(include=["metadatas"])
    assert got["metadatas"][0]["path"] == "Login.swift"
    assert got["metadatas"][0]["start_line"] == 42
