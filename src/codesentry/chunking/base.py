"""切块层的地基:一块代码的数据结构 + 切块器接口。

设计见 spec 第 6 节。CodeChunk 是"切出来的一块代码",CodeChunker 是"切块器"的统一接口。
"""

from dataclasses import dataclass
from typing import Protocol


# ══════════════════════════════════════════════════════════
# CodeChunk —— 切出来的一块代码(≈ Swift struct)
#   用 @dataclass(上面已 import)。8 个字段(照 spec 第 6 节):
#     path:str  start_line:int  end_line:int
#     symbol:str  kind:str  parent:str | None
#     code:str  language:str
#   提示:dataclass 里直接写「字段名: 类型」,一行一个,不用写 __init__
# ══════════════════════════════════════════════════════════
@dataclass
class CodeChunk:
    path: str
    start_line: int
    end_line: int
    symbol: str
    kind: str
    parent: str | None
    code: str
    language: str


# ══════════════════════════════════════════════════════════
# CodeChunker —— 切块器接口(≈ Swift protocol)
#   继承 Protocol(上面已 import)。一个方法:
#     chunk(self, source: str, path: str) -> list[CodeChunk]
#   方法体写 ...(接口只声明签名,不实现);记得写 docstring 说明它干嘛
#   关键设计:只吃字符串 source、不读文件 → 纯函数、易单测
# ══════════════════════════════════════════════════════════
class CodeChunker(Protocol):
    def chunk(self, source: str, path: str) -> list[CodeChunk]:
        '''把一段代码源码切块成若干CodeChunk'''
        ...
