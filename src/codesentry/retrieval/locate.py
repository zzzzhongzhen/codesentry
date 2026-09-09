"""检索层:把切好的块建成 Chroma 索引(build_index),之后按 bug 定位(locate,下个任务)。

关键设计:embed 通过参数 embed_fn 注入 —— 生产传真 embed,测试传假 embedder,不碰网络。
"""

from collections.abc import Callable

from codesentry.chunking.base import CodeChunk

EmbedFn = Callable[[str], list[float]]  # "吃一段文本、吐一个向量"的函数类型

BATCH = 5000

def build_index(chunks: list[CodeChunk], embed_fn: EmbedFn, collection) -> None:
    """把每个 CodeChunk embed 后存进 Chroma collection。"""
    # ══════════════════════════════════════════════════════
    # 该你写(回忆 40 号的 collection.add):
    #   遍历 chunks,对每块:
    #     - 向量  = embed_fn(chunk.code)          ← 用注入的 embed_fn,别直接 import embed
    #     - id    = f"{chunk.path}:{chunk.start_line}"   (要唯一)
    #     - 文档  = chunk.code
    #     - 元数据 = {"path":.., "start_line":.., "end_line":.., "symbol":.., "kind":..}
    #   然后 collection.add(ids=[...], embeddings=[...], documents=[...], metadatas=[...])
    #   (可以先攒成 4 个列表,最后一次 add;或循环里一个个 add)
    #
    #   ⚠️ 坑:Chroma 元数据值只能是 str/int/float/bool,【不能放 None】。
    #         chunk.parent 可能是 None,所以【别把 parent 放进 metadata】(或转成 "")。
    # ══════════════════════════════════════════════════════
    vecs = [embed_fn(chunk.code) for chunk in chunks]
    ids = [f"{chunk.path}:{chunk.start_line}" for chunk in chunks]
    docs = [chunk.code for chunk in chunks]
    metadatas = [{
        'path': chunk.path, 'start_line': chunk.start_line, 'end_line': chunk.end_line,
        'symbol': chunk.symbol, 'kind': chunk.kind
    } for chunk in chunks]

    # 分批次加向量防止chorma报错
    for i in range(0, len(ids), BATCH):
        collection.add(
            ids=ids[i:i+BATCH],
            embeddings=vecs[i:i+BATCH],
            documents=docs[i:i+BATCH],
            metadatas=metadatas[i:i+BATCH]
        )


def locate(bug_text: str, collection, embed_fn: EmbedFn, k: int = 5) -> list[dict]:
    """按 bug 描述,查出最可疑的 k 个代码块;返回带定位信息的字典列表(按相似度)。"""
    q_vec = embed_fn(bug_text)
    res = collection.query(
        query_embeddings=[q_vec],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    # res 的每个字段都套了一层"批次"维度,取 [0](呼应你 28/40 号):
    #   res["documents"][0]  / res["metadatas"][0]  / res["distances"][0]  一一对应
    # ══════════════════════════════════════════════════════
    # 该你写:遍历这三个并列的列表,每个命中组装成一个 dict:
    #     {"path":.., "start_line":.., "symbol":.., "code":.., "distance":..}
    #   path/start_line/symbol 从 metadata 取;code 从 documents 取;distance 从 distances 取
    #   返回这些 dict 的列表(已按相似度排好,Chroma 返回就是近→远)
    #   提示:zip(res["documents"][0], res["metadatas"][0], res["distances"][0]) 三个并排遍历
    # ══════════════════════════════════════════════════════
    result = []
    for doc, metadata, distance in zip(res['documents'][0], res['metadatas'][0], res['distances'][0]):
        result.append({
            'path': metadata['path'],
            'start_line': metadata['start_line'],
            'end_line': metadata['end_line'],
            'symbol': metadata['symbol'],
            'kind': metadata['kind'],
            'code': doc,
            'distance': distance
        })
    return result