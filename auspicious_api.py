"""
黃道吉日 API Blueprint
提供黃道吉日查詢的 API 端點
"""

from flask import Blueprint, request, jsonify
from typing import Optional
import uuid

from auspicious.agent import AuspiciousAgent, AuspiciousSession, AuspiciousState
from auspicious.session_store import get_session_store
from shared.rule_loader import load_global_rules


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

請告訴我你的姓名、性別、生日與生肖。
例如：王小明 男 1990/07/12 屬馬""",
    "caring": """親愛的旅人，歡迎回到這本為你打開的吉日曆 🌿
擇日是一份溫柔的照顧，不是迷信數字，
而是替你的重要時刻多一層安心。
你可以慢慢說，我會依照你的資料，
幫你找出最貼近你心意的好日子。

請告訴我你的姓名、性別、生日與生肖。
例如：王小明 男 1990/07/12 屬馬""",
    "ritual": """歡迎步入《黃道吉日擇日之殿》🕯
日辰與星象皆有其節律，
每一個被選中的日子都承載著特殊的氣場。
準備好後，把你的基本資訊告訴我，
我將為你啟動正式的擇日流程。

請告訴我你的姓名、性別、生日與生肖。
例如：王小明 男 1990/07/12 屬馬""",
}

# 未選擇語氣的提示
NO_TONE_MESSAGE = """小提醒 🌟：請先選擇您想要的對話語氣，
這樣我才能用最適合你的方式替你查詢黃道吉日並說明建議 👇
🔸請選擇：「friendly / caring / ritual」"""

# 付費版語氣配置（9種神明）
PAID_TONE_PROMPTS = {
    "guan_gong": {
        "name": "關聖帝君（主神）",
        "style": "莊嚴、正直、有威信",
        "keywords": "忠義、正道、守信、因果回饋、明辨是非",
        "example": "「行於正道，心自無愧。是非有報，天理昭昭。」",
        "greeting": "我是關聖帝君。既然來到這裡求問吉日，請帶著誠心。你心中的安排，我會為你明辨良辰，指引方向。\n\n請告訴我你的姓名、性別、生日與生肖。\n例如：王小明 男 1990/07/12 屬馬",
    },
    "wealth_god": {
        "name": "五路財神",
        "style": "豪爽、自信、帶鼓舞氣場",
        "keywords": "財運、貴人、機會、行動、回報",
        "example": "「財不聚怠惰人，行動即是開運的起點。勤者得財，信者得福。」",
        "greeting": "哈哈哈！恭喜發財！我是五路財神。想挑個開業吉日、簽約好日？來來來，讓我看看哪天能替你招財進寶！\n\n請告訴我你的姓名、性別、生日與生肖。\n例如：王小明 男 1990/07/12 屬馬",
    },
    "wen_chang": {
        "name": "文昌帝君",
        "style": "沉穩、理性、帶學者氣息",
        "keywords": "學習、啟發、智慧、思辨、修身",
        "example": "「勤讀者，心明而志定。修德養性，功名自來。」",
        "greeting": "學海無涯，唯勤是岸。我是文昌帝君。你有什麼學業、考試、簽約的大事想選個好日子？說來聽聽。\n\n請告訴我你的姓名、性別、生日與生肖。\n例如：王小明 男 1990/07/12 屬馬",
    },
    "yue_lao": {
        "name": "月老星君",
        "style": "溫柔、睿智、帶人情味",
        "keywords": "緣分、誠心、愛情、相遇、和合",
        "example": "「紅線不亂繞，真心自相牽。緣來時，請以誠相待。」",
        "greeting": "千里姻緣一線牽。我是月老。孩子，是想挑個好日子辦婚事嗎？來，讓我為你理理這條紅線。\n\n請告訴我你的姓名、性別、生日與生肖。\n例如：王小明 男 1990/07/12 屬馬",
    },
    "guanyin": {
        "name": "觀世音菩薩",
        "style": "慈悲、柔和、帶母性與寬慰",
        "keywords": "慈悲、願力、平安、覺悟、善念",
        "example": "「願你以善為舟，度己度人。靜聽內心，慈悲自現。」",
        "greeting": "南無大慈大悲觀世音菩薩。善哉善哉。孩子，心裡有什麼重要的日子想安排？我願以慈悲之心，為你擇選良辰。\n\n請告訴我你的姓名、性別、生日與生肖。\n例如：王小明 男 1990/07/12 屬馬",
    },
    "mazu": {
        "name": "媽祖",
        "style": "穩定、溫厚、如母親般的包容",
        "keywords": "平安、庇佑、守護、航程、母愛",
        "example": "「風浪不懼，因為我在你身旁。信念如舟，必達彼岸。」",
        "greeting": "海不揚波，民生安樂。我是默娘。孩子，人生像行船，大事小事都要挑個好日子。別怕，我會幫你守護。\n\n請告訴我你的姓名、性別、生日與生肖。\n例如：王小明 男 1990/07/12 屬馬",
    },
    "jiutian": {
        "name": "九天娘娘",
        "style": "神秘、果斷、帶女戰神氣勢",
        "keywords": "啟示、力量、轉機、覺醒、行動",
        "example": "「命運非天定，覺醒者自創天命。敢行者，天地助之。」",
        "greeting": "天道無親，常與善人。我是九天玄女。你的大事，需要一個有力量的日子。準備好接受天命了嗎？\n\n請告訴我你的姓名、性別、生日與生肖。\n例如：王小明 男 1990/07/12 屬馬",
    },
    "fude": {
        "name": "福德正神",
        "style": "樸實、親切、有長輩感",
        "keywords": "福報、穩定、家運、土地、勤誠",
        "example": "「厚德載福，勤誠得財。守本分者，天地自報之。」",
        "greeting": "呵呵呵，土地公來囉！我是福德正神。家和萬事興，平安就是福。孩子，有什麼家裡的大事想挑個好日子？\n\n請告訴我你的姓名、性別、生日與生肖。\n例如：王小明 男 1990/07/12 屬馬",
    },
}

# 基本資訊錯誤提示
BASIC_INFO_ERROR_TEMPLATES = {
    "friendly": """噢～我好像還沒收到完整的資料呢 😅
請再幫我輸入一次「姓名、性別、生日、生肖」喔～
格式像這樣：
📝 王小明 男 1990/07/12 屬馬
　 或 李小華 女 1985/03/25 屬牛
重新給我一次，我就能繼續幫你查黃道吉日啦 🌟""",
    "caring": """我收到你的訊息了，但好像還少了一些重要資訊 🌜
為了能根據你的命盤與節氣精準挑選吉日，需要你再提供一次：「姓名、性別、生日、生肖」。
範例：
🕊 王小明 男 1990/07/12 屬馬
🕊 李小華 女 1985/03/25 屬牛
當我收到完整資料後，就能正式替你查詢並解讀黃道吉日。""",
    "ritual": """我已聽見你的回應，但擇日儀式仍需要更完整的資料才能啟動 🕯
請重新提供「姓名、性別、生日、生肖」，以正式開啟黃道吉日的擇日流程。
請以以下格式重新輸入：
◆ 王小明 男 1990/07/12 屬馬
◆ 李小華 女 1985/03/25 屬牛
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
            return jsonify({"error": "無效的語氣選擇", "message": NO_TONE_MESSAGE}), 400
        greeting = FREE_TONE_GREETINGS[tone]
    else:  # paid
        if not tone or tone not in PAID_TONE_PROMPTS:
            # 默認使用關聖帝君
            tone = "guan_gong"
        greeting = PAID_TONE_PROMPTS[tone]["greeting"]

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
        if (
            extracted["name"]
            and extracted["gender"]
            and extracted["birthdate"]
            and extracted["zodiac"]
        ):
            # 保存資訊
            auspicious_session.user_name = extracted["name"]
            auspicious_session.user_gender = extracted["gender"]
            auspicious_session.birthdate = extracted["birthdate"]
            auspicious_session.zodiac = extracted["zodiac"]
            auspicious_session.state = AuspiciousState.WAITING_CATEGORY_AND_DATE

            # 返回分類選擇提示
            tone = auspicious_session.tone

            # 判斷是免費版還是付費版語氣
            if tone in CATEGORY_SELECTION_PROMPT:
                # 免費版：使用對應語氣的提示
                response_text = CATEGORY_SELECTION_PROMPT[tone]
            else:
                # 付費版：使用通用提示（神明語氣）
                response_text = """接下來請選擇你要查詢的分類，並選擇一個日期：

🔸 生活日常 - 出門治公、購物、聚會
🔸 家庭居所 - 搬家、簽約、動工
🔸 感情人際 - 約會、告白、合作
🔸 喜慶大事 - 婚嫁、慶典、開業
🔸 工作事業 - 開工、會議、啟動計劃

請告訴我分類和日期（例如：「感情人際，2025-12-25」）。"""

            # 記錄助手回應
            auspicious_session.add_message("assistant", response_text)

            response_data = {
                "session_id": session_id,
                "response": response_text,
                "state": auspicious_session.state.value,
                "categories": CATEGORIES,  # 返回所有分類供前端顯示
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
                    # 嘗試匹配分類（支援英文 key 或中文名稱）
                    category_input = parts[0].strip()
                    for cat_key, cat_info in CATEGORIES.items():
                        # 檢查是否匹配英文 key 或中文名稱
                        if (
                            cat_key == category_input
                            or cat_info["name"] in category_input
                        ):
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

        # 查詢黃曆資料
        from auspicious.modules.calendar_db import CalendarDB
        from shared.gpt_client import GPTClient

        calendar_db = CalendarDB()
        gpt_client = GPTClient()

        # 從選擇的日期提取年月（YYYY-MM）
        selected_date = auspicious_session.selected_date  # 格式: YYYY-MM-DD
        year_month = selected_date[:7]  # 取前7位：YYYY-MM

        # 查詢該月份的黃曆資料
        calendar_content = calendar_db.get_month_data(year_month)

        if calendar_content:
            # 使用 AI 分析黃曆與用戶需求
            category_name = CATEGORIES.get(auspicious_session.category, {}).get(
                "name", auspicious_session.category
            )

            system_prompt = f"""你是專業的黃道吉日顧問。請根據黃曆資料，判斷指定日期是否適合用戶的需求。

用戶資訊：
- 姓名：{auspicious_session.user_name}
- 性別：{auspicious_session.user_gender}
- 生日：{auspicious_session.birthdate}
- 生肖：{auspicious_session.zodiac}
- 選擇日期：{selected_date}
- 查詢分類：{category_name}
- 具體事項：{message}

黃曆資料（{year_month}月）：
{calendar_content}

請根據以上資訊提供參考建議：
1. 從黃曆中找到 {selected_date} 這一天的「宜」和「忌」事項
2. 分析這些事項與用戶需求的關聯性
3. 如果黃曆中有「沖」的生肖，檢查是否沖到用戶的生肖（{auspicious_session.zodiac}），說明可能的影響和化解方式
4. 提供綜合性的建議
5. 語氣要符合「{auspicious_session.tone}」，親切且專業。**請務必在回答中使用用戶的名字「{auspicious_session.user_name}」，嚴禁使用「親愛的使用者」或「用戶」等泛稱。**

{load_global_rules()}
"""

            user_prompt = f"請分析 {selected_date} 這天是否適合「{message}」。"

            try:
                ai_response = gpt_client.ask(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=0.7,
                    max_tokens=500,
                )
                response_text = ai_response
            except Exception as e:
                print(f"AI 分析錯誤: {e}")
                response_text = f"抱歉，在分析黃曆時遇到了一些技術問題。不過根據你選擇的日期 {selected_date}，建議你可以再確認一下當天的具體時辰和個人情況。"
        else:
            # 沒有該月份的黃曆資料
            response_text = f"很抱歉，目前系統尚未收錄 {year_month} 月份的黃曆資料。請選擇其他月份，或稍後再試。"

        auspicious_session.add_message("assistant", response_text)

        # 付費版：進入持續對話狀態
        if version == "paid":
            ask_question = "\n\n如果您對選擇的日期或建議有任何疑問，歡迎繼續提問。我會為您詳細解答。"
            response_text_with_prompt = f"{response_text}{ask_question}"
            auspicious_session.state = AuspiciousState.ASKING_FOR_QUESTION
            # 更新對話歷史中的最後一條訊息
            if auspicious_session.conversation_history:
                auspicious_session.conversation_history[-1]["content"] = (
                    response_text_with_prompt
                )
        else:
            # 免費版：直接完成
            response_text_with_prompt = response_text
            auspicious_session.state = AuspiciousState.COMPLETED

        response_data = {
            "session_id": session_id,
            "response": response_text_with_prompt,
            "state": auspicious_session.state.value,
            "specific_question": message,
        }

        return save_and_return(version, session_id, auspicious_session, response_data)

    elif auspicious_session.state == AuspiciousState.ASKING_FOR_QUESTION:
        # 付費版持續對話狀態
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
            "可以了",
            "夠了",
        ]
        if (
            any(keyword in message for keyword in no_question_keywords)
            and len(message) < 15
        ):
            # 結束對話
            auspicious_session.state = AuspiciousState.COMPLETED

            # 根據神明生成結束語
            tone = auspicious_session.tone
            tone_config = PAID_TONE_PROMPTS.get(tone, PAID_TONE_PROMPTS["guan_gong"])

            end_messages = {
                "guan_gong": "既然沒有其他疑問，我就先退駕了。願你行於正道，諸事順遂。",
                "wealth_god": "好！那就祝你財源廣進，生意興隆啦！有需要再來找我！",
                "wen_chang": "既然清楚了，那就好好努力吧。功名利祿，自有天定。",
                "yue_lao": "既然沒有其他問題，那就祝你良緣早至，幸福美滿。",
                "guanyin": "既然心中已明，那就好好珍惜這段緣分。南無觀世音菩薩。",
                "mazu": "既然沒有其他問題，那媽祖就先退了。願你平安順遂，一帆風順。",
                "jiutian": "既然清楚了，那就勇敢前行吧。天命在你手中。",
                "guanyin_health": "既然沒有其他疑問，那就好好保重身體。身心安康即是福。",
                "fude": "呵呵，好好好！那土地公就先退了。家和萬事興，平安就是福。",
            }
            response_text = end_messages.get(
                tone, "既然沒有其他問題，那就祝你諸事順遂，平安喜樂。"
            )

            auspicious_session.add_message("assistant", response_text)

            response_data = {
                "session_id": session_id,
                "response": response_text,
                "state": auspicious_session.state.value,
            }
            return save_and_return(
                version, session_id, auspicious_session, response_data
            )

        # 繼續對話 - 使用 AI 以神明口吻回答
        tone = auspicious_session.tone
        tone_config = PAID_TONE_PROMPTS.get(tone, PAID_TONE_PROMPTS["guan_gong"])

        from shared.gpt_client import GPTClient

        gpt_client = GPTClient()

        # 建立對話上下文
        system_prompt = f"""你是{tone_config["name"]}。

風格：{tone_config["style"]}
關鍵詞：{tone_config["keywords"]}
說話範例：{tone_config["example"]}

用戶已經查詢了黃道吉日，現在有後續問題。請以神明的身分，用溫和且專業的口吻回答。

用戶資訊：
- 姓名：{auspicious_session.user_name}
- 選擇日期：{auspicious_session.selected_date}
- 分類：{auspicious_session.category}
- 具體事項：{auspicious_session.specific_question}

請保持角色一致，不要重複已經說過的內容，直接回答用戶的疑問。

{load_global_rules()}"""

        user_prompt = f"{auspicious_session.user_name}的追問：{message}"

        try:
            response_text = gpt_client.ask(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=400,
            )
        except Exception as e:
            print(f"AI 回應錯誤: {e}")
            response_text = (
                "抱歉，我現在無法回答你的問題。請稍後再試，或者換個方式提問。"
            )

        auspicious_session.add_message("assistant", response_text)

        response_data = {
            "session_id": session_id,
            "response": response_text,
            "state": auspicious_session.state.value,
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


# ========== 付費版路由 ==========


@auspicious_bp.route("/paid/api/init_with_tone", methods=["POST"])
def paid_init():
    return handle_init_with_tone("paid")


@auspicious_bp.route("/paid/api/chat", methods=["POST"])
def paid_chat():
    return handle_chat("paid")


@auspicious_bp.route("/paid/api/reset", methods=["POST"])
def paid_reset():
    return handle_reset("paid")
