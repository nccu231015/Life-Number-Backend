"""
黃道吉日 API Blueprint
提供黃道吉日查詢的 API 端點
"""

from flask import Blueprint, request, jsonify
from typing import Optional
import uuid

from auspicious.agent import AuspiciousAgent, AuspiciousSession, AuspiciousState
from auspicious.session_store import get_session_store


# 創建 Blueprint
auspicious_bp = Blueprint("auspicious", __name__, url_prefix="/auspicious")

# 創建 Session Store
session_store = get_session_store()

# 創建 Agent
agent = AuspiciousAgent()

# ========== 語氣配置 ==========

# 免費版語氣配置（3種）
FREE_TONE_PROMPTS = {"friendly": "親切版", "caring": "貼心版", "ritual": "儀式感"}

FREE_TONE_GREETINGS = {
    "friendly": """歡迎來到《黃道吉日 AI 小日曆》📅
最近有什麼重要的事情想安排嗎？搬家、結婚、開業，或只是想找個順利一點的日子都可以～
把你的計畫放心交給我，我會先記下你的資料，再幫你從黃曆裡找出適合的好日子 🙌

請告訴我你的姓名、性別與生日。
例如：王小明 男 1990/07/12""",
    "caring": """親愛的旅人，歡迎回到這本為你打開的吉日曆 🌿
擇日是一份溫柔的照顧，不是迷信數字，
而是替你的重要時刻多一層安心。
你可以慢慢說，我會依照你的資料，
幫你找出最貼近你心意的好日子。

請告訴我你的姓名、性別與生日。
例如：王小明 男 1990/07/12""",
    "ritual": """歡迎步入《黃道吉日擇日之殿》🕯
日辰與星象皆有其節律，
每一個被選中的日子都承載著特殊的氣場。
準備好後，把你的基本資訊告訴我，
我將為你啟動正式的擇日流程。

請告訴我你的姓名、性別與生日。
例如：王小明 男 1990/07/12""",
}

# 未選擇語氣的提示
NO_TONE_MESSAGE = """小提醒 🌟：請先選擇您想要的對話語氣，
這樣我才能用最適合你的方式替你查詢黃道吉日並說明建議 👇
🔸請選擇：「friendly / caring / ritual」"""

# 基本資訊錯誤提示
BASIC_INFO_ERROR_TEMPLATES = {
    "friendly": """噢～我好像還沒收到完整的資料呢 😅
請再幫我輸入一次「姓名、性別、生日」喔～
格式像這樣：
📝 王小明 男 1990/07/12
　 或 李小華 女 1985/03/25
重新給我一次，我就能繼續幫你查黃道吉日啦 🌟""",
    "caring": """我收到你的訊息了，但好像還少了一些重要資訊 🌜
為了能根據你的命盤與節氣精準挑選吉日，需要你再提供一次：「姓名、性別、生日」。
範例：
🕊 王小明 男 1990/07/12
🕊 李小華 女 1985/03/25
當我收到完整資料後，就能正式替你查詢並解讀黃道吉日。""",
    "ritual": """我已聽見你的回應，但擇日儀式仍需要更完整的資料才能啟動 🕯
請重新提供「姓名、性別、生日」，以正式開啟黃道吉日的擇日流程。
請以以下格式重新輸入：
◆ 王小明 男 1990/07/12
◆ 李小華 女 1985/03/25
當資料齊備後，我便能為你開啟通往吉日之門 ✨""",
}

# 基本資訊成功後的提示
BASIC_INFO_SUCCESS = {
    "friendly": """{name}，收到你的資料囉 🌿
接下來只差最後一步，就能幫你挑吉日啦～
你想安排的事情是什麼呢？
可以是搬家、結婚、簽約、開業、手術，或是單純想找個適合出門辦事的日子都可以。
把你打算做的事，還有大概的時間區間告訴我，
我會替你從黃道吉日中篩出幾個適合你的選擇 ✨""",
    "caring": """{name}，謝謝你分享這些資訊 🌜
下一步，我想知道你此刻真正想安排好的是哪一件事。
最近是否有什麼重要計畫，讓你想選一個比較順利、安心的日子？
或是你在猶豫何時適合搬家、談合作、舉辦儀式？
請把你準備進行的事情與大概時程告訴我，
我會以你的需求為中心替你挑選黃道吉日，
並說明每個日子想帶給你的提醒與安穩 ✨""",
    "ritual": """{name}，你的基本資訊已備妥 🕯
在啟動黃道吉日擇日儀式之前，還有一項關鍵內容需要你明確說出。
請告訴我你此刻要為哪一件事情擇日。
可以是一場婚禮、一樁簽約、一趟搬遷，或是一份重要啟程。
只要你誠實地描述清楚，它就會在日期與時辰的排列中得到回應。
當你準備好事情與大致時間範圍後，我將正式為你開啟擇日流程，
並解讀其中對你最有利的吉日與提醒 ✨""",
}

# ========== 分類定義 ==========

# 五種分類配置
CATEGORIES = {
    "daily_life": {
        "name": "生活日常",
        "examples": "出門治公、購物、聚會",
        "description": "出行、出火、捕捉、畋獵、取魚、結網、沐浴、會親友、進人口、納財、牧養、平治道塗、交車、入殮、破土、火化、安葬、立碑、移柩等日常生活及喪葬活動",
    },
    "family_home": {
        "name": "家庭居所",
        "examples": "搬家、簽約、動工",
        "description": "入宅、安床、作灶、動土、上樑、裁衣、破屋壞垣等居家相關",
    },
    "relationship": {
        "name": "感情人際",
        "examples": "約會、告白、合作",
        "description": "納采、嫁娶、冠笄等婚嫁感情相關",
    },
    "celebration": {
        "name": "喜慶大事",
        "examples": "婚嫁、慶典、開業",
        "description": "祭祀、祈福、開光、設醮、齋醮、安香等祭祀祈福儀式",
    },
    "work_career": {
        "name": "工作事業",
        "examples": "開工、會議、啟動計劃",
        "description": "開市等商業經營相關",
    },
}

# 選擇分類後的引導訊息（成功收到基本資訊後）
CATEGORY_SELECTION_PROMPT = {
    "friendly": """好的！接下來請選擇你想查詢的分類，並選擇一個日期：

🔸 生活日常 - 出門治公、購物、聚會
🔸 家庭居所 - 搬家、簽約、動工
🔸 感情人際 - 約會、告白、合作
🔸 喜慶大事 - 婚嫁、慶典、開業
🔸 工作事業 - 開工、會議、啟動計劃

請選擇分類和日期（例如：「家庭居所，2025-12-15」）～""",
    "caring": """接下來，請選擇最符合你需求的分類，並選擇一個日期：

🕊 生活日常 - 出門治公、購物、聚會
🕊 家庭居所 - 搬家、簽約、動工
🕊 感情人際 - 約會、告白、合作
🕊 喜慶大事 - 婚嫁、慶典、開業
🕊 工作事業 - 開工、會議、啟動計劃

請告訴我分類和日期（例如：「家庭居所，12月15日」）✨""",
    "ritual": """請從以下五個時辰領域中，選擇與你所需最為相應的一項，並選定日期：

◆ 生活日常 - 出門治公、購物、聚會
◆ 家庭居所 - 搬家、簽約、動工
◆ 感情人際 - 約會、告白、合作
◆ 喜慶大事 - 婚嫁、慶典、開業
◆ 工作事業 - 開工、會議、啟動計劃

請示知分類與日期（例如：「家庭居所，2025年12月15日」）🕯""",
}

# ========== 工具函數 ==========


def get_session_by_id(version: str, session_id: str) -> Optional[AuspiciousSession]:
    """根據 session_id 從 Redis 獲取會話"""
    return session_store.load_session(version, session_id)


def save_and_return(
    version: str,
    session_id: str,
    auspicious_session: AuspiciousSession,
    response_data: dict,
):
    """保存會話到 Redis 並返回 JSON 響應"""
    session_store.save_session(version, session_id, auspicious_session)
    return jsonify(response_data)


# ========== 處理函數 ==========


def handle_init_with_tone(version: str):
    """初始化對話並使用指定語氣"""
    data = request.get_json()
    tone = data.get("tone")

    # 驗證語氣
    if version == "free":
        if not tone or tone not in FREE_TONE_PROMPTS:
            return (
                jsonify(
                    {
                        "error": "無效的語氣選擇",
                        "message": NO_TONE_MESSAGE,
                        "valid_tones": list(FREE_TONE_PROMPTS.keys()),
                    }
                ),
                400,
            )
        greeting = FREE_TONE_GREETINGS[tone]
    else:
        # 付費版（暫未實作）
        return jsonify({"error": "付費版尚未開放"}), 400

    # 創建新會話
    session_id = str(uuid.uuid4())
    auspicious_session = AuspiciousSession(session_id)
    auspicious_session.tone = tone
    auspicious_session.state = AuspiciousState.WAITING_BASIC_INFO

    # 記錄助手回應
    auspicious_session.add_message("assistant", greeting)

    # 返回響應
    response_data = {
        "session_id": session_id,
        "response": greeting,
        "state": auspicious_session.state.value,
    }

    return save_and_return(version, session_id, auspicious_session, response_data)


def handle_chat(version: str):
    """處理對話互動"""
    data = request.get_json()
    session_id = data.get("session_id")
    message = data.get("message", "").strip()

    # 支持前端直接傳遞 category 和 selected_date
    category = data.get("category")  # 前端按鈕可以直接傳
    selected_date = data.get("selected_date")  # 前端日期選擇器傳 YYYY-MM-DD

    # 驗證 session_id
    if not session_id:
        return jsonify({"error": "缺少 session_id"}), 400

    # 載入會話
    auspicious_session = get_session_by_id(version, session_id)
    if not auspicious_session:
        return jsonify({"error": "會話不存在或已過期"}), 404

    # 記錄用戶輸入
    if message:
        auspicious_session.add_message("user", message)

    # 根據當前狀態處理
    if auspicious_session.state == AuspiciousState.WAITING_BASIC_INFO:
        # 使用 AI 提取基本資訊
        extracted = agent.extract_basic_info(message)

        # 驗證是否提取成功
        if extracted["name"] and extracted["gender"] and extracted["birthdate"]:
            # 保存資訊
            auspicious_session.user_name = extracted["name"]
            auspicious_session.user_gender = extracted["gender"]
            auspicious_session.birthdate = extracted["birthdate"]
            auspicious_session.state = AuspiciousState.WAITING_CATEGORY_AND_DATE

            # 返回分類選擇提示
            tone = auspicious_session.tone
            response_text = CATEGORY_SELECTION_PROMPT[tone]

            # 記錄助手回應
            auspicious_session.add_message("assistant", response_text)

            response_data = {
                "session_id": session_id,
                "response": response_text,
                "state": auspicious_session.state.value,
                "categories": CATEGORIES,  # 返回分類供前端顯示
            }
        else:
            # 格式錯誤，返回錯誤訊息
            tone = auspicious_session.tone
            response_text = BASIC_INFO_ERROR_TEMPLATES[tone]

            # 記錄助手回應
            auspicious_session.add_message("assistant", response_text)

            response_data = {
                "session_id": session_id,
                "response": response_text,
                "state": auspicious_session.state.value,
            }

        return save_and_return(version, session_id, auspicious_session, response_data)

    elif auspicious_session.state == AuspiciousState.WAITING_CATEGORY_AND_DATE:
        # 處理分類和日期選擇
        # 前端可以通過按鈕直接傳遞 category 和 selected_date
        # 或用戶可以文字輸入（例如：「家庭居所，2025-12-15」）

        if category and selected_date:
            # 前端直接傳遞
            auspicious_session.category = category
            auspicious_session.selected_date = selected_date
        else:
            # TODO: 使用 AI 從文字中提取分類和日期
            # 目前簡單處理：假設用戶輸入格式正確
            if "，" in message or "," in message:
                parts = message.replace("，", ",").split(",")
                if len(parts) >= 2:
                    # 嘗試匹配分類
                    for cat_key, cat_info in CATEGORIES.items():
                        if cat_info["name"] in parts[0]:
                            auspicious_session.category = cat_key
                            break
                    auspicious_session.selected_date = parts[1].strip()

        if auspicious_session.category and auspicious_session.selected_date:
            auspicious_session.state = AuspiciousState.WAITING_SPECIFIC_QUESTION

            category_name = CATEGORIES[auspicious_session.category]["name"]
            response_text = f"好的！你選擇了「{category_name}」，日期是「{auspicious_session.selected_date}」。\n\n請具體描述你想做的事情，例如：搬家到新家、簽約買房、開業典禮等。"

            auspicious_session.add_message("assistant", response_text)

            response_data = {
                "session_id": session_id,
                "response": response_text,
                "state": auspicious_session.state.value,
                "category": auspicious_session.category,
                "selected_date": auspicious_session.selected_date,
            }
        else:
            response_text = "請選擇分類並告訴我日期～"
            auspicious_session.add_message("assistant", response_text)

            response_data = {
                "session_id": session_id,
                "response": response_text,
                "state": auspicious_session.state.value,
            }

        return save_and_return(version, session_id, auspicious_session, response_data)

    elif auspicious_session.state == AuspiciousState.WAITING_SPECIFIC_QUESTION:
        # 收到具體問題描述
        auspicious_session.specific_question = message
        auspicious_session.state = AuspiciousState.PROVIDING_DATES

        # TODO: 實作黃曆查詢和 LLM 推薦邏輯
        # 目前先返回簡單訊息
        response_text = f"收到！我會為你查詢「{message}」在「{auspicious_session.selected_date}」這天是否適合。\n\n（此功能正在開發中，敬請期待 🚧）"

        auspicious_session.add_message("assistant", response_text)
        auspicious_session.state = AuspiciousState.COMPLETED

        response_data = {
            "session_id": session_id,
            "response": response_text,
            "state": auspicious_session.state.value,
            "specific_question": message,
        }

        return save_and_return(version, session_id, auspicious_session, response_data)

    return (
        jsonify(
            {
                "error": "此狀態尚未實作",
                "current_state": auspicious_session.state.value,
            }
        ),
        501,
    )


def handle_reset(version: str):
    """重置會話"""
    data = request.get_json()
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "缺少 session_id"}), 400

    # 刪除會話
    key = session_store._make_key(version, session_id)
    session_store.redis_client.delete(key)

    return jsonify({"success": True, "message": "會話已重置"})


# ========== 免費版路由 ==========


@auspicious_bp.route("/free/api/init_with_tone", methods=["POST"])
def free_init():
    return handle_init_with_tone("free")


@auspicious_bp.route("/free/api/chat", methods=["POST"])
def free_chat():
    return handle_chat("free")


@auspicious_bp.route("/free/api/reset", methods=["POST"])
def free_reset():
    return handle_reset("free")
