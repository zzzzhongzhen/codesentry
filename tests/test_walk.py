from codesentry.chunking.walk import walk_repo


def test_walk_yields_only_swift_recursively():
    items = list(walk_repo("tests/fixtures/repo"))
    paths = {p for p, _ in items}

    assert len(items) == 2                          # 2 个 .swift(含嵌套),.md 不算
    assert all(p.endswith(".swift") for p in paths)  # 只要 swift
    assert any("B.swift" in p for p in paths)        # 嵌套子目录里的也被找到(递归)
    assert all(isinstance(src, str) and src for _, src in items)  # 内容是非空字符串


def test_walk_paths_are_relative_to_root():
    items = list(walk_repo("tests/fixtures/repo"))
    paths = {p for p, _ in items}
    # 路径相对 root,不含 root 前缀(报告里要短路径,不要绝对机器路径)
    assert "tests/fixtures/repo" not in " ".join(paths)
    assert any(p == "A.swift" for p in paths)
