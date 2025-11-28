"""
擲筊神諭 Agent
處理擲筊對話邏輯和狀態管理
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from shared.gpt_client import GPTClient


class DivinationState(Enum):
    """擲筊對話狀態"""
    INIT = "init"
    WAITING_BASIC_INFO = "waiting_basic_info"
    WAITING_QUESTION = "waiting_question"
    DIVINING = "divining"
    INTERPRETING = "interpreting"
    ASKING_FOR_QUESTION = "asking_for_question"  # 付費版：持續提問
    COMPLETED = "completed"


class DivinationSession:
    """擲筊會話狀態"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = DivinationState.INIT
        
        # 基本資訊
        self.user_name: Optional[str] = None
        self.user_gender: Optional[str] = None
        self.birthdate: Optional[str] = None
        
        # 語氣設置
        self.tone: str = "friendly"
        
        # 問題和結果
        self.question: Optional[str] = None
        self.divination_result: Optional[str] = None  # holy, laughing, negative
        
        # 對話歷史
        self.conversation_history: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        """添加對話訊息"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })


class DivinationAgent:
    """擲筊 Agent - 處理業務邏輯"""
    
    def __init__(self):
        self.gpt_client = GPTClient()
    
    def extract_basic_info(self, user_input: str) -> Dict[str, Optional[str]]:
        """
        使用 AI 提取用戶的基本資訊
        
        Args:
            user_input: 用戶輸入的文字
            
        Returns:
            包含 name, gender, birthdate 的字典
        """
        system_prompt = """你是一位專業的資訊擷取助理。請從使用者輸入中提取姓名、性別、生日。

生日格式不限，可能的格式包括但不限於：
- 1990年7月12日
- 1990/07/12
- 1990-07-12
- 1990.07.12
- 1990 年 7 月 12 日

性別可能以以下方式表達，請統一轉換為標準格式：
- 男、男性、先生 → 轉換為 "男"
- 女、女性、小姐 → 轉換為 "女"

請以 JSON 格式回應，包含：
{
"name": "姓名或null",
"gender":" 男/女/null",
"birthdate": "YYYY/MM/DD格式的生日或null"
}

注意事項：
1. 生日必須轉換為 YYYY/MM/DD 格式
2. 如果缺少姓名、性別或生日，對應欄位填 null
3. 如果只有部分資訊，也要在對應欄位填入已知資訊"""

        user_prompt = f"""請從以下輸入中提取姓名、性別、生日資訊：
{user_input}"""

        try:
            response = self.gpt_client.structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=500
            )
            
            print(f"[DEBUG] GPT Response: {response}")
            
            import json
            result = json.loads(response)
            
            extracted = {
                "name": result.get("name"),
                "gender": result.get("gender"),
                "birthdate": result.get("birthdate")
            }
            
            print(f"[DEBUG] Extracted: {extracted}")
            return extracted
            
        except Exception as e:
            print(f"提取基本資訊失敗: {e}")
            import traceback
            traceback.print_exc()
            return {"name": None, "gender": None, "birthdate": None}

    def generate_interpretation(self, tone_config: Dict[str, str], user_name: str, question: str, result: str) -> str:
        """
        生成擲筊解讀（付費版）
        
        Args:
            tone_config: 語氣配置
            user_name: 用戶姓名
            question: 用戶問題
            result: 擲筊結果 (holy, laughing, negative)
            
        Returns:
            生成的解讀文本
        """
        result_meaning = {
            "holy": "聖筊（肯定、允許、順勢）",
            "laughing": "笑筊（暫不回答、調整、時機未到）",
            "negative": "陰筊（否定、提醒、改變方向）"
        }
        
        system_prompt = f"""你現在扮演 {tone_config['name']}。
你的語氣風格是：{tone_config['style']}。
你的關鍵詞是：{tone_config['keywords']}。
你的說話範例：{tone_config['example']}。

請根據擲筊結果，為信眾 {user_name} 解讀神意。

擲筊結果：{result_meaning[result]}
信眾問題：{question}

請用符合你身份的語氣進行解讀。
如果是聖筊，給予肯定和鼓勵。
如果是笑筊，溫和地提示問題可能不清楚，或時機未到。
如果是陰筊，嚴肅但慈悲地提醒此路不通，應另尋他法。

請直接以神明的口吻回答，不要有「我是AI」等出戲的語句。
請使用現代白話文，語氣親切自然，不要使用「吾」、「汝」等文言文，但要保持神明的威嚴或慈悲感。
回答長度約 150-200 字。"""

        try:
            response = self.gpt_client.ask(
                system_prompt=system_prompt,
                user_prompt=f"請為 {user_name} 解讀這個擲筊結果。",
                temperature=0.7,
                max_tokens=500
            )
            return response
        except Exception as e:
            print(f"生成解讀失敗: {e}")
            return "我此刻感應微弱，請稍後再試。"

    def generate_followup_response(self, tone_config: Dict[str, str], user_name: str, question: str, history: List[Dict[str, str]]) -> str:
        """
        生成持續對話回應（付費版）
        
        Args:
            tone_config: 語氣配置
            user_name: 用戶姓名
            question: 用戶的新問題
            history: 對話歷史
            
        Returns:
            生成的回應
        """
        # 構建歷史對話文本
        history_text = ""
        for msg in history[-5:]:  # 只取最近 5 條
            role = "信眾" if msg["role"] == "user" else "神明"
            history_text += f"{role}: {msg['content']}\n"
            
        system_prompt = f"""你現在扮演 {tone_config['name']}。
你的語氣風格是：{tone_config['style']}。
你的關鍵詞是：{tone_config['keywords']}。
你的說話範例：{tone_config['example']}。

你正在與信眾 {user_name} 進行對話。
之前的對話記錄：
{history_text}

信眾的新問題：{question}

請根據神明的身份和之前的擲筊結果，回答信眾的問題。
回答應具有指引性、慈悲心或威嚴感（視神明身份而定）。
請使用現代白話文，語氣親切自然，不要使用「吾」、「汝」等文言文。
回答長度約 100-150 字。"""

        try:
            response = self.gpt_client.ask(
                system_prompt=system_prompt,
                user_prompt=f"請回答 {user_name} 的問題。",
                temperature=0.7,
                max_tokens=300
            )
            return response
        except Exception as e:
            print(f"生成回應失敗: {e}")
            return "我此刻感應微弱，請稍後再試。"
