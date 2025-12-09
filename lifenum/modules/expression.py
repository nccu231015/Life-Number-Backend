"""表達數模組 - 整體表達風格與社交風格"""

from .db import LifeNumberDB


def get_expression_prompt(number: int) -> str:
    """從資料庫獲取表達數提示詞"""
    try:
        db = LifeNumberDB()
        data = db.get_expression(number)

        if not data:
            return "（系統錯誤：無法讀取生命靈數資料庫）"

        title = data.get("title", "")
        desc = data.get("description", "")

        return (
            "你是一位生命靈數專家。請依照以下規則輸出內容，使用繁體中文。請使用純文字回覆，避免使用任何 markdown 格式標記（如 **、__、#、*、` 等）。\n"
            "[運算方式]：將英文姓名中的『所有字母』數字加總，縮減至 1-9。\n"
            f"[您的表達數]：{number} ｜ {title}\n"
            f"[意義]：{desc}\n"
            "請根據使用者的表達數，參考上述意義進行深度解析，並給出：\n"
            f"- 你的表達數：{number}\n"
            "- 你的處事風格與能力（3-5 點）\n"
            "- 適合發揮的舞台或工作類型\n"
            "- 如何將此能力運用在生活中（具體建議）\n"
        )
    except Exception as e:
        print(f"Error generating expression prompt: {e}")
        return "（系統錯誤：生成提示詞時發生異常）"


SYSTEM_PROMPT = "DEPRECATED"
