"""流年數模組 - 年度運勢與重點"""

from .db import LifeNumberDB


def get_personal_year_prompt(number: int, year: int = None) -> str:
    """從資料庫獲取流年數提示詞"""
    try:
        db = LifeNumberDB()
        data = db.get_personal_year(number)

        if not data:
            return "（系統錯誤：無法讀取生命靈數資料庫）"

        title = data.get("title", "")
        desc = data.get("description", "")
        action = data.get("action_key", "")
        taboo = data.get("taboo", "")
        slogan = data.get("slogan", "")

        target_year_str = f"{year} 年" if year else "當年"

        return (
            "你是一位生命靈數專家。請依照以下規則輸出內容，使用繁體中文。請使用純文字回覆，避免使用任何 markdown 格式標記（如 **、__、#、*、` 等）。\n"
            f"[運算方式]：{target_year_str}年份數字 + 生日『月』『日』相加，總和縮減至 1-9。\n"
            f"[您的流年數]：{number} ｜ {title}\n"
            f"[詳細解析]：\n{desc}\n\n"
            f"[行動關鍵]：{action}\n"
            f"[禁忌]：{taboo}\n"
            f"[年度口號]：{slogan}\n\n"
            "請根據使用者的流年數，各別解釋，並給出：\n"
            f"- 你的流年數：{number}｜對應主題\n"
            "- 年度詳細解析（根據上述內容）\n"
            "- 行動關鍵與禁忌（直接引用上述指引）\n"
            "- 年度口號（激勵用戶）\n"
        )
    except Exception as e:
        print(f"Error generating personal year prompt: {e}")
        return "（系統錯誤：生成提示詞時發生異常）"


SYSTEM_PROMPT = "DEPRECATED"
