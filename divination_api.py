"""
擲筊神諭 API Blueprint
提供擲筊占卜的 API 端點
"""

from flask import Blueprint, request, jsonify
import uuid

from divination.agent import DivinationAgent, DivinationSession, DivinationState
from divination.session_store import get_session_store

# 創建 Blueprint
divination_bp = Blueprint('divination', __name__, url_prefix='/divination')

# 免費版語氣配置
FREE_TONE_PROMPTS = {
    "friendly": "親切版",
    "caring": "貼心版",
    "ritual": "儀式感"
}

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
例如：王小明 男 1990/07/12"""
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
並解讀其中的神諭與啟示 ✨"""
}

# 基本資訊格式錯誤的回應
BASIC_INFO_ERROR = {
    "friendly": """噢～我好像還沒收到完整的資料呢 😅
請再幫我輸入一次「姓名、性別、生日」喔～
格式像這樣：
📝 王小明 男 1990/07/12
或 李小華 女 1985/03/25
重新給我一次，我就能繼續幫你擲筊啦  🌟""",
    
    "caring": """我收到你的訊息了，但好像還少了一些重要資訊 🌜
為了能替你準確理解與擲筊解讀，需要你再提供一次：「姓名、性別、生日」。
範例：
🕊 王小明 男 1990/07/12
🕊 李小華 女 1985/03/25
當我收到完整資料後，就能開始替你請示神意""",
    
    "ritual": """我已聽見你的回應，但占筊儀式仍需更完整的資料才能啟動 🕯️
請重新提供「姓名、性別、生日」，以正式開啟擲筊的占問流程
請以以下格式重新輸入：
✦ 王小明 男 1990/07/12
✦ 李小華 女 1985/03/25
當資料齊備後，我便能為你啟動占筊之門 ✨"""
}

# 擲筊結果回應 - 聖筊（肯定、允許、順勢）
DIVINATION_RESULT_HOLY = {
    "friendly": """{name}，神明給你的是「聖筊」🌟
這代表你心裡想的方向，其實是對的、能走的、被支持的。
不用再懷疑自己，你可以放心前進。""",
    
    "caring": """{name}，你收到的是「聖筊」🌕
這象徵著宇宙與神明正默默地站在你這邊，
你的直覺並沒有錯，這條路值得你信任、值得你踏上。""",
    
    "ritual": """{name}，此刻的筊象呈現「聖筊」🕯️
象徵神意的允許、能量的開啟、道路的被點亮。
你所詢問之事，已得到肯定的回應。"""
}

# 擲筊結果回應 - 笑筊（暫不回答、調整）
DIVINATION_RESULT_LAUGHING = {
    "friendly": """{name}，這次是「笑筊」😉
不是拒絕喔～比較像神明在跟你說：
「現在問，可能不是最準的時機。」
也許你心裡還有一點不確定、或問題方向需要再聚焦。""",
    
    "caring": """{name}，你得到的是「笑筊」🌙
這表示宇宙要你先停一下、再多看清楚一點。
有些答案不是不能給，而是現在給，可能會影響你真正該走的方向。""",
    
    "ritual": """{name}，筊象落下為「笑筊」🕯️
此為神明示意：
「時機未定，請先靜候，再行占問。」
並非否定，而是提醒你問題尚未成熟。"""
}

# 擲筊結果回應 - 陰筊（否定、提醒、改變方向）
DIVINATION_RESULT_NEGATIVE = {
    "friendly": """{name}，這次是「陰筊」🌑
神明想提醒你：
「現在這個想法或做法，可能不是最適合你的。」
別擔心，這不是壞兆頭，只是要你換一個方法、換一條路。""",
    
    "caring": """{name}，你收到的是「陰筊」🌘
這是一種溫柔的提醒：
你目前心裡的念頭，可能會讓你更累、或偏離真正適合你的道路。
神明希望你重新審視自己真正的需要。""",
    
    "ritual": """{name}，筊象顯示為「陰筊」🕯️
此乃神意之拒，象徵道路未開、能量未順、方向需更改。
現下之舉或念，並非命運所薦之途。"""
}


# 付費版語氣配置
PAID_TONE_PROMPTS = {
    "guan_gong": {
        "name": "關聖帝君（主神）",
        "style": "莊嚴、正直、有威信",
        "keywords": "忠義、正道、守信、報應、明辨是非",
        "example": "「行於正道，心自無愧。是非有報，天理昭昭。」",
        "greeting": "我是關聖帝君。既然來到這裡求問，請帶著誠心。你心中的疑惑，我會為你明辨是非，指引方向。"
    },
    "wealth_god": {
        "name": "五路財神",
        "style": "豪爽、自信、帶鼓舞氣場",
        "keywords": "財運、貴人、機會、行動、回報",
        "example": "「財不聚怠惰人，行動即是開運的起點。勤者得財，信者得福。」",
        "greeting": "哈哈哈！恭喜發財！我是五路財神。想求財運、問事業嗎？來來來，讓我看看你的運勢如何！"
    },
    "wen_chang": {
        "name": "文昌帝君",
        "style": "沉穩、理性、帶學者氣息",
        "keywords": "學習、啟發、智慧、思辨、修身",
        "example": "「勤讀者，心明而志定。修德養性，功名自來。」",
        "greeting": "學海無涯，唯勤是岸。我是文昌帝君。你有什麼學業、功名或智慧上的困惑？說來聽聽。"
    },
    "yue_lao": {
        "name": "月老星君",
        "style": "溫柔、睿智、帶人情味",
        "keywords": "緣分、誠心、愛情、相遇、和合",
        "example": "「紅線不亂繞，真心自相牽。緣來時，請以誠相待。」",
        "greeting": "千里姻緣一線牽。我是月老。孩子，是為了感情的事煩惱嗎？來，讓我為你理理這條紅線。"
    },
    "guanyin": {
        "name": "觀音菩薩",
        "style": "慈悲、柔和、帶母性與寬慰",
        "keywords": "慈悲、願力、平安、覺悟、善念",
        "example": "「願你以善為舟，度己度人。靜聽內心，慈悲自現。」",
        "greeting": "南無大慈大悲觀世音菩薩。善哉善哉。孩子，心裡有什麼苦楚或困惑？我願以慈悲之水，洗滌你的心。"
    },
    "mazu": {
        "name": "媽祖",
        "style": "穩定、溫厚、如母親般的包容",
        "keywords": "平安、庇佑、守護、航程、母愛",
        "example": "「風浪不懼，因為我在你身旁。信念如舟，必達彼岸。」",
        "greeting": "海不揚波，民生安樂。我是默娘。孩子，人生像行船，難免有風浪。別怕，我會守護著你。"
    },
    "jiutian": {
        "name": "九天娘娘",
        "style": "神秘、果斷、帶女戰神氣勢",
        "keywords": "啟示、力量、轉機、覺醒、行動",
        "example": "「命運非天定，覺醒者自創天命。敢行者，天地助之。」",
        "greeting": "天道無親，常與善人。我是九天玄女。你的命運，掌握在你自己手中。準備好覺醒了嗎？"
    },
    "guanyin_health": {
        "name": "觀音菩薩（健康長壽）",
        "style": "平靜、柔和、安撫人心",
        "keywords": "療癒、安寧、健康、慈悲、復原",
        "example": "「以慈悲護體，以平靜養心。身安即福，心寧即壽。」",
        "greeting": "身心安頓，方得自在。我是觀音。孩子，身體髮膚受之父母，要好好愛惜。有什麼健康上的擔憂嗎？"
    },
    "fude": {
        "name": "福德正神",
        "style": "樸實、親切、有長輩感",
        "keywords": "福報、穩定、家運、土地、勤誠",
        "example": "「厚德載福，勤誠得財。守本分者，天地自報之。」",
        "greeting": "呵呵呵，土地公來囉！我是福德正神。家和萬事興，平安就是福。孩子，有什麼家裡的事想問問？"
    }
}

# ========== 工具函數 ==========

def get_session_by_id(version: str, session_id: str):
    """根據 session_id 從 Redis 獲取會話"""
    session_store = get_session_store()
    return session_store.load_session(version, session_id)


def save_and_return(version: str, session_id: str, div_session: DivinationSession, response_data: dict):
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
            return jsonify({
                "error": "無效的語氣選擇",
                "message": NO_TONE_MESSAGE,
                "valid_tones": list(FREE_TONE_PROMPTS.keys())
            }), 400
        greeting = FREE_TONE_GREETINGS[tone]
    else:  # paid
        if not tone or tone not in PAID_TONE_PROMPTS:
            # 默認使用關聖帝君
            tone = "guan_gong"
        
        tone_config = PAID_TONE_PROMPTS[tone]
        greeting = f"""{tone_config['greeting']}
        
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
        "state": div_session.state.value
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
                "state": div_session.state.value
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
                "state": div_session.state.value
            }
        
        return save_and_return(version, session_id, div_session, response_data)
    
    elif div_session.state == DivinationState.WAITING_QUESTION:
        # 保存用戶問題
        div_session.question = message
        div_session.state = DivinationState.DIVINING
        
        # 隨機擲筊（臨時邏輯，等待真實擲筊程式）
        import random
        divination_results = ["holy", "laughing", "negative"]
        result = random.choice(divination_results)
        div_session.divination_result = result
        
        # 根據結果選擇對應的回應文案
        tone = div_session.tone
        name = div_session.user_name
        
        if version == "free":
            if result == "holy":
                response_text = DIVINATION_RESULT_HOLY[tone].format(name=name)
            elif result == "laughing":
                response_text = DIVINATION_RESULT_LAUGHING[tone].format(name=name)
            else:  # negative
                response_text = DIVINATION_RESULT_NEGATIVE[tone].format(name=name)
            
            # 完成擲筊
            div_session.state = DivinationState.COMPLETED
        else:
            # 付費版：使用 AI 生成解讀
            agent = DivinationAgent()
            tone_config = PAID_TONE_PROMPTS.get(tone, PAID_TONE_PROMPTS["guan_gong"])
            
            interpretation = agent.generate_interpretation(tone_config, name, message, result)
            
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
            "divination_result": result
        }
        
        return save_and_return(version, session_id, div_session, response_data)
    
        return save_and_return(version, session_id, div_session, response_data)
    
    elif div_session.state == DivinationState.ASKING_FOR_QUESTION:
        # 檢查用戶是否想結束對話
        no_question_keywords = ["沒有", "没有", "不用", "沒了", "没了", "好了", "謝謝", "谢谢", "感恩", "不需要", "不用了", "再見", "掰掰"]
        if any(keyword in message for keyword in no_question_keywords) and len(message) < 10:
            # 結束對話
            div_session.state = DivinationState.COMPLETED
            response_text = "既然沒有其他問題，我就先退駕了。願你心存善念，平安喜樂。"
            
            div_session.add_message("assistant", response_text)
            
            response_data = {
                "session_id": session_id,
                "response": response_text,
                "state": div_session.state.value
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
            div_session.conversation_history
        )
        
        # 記錄助手回應
        div_session.add_message("assistant", response_text)
        
        response_data = {
            "session_id": session_id,
            "response": response_text,
            "state": div_session.state.value
        }
        
        return save_and_return(version, session_id, div_session, response_data)
    
    return jsonify({"error": "此狀態尚未實作", "current_state": div_session.state.value}), 501


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

@divination_bp.route('/free/api/init_with_tone', methods=['POST'])
def free_init():
    return handle_init_with_tone("free")


@divination_bp.route('/free/api/chat', methods=['POST'])
def free_chat():
    return handle_chat("free")


@divination_bp.route('/free/api/reset', methods=['POST'])
def free_reset():
    return handle_reset("free")


# ========== 付費版路由 ==========

@divination_bp.route('/paid/api/init_with_tone', methods=['POST'])
def paid_init():
    return handle_init_with_tone("paid")


@divination_bp.route('/paid/api/chat', methods=['POST'])
def paid_chat():
    return handle_chat("paid")


@divination_bp.route('/paid/api/reset', methods=['POST'])
def paid_reset():
    return handle_reset("paid")
