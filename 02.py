import re
from datetime import datetime

MAX_CHARS = 20000

def _split_sentences(text):
    if not text:
        return []
    parts = re.split(r"[。！？!?\n]+", text)
    return [p.strip() for p in parts if p.strip()]

def _summarize_text(text, target_chars):
    if len(text) <= target_chars:
        return text
    sents = _split_sentences(text)
    if not sents:
        return text[:target_chars]
    keys = {"需求","问题","方案","结论","下一步","结果","决定","风险","计划","进展"}
    ordered = []
    seen = set()
    for s in sents:
        if any(k in s for k in keys):
            if s not in seen:
                ordered.append(s)
                seen.add(s)
    for s in sents[:3]:
        if s not in seen:
            ordered.append(s)
            seen.add(s)
    for s in sents[-3:]:
        if s not in seen:
            ordered.append(s)
            seen.add(s)
    for s in sents:
        if s not in seen:
            ordered.append(s)
            seen.add(s)
    out = []
    cur = 0
    for s in ordered:
        if cur + len(s) + 1 > target_chars:
            break
        out.append(s)
        cur += len(s) + 1
    if not out:
        return text[:target_chars]
    return "。".join(out)

def _parse_ts(ts):
    dt = datetime.fromisoformat(ts)
    day = dt.strftime("%Y-%m-%d")
    month = dt.strftime("%Y-%m")
    return dt, day, month

def _group_by_day(records):
    days = {}
    for r in records:
        dt, day, _ = _parse_ts(r["timestamp"])
        g = days.setdefault(day, [])
        g.append((dt, r))
    for day in list(days.keys()):
        days[day] = [r for _, r in sorted(days[day], key=lambda x: x[0])]
    return days

def _group_by_month(records):
    months = {}
    for r in records:
        dt = datetime.fromisoformat(r["timestamp"])
        key = dt.strftime("%Y-%m")
        g = months.setdefault(key, [])
        g.append((dt, r))
    for m in list(months.keys()):
        months[m] = [r for _, r in sorted(months[m], key=lambda x: x[0])]
    return months

def _join_records(records):
    parts = []
    for r in records:
        parts.append(r.get("content",""))
    return "\n---\n".join(parts)

def _budget_split(total, n):
    if n <= 0:
        return []
    base = max(500, total // n)
    return [base for _ in range(n)]

def summarize_day(records, max_chars=MAX_CHARS):
    merged = _join_records(records)
    if len(merged) <= max_chars:
        return merged
    budgets = _budget_split(max_chars, len(records))
    pieces = []
    for i, r in enumerate(records):
        pieces.append(_summarize_text(r.get("content",""), budgets[i]))
    combined = "\n".join(pieces)
    if len(combined) <= max_chars:
        return combined
    return _summarize_text(combined, max_chars)

def summarize_month(day_map, month_key, max_chars=MAX_CHARS):
    days_sorted = sorted(day_map.items(), key=lambda x: x[0])
    contents = [d for _, d in days_sorted]
    merged = "\n\n".join(contents)
    if len(merged) <= max_chars:
        return merged
    budgets = _budget_split(max_chars, len(contents))
    pieces = []
    for i, d in enumerate(contents):
        pieces.append(_summarize_text(d, budgets[i]))
    combined = "\n".join(pieces)
    if len(combined) <= max_chars:
        return combined
    return _summarize_text(combined, max_chars)

def summarize_multi_month(month_map, max_chars=MAX_CHARS):
    keys_sorted = sorted(month_map.keys())
    contents = [month_map[k] for k in keys_sorted]
    merged = "\n\n".join(contents)
    if len(merged) <= max_chars:
        return merged
    budgets = _budget_split(max_chars, len(contents))
    pieces = []
    for i, c in enumerate(contents):
        pieces.append(_summarize_text(c, budgets[i]))
    combined = "\n".join(pieces)
    if len(combined) <= max_chars:
        return combined
    return _summarize_text(combined, max_chars)

def process(records, max_chars=MAX_CHARS):
    days = _group_by_day(records)
    months = {}
    for day, recs in days.items():
        month = day[:7]
        dsum = summarize_day(recs, max_chars)
        m = months.setdefault(month, {})
        m[day] = dsum
    month_summaries = {}
    for mk, dm in months.items():
        month_summaries[mk] = summarize_month(dm, mk, max_chars)
    return month_summaries

def count_tokens(text):
    try:
        import tiktoken
        try:
            enc = tiktoken.get_encoding("o200k_base")
        except Exception:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        return -1

if __name__ == "__main__":
    sample = []
    for i in range(3):
        sample.append({"timestamp": f"2025-11-01 0{i}:00:00", "channel": "call", "content": ("通话内容A。"*800)})
    for i in range(2):
        sample.append({"timestamp": f"2025-11-01 1{i}:30:00", "channel": "wechat", "content": ("微信聊天B。"*600)})
    for i in range(4):
        sample.append({"timestamp": f"2025-11-02 0{i}:15:00", "channel": "call", "content": ("通话内容C。"*500)})
    for i in range(2):
        sample.append({"timestamp": f"2025-12-03 0{i}:45:00", "channel": "wechat", "content": ("微信聊天D。"*900)})
    result = process(sample, MAX_CHARS)
    for mk in sorted(result.keys()):
        txt = result[mk]
        print(mk, len(txt), count_tokens(txt))
