import os
from flask import Flask, jsonify
from flask_cors import CORS

# 導入 Blueprints
try:
    from lifenum_api import lifenum_bp
    from angelnum_api import angelnum_bp
    from divination_api import divination_bp
except ImportError as e:
    print(f"Warning: Failed to import blueprints: {e}")
    # 在測試環境中可能會失敗，這裡做簡單處理
    lifenum_bp = None
    angelnum_bp = None
    divination_bp = None


def create_app():
    app = Flask(__name__)

    # 配置 CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # 註冊 Blueprints
    if lifenum_bp:
        app.register_blueprint(lifenum_bp)
        print("Registered Blueprint: lifenum (prefix: /life)")

    if angelnum_bp:
        app.register_blueprint(angelnum_bp)
        print("Registered Blueprint: angelnum (prefix: /angel)")

    if divination_bp:
        app.register_blueprint(divination_bp)
        print("Registered Blueprint: divination (prefix: /divination)")

    @app.route("/", methods=["GET", "POST"])
    def index():
        return jsonify(
            {
                "status": "ok",
                "message": "Life Number Backend Unified API is running",
                "modules": {
                    "lifenum": bool(lifenum_bp),
                    "angelnum": bool(angelnum_bp),
                    "divination": bool(divination_bp),
                },
            }
        )

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "healthy"}), 200

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
