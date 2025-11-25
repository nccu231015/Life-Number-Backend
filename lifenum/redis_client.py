"""
生命靈數模組的 Redis 客戶端（重新導出共享的 Redis 客戶端）
保持向後兼容性
"""

from shared.redis_client import get_redis_client, close_redis_client, test_redis_connection, SESSION_TTL

__all__ = ['get_redis_client', 'close_redis_client', 'test_redis_connection', 'SESSION_TTL']
