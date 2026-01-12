from .db import LifeNumberDB
from typing import List


def get_grid_prompt(present_lines: List[str], counts: dict) -> str:
    """從資料庫獲取九宮格連線提示詞"""

    # 若無連線，直接返回特定訊息
    if not present_lines:
        return (
            "本次九宮格未形成有效數字結構，因此暫不提供九宮格解讀。\n"
            "建議改查詢其他已開放的分析項目。\n\n"
            "建議查詢順序：\n"
            "1️⃣ 流年數（目前的人生節奏）\n"
            "2️⃣ 業力數（正在學習的課題）\n"
            "3️⃣ 靈魂數（內在動機與核心能量）\n"
            "4️⃣ 其餘分析項目"
        )

    try:
        db = LifeNumberDB()
        prompt = (
            "你是一位生命靈數專家。請依照以下規則輸出內容，使用繁體中文。請使用純文字回覆，避免使用任何 markdown 格式標記（如 **、__、#、*、` 等）。\n"
            "[運算方式]：將出生年月日所有數字填入九宮格，統計連線。\n\n"
        )

        # 1. Fetch Present Lines Info
        prompt += "[您的連線特質]：\n"
        for line_key in present_lines:
            line_data = db.get_grid_line(line_key)
            if line_data:
                prompt += (
                    f"【{line_key} 連線｜{line_data.get('name')}】\n"
                    f"主題：{line_data.get('theme')}\n"
                    f"詳細解讀：{line_data.get('description')}\n"
                    f"特質：{line_data.get('features')}\n\n"
                )

        prompt += (
            "請整合以上連線優勢，進行完整解析，並給出：\n"
            "- 你的九宮格分析：總結連線帶來的優勢\n"
            "- 整體建議：如何更好發揮這些天賦特質\n"
        )
        return prompt

    except Exception as e:
        print(f"Error generating grid prompt: {e}")
        return "（系統錯誤：生成提示詞時發生異常）"
