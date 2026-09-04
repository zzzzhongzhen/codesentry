from codesentry.chunking.naive import NaiveChunker
from codesentry.chunking.registry import get_chunker
from codesentry.chunking.swift import SwiftChunker


def test_swift_uses_swift_chunker():
    assert isinstance(get_chunker("Foo.swift"), SwiftChunker)
    assert isinstance(get_chunker("path/to/View.swift"), SwiftChunker)


def test_other_extensions_fall_back_to_naive():
    assert isinstance(get_chunker("bar.unknown"), NaiveChunker)
    assert isinstance(get_chunker("no_extension"), NaiveChunker)
