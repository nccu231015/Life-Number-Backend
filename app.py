"""
Life Number Backend - 主應用
使用模組化架構，支持多個獨立的功能模組
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

# 導入生命靈數 API Blueprint
from lifenum_api import lifenum_bp

# 導入天使數字 API Blueprint
from angelnum_api import angelnum_bp

# 導入擲筊 API Blueprint
from divination_api import divination_bp

# 測試 Redis 連線
from shared.redis_client import test_redis_connection

# 創建 Flask 應用
app = Flask(__name__)
app.secret_key = "unified-life-number-backend-2025"
CORS(app, supports_credentials=True)

# 註冊 Blueprints
app.register_blueprint(lifenum_bp)
app.register_blueprint(angelnum_bp)
app.register_blueprint(divination_bp)

# 測試 Redis 連線
print("\n" + "="*60)
print("🔌 正在連線 Redis...")
print("="*60)
if test_redis_connection():
    print("✅ Redis 已就緒，會話將存儲在 Redis 中")
else:
    print("⚠️  Redis 連線失敗，請檢查配置")
print("="*60 + "\n")

# ========== 通用路由 ==========
@app.route("/health")
def health():
    """健康檢查端點"""
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "modules": ["lifenum", "angelnum", "divination"]
    })

@app.route("/")
def index():
    """首頁 - API 信息"""
    return jsonify({
        "service": "Life Number Backend (Modular)",
        "version": "2.0.0",
        "architecture": "Blueprint-based modular architecture",
        "modules": {
            "lifenum": {
                "endpoints": {
                    "free": [
                        "/life/free/api/init_with_tone",
                        "/life/free/api/chat",
                        "/life/free/api/reset"
                    ],
                    "paid": [
                        "/life/paid/api/init_with_tone",
                        "/life/paid/api/chat",
                        "/life/paid/api/reset"
                    ]
                }
            },
            "angelnum": {
                "endpoints": {
                    "free": [
                        "/angel/free/api/init_with_tone",
                        "/angel/free/api/chat",
                        "/angel/free/api/reset"
                    ],
                    "paid": [
                        "/angel/paid/api/init_with_tone",
                        "/angel/paid/api/chat",
                        "/angel/paid/api/reset"
                    ]
                }
            },
            "divination": {
                "endpoints": {
                    "free": [
                        "/divination/free/api/init_with_tone",
                        "/divination/free/api/chat",
                        "/divination/free/api/reset"
                    ]
                }
            }
        },
        "shared_infrastructure": [
            "Redis Session Store",
            "GPT Client",
            "Session Management"
        ]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
