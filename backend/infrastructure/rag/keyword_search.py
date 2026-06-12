import re
from typing import Optional


def extract_keywords(query: str, max_keywords: int = 10) -> list[str]:
    """Extract meaningful keywords from a query string."""
    words = re.findall(r"[a-zA-Z0-9一-鿿]+", query)
    # Filter out very short words and common stop words
    stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这", "他", "她", "它", "们"}
    keywords = [w for w in words if len(w) > 1 and w.lower() not in stop_words]
    return keywords[:max_keywords]
