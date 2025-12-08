"""
擲筊 Session 存儲模組
處理 DivinationSession 的序列化、反序列化和 Redis 存儲
"""

from typing import Optional, Dict, Any
from shared.session_store import BaseSessionStore
from .agent import DivinationSession, DivinationState


class DivinationSessionStore(BaseSessionStore):
    """擲筊 Session 存儲管理器"""

    def __init__(self):
        super().__init__(module_name="divination")

    def save_session(
        self, version: str, session_id: str, div_session: DivinationSession
    ) -> bool:
        """
        保存擲筊會話

        Args:
            version: 版本（'free' 或 'paid'）
            session_id: 會話 ID
            div_session: DivinationSession 實例

        Returns:
            bool: 是否保存成功
        """
        data = self._serialize(div_session)
        return self.save(version, session_id, data)

    def load_session(
        self, version: str, session_id: str
    ) -> Optional[DivinationSession]:
        """
        從 Redis 載入擲筊會話

        Args:
            version: 版本（'free' 或 'paid'）
            session_id: 會話 ID

        Returns:
            DivinationSession 實例或 None
        """
        data = self.load(version, session_id)
        if data is None:
            return None

        return self._deserialize(data)

    def _serialize(self, div_session: DivinationSession) -> Dict[str, Any]:
        """序列化 DivinationSession 為字典"""
        return {
            "session_id": div_session.session_id,
            "state": div_session.state.value,
            "user_name": div_session.user_name,
            "user_gender": div_session.user_gender,
            "birthdate": div_session.birthdate,
            "tone": div_session.tone,
            "question": div_session.question,
            "divination_result": div_session.divination_result,
            "divination_results": div_session.divination_results,  # 新增：三次結果
            "conversation_history": div_session.conversation_history,
        }

    def _deserialize(self, data: Dict[str, Any]) -> DivinationSession:
        """反序列化字典為 DivinationSession"""
        session_id = data.get("session_id", "unknown")
        div_session = DivinationSession(session_id)

        div_session.state = DivinationState(data.get("state", "init"))
        div_session.user_name = data.get("user_name")
        div_session.user_gender = data.get("user_gender")
        div_session.birthdate = data.get("birthdate")
        div_session.tone = data.get("tone", "friendly")
        div_session.question = data.get("question")
        div_session.divination_result = data.get("divination_result")
        div_session.divination_results = data.get(
            "divination_results", []
        )  # 新增：三次結果
        div_session.conversation_history = data.get("conversation_history", [])

        return div_session


# 全局實例
_session_store: Optional[DivinationSessionStore] = None


def get_session_store() -> DivinationSessionStore:
    """獲取 DivinationSessionStore 實例（單例模式）"""
    global _session_store

    if _session_store is None:
        _session_store = DivinationSessionStore()

    return _session_store
