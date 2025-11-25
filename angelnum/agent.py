"""對話管理模組 - 處理天使數字 AI 的會話狀態和資訊提取"""

from __future__ import annotations

import json
from typing import Optional, Dict, Any
from enum import Enum

from shared.gpt_client import GPTClient


class AngelConversationState(Enum):
    """對話狀態"""
    INIT = "init"  # 初始狀態
    WAITING_BASIC_INFO = "waiting_basic_info"  # 等待基本資訊
    WAITING_ANGEL_NUMBER = "waiting_angel_number"  # 等待天使數字選擇
    ASKING_FOR_QUESTION = "asking_for_question"  # 詢問是否有問題（付費版）
    CONVERSATION = "conversation"  # 持續對話中（付費版）
    COMPLETED = "completed"  # 完成


class AngelConversationSession:
    """對話會話"""
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = AngelConversationState.INIT
        self.user_name: Optional[str] = None
        self.user_gender: Optional[str] = None
        self.birthdate: Optional[str] = None
        self.angel_number: Optional[str] = None  # 使用者選擇的天使數字
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
            "angel_number": self.angel_number,
            "tone": self.tone,
            "conversation_history": self.conversation_history,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AngelConversationSession':
        """從字典創建會話"""
        session = cls(data["session_id"])
        session.state = AngelConversationState(data.get("state", "init"))
        session.user_name = data.get("user_name")
        session.user_gender = data.get("user_gender")
        session.birthdate = data.get("birthdate")
        session.angel_number = data.get("angel_number")
        session.tone = data.get("tone", "friendly")
        session.conversation_history = data.get("conversation_history", [])
        return session


class AngelNumberAgent:
    """天使數字 AI Agent - 負責提取使用者資訊"""
    
    def __init__(self):
        self.gpt_client = GPTClient()
    
    def extract_birthdate_with_ai(self, user_input: str) -> tuple[str | None, str | None, str | None, str | None]:
        """
        使用 AI 從使用者輸入中提取姓名、性別與生日（不限格式）
        返回：(姓名, 性別, 生日, 錯誤訊息)
        """
        system_prompt = """你是一位專業的資訊擷取助理。請從使用者輸入中提取姓名、性別與生日資訊。

生日格式不限,可能的格式包括但不限於：
- 1990年7月12日
- 1990/07/12
- 1990-07-12
- 1990.07.12
- 民國79年7月12日
- 七十九年七月十二日
- 1990 年 7 月 12 日
- 一九九零年七月十二日

性別可能以以下方式表達：
- 男、女
- 先生、小姐
- M、F
- male、female

請以 JSON 格式回應,包含：
{
    "has_birthdate": true/false,  // 是否包含生日信息
    "name": "姓名或null",
    "gender": "male/female/null",
    "birthdate": "YYYY/MM/DD格式的生日或null",
    "error_message": "如果資訊不完整,說明缺少什麼"
}

注意事項：
1. 如果輸入中沒有明確的年月日資訊,has_birthdate 應為 false
2. 生日必須轉換為 YYYY/MM/DD 格式
3. 民國年份需要轉換為西元年份（民國年+1911）
4. 如果只有部分資訊（如只有姓名沒有生日）,也要在對應欄位填入已知資訊
"""
        
        user_prompt = f"請從以下輸入中提取姓名、性別與生日資訊：\n{user_input}"
        
        try:
            response = self.gpt_client.structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=300
            )
            
            result = json.loads(response)
            has_birthdate = result.get("has_birthdate", False)
            
            if not has_birthdate:
                error_msg = result.get("error_message", "未能識別生日資訊")
                return None, None, None, error_msg
            
            name = result.get("name")
            gender = result.get("gender")
            birthdate = result.get("birthdate")
            
            # 驗證必要資訊
            if not name or not gender or not birthdate:
                missing = []
                if not name:
                    missing.append("姓名")
                if not gender:
                    missing.append("性別")
                if not birthdate:
                    missing.append("生日")
                error_msg = f"缺少{'、'.join(missing)}資訊"
                return name, gender, birthdate, error_msg
            
            return name, gender, birthdate, None
            
        except Exception as e:
            print(f"Error in extract_birthdate_with_ai: {e}")
            return None, None, None, "無法解析輸入資訊"
