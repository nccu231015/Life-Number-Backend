"""挑戰數模組 - 人生課題與限制"""

from .db import LifeNumberDB


def get_challenge_prompt(number: int) -> str:
    """從資料庫獲取挑戰數提示詞"""
    try:
        db = LifeNumberDB()
        data = db.get_challenge(number)

        if not data:
            return "（系統錯誤：無法讀取生命靈數資料庫）"

        title = data.get("title", "")
        desc = data.get("description", "")

        return (
            "你是一位生命靈數專家。請依照以下規則輸出內容，使用繁體中文。請使用純文字回覆，避免使用任何 markdown 格式標記（如 **、__、#、*、` 等）。\n"
            "[運算方式]：出生日月日數字之差值絕對值。\n"
            f"[您的挑戰數]：{number} ｜ {title}\n"
            f"[意義]：{desc}\n"
            "請根據使用者的挑戰數，參考上述意義進行深度解析，並給出：\n"
            f"- 你的挑戰數：{number}\n"
            "- 此生需要克服的課題（3-5 點）\n"
            "- 面對與轉化這些挑戰的實用建議（2-4 條）\n"
            "- 成長後的正面轉化方向\n"
        )
    except Exception as e:
        print(f"Error generating challenge prompt: {e}")
        return "（系統錯誤：生成提示詞時發生異常）"


SYSTEM_PROMPT = "DEPRECATED"
