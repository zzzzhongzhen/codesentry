from codesentry.chunking.base import CodeChunk


def test_codechunk_holds_location_and_symbol():
    c = CodeChunk(
        path="A.swift",
        start_line=10,
        end_line=20,
        symbol="foo()",
        kind="function",
        parent=None,
        code="func foo() {}",
        language="swift",
    )
    assert c.path == "A.swift" and c.start_line == 10
    assert c.symbol == "foo()"
    assert c.parent is None
