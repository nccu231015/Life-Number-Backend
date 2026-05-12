"""
全域規則載入器
從 Supabase 動態載入 AI 全域規則
"""

from typing import Optional
from shared.supabase_client import get_supabase_client
import time

# 緩存全域規則（避免每次請求都查詢數據庫）
_global_rules_cache: Optional[str] = None
_cache_timestamp: Optional[float] = None
CACHE_DURATION = 300  # 5分鐘


def load_global_rules(force_refresh: bool = False) -> str:
    """
    載入所有全域規則並組合成字符串

    Args:
        force_refresh: 是否強制刷新緩存

    Returns:
        組合後的規則文本，可直接添加到 prompt
    """
    global _global_rules_cache, _cache_timestamp

    current_time = time.time()

    # 使用緩存（5分鐘內）
    if (
        not force_refresh
        and _global_rules_cache is not None
        and _cache_timestamp is not None
        and current_time - _cache_timestamp < CACHE_DURATION
    ):
        return _global_rules_cache

    try:
        supabase = get_supabase_client()

        # 查詢所有規則，按 id 排序
        response = (
            supabase.table("ai_global_rules")
            .select("rule_content")
            .order("id")
            .execute()
        )

        if not response.data:
            print("[Rule Loader] Warning: No global rules found in database")
            return get_fallback_rules()

        # 組合所有規則
        rules = [
            item["rule_content"] for item in response.data if item.get("rule_content")
        ]
        combined_rules = "\n\n".join(rules)

        # 更新緩存
        _global_rules_cache = combined_rules
        _cache_timestamp = current_time

        print(f"[Rule Loader] Loaded {len(rules)} global rules from database")
        return combined_rules

    except Exception as e:
        print(f"[Rule Loader] Error loading global rules: {e}")
        return get_fallback_rules()


def get_fallback_rules() -> str:
    """
    當數據庫不可用時的備用規則（硬編碼）
    包含所有三個全域規則
    """
    return """【回答原則】避免給予絕對性的判斷，改用建議導向的表達：
- 禁止使用「你一定會」、「你絕對不該」、「必須」、「千萬不要」等絕對性表達
- 請使用「建議」、「可以考慮」、「值得留意」、「或許」等引導性語言
- 提供多種可能性和方向，而非單一確定的結論

【禁語要求】
- **嚴格禁止使用「因果報應」四字，若需表達相關概念，請統一改用「因果回饋分析」或「業力課題」。**

【內容審核與建議規範】
若使用者的問題涉及「財運、金錢、事業、買房、置產」等主題，請務必照常進行深度分析與解答，絕不可拒絕回答。
在給予財運或金錢相關建議時，請遵守以下原則：
1. 著重於個人潛力、心態調整、流年運勢方向或努力的建議。
2. 禁止推薦任何可能涉及高風險、非法、投機性的具體金融行為（例如：指定買哪支股票、期貨操作建議、彩券號碼、賭博、保證獲利等）。
3. 若使用者要求上述高風險的具體建議，請委婉告知「此處僅提供靈數與運勢的分析指引，無法提供具體的投資標的或賭博建議」，並轉而提供一般性的財運方向。"""


def clear_rules_cache():
    """清除規則緩存（用於測試或手動刷新）"""
    global _global_rules_cache, _cache_timestamp
    _global_rules_cache = None
    _cache_timestamp = None
    print("[Rule Loader] Cache cleared")
