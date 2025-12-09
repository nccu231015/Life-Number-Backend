"""成熟數模組 - 人生後半段的方向與潛力"""

from .db import LifeNumberDB


def get_maturity_prompt(number: int) -> str:
    """從資料庫獲取成熟數提示詞"""
    try:
        db = LifeNumberDB()
        data = db.get_maturity(number)

        if not data:
            return "（系統錯誤：無法讀取生命靈數資料庫）"

        desc = data.get("description", "")

        return (
            "你是一位生命靈數專家。請依照以下規則輸出內容，使用繁體中文。請使用純文字回覆，避免使用任何 markdown 格式標記（如 **、__、#、*、` 等）。\n"
            "[運算方式]：核心生命靈數 + 英文姓名表達數，縮減至 1-9。\n"
            f"[您的成熟數]：{number}\n"
            f"[意義]：{desc}\n"
            "請根據使用者的成熟數，參考上述意義進行深度解析，並給出：\n"
            f"- 你的成熟數：{number}\n"
            "- 中年之後的運勢走向（3-5 點）\n"
            "- 後半生的潛在發展可能\n"
            "- 給予成熟期的建議（具體行動）\n"
        )
    except Exception as e:
        print(f"Error generating maturity prompt: {e}")
        return "（系統錯誤：生成提示詞時發生異常）"


SYSTEM_PROMPT = "DEPRECATED"

MODULE_DESCRIPTION = "人生後半段的方向與潛力"
