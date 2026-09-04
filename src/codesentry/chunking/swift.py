"""SwiftChunker:用 tree-sitter 按【语法树】切块。

比 NaiveChunker 强在:边界是真实的函数/类边界(不会切出半行或几万字的巨块),
且每个方法带上【所属类型名 parent】当上下文。
设计:遍历语法树,遇到函数/init 就切一块;进入 class/extension 时记下类型名传给子节点当 parent。
"""

import tree_sitter_swift as tss
from tree_sitter import Language, Parser

from codesentry.chunking.base import CodeChunk

_LANG = Language(tss.language())
_PARSER = Parser(_LANG)

# 当成"一块"产出的声明(函数/构造器 —— bug 主要住在这里)
_DECL_TYPES = {"function_declaration", "init_declaration"}
# 提供 parent 上下文的容器(class/enum/struct 在此 grammar 里都是 class_declaration)
_CONTAINER_TYPES = {
    "class_declaration",
    "struct_declaration",
    "extension_declaration",
    "protocol_declaration",
}

MAX_CHARS = 6000  # 兜底:超大函数截断,防 embedding 输入超限(你撞过的 400)


def _name_of(node, src: bytes) -> str:
    """取声明的名字:第一个 simple_identifier / type_identifier 子节点。"""
    for ch in node.children:
        if ch.type in ("simple_identifier", "type_identifier"):
            return src[ch.start_byte : ch.end_byte].decode()
    return ""


class SwiftChunker:
    def chunk(self, source: str, path: str) -> list[CodeChunk]:
        src = source.encode()
        tree = _PARSER.parse(src)
        chunks: list[CodeChunk] = []

        def visit(node, parent: str | None):
            if node.type in _DECL_TYPES:
                is_init = node.type == "init_declaration"
                name = _name_of(node, src) or ("init" if is_init else "")
                chunks.append(
                    CodeChunk(
                        path=path,
                        start_line=node.start_point[0] + 1,   # tree-sitter 行号从 0 起,+1 转 1 基
                        end_line=node.end_point[0] + 1,
                        symbol=name,
                        kind="init" if is_init else "func",
                        parent=parent,                        # 所属类型名(上下文)
                        code=src[node.start_byte : node.end_byte].decode()[:MAX_CHARS],
                        language="swift",
                    )
                )
                return  # v1 不再钻进函数体找嵌套函数(简化)

            # 进入容器类型时,更新 parent 传给子节点
            new_parent = _name_of(node, src) or parent if node.type in _CONTAINER_TYPES else parent
            for ch in node.children:
                visit(ch, new_parent)

        visit(tree.root_node, None)

        # 兜底:整个文件没有任何函数(纯声明/常量文件)→ 整文件一块(也截断)
        if not chunks:
            chunks.append(
                CodeChunk(path, 1, len(source.split("\n")), "", "file", None, source[:MAX_CHARS], "swift")
            )
        return chunks
