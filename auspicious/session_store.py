"""
黃道吉日會話存儲
使用 Redis 管理會話狀態
"""

from typing import Optional
from shared.session_store import BaseSessionStore
from auspicious.agent import AuspiciousSession


class AuspiciousSessionStore(BaseSessionStore):
    """黃道吉日會話存儲"""

    def __init__(self):
        super().__init__(module_name="auspicious")

    def load_session(
        self, version: str, session_id: str
    ) -> Optional[AuspiciousSession]:
        """載入會話"""
        data = self.load(version, session_id)
        if data:
            return AuspiciousSession.from_dict(data)
        return None

    def save_session(self, version: str, session_id: str, session: AuspiciousSession):
        """保存會話"""
        self.save(version, session_id, session.to_dict())


# 全域單例
_session_store = None


def get_session_store() -> AuspiciousSessionStore:
    """獲取會話存儲實例（單例模式）"""
    global _session_store
    if _session_store is None:
        _session_store = AuspiciousSessionStore()
    return _session_store
