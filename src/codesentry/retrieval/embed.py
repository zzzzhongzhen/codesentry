"""真·embedding 函数:调硅基 bge-m3(和 40 号一样)。

只在真跑(CLI)时用;测试里用假 embedder 代替,不碰网络。
"""

from openai import OpenAI

from codesentry.config import EMBED_MODEL, SILICONFLOW_API_KEY, SILICONFLOW_BASE_URL

_client = OpenAI(api_key=SILICONFLOW_API_KEY, base_url=SILICONFLOW_BASE_URL)


def embed(text: str) -> list[float]:
    """把一段文本转成向量(调硅基 bge-m3)。"""
    resp = _client.embeddings.create(model=EMBED_MODEL, input=text)
    return resp.data[0].embedding
