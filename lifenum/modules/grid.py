from .db import LifeNumberDB
from typing import List


def get_grid_prompt(present_lines: List[str], counts: dict) -> str:
    """從資料庫獲取九宮格連線與缺數提示詞"""
    try:
        db = LifeNumberDB()
        prompt = (
            "你是一位生命靈數專家。請依照以下規則輸出內容，使用繁體中文。請使用純文字回覆，避免使用任何 markdown 格式標記（如 **、__、#、*、` 等）。\n"
            "[運算方式]：將出生年月日所有數字填入九宮格，統計連線與缺數。\n\n"
        )

        # 1. Fetch Present Lines Info
        if present_lines:
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
        else:
            prompt += "[您的連線特質]：無特殊連線（代表可塑性高，但也可能較缺乏特定方向感）。\n\n"

        # 2. Fetch Missing Numbers Info
        # Calculate missing numbers from counts (where count is 0)
        missing_nums = [n for n in range(1, 10) if counts.get(n, 0) == 0]

        if missing_nums:
            prompt += "[您的缺數課題]：\n"
            for num in missing_nums:
                missing_data = db.get_grid_missing(num)
                if missing_data:
                    prompt += (
                        f"【缺 {num}：{missing_data.get('title')}】\n"
                        f"詳細解讀：{missing_data.get('description')}\n"
                        f"學習課題：{missing_data.get('lesson')}\n"
                        f"補能建議：{missing_data.get('advice')}\n"
                        f"推薦活動：{missing_data.get('recommendation')}\n\n"
                    )

        prompt += (
            "請整合以上連線優勢與缺數課題，進行完整解析，並給出：\n"
            "- 你的九宮格分析：總結連線帶來的優勢\n"
            "- 缺數的挑戰與補強建議（針對缺失的數字提供具體行動）\n"
            "- 整體能量平衡建議（如何發揮優勢彌補劣勢）\n"
        )
        return prompt

    except Exception as e:
        print(f"Error generating grid prompt: {e}")
        return "（系統錯誤：生成提示詞時發生異常）"


SYSTEM_PROMPT = "DEPRECATED"
