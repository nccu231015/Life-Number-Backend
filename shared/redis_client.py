"""
Redis 連線管理模組（共享）
"""

import os
import redis
from typing import Optional
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()

# Redis 連線配置（從環境變量讀取）
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'username': os.getenv('REDIS_USERNAME', 'default'),
    'password': os.getenv('REDIS_PASSWORD'),
    'decode_responses': True,  # 自動解碼為字串
    'socket_connect_timeout': 5,  # 連線超時
    'socket_timeout': 5,  # 操作超時
}

# Session TTL 配置（秒）
# 統一設定為 12 小時（從環境變量讀取）
SESSION_TTL = {
    'free': int(os.getenv('SESSION_TTL', 43200)),   # 12小時
    'paid': int(os.getenv('SESSION_TTL', 43200)),   # 12小時
}

# 全局 Redis 客戶端實例
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """
    獲取 Redis 客戶端實例（單例模式）
    """
    global _redis_client
    
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(**REDIS_CONFIG)
            # 測試連線
            _redis_client.ping()
            print("✅ Redis 連線成功")
        except redis.ConnectionError as e:
            print(f"❌ Redis 連線失敗: {e}")
            raise
        except Exception as e:
            print(f"❌ Redis 初始化錯誤: {e}")
            raise
    
    return _redis_client


def close_redis_client():
    """
    關閉 Redis 連線
    """
    global _redis_client
    if _redis_client:
        _redis_client.close()
        _redis_client = None
        print("✅ Redis 連線已關閉")


def test_redis_connection() -> bool:
    """
    測試 Redis 連線
    """
    try:
        client = get_redis_client()
        client.ping()
        print("✅ Redis 連線測試成功")
        return True
    except Exception as e:
        print(f"❌ Redis 連線測試失敗: {e}")
        return False


if __name__ == "__main__":
    # 測試連線
    test_redis_connection()

