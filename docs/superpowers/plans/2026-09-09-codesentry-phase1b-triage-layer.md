# CodeSentry 一期 · 分诊层(Phase 1b)实施计划

> **教学模式**:学习关键码用户手写(prompt/解析/组装),胶水我搭骨架;TDD 先给测试当靶子。步骤 `- [ ]`。
> **Spec:** `docs/superpowers/specs/2026-08-27-codesentry-design.md`(第 5B 步②③⑤)

**目标:** 在已有检索(locate)之上加"大脑":把 bug + top 候选代码喂给 LLM,产出**带理由的结构化分诊判断**(最可能位置 + 原因假设 + 修复方向 + 置信度)。让工具从"搜索框"变成"会分诊的 agent"。

**架构:** 两次 LLM 调用夹住检索 —— ①理解 bug(中文→英文功能关键词/症状,吃"页面名"强信号)→ ②locate 检索(已有)→ ③分诊推理(读候选真实代码出判断)。本期先做 ① 和 ③,把链路跑通。

**Tech Stack:** openai 客户端调 Kimi(复用 40 号配方)、pydantic 结构化输出、JSON。

## 全局约束

- Python 3.12+ / uv;LLM 走 Kimi(`.env` 里 `MOONSHOT_API_KEY`,base_url `https://api.moonshot.cn/v1`)。
- LLM 调用通过参数注入(`chat_fn`),测试用假 chat 不联网(呼应 build_index 的 embed_fn 注入)。
- 结构化输出:LLM 返回 JSON,用 pydantic 校验解析。
- 低温(temperature 低)——分诊要稳、可复现,不要发挥。

## 文件结构

```
src/codesentry/triage/
├── __init__.py
├── models.py        BugUnderstanding / TriageReport 两个 pydantic 模型
├── understand.py    understand_bug(bug_text, chat_fn) -> BugUnderstanding
├── diagnose.py      diagnose(bug_text, hits, chat_fn) -> TriageReport
└── prompts.py       两段 system prompt
tests/
├── test_understand.py
└── test_diagnose.py
```

---

### Task 1:pydantic 结构化模型 ✍️你手写

**Files:** Create `src/codesentry/triage/__init__.py`, `src/codesentry/triage/models.py`, `tests/test_models.py`

**Produces:**
- `BugUnderstanding`(BaseModel):`keywords: list[str]`、`feature: str`、`symptom: str`
- `TriageReport`(BaseModel):`suspect_path: str`、`suspect_line: int`、`cause: str`、`fix_hint: str`、`confidence: float`

- [ ] **Step 1(我给测试):**
```python
from codesentry.triage.models import BugUnderstanding, TriageReport

def test_models_parse_from_dict():
    u = BugUnderstanding(keywords=["Market", "refresh"], feature="行情页", symptom="crash")
    assert "Market" in u.keywords
    r = TriageReport(suspect_path="A.swift", suspect_line=42,
                     cause="主线程更新", fix_hint="加 DispatchQueue.main", confidence=0.7)
    assert r.suspect_line == 42 and 0 <= r.confidence <= 1
```
- [ ] **Step 2:** 跑 → FAIL
- [ ] **Step 3(✍️你写):** 用 pydantic `BaseModel` 定义两个模型(照 Produces 的字段;pydantic 你 Month3 用过 model_dump,这次定义模型)
- [ ] **Step 4:** 跑 → PASS
- [ ] **Step 5:** commit `feat(triage): BugUnderstanding / TriageReport 结构化模型`

---

### Task 2:understand_bug —— 理解 bug(中文→英文关键词)✍️你写 prompt + 组装

**Files:** Create `src/codesentry/triage/prompts.py`, `src/codesentry/triage/understand.py`, `tests/test_understand.py`

**Consumes:** `BugUnderstanding`
**Produces:** `understand_bug(bug_text: str, chat_fn) -> BugUnderstanding`
- `chat_fn: Callable[[str, str], str]`(system, user)-> LLM 原始回复文本;注入便于测试

- [ ] **Step 1(我给测试,假 chat):**
```python
import json
from codesentry.triage.understand import understand_bug

def _fake_chat(system, user):
    return json.dumps({"keywords": ["Market", "refresh"], "feature": "行情页", "symptom": "crash"})

def test_understand_extracts_english_keywords():
    u = understand_bug("行情页下拉刷新崩溃", _fake_chat)
    assert "Market" in u.keywords
    assert u.symptom == "crash"
```
- [ ] **Step 2:** 跑 → FAIL
- [ ] **Step 3(✍️你写):**
  - `prompts.py` 写 `UNDERSTAND_SYSTEM`:让 LLM 把中文 bug 转成 {keywords(英文功能/类名候选), feature, symptom} 的 **JSON**。强调:页面名→英文代码术语(提现→Withdraw、行情→Market)。
  - `understand.py`:调 `chat_fn(UNDERSTAND_SYSTEM, bug_text)` → `json.loads` → `BugUnderstanding(**data)`
- [ ] **Step 4:** 跑 → PASS
- [ ] **Step 5:** commit `feat(triage): understand_bug 中文 bug→英文关键词`

---

### Task 3:diagnose —— 分诊推理(读候选代码出判断)✍️你写 prompt + 组装

**Files:** Create `src/codesentry/triage/diagnose.py`, `tests/test_diagnose.py`;Modify `prompts.py`

**Consumes:** `TriageReport`,locate 返回的 hits(list[dict],含 path/start_line/symbol/code)
**Produces:** `diagnose(bug_text: str, hits: list[dict], chat_fn) -> TriageReport`

- [ ] **Step 1(我给测试,假 chat):**
```python
import json
from codesentry.triage.diagnose import diagnose

def _fake_chat(system, user):
    return json.dumps({"suspect_path": "Refresh.swift", "suspect_line": 24,
                       "cause": "刷新回调未在主线程更新数组", "fix_hint": "包 DispatchQueue.main",
                       "confidence": 0.72})

def test_diagnose_returns_report():
    hits = [{"path": "Refresh.swift", "start_line": 24, "symbol": "refresh()", "code": "func refresh(){...}"}]
    r = diagnose("下拉刷新崩溃", hits, _fake_chat)
    assert r.suspect_path == "Refresh.swift"
    assert r.suspect_line == 24
    assert r.confidence <= 1
```
- [ ] **Step 2:** 跑 → FAIL
- [ ] **Step 3(✍️你写):**
  - `prompts.py` 加 `DIAGNOSE_SYSTEM`:给定 bug + 若干候选代码,判断最可能位置+原因假设+修复方向+置信度,输出 JSON;**强调只依据给的代码、不确定要低置信度、不许编造行号**(grounding + 不硬编,呼应你 Month3 的教训)。
  - `diagnose.py`:把 hits 拼成 user 消息(每个候选:path:line + code)→ `chat_fn(DIAGNOSE_SYSTEM, user)` → `json.loads` → `TriageReport(**data)`
- [ ] **Step 4:** 跑 → PASS
- [ ] **Step 5:** commit `feat(triage): diagnose 读候选代码出结构化分诊判断`

---

### Task 4:接进 CLI + 真机验证 🤝我搭骨架,你读懂 + 真跑

**Files:** Create `scripts/triage.py`(或改 triage_skeleton);Create `src/codesentry/triage/chat.py`(真 Kimi chat_fn)

- [ ] **Step 1(🤝我搭):** `chat.py` 真 `chat_fn`(openai 调 Kimi,低温);`triage.py` 串:understand_bug → locate(用 keywords) → diagnose → 打印 TriageReport(带理由的报告)
- [ ] **Step 2(你读):** 读懂全链路,能讲每步
- [ ] **Step 3:** 对 RefreshUtil + 一个真实 bug 跑,看**带理由的判断**(对比之前只有片段)
- [ ] **Step 4:** commit `feat(triage): 分诊 CLI —— bug→理解→检索→带理由判断`

---

## 完成 = 你有了什么

从"打印 6 个相似片段"→"给出一个**带原因、修复方向、置信度**的分诊判断"。工具第一次像 agent。**后续**:双评估集量化、ClickUp 接入、生产硬化。

## 自审

- 覆盖 spec 5B②(理解)③后半(检索用关键词)⑤(报告生成);④严重度评分本期暂并入 diagnose 的 confidence,独立严重度规则留后续。
- 无占位符;测试均完整;chat_fn 注入保证不联网可测;类型一致(BugUnderstanding/TriageReport/hits dict 字段跨任务一致)。
