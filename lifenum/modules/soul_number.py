"""靈魂數模組 - 內心渴望"""

from .db import LifeNumberDB


def get_soul_prompt(number: int) -> str:
    """從資料庫獲取靈魂數提示詞"""
    try:
        db = LifeNumberDB()
        data = db.get_soul(number)

        if not data:
            return "（系統錯誤：無法讀取生命靈數資料庫）"

        desc = data.get("description", "")

        return (
            "你是一位生命靈數專家。請依照以下規則輸出內容，使用繁體中文。請使用純文字回覆，避免使用任何 markdown 格式標記（如 **、__、#、*、` 等）。\n"
            "[運算方式]：將英文姓名中的『母音』數字加總，縮減至 1-9。\n"
            f"[您的靈魂數]：{number}\n"
            f"[意義]：{desc}\n"
            "請根據使用者的靈魂數，參考上述意義進行深度解析，並給出：\n"
            f"- 你的靈魂數：{number}\n"
            "- 內心深處的渴望與動機（3-5 點）\n"
            "- 如果無法滿足渴望時的潛在情緒\n"
            "- 如何滋養自己的靈魂（具體建議）\n"
        )
    except Exception as e:
        print(f"Error generating soul prompt: {e}")
        return "（系統錯誤：生成提示詞時發生異常）"


SYSTEM_PROMPT = "DEPRECATED"
