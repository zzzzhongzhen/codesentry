"""切块器注册表:按文件后缀分发到对应 chunker。

依赖方向:registry → base + naive(站在两者上面),避免 base 反向依赖具体实现造成循环导入。
加语言 = 往 _REGISTRY 塞一个,下游一个字不改(可插拔的落点)。
"""

from pathlib import Path

from codesentry.chunking.base import CodeChunker
from codesentry.chunking.naive import NaiveChunker

# 骨架期:还没有 SwiftChunker,注册表先空着,全部回退 NaiveChunker。
# SwiftChunker 实现后,这里加一行:".swift": SwiftChunker()
_REGISTRY: dict[str, CodeChunker] = {}
_FALLBACK: CodeChunker = NaiveChunker()


def get_chunker(path: str) -> CodeChunker:
    """按文件后缀返回对应的 chunker;没匹配到就回退 NaiveChunker。"""
    # ══════════════════════════════════════════════════════
    # 该你写:
    #   1) 取后缀:Path(path).suffix  → 如 "Foo.swift" 得 ".swift"
    #   2) 从 _REGISTRY 按后缀取;取不到就返回 _FALLBACK
    #   提示:dict 的 .get(key, 默认值) 一行搞定(呼应你 14 号 TOOL_FUNCTIONS 分发)
    # ══════════════════════════════════════════════════════
    suffix = Path(path).suffix
    return _REGISTRY.get(suffix, _FALLBACK)