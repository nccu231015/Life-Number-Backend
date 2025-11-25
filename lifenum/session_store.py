"""
Session 存儲管理模組
處理 ConversationSession 的序列化、反序列化和 Redis 存儲
"""

import json
from typing import Optional, Dict, Any
from datetime import datetime
from .redis_client import get_redis_client, SESSION_TTL
from .agent import ConversationSession, ConversationState


class SessionStore:
    """Session 存儲管理器"""
    
    def __init__(self):
        self.redis_client = get_redis_client()
    
    def _make_key(self, version: str, session_id: str) -> str:
        """
        生成 Redis key
        格式: session:{version}:{session_id}
        """
        return f"session:{version}:{session_id}"
    
    def save(self, version: str, session_id: str, conv_session: ConversationSession) -> bool:
        """
        保存會話到 Redis
        
        Args:
            version: 版本（'free' 或 'paid'）
            session_id: 會話 ID
            conv_session: ConversationSession 實例
            
        Returns:
            bool: 是否保存成功
        """
        try:
            key = self._make_key(version, session_id)
            data = self._serialize(conv_session)
            ttl = SESSION_TTL.get(version, SESSION_TTL['free'])
            
            # 使用 setex 設定帶有過期時間的值
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(data, ensure_ascii=False)
            )
            
            print(f"[Redis] 保存會話: {key}, TTL: {ttl}s")
            return True
            
        except Exception as e:
            print(f"[Redis] 保存會話失敗: {e}")
            return False
    
    def load(self, version: str, session_id: str) -> Optional[ConversationSession]:
        """
        從 Redis 載入會話
        
        Args:
            version: 版本（'free' 或 'paid'）
            session_id: 會話 ID
            
        Returns:
            ConversationSession 實例或 None
        """
        try:
            key = self._make_key(version, session_id)
            data_str = self.redis_client.get(key)
            
            if data_str is None:
                print(f"[Redis] 會話不存在: {key}")
                return None
            
            data = json.loads(data_str)
            conv_session = self._deserialize(data)
            
            print(f"[Redis] 載入會話: {key}")
            return conv_session
            
        except Exception as e:
            print(f"[Redis] 載入會話失敗: {e}")
            return None
    
    def delete(self, version: str, session_id: str) -> bool:
        """
        刪除會話
        
        Args:
            version: 版本（'free' 或 'paid'）
            session_id: 會話 ID
            
        Returns:
            bool: 是否刪除成功
        """
        try:
            key = self._make_key(version, session_id)
            result = self.redis_client.delete(key)
            print(f"[Redis] 刪除會話: {key}, 結果: {result}")
            return result > 0
            
        except Exception as e:
            print(f"[Redis] 刪除會話失敗: {e}")
            return False
    
    def exists(self, version: str, session_id: str) -> bool:
        """
        檢查會話是否存在
        
        Args:
            version: 版本（'free' 或 'paid'）
            session_id: 會話 ID
            
        Returns:
            bool: 是否存在
        """
        try:
            key = self._make_key(version, session_id)
            return self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"[Redis] 檢查會話存在失敗: {e}")
            return False
    
    def get_ttl(self, version: str, session_id: str) -> int:
        """
        獲取會話剩餘過期時間
        
        Args:
            version: 版本（'free' 或 'paid'）
            session_id: 會話 ID
            
        Returns:
            int: 剩餘秒數，-1 表示永不過期，-2 表示不存在
        """
        try:
            key = self._make_key(version, session_id)
            return self.redis_client.ttl(key)
        except Exception as e:
            print(f"[Redis] 獲取 TTL 失敗: {e}")
            return -2
    
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
            
            # 時間戳記
            "updated_at": datetime.now().isoformat(),
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
_session_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """
    獲取 SessionStore 實例（單例模式）
    """
    global _session_store
    
    if _session_store is None:
        _session_store = SessionStore()
    
    return _session_store

