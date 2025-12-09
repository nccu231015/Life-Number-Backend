"""生日數模組 - 天生才華"""

from .db import LifeNumberDB


def get_birthday_prompt(number: int) -> str:
    """從資料庫獲取生日數提示詞"""
    try:
        db = LifeNumberDB()
        data = db.get_birthday_number(number)

        if not data:
            return "（系統錯誤：無法讀取生命靈數資料庫）"

        desc = data.get("description", "")

        return (
            "你是一位生命靈數專家。請依照以下規則輸出內容，使用繁體中文。請使用純文字回覆，避免使用任何 markdown 格式標記（如 **、__、#、*、` 等）。\n"
            "[運算方式]：生日『當天』數字累加至 1-9。\n"
            f"[使用者生日數]：{number}\n"
            f"[意義]：{desc}\n"
            "請針對使用者的生日數與上述提供的資料，進行深度解析，並給出：\n"
            f"- 你的生日數：{number}\n"
            "- 你與生俱來的才華（3-5 點）\n"
            "- 如何善用此天賦（2-4 條）\n"
            "- 相關領域/場合的建議（2-4 個）\n"
        )
    except Exception as e:
        print(f"Error generating birthday prompt: {e}")
        return "（系統錯誤：生成提示詞時發生異常）"


SYSTEM_PROMPT = "DEPRECATED"
