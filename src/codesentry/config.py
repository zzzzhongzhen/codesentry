"""配置:从 .env 读密钥/路径,集中管理常量。"""

import os

from dotenv import load_dotenv

load_dotenv()  # 读取项目根的 .env(SILICONFLOW_API_KEY 等)

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
EMBED_MODEL = "BAAI/bge-m3"

# 目标代码库路径(默认指向测试 fixtures;真跑 CoinEx 时在 .env 里设 REPO_PATH)
REPO_PATH = os.getenv("REPO_PATH", "tests/fixtures/repo")
