"""
Session 存儲管理模組（共享基礎設施）
提供通用的 Session 序列化和 Redis 存儲功能
"""

import json
from typing import Optional, Dict, Any
from datetime import datetime
from .redis_client import get_redis_client, SESSION_TTL


class BaseSessionStore:
    """基礎 Session 存儲管理器（可被各模組繼承）"""
    
    def __init__(self, module_name: str = "default"):
        """
        Args:
            module_name: 模組名稱（用於區分不同模組的 session key）
        """
        self.module_name = module_name
        self.redis_client = get_redis_client()
    
    def _make_key(self, version: str, session_id: str) -> str:
        """
        生成 Redis key
        格式: session:{module}:{version}:{session_id}
        """
        return f"session:{self.module_name}:{version}:{session_id}"
    
    def save(self, version: str, session_id: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        保存會話到 Redis
        
        Args:
            version: 版本（'free' 或 'paid'）
            session_id: 會話 ID
            data: 要保存的數據（字典格式）
            ttl: 過期時間（秒），None 則使用默認值
            
        Returns:
            bool: 是否保存成功
        """
        try:
            key = self._make_key(version, session_id)
            
            # 添加時間戳
            data['updated_at'] = datetime.now().isoformat()
            
            # 使用默認 TTL 或指定 TTL
            expire_time = ttl if ttl is not None else SESSION_TTL.get(version, SESSION_TTL['free'])
            
            # 使用 setex 設定帶有過期時間的值
            self.redis_client.setex(
                key,
                expire_time,
                json.dumps(data, ensure_ascii=False)
            )
            
            print(f"[Redis] 保存會話: {key}, TTL: {expire_time}s")
            return True
            
        except Exception as e:
            print(f"[Redis] 保存會話失敗: {e}")
            return False
    
    def load(self, version: str, session_id: str) -> Optional[Dict[str, Any]]:
        """
        從 Redis 載入會話
        
        Args:
            version: 版本（'free' 或 'paid'）
            session_id: 會話 ID
            
        Returns:
            字典數據或 None
        """
        try:
            key = self._make_key(version, session_id)
            data_str = self.redis_client.get(key)
            
            if data_str is None:
                print(f"[Redis] 會話不存在: {key}")
                return None
            
            data = json.loads(data_str)
            print(f"[Redis] 載入會話: {key}")
            return data
            
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
        
        Returns:
            int: 剩餘秒數，-1 表示永不過期，-2 表示不存在
        """
        try:
            key = self._make_key(version, session_id)
            return self.redis_client.ttl(key)
        except Exception as e:
            print(f"[Redis] 獲取 TTL 失敗: {e}")
            return -2

