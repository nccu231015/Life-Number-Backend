"""
黃道吉日對話管理模組
處理會話狀態和資訊提取
"""

from __future__ import annotations

import json
from typing import Optional, Dict, Any
from enum import Enum

from shared.gpt_client import GPTClient


class AuspiciousState(Enum):
    """對話狀態"""

    INIT = "init"  # 初始狀態
    WAITING_BASIC_INFO = "waiting_basic_info"  # 等待基本資訊
    WAITING_CATEGORY_AND_DATE = "waiting_category_and_date"  # 等待分類和日期選擇
    WAITING_SPECIFIC_QUESTION = "waiting_specific_question"  # 等待具體問題描述
    PROVIDING_DATES = "providing_dates"  # 提供吉日建議
    COMPLETED = "completed"  # 完成


class AuspiciousSession:
    """黃道吉日會話"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = AuspiciousState.INIT
        self.user_name: Optional[str] = None
        self.user_gender: Optional[str] = None
        self.birthdate: Optional[str] = None
        self.category: Optional[str] = None  # 選擇的分類
        self.selected_date: Optional[str] = None  # 選擇的具體日期 (YYYY-MM-DD)
        self.specific_question: Optional[str] = None  # 具體問題描述
        self.tone: str = "friendly"
        self.conversation_history: list[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        """添加對話歷史"""
        self.conversation_history.append({"role": role, "content": content})

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "user_name": self.user_name,
            "user_gender": self.user_gender,
            "birthdate": self.birthdate,
            "category": self.category,
            "selected_date": self.selected_date,
            "specific_question": self.specific_question,
            "tone": self.tone,
            "conversation_history": self.conversation_history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuspiciousSession":
        """從字典創建會話"""
        session = cls(data["session_id"])
        session.state = AuspiciousState(data.get("state", "init"))
        session.user_name = data.get("user_name")
        session.user_gender = data.get("user_gender")
        session.birthdate = data.get("birthdate")
        session.category = data.get("category")
        session.selected_date = data.get("selected_date")
        session.specific_question = data.get("specific_question")
        session.tone = data.get("tone", "friendly")
        session.conversation_history = data.get("conversation_history", [])
        return session


class AuspiciousAgent:
    """黃道吉日 Agent - 負責資訊提取和日期推薦"""

    def __init__(self):
        self.gpt_client = GPTClient()

    def extract_basic_info(self, user_input: str) -> Dict[str, Optional[str]]:
        """
        使用 AI 提取基本資訊

        Args:
            user_input: 用戶輸入

        Returns:
            包含 name, gender, birthdate 的字典
        """
        system_prompt = """你是專業的資訊擷取助理。請從使用者輸入中提取姓名、性別與生日資訊。

生日格式不限，可能的格式包括：
- 1990年7月12日
- 1990/07/12
- 1990-07-12
- 民國79年7月12日

性別可能以以下方式表達：
- 男、女
- 先生、小姐
- M、F
- male、female

請以 JSON 格式回應：
{
    "name": "姓名或null",
    "gender": "male/female/null",
    "birthdate": "YYYY/MM/DD格式或null",
    "error_message": "如果資訊不完整，說明缺少什麼"
}

注意：
1. 生日必須轉換為 YYYY/MM/DD 格式
2. 民國年份需要轉換為西元年份（民國年+1911）
3. 如果資訊不完整，在 error_message 中說明
"""

        user_prompt = f"請從以下輸入中提取姓名、性別與生日資訊：\n{user_input}"

        try:
            response = self.gpt_client.structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=300,
            )

            result = json.loads(response)
            return {
                "name": result.get("name"),
                "gender": result.get("gender"),
                "birthdate": result.get("birthdate"),
                "error_message": result.get("error_message"),
            }

        except Exception as e:
            print(f"Error in extract_basic_info: {e}")
            return {
                "name": None,
                "gender": None,
                "birthdate": None,
                "error_message": "無法解析輸入資訊",
            }
