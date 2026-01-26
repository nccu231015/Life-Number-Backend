"""業力數模組 - 前世未完成的課題"""

from .db import LifeNumberDB


def get_karma_prompt(number: int) -> str:
    """從資料庫獲取業力數提示詞"""
    try:
        db = LifeNumberDB()
        data = db.get_karma(number)

        if number == 0:
            return (
                "你是一位生命靈數專家。請依照以下規則輸出內容，使用繁體中文。請使用純文字回覆。\n"
                "[特殊情況]：使用者的業力數為 0，代表「無特定業力債」。\n"
                "[意義]：象徵靈魂是自由的，此生沒有前世遺留的重大未竟課題，這是一個正向的指標。\n"
                "請根據這個結果進行解析，並給出：\n"
                "- 你的業力數：0（無特定業力）\n"
                "- 意義解析：說明這代表靈魂的自由度，以及此生可以更自主創造命運\n"
                "- 生活建議：如何善用這份自由，避免因為太過隨興而失去方向\n"
                "- 正向鼓勵\n"
            )

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
