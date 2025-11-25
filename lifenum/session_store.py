"""
生命靈數 Session 存儲模組
處理 ConversationSession 的序列化、反序列化和 Redis 存儲
"""

from typing import Optional, Dict, Any
from datetime import datetime
from shared.session_store import BaseSessionStore
from .agent import ConversationSession, ConversationState


class LifeNumSessionStore(BaseSessionStore):
    """生命靈數 Session 存儲管理器"""
    
    def __init__(self):
        super().__init__(module_name="lifenum")
    
    def save_session(self, version: str, session_id: str, conv_session: ConversationSession) -> bool:
        """
        保存生命靈數會話
        
        Args:
            version: 版本（'free' 或 'paid'）
            session_id: 會話 ID
            conv_session: ConversationSession 實例
            
        Returns:
            bool: 是否保存成功
        """
        data = self._serialize(conv_session)
        return self.save(version, session_id, data)
    
    def load_session(self, version: str, session_id: str) -> Optional[ConversationSession]:
        """
        從 Redis 載入生命靈數會話
        
        Args:
            version: 版本（'free' 或 'paid'）
            session_id: 會話 ID
            
        Returns:
            ConversationSession 實例或 None
        """
        data = self.load(version, session_id)
        if data is None:
            return None
        
        return self._deserialize(data)
    
    def _serialize(self, conv_session: ConversationSession) -> Dict[str, Any]:
        """
        序列化 ConversationSession 為字典
        """
        return {
            "session_id": conv_session.session_id,
            "state": conv_session.state.value,
            "user_name": conv_session.user_name,
            "user_gender": conv_session.user_gender,
            "birthdate": conv_session.birthdate,
            "english_name": conv_session.english_name,
            "user_purpose": conv_session.user_purpose,
            "suggested_module": conv_session.suggested_module,
            "selected_module": conv_session.selected_module,
            "current_module": conv_session.current_module,
            "tone": conv_session.tone,
            
            # 對話歷史和記憶
            "conversation_history": conv_session.conversation_history,
            "memory": conv_session.memory,
            "conversation_count": conv_session.conversation_count,
            "max_memory_turns": conv_session.max_memory_turns,
            
            # 核心生命靈數相關
            "core_number": conv_session.core_number,
            "selected_category": conv_session.selected_category,
            "user_age": conv_session.user_age,
            
            # 各模組計算結果
            "birthday_number": conv_session.birthday_number,
            "grid_result": conv_session.grid_result,
            "year_number": conv_session.year_number,
            "soul_number": conv_session.soul_number,
            "personality_number": conv_session.personality_number,
            "expression_number": conv_session.expression_number,
            "maturity_number": conv_session.maturity_number,
            "challenge_number": conv_session.challenge_number,
            "karma_numbers": conv_session.karma_numbers if hasattr(conv_session, 'karma_numbers') else None,
        }
    
    def _deserialize(self, data: Dict[str, Any]) -> ConversationSession:
        """
        反序列化字典為 ConversationSession
        """
        session_id = data.get("session_id", "unknown")
        conv_session = ConversationSession(session_id)
        
        # 基本資訊
        conv_session.state = ConversationState(data.get("state", "init"))
        conv_session.user_name = data.get("user_name")
        conv_session.user_gender = data.get("user_gender")
        conv_session.birthdate = data.get("birthdate")
        conv_session.english_name = data.get("english_name")
        conv_session.user_purpose = data.get("user_purpose")
        conv_session.suggested_module = data.get("suggested_module")
        conv_session.selected_module = data.get("selected_module")
        conv_session.current_module = data.get("current_module")
        conv_session.tone = data.get("tone", "friendly")
        
        # 對話歷史和記憶
        conv_session.conversation_history = data.get("conversation_history", [])
        conv_session.memory = data.get("memory", [])
        conv_session.conversation_count = data.get("conversation_count", 0)
        conv_session.max_memory_turns = data.get("max_memory_turns", 50)
        
        # 核心生命靈數相關
        conv_session.core_number = data.get("core_number")
        conv_session.selected_category = data.get("selected_category")
        conv_session.user_age = data.get("user_age")
        
        # 各模組計算結果
        conv_session.birthday_number = data.get("birthday_number")
        conv_session.grid_result = data.get("grid_result")
        conv_session.year_number = data.get("year_number")
        conv_session.soul_number = data.get("soul_number")
        conv_session.personality_number = data.get("personality_number")
        conv_session.expression_number = data.get("expression_number")
        conv_session.maturity_number = data.get("maturity_number")
        conv_session.challenge_number = data.get("challenge_number")
        
        karma_numbers = data.get("karma_numbers")
        if karma_numbers is not None:
            conv_session.karma_numbers = karma_numbers
        
        return conv_session


# 全局實例
_session_store: Optional[LifeNumSessionStore] = None


def get_session_store() -> LifeNumSessionStore:
    """
    獲取 LifeNumSessionStore 實例（單例模式）
    """
    global _session_store
    
    if _session_store is None:
        _session_store = LifeNumSessionStore()
    
    return _session_store
