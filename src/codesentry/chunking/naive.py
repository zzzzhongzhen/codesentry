"""NaiveChunker:基线切块器——按"顶层符号"(func/class/struct...)粗切。

刻意简单:先跑通全链路,后面再上 SwiftChunker(AST)。
呼应你 23/40 号的 chunk_text,但这次按【代码结构】切,不是按 markdown 标题。
"""

import re

from codesentry.chunking.base import CodeChunk

# 真·样板(给你):匹配"顶层符号声明行",抓出 kind(func/class/...)和 symbol(名字)
# 例:  "func greet(name: String) -> String {"  →  kind="func", name="greet"
_SYMBOL_RE = re.compile(r"^\s*(func|class|struct|enum|extension|protocol)\s+(\w+)")


class NaiveChunker:
    def chunk(self, source: str, path: str) -> list[CodeChunk]:
        """把源码按顶层符号切成若干 CodeChunk。"""
        # ══════════════════════════════════════════════════════
        # 该你写:核心算法
        #   1) 把 source 按 "\n" 切成行:lines = source.split("\n")
        #   2) 找出所有"符号行"的下标:遍历 lines,用 _SYMBOL_RE.match(line) 命中的记下
        #        (行号从 1 起;下标 i 对应行号 i+1)
        #   3) 每个符号行 = 一块的开头,这块一直延伸到【下一个符号行之前】(或文件末尾)
        #   4) 每块造一个 CodeChunk:
        #        path=path, start_line, end_line(1 起),
        #        symbol=名字(match.group(2)), kind=类型(match.group(1)),
        #        parent=None, code="\n".join(这块的行), language="swift"
        #   5) 兜底:如果一个符号都没找到 → 整个文件当一块
        #        (symbol="", kind="file", start_line=1, end_line=len(lines))
        #   返回:list[CodeChunk]
        # ══════════════════════════════════════════════════════
        lines = source.split('\n')
        symbols = [(i, m) for i, line in enumerate(lines, start=1) if (m :=_SYMBOL_RE.match(line))]
        if not symbols: #如果一个符号都没找到
            return [CodeChunk(path, 1, len(lines), '', 'file', None, source, 'swift')]

        code_chunks = []
        for j, (lineno, match) in enumerate(symbols):
            start_line = lineno
            end_line = symbols[j+1][0]-1 if j+1<len(symbols) else len(lines)-1
            code = '\n'.join(lines[start_line-1:end_line])
            code_chunks.append(CodeChunk(path, start_line, end_line, match.group(2), match.group(1), None, code, 'swift'))
        return code_chunks
            
        