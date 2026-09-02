from codesentry.chunking.registry import get_chunker
from codesentry.chunking.naive import NaiveChunker


def test_get_chunker_falls_back_to_naive():
    # 骨架期还没有 SwiftChunker,任何后缀都先回退到 NaiveChunker
    assert isinstance(get_chunker("Foo.swift"), NaiveChunker)
    assert isinstance(get_chunker("bar.unknown"), NaiveChunker)
    assert isinstance(get_chunker("no_extension"), NaiveChunker)
