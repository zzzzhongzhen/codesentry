from pathlib import Path

from codesentry.chunking.naive import NaiveChunker


def test_naive_splits_by_top_level_symbols():
    src = Path("tests/fixtures/Sample.swift").read_text(encoding="utf-8")
    chunks = NaiveChunker().chunk(src, "Sample.swift")

    assert len(chunks) >= 2                                    # 至少切出几块
    assert all(c.path == "Sample.swift" for c in chunks)      # path 都对
    assert all(c.start_line >= 1 for c in chunks)             # 行号从 1 起
    assert all(c.end_line >= c.start_line for c in chunks)    # 结束 >= 开始


def test_chunk_captures_the_whole_function_body():
    # 抓 Bug A:每块必须包含【函数体】,不只是声明行
    src = Path("tests/fixtures/Sample.swift").read_text(encoding="utf-8")
    chunks = NaiveChunker().chunk(src, "Sample.swift")

    greet = next(c for c in chunks if c.symbol == "greet")
    assert greet.kind == "func"
    assert "Hello" in greet.code                              # 函数体进来了吗
    assert greet.end_line > greet.start_line                  # 不止一行
    assert greet.start_line == 3                              # greet 真实在第 3 行(1 基,别 off-by-one)
    assert greet.end_line == 6                                # 到下一个符号行之前(第 7 行是 func add)


def test_fallback_when_no_symbols():
    # 抓 Bug B:没有顶层符号时,整文件当一块(不是返回空)
    chunks = NaiveChunker().chunk("let x = 1\nlet y = 2", "Consts.swift")
    assert len(chunks) == 1
    assert chunks[0].kind == "file"


def test_naive_handles_empty_source():
    chunks = NaiveChunker().chunk("", "Empty.swift")
    assert isinstance(chunks, list)
