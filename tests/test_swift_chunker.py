from pathlib import Path

from codesentry.chunking.swift import SwiftChunker


def test_splits_functions_with_parent_context():
    src = Path("tests/fixtures/Sample.swift").read_text(encoding="utf-8")
    chunks = SwiftChunker().chunk(src, "Sample.swift")
    by_symbol = {c.symbol: c for c in chunks}

    # 顶层函数:无 parent
    assert "greet" in by_symbol
    assert by_symbol["greet"].parent is None
    assert by_symbol["greet"].kind == "func"

    # 类里的方法:带 parent = 类名(这正是 NaiveChunker 丢掉的上下文)
    assert "addToTotal" in by_symbol
    assert by_symbol["addToTotal"].parent == "Calculator"


def test_function_boundaries_are_real():
    src = Path("tests/fixtures/Sample.swift").read_text(encoding="utf-8")
    chunks = SwiftChunker().chunk(src, "Sample.swift")
    greet = next(c for c in chunks if c.symbol == "greet")
    # 完整函数体进来了,且行号是真实边界
    assert "Hello" in greet.code
    assert greet.end_line >= greet.start_line


def test_caps_oversized_chunk():
    # 造一个超大函数,验证被截断(防 embedding 400)
    huge = "func big() {\n" + ("    print(1)\n" * 5000) + "}\n"
    chunks = SwiftChunker().chunk(huge, "Big.swift")
    assert all(len(c.code) <= 6000 for c in chunks)
