"""walk_repo:遍历一个代码库目录,读出所有匹配后缀的源码文件。

设计:把"读文件"和"切块"分开——walk 负责磁盘 IO,chunker 只吃字符串(纯函数、好测)。
"""

from pathlib import Path
from typing import Iterator


def walk_repo(root: str, ext: str = ".swift") -> Iterator[tuple[str, str]]:
    """递归遍历 root,产出 (相对路径, 文件内容) 每一个匹配后缀的文件。"""
    # ══════════════════════════════════════════════════════
    # 该你写:
    #   1) 递归找文件:Path(root).rglob("*" + ext)  ← rglob 会钻进子目录
    #   2) 对每个文件 p:
    #        内容 = p.read_text(encoding="utf-8")
    #        相对路径 = str(p.relative_to(root))     ← 去掉 root 前缀,报告要短路径
    #        yield (相对路径, 内容)
    #   提示:用 for + yield 一个个产出(生成器,不一次把整库读进内存)
    # ══════════════════════════════════════════════════════
    for p in Path(root).rglob('*'+ext):
        content = p.read_text(encoding='utf-8')
        rel = str(p.relative_to(root))
        yield (rel, content)   