"""核心生命靈數模組 - 性格天賦與人生方向"""

from .db import LifeNumberDB


def get_core_prompt(number: int, category: str = None) -> str:
    """從資料庫獲取核心生命靈數提示詞"""
    try:
        db = LifeNumberDB()
        data = db.get_main_number(number)

        if not data:
            return "（系統錯誤：無法讀取生命靈數資料庫）"

        basic_desc = data.get("description", "")
        title = data.get("title", "")

        # 構建 Prompt
        prompt = (
            "你是一位生命靈數專家。請依照以下規則輸出內容，使用繁體中文。請使用純文字回覆，避免使用任何 markdown 格式標記（如 **、__、#、*、` 等）。\n"
            "[運算方式]：生日所有數字累加至 1-9。\n"
            f"[使用者命數]：{number} ({title})\n"
            f"[基本意義]：{basic_desc}\n"
        )

        # 注入詳細類別內容 (如果是付費版請求)
        if category:
            category_map = {
                "財運事業": "career_wealth",
                "家庭人際": "relationship",
                "自我成長": "growth",
                "目標規劃": "goals",
            }
            col_name = category_map.get(category)
            if col_name and data.get(col_name):
                prompt += f"\n[詳細分析 - {category}]：\n{data.get(col_name)}\n"

        prompt += (
            "\n請針對使用者的命數與上述提供的資料，進行深度解析，並給出：\n"
            f"- 你的核心數：{number}\n"
            "- 你的性格底色與優勢（3-5 點）\n"
            "- 建議的人生方向與行動（3-5 條）\n"
        )
        return prompt

    except Exception as e:
        print(f"Error generating core prompt: {e}")
        return "（系統錯誤：生成提示詞時發生異常）"


# 保留雖已廢棄但為了避免 import 錯誤的變數 (暫時)
SYSTEM_PROMPT = "DEPRECATED"
