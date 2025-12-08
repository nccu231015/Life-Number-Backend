"""
擲筊神諭 API Blueprint
提供擲筊占卜的 API 端點
"""

from flask import Blueprint, request, jsonify
import uuid

from divination.agent import DivinationSession, DivinationAgent, DivinationState
from divination.session_store import get_session_store
from divination.modules.divination_data import (
    BASIC_INFO_ERROR,
    DIVINATION_RESULT_HOLY,
    DIVINATION_RESULT_LAUGHING,
    DIVINATION_RESULT_NEGATIVE,
    PAID_TONE_PROMPTS,
    THREE_CAST_INTERPRETATIONS,
)

# 創建 Blueprint
divination_bp = Blueprint("divination", __name__, url_prefix="/divination")

# 免費版語氣配置
FREE_TONE_PROMPTS = {"friendly": "親切版", "caring": "貼心版", "ritual": "儀式感"}

# 免費版語氣問候語（用戶提供的文案）
FREE_TONE_GREETINGS = {
    "friendly": """歡迎來到《擲筊神諭 AI 小神桌》🌺
最近有什麼想問的嗎？感情、工作，或只是想看運勢都可以～
把你的問題交給我，我幫你擲筊看看神明怎麼說 🙌

請告訴我你的姓名、性別與生日。
例如：王小明 男 1990/07/12""",
    "caring": """親愛的旅人，歡迎回到這座安靜的小神桌🌿擲筊是一份溫柔的指引，不是急著求答案，而是讓心找到方向。
你可以慢慢說，我會替你擲出屬於你的啟示。

請告訴我你的姓名、性別與生日。
例如：王小明 男 1990/07/12""",
    "ritual": """歡迎步入《擲筊神諭之殿》🕯️
每一筊都象徵著神意的回響。
準備好後，把你的基本資訊告訴我，我將為你啟動占筊儀式。

請告訴我你的姓名、性別與生日。
例如：王小明 男 1990/07/12""",
}

# 未選擇語氣的提示
NO_TONE_MESSAGE = """小提醒 🌟：請先選擇您想要的對話語氣，
這樣我才能用最適合的方式替您擲筊並解讀指引 💫
🔸請選擇：「friendly / caring / ritual」"""

# 基本資訊提交成功的回應（包含 {name} 佔位符）
BASIC_INFO_SUCCESS = {
    "friendly": """{name}，收到你的資料囉 🌿
接下來只差最後一步，就能幫你擲筊啦～
你想問的事情是什麼呢？
可以是感情、工作、合作、選擇題、糾結的事，或是單純想知道方向也可以。
把你的問題告訴我，我會替你擲筊看看神明怎麼回應 ✨""",
    "caring": """{name}，謝謝你分享這些資訊 🌜
下一步，我需要知道你此刻真正想尋求的答案是什麼。
最近是否有某件事讓你反覆思考？
或是你想確認某個方向、關係、決定？
請把你想詢問的內容告訴我，
我會以你的心念為中心替你擲筊，
並解讀神意想給你的提示與安定 ✨""",
    "ritual": """{name}，你的基本資訊已備妥 🕯️
在啟動占筊儀式之前，還有一項關鍵內容需要你說出。
請告訴我你此刻想向神明請示的問題。
可以是一段困惑、一道選擇、一份祈願，
只要你真實地說出來，它就會在筊落下時得到回應。
當你準備好問題後，我將正式為你擲筊，
並解讀其中的神諭與啟示 ✨""",
}

# ========== 工具函數 ==========


def determine_combination_type(results):
    """判斷三次擲筊的組合類型"""
    holy_count = results.count("holy")
    negative_count = results.count("negative")
    laughing_count = results.count("laughing")

    # 三個相同
    if holy_count == 3:
        return "holy_holy_holy"
    if negative_count == 3:
        return "negative_negative_negative"
    if laughing_count == 3:
        return "laughing_laughing_laughing"

    # 兩個相同
    if holy_count == 2 and negative_count == 1:
        return "holy_holy_negative"
    if holy_count == 2 and laughing_count == 1:
        return "holy_holy_laughing"
    if negative_count == 2 and holy_count == 1:
        return "negative_negative_holy"
    if negative_count == 2 and laughing_count == 1:
        return "negative_negative_laughing"
    if laughing_count == 2 and holy_count == 1:
        return "laughing_laughing_holy"
    if laughing_count == 2 and negative_count == 1:
        return "laughing_laughing_negative"

    # 三象齊聚（各一個）
    return "mixed_all_three"


def get_session_by_id(version: str, session_id: str):
    """根據 session_id 從 Redis 獲取會話"""
    session_store = get_session_store()
    return session_store.load_session(version, session_id)


def save_and_return(
    version: str, session_id: str, div_session: DivinationSession, response_data: dict
):
    """保存會話到 Redis 並返回 JSON 響應"""
    session_store = get_session_store()
    session_store.save_session(version, session_id, div_session)
    return jsonify(response_data)


# ========== 處理函數 ==========


def handle_init_with_tone(version: str):
    """初始化對話並使用指定語氣"""
    data = request.get_json()
    tone = data.get("tone")

    # 驗證語氣
    if version == "free":
        if not tone or tone not in FREE_TONE_PROMPTS:
            return jsonify(
                {
                    "error": "無效的語氣選擇",
                    "message": NO_TONE_MESSAGE,
                    "valid_tones": list(FREE_TONE_PROMPTS.keys()),
                }
            ), 400
        greeting = FREE_TONE_GREETINGS[tone]
    else:  # paid
        if not tone or tone not in PAID_TONE_PROMPTS:
            # 默認使用關聖帝君
            tone = "guan_gong"

        tone_config = PAID_TONE_PROMPTS[tone]
        greeting = f"""{tone_config["greeting"]}
        
請告訴我你的姓名、性別與生日。
例如：王小明 男 1990/07/12"""

    # 創建新會話
    session_id = str(uuid.uuid4())
    div_session = DivinationSession(session_id)
    div_session.tone = tone
    div_session.state = DivinationState.WAITING_BASIC_INFO

    # 記錄助手回應
    div_session.add_message("assistant", greeting)

    # 返回響應
    response_data = {
        "session_id": session_id,
        "response": greeting,
        "state": div_session.state.value,
    }

    return save_and_return(version, session_id, div_session, response_data)


def handle_chat(version: str):
    """處理對話互動"""
    data = request.get_json()
    session_id = data.get("session_id")
    message = data.get("message", "").strip()

    # 驗證 session_id
    if not session_id:
        return jsonify({"error": "缺少 session_id"}), 400

    # 載入會話
    div_session = get_session_by_id(version, session_id)
    if not div_session:
        return jsonify({"error": "會話不存在或已過期"}), 404

    # 記錄用戶輸入
    div_session.add_message("user", message)

    # 根據當前狀態處理
    if div_session.state == DivinationState.WAITING_BASIC_INFO:
        # 使用 AI 提取基本資訊
        agent = DivinationAgent()
        extracted = agent.extract_basic_info(message)

        # 驗證是否提取成功
        if extracted["name"] and extracted["gender"] and extracted["birthdate"]:
            # 保存資訊
            div_session.user_name = extracted["name"]
            div_session.user_gender = extracted["gender"]
            div_session.birthdate = extracted["birthdate"]
            div_session.state = DivinationState.WAITING_QUESTION

            # 根據語氣返回成功訊息
            tone = div_session.tone
            if version == "free":
                response_text = BASIC_INFO_SUCCESS[tone].format(name=extracted["name"])
            else:
                # 付費版成功訊息
                response_text = f"""{extracted["name"]}，資料已確認。
請告訴我你此刻想向神明請示的問題。
我將為你擲筊，指點迷津。"""

            # 記錄助手回應
            div_session.add_message("assistant", response_text)

            response_data = {
                "session_id": session_id,
                "response": response_text,
                "state": div_session.state.value,
            }
        else:
            # 格式錯誤，返回錯誤訊息
            tone = div_session.tone
            if version == "free":
                response_text = BASIC_INFO_ERROR[tone]
            else:
                response_text = """資料不完整。請重新提供「姓名、性別、生日」，以便我為你啟動儀式。"""

            # 記錄助手回應
            div_session.add_message("assistant", response_text)

            response_data = {
                "session_id": session_id,
                "response": response_text,
                "state": div_session.state.value,
            }

        return save_and_return(version, session_id, div_session, response_data)

    elif div_session.state == DivinationState.WAITING_QUESTION:
        # 保存用戶問題
        div_session.question = message
        div_session.state = DivinationState.DIVINING

        # 根據結果選擇對應的回應文案
        tone = div_session.tone
        name = div_session.user_name

        if version == "free":
            # 免費版：單次擲筊
            import random

            result = random.choice(["holy", "laughing", "negative"])
            div_session.divination_result = result

            if result == "holy":
                response_text = DIVINATION_RESULT_HOLY[tone].format(name=name)
            elif result == "laughing":
                response_text = DIVINATION_RESULT_LAUGHING[tone].format(name=name)
            else:  # negative
                response_text = DIVINATION_RESULT_NEGATIVE[tone].format(name=name)

            # 完成擲筊
            div_session.state = DivinationState.COMPLETED

            # 記錄助手回應
            div_session.add_message("assistant", response_text)

            response_data = {
                "session_id": session_id,
                "response": response_text,
                "state": div_session.state.value,
                "question": message,
                "divination_result": result,
            }
        else:
            # 付費版：擲三次
            import random

            results = [
                random.choice(["holy", "laughing", "negative"]) for _ in range(3)
            ]
            div_session.divination_results = results

            # 判斷組合類型
            combination_type = determine_combination_type(results)

            # 取得基礎解讀
            base_interpretation = THREE_CAST_INTERPRETATIONS[combination_type]

            # 使用 AI 生成解讀
            agent = DivinationAgent()
            tone_config = PAID_TONE_PROMPTS.get(tone, PAID_TONE_PROMPTS["guan_gong"])

            interpretation = agent.generate_three_cast_interpretation(
                tone_config,
                name,
                message,
                results,
                combination_type,
                base_interpretation,
            )

            # 添加持續提問引導
            ask_question = "\n\n如果有什麼還不清楚的，或是想再深入了解，請繼續提問。我會盡力為你解答。"
            response_text = f"{interpretation}{ask_question}"

            # 進入持續提問狀態
            div_session.state = DivinationState.ASKING_FOR_QUESTION

            # 記錄助手回應
            div_session.add_message("assistant", response_text)

            response_data = {
                "session_id": session_id,
                "response": response_text,
                "state": div_session.state.value,
                "question": message,
                "divination_results": results,  # 返回三次結果
                "combination_type": combination_type,
                "divination_result": combination_type,  # 向後相容
            }

        return save_and_return(version, session_id, div_session, response_data)

    elif div_session.state == DivinationState.ASKING_FOR_QUESTION:
        # 檢查用戶是否想結束對話
        no_question_keywords = [
            "沒有",
            "没有",
            "不用",
            "沒了",
            "没了",
            "好了",
            "謝謝",
            "谢谢",
            "感恩",
            "不需要",
            "不用了",
            "再見",
            "掰掰",
        ]
        if (
            any(keyword in message for keyword in no_question_keywords)
            and len(message) < 10
        ):
            # 結束對話
            div_session.state = DivinationState.COMPLETED
            response_text = "既然沒有其他問題，我就先退駕了。願你心存善念，平安喜樂。"

            div_session.add_message("assistant", response_text)

            response_data = {
                "session_id": session_id,
                "response": response_text,
                "state": div_session.state.value,
            }
            return save_and_return(version, session_id, div_session, response_data)

        # 繼續對話
        agent = DivinationAgent()
        tone = div_session.tone
        tone_config = PAID_TONE_PROMPTS.get(tone, PAID_TONE_PROMPTS["guan_gong"])

        response_text = agent.generate_followup_response(
            tone_config,
            div_session.user_name,
            message,
            div_session.conversation_history,
        )

        # 記錄助手回應
        div_session.add_message("assistant", response_text)

        response_data = {
            "session_id": session_id,
            "response": response_text,
            "state": div_session.state.value,
        }

        return save_and_return(version, session_id, div_session, response_data)

    return jsonify(
        {"error": "此狀態尚未實作", "current_state": div_session.state.value}
    ), 501


def handle_reset(version: str):
    """重置會話"""
    data = request.get_json()
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "缺少 session_id"}), 400

    # 刪除會話
    session_store = get_session_store()
    key = session_store._make_key(version, session_id)
    session_store.redis_client.delete(key)

    return jsonify({"success": True, "message": "會話已重置"})


# ========== 免費版路由 ==========


@divination_bp.route("/free/api/init_with_tone", methods=["POST"])
def free_init():
    return handle_init_with_tone("free")


@divination_bp.route("/free/api/chat", methods=["POST"])
def free_chat():
    return handle_chat("free")


@divination_bp.route("/free/api/reset", methods=["POST"])
def free_reset():
    return handle_reset("free")


# ========== 付費版路由 ==========


@divination_bp.route("/paid/api/init_with_tone", methods=["POST"])
def paid_init():
    return handle_init_with_tone("paid")


@divination_bp.route("/paid/api/chat", methods=["POST"])
def paid_chat():
    return handle_chat("paid")


@divination_bp.route("/paid/api/reset", methods=["POST"])
def paid_reset():
    return handle_reset("paid")
