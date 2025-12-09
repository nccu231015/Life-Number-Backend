"""業力數模組 - 前世未完成的課題"""

from .db import LifeNumberDB


def get_karma_prompt(number: int) -> str:
    """從資料庫獲取業力數提示詞"""
    try:
        db = LifeNumberDB()
        data = db.get_karma(number)

        if not data:
            return "（系統錯誤：無法讀取生命靈數資料庫）"

        title = data.get("title", "")
        desc = data.get("description", "")

        return (
            "你是一位生命靈數專家。請依照以下規則輸出內容，使用繁體中文。請使用純文字回覆，避免使用任何 markdown 格式標記（如 **、__、#、*、` 等）。\n"
            "[運算方式]：特殊業力數字（13, 14, 16, 19）。\n"
            f"[您的業力數]：{number} ｜ {title}\n"
            f"[意義]：{desc}\n"
            "請根據使用者的業力數，參考上述意義進行深度解析，並給出：\n"
            f"- 你的業力數：{number}\n"
            "- 此生帶來的因果課題（3-5 點）\n"
            "- 如果在生活中遇到阻礙，通常是...（舉例）\n"
            "- 如何償還或轉化這份業力（具體行動）\n"
        )
    except Exception as e:
        print(f"Error generating karma prompt: {e}")
        return "（系統錯誤：生成提示詞時發生異常）"


SYSTEM_PROMPT = "DEPRECATED"
