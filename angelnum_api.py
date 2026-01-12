"""
Angel Number API Blueprint
提供天使數字解讀的 API 端點
"""

from flask import Blueprint, request, jsonify
from typing import Optional
import uuid
import re

from angelnum.agent import (
    AngelNumberAgent,
    AngelConversationSession,
    AngelConversationState,
)
from angelnum.modules.angel_numbers import get_angel_number_meaning
from shared.gpt_client import GPTClient
from shared.session_store import BaseSessionStore

# 創建 Blueprint
angelnum_bp = Blueprint("angelnum", __name__, url_prefix="/angel")

# 創建 Session Store
session_store = BaseSessionStore(module_name="angelnum")

# 創建 Agent
agent = AngelNumberAgent()

# 免費版語氣配置（3種）
FREE_TONE_PROMPTS = {
    "friendly": "親切輕鬆,像朋友聊天一樣溫暖自然",
    "caring": "溫暖關懷,像靈性導師般深情陪伴",
    "ritual": "莊重神聖,充滿儀式感與神性",
}

# 付費版語氣配置（10種）- 參考 lifenum 的語氣風格
PAID_TONE_PROMPTS = {
    "guan_yu": "請使用關聖帝君的莊嚴、正直語氣，帶有沉穩節奏。關鍵語彙：忠義、正道、守信、因果、明辨是非。**嚴格警告：禁止使用任何文言文詞彙（汝、吾、乃、之、於、若、然、故、是以、當、須、方能、焉、矣、已為汝析得、為汝、汝之等），必須100%使用現代中文（你、我、的、在、如果、因此、應該、需要、能夠、已為你分析、為你、你的）。語調莊重威嚴但完全現代化表達。同時，嚴格禁止提到「因果報應」，請統一改用「因果回饋分析」或「業力課題」。**",
    "michael": "請使用大天使米迦勒的堅定、有領導感語氣，帶安定力量。關鍵語彙：勇氣、信任、光明、防禦、戰士。語調堅定且充滿力量。",
    "gabriel": "請使用大天使加百列的溫柔中帶清晰指引語氣，像傳信者。關鍵語彙：啟發、信息、真理、溝通、覺醒。語調溫和且具有啟發性。",
    "raphael": "請使用大天使拉斐爾的柔和、慈悲、安撫人心語氣。關鍵語彙：療癒、平衡、綠光、修復、愛自己。語調溫暖且充滿愛意。",
    "uriel": "請使用大天使烏列爾的沈穩、智者風格語氣，講話慢而深。關鍵語彙：洞察、智慧、火焰、真理、學習。語調深沈且充滿智慧。",
    "zadkiel": "請使用大天使沙德基爾的柔中帶慈悲語氣，像引導人放下怨恨的導師。關鍵語彙：寬恕、紫焰、轉化、慈悲、理解。語調慈悲且包容。",
    "jophiel": "請使用大天使喬菲爾的溫柔、鼓舞、偏女性化語氣，有藝術氣息。關鍵語彙：美感、靈感、光彩、愛自己。語調優雅且具有美感。",
    "chamuel": "請使用大天使沙木爾的溫暖、包容語氣，像心理諮商師。關鍵語彙：愛、關係、理解、和解、自我接納。語調溫暖且充滿愛。",
    "metatron": "請使用大天使梅塔特隆的權威、理性語氣，有數據感與宇宙秩序感。關鍵語彙：紀律、次序、靈性法則、神聖幾何。語調理性且系統化。",
    "ariel": "請使用大天使阿列爾的豐盛、自然語氣，帶大地母親般的滋養感。關鍵語彙：豐盛、大地、自然、繁榮、創造。語調溫和且充滿生命力。",
}


def get_tone_prompts(version: str = "free") -> dict:
    """根據版本獲取語氣配置"""
    if version == "paid":
        return PAID_TONE_PROMPTS
    return FREE_TONE_PROMPTS


# ========== 工具函數 ==========


def get_session_by_id(
    version: str, session_id: str
) -> Optional[AngelConversationSession]:
    """根據 session_id 從 Redis 獲取會話"""
    try:
        data = session_store.load(version, session_id)
        if data is None:
            return None
        return AngelConversationSession.from_dict(data)
    except Exception as e:
        print(f"[ERROR] 獲取會話失敗: {e}")
        return None


def save_and_return(
    version: str,
    session_id: str,
    conv_session: AngelConversationSession,
    response_data: dict,
):
    """保存會話到 Redis 並返回 JSON 響應"""
    try:
        session_store.save(version, session_id, conv_session.to_dict())
        return jsonify(response_data)
    except Exception as e:
        print(f"[ERROR] 保存會話失敗: {e}")
        return jsonify({"error": "Session 存儲服務暫時不可用"}), 503


def generate_greeting(tone: str, stage: str = "init") -> str:
    """根據語氣生成問候語"""
    if stage == "init":
        if tone == "friendly":
            return "嗨～歡迎來到 天使數字 AI 對話空間 💫\n\n你是不是最近也常常看到某個數字一直出現呢？\n\n像是 1111、3333 或是車牌、時鐘都在重複提醒你？⌛️\n\n別懷疑,這可不是巧合～\n\n那是天使在用數字跟你打招呼呢 ✨\n\n請告訴我你的姓名、性別與生日,\n\n然後我會請你選擇最近看到的天使數字 💌\n\n例如：王小明 男 1990/07/12"
        elif tone == "caring":
            return "親愛的靈魂旅人,歡迎來到 天使數字的光之門 🌙\n\n當某個數字頻繁出現在你眼前,\n\n那是宇宙在輕喚你注意內在的訊息。\n\n或許它是鼓勵、或是一份提醒——\n\n但無論是什麼,都代表你正在被溫柔地指引著 💫\n\n請先告訴我你的姓名、性別與生日,\n\n接著我會請你選擇最近最常出現的數字 🕊️\n\n例如：王小明 男 1990/07/12"
        else:  # ritual
            return "歡迎步入 天使數字殿堂 ✨\n\n當你多次看見相同的數字,\n\n那並非偶然,而是一道來自宇宙的密碼。\n\n每個數字皆蘊含神聖能量,\n\n象徵著靈魂階段的覺醒與啟示。\n\n請先告訴我你的姓名、性別與出生之日,\n\n隨後我將請你選擇那組反覆出現的數字 🕯️\n\n例如：王小明 男 1990/07/12"
        # 付費版默認問候（如果 tone 不在上述三種中）
        return "歡迎來到天使數字解讀空間。請告訴我您的姓名、性別與生日，讓我為您解讀宇宙的訊息。"

    elif stage == "ask_angel_number":
        if tone == "friendly":
            return "接下來想請你告訴我一件小事：\n\n你最近最常看到的天使數字是什麼呢？💫\n\n像是「1111」、「3333」或是「5555」這樣的數字～\n\n別擔心沒有對錯,\n\n那只是宇宙在用數字的語言和你打招呼 🌈\n\n請告訴我你看到的數字吧！"
        elif tone == "caring":
            return "接下來,讓我們一起傾聽宇宙的語言吧～\n\n請回想一下,最近是否有某個數字反覆出現在你眼前？\n\n那是天使想讓你注意的訊息喔 🕊️\n\n請告訴我那組數字,\n\n像是「1111」、「7777」或「4444」這樣的,\n\n我會幫你解讀其中所蘊含的能量與指引 💫"
        elif tone == "ritual":
            return "在揭開符碼之前,我需要知道一件重要的事：\n\n近期反覆出現在你生命中的數字是什麼？\n\n那是一道宇宙的訊號,一段天使傳遞的能量序列。\n\n像是「1111」、「9999」這樣的重複數,\n\n它都象徵著你與宇宙能量正在共振。\n\n請輸入那組數字,\n\n讓我為你解讀這份來自天界的啟示 ✨"
        # 付費版通用問候
        return "請告訴我您最近反覆看到的天使數字，我將為您解讀其中的神聖含義。"

    return ""


def generate_error_message(tone: str, error_type: str = "incomplete_info") -> str:
    """根據語氣生成錯誤訊息"""
    if error_type == "incomplete_info":
        if tone == "friendly":
            return "噢～我好像還沒收到完整的資料呢 😅\n\n請再幫我輸入一次「姓名、性別、生日」喔～\n\n格式像這樣：\n📝 王小明 男 1990/07/12\n或 李小華 女 1985/03/25\n\n這樣我就能幫你準確解讀天使數字囉 🌟"
        elif tone == "caring":
            return "我收到您的訊息了,但還缺少一些小小的關鍵資訊 🌙\n\n為了讓我能準確為您解讀天使數字,\n請您提供「姓名、性別與生日」。\n\n範例：\n🕊 王小明 男 1990/07/12\n🕊 李小華 女 1985/03/25\n\n當我收到完整資料後,我就能為您開啟光之門。"
        else:  # ritual
            return "天使數字之門尚未完全開啟。\n\n我需要更完整的召喚資訊,才能解讀數字的能量。\n\n請以以下格式重新輸入：\n✦ 王小明 男 1990/07/12\n✦ 李小華 女 1985/03/25\n\n當正確的姓名、性別與生日被輸入時,\n天使之光將再次流動,指引屬於您的數字之途 🔮"
        return "資料不完整，請提供姓名、性別與生日。"

    elif error_type == "invalid_number":
        if tone == "friendly":
            return "咦？我好像沒看到數字耶 😅\n\n請直接輸入你看到的數字就好囉～\n\n像是「1111」、「2222」、「5555」這樣 ✨"
        elif tone == "caring":
            return "親愛的,我沒有收到數字喔 🌙\n\n請直接告訴我那組數字吧,\n\n像是「2222」或「8888」這樣的形式 💫"
        else:  # ritual
            return "請直接輸入數字序列,\n\n例如「7777」或「1111」🔮"
        return "請輸入有效的天使數字。"

    return "抱歉,發生了一些錯誤,請重試。"


# ========== 通用處理函數 ==========


def handle_init_with_tone(version: str):
    """初始化對話並使用指定語氣"""
    data = request.json
    default_tone = "friendly" if version == "free" else "guan_yu"
    tone = data.get("tone", default_tone)

    # 獲取語氣配置
    tone_prompts = get_tone_prompts(version)

    # 驗證語氣
    if tone not in tone_prompts:
        return jsonify({"error": "無效的語氣選項"}), 400

    # 創建新會話
    session_id = str(uuid.uuid4())
    conv_session = AngelConversationSession(session_id)
    conv_session.tone = tone
    conv_session.state = AngelConversationState.WAITING_BASIC_INFO

    # 生成問候語
    response = generate_greeting(tone, "init")
    conv_session.add_message("assistant", response)

    return save_and_return(
        version,
        session_id,
        conv_session,
        {
            "session_id": session_id,
            "response": response,
            "state": conv_session.state.value,
            "requires_input": True,
        },
    )


def handle_chat(version: str):
    """統一對話處理"""
    data = request.json
    session_id = data.get("session_id")
    user_input = data.get("message", "").strip()

    # 驗證 session_id
    if not session_id:
        return jsonify(
            {
                "error": "缺少 session_id",
                "message": "請先調用 init_with_tone 初始化會話",
            }
        ), 400

    # 獲取會話
    conv_session = get_session_by_id(version, session_id)
    if conv_session is None:
        return jsonify(
            {
                "error": "會話不存在或已過期",
                "message": "請重新調用 init_with_tone 初始化會話",
                "session_id": session_id,
            }
        ), 404

    # 記錄使用者輸入
    conv_session.add_message("user", user_input)

    # 獲取語氣配置
    tone_prompts = get_tone_prompts(version)

    # ========== 狀態機處理 ==========

    # 1. WAITING_BASIC_INFO - 等待基本資訊
    if conv_session.state == AngelConversationState.WAITING_BASIC_INFO:
        # 使用 AI 解析基本資訊
        name, gender, birthdate, error_msg = agent.extract_birthdate_with_ai(user_input)

        if error_msg:
            response = generate_error_message(conv_session.tone, "incomplete_info")
            conv_session.add_message("assistant", response)
            return save_and_return(
                version,
                session_id,
                conv_session,
                {
                    "session_id": session_id,
                    "response": response,
                    "state": conv_session.state.value,
                    "requires_input": True,
                },
            )

        # 保存基本資訊
        conv_session.user_name = name
        conv_session.user_gender = gender
        conv_session.birthdate = birthdate

        # 詢問天使數字
        greeting_part = (
            f"{name},你好呀～我這邊已經收到你的資料囉 ✨\n\n"
            if conv_session.tone == "friendly"
            else f"{name},感謝你分享你的資料 🌙\n\n"
            if conv_session.tone == "caring"
            else f"{name},感謝你的回應 🕯️\n\n"
        )

        # 如果是付費版且語氣不是免費的三種，使用通用開頭
        if version == "paid" and conv_session.tone not in FREE_TONE_PROMPTS:
            greeting_part = f"{name}，已收到您的資料。\n\n"

        angel_number_prompt = generate_greeting(conv_session.tone, "ask_angel_number")
        response = greeting_part + angel_number_prompt

        conv_session.state = AngelConversationState.WAITING_ANGEL_NUMBER
        conv_session.add_message("assistant", response)

        return save_and_return(
            version,
            session_id,
            conv_session,
            {
                "session_id": session_id,
                "response": response,
                "state": conv_session.state.value,
                "show_angel_number_selector": (
                    version == "free"
                ),  # 免費版顯示選擇器，付費版輸入文字
                "requires_input": True,
            },
        )

    # 2. WAITING_ANGEL_NUMBER - 等待天使數字
    elif conv_session.state == AngelConversationState.WAITING_ANGEL_NUMBER:
        # 提取數字
        angel_number = re.sub(r"[^\d]", "", user_input.strip())

        if not angel_number or len(angel_number) == 0:
            response = generate_error_message(conv_session.tone, "invalid_number")
            conv_session.add_message("assistant", response)
            return save_and_return(
                version,
                session_id,
                conv_session,
                {
                    "session_id": session_id,
                    "response": response,
                    "state": conv_session.state.value,
                    "requires_input": True,
                },
            )

        # 付費版：檢查數字長度限制（4位數以內）
        if version == "paid" and len(angel_number) > 4:
            if conv_session.tone == "friendly":
                response = f"嗯...你輸入的數字「{angel_number}」有點太長囉 😅\n\n天使數字通常是 4 位數以內的喔～\n\n請重新輸入一個簡短一點的數字吧！像是「1111」、「333」或「88」✨"
            elif conv_session.tone == "caring":
                response = f"親愛的,你輸入的「{angel_number}」超過了 4 位數 🌙\n\n讓我們專注在更精煉的數字上吧～\n\n請輸入 4 位數以內的天使數字,像是「444」或「1212」💫"
            else:  # ritual
                response = f"數字「{angel_number}」超出了天使數字的規範。\n\n請輸入 4 位數以內的數字序列 🔮"

            conv_session.add_message("assistant", response)
            return save_and_return(
                version,
                session_id,
                conv_session,
                {
                    "session_id": session_id,
                    "response": response,
                    "state": conv_session.state.value,
                    "requires_input": True,
                },
            )

        # 保存天使數字
        conv_session.angel_number = angel_number

        # 取得天使數字的核心意義
        # 付費版使用智能分析，免費版使用固定意義
        use_intelligent = version == "paid"
        angel_data = get_angel_number_meaning(
            angel_number, use_intelligent_analysis=use_intelligent
        )
        meanings_text = "\n".join(angel_data["meanings"])

        # 根據語氣設定 system prompt
        tone_description = tone_prompts.get(
            conv_session.tone, tone_prompts.get("guan_yu", "friendly")
        )

        # 構建 Prompt
        system_prompt = f"""你是一位專業的天使數字解讀師。

天使數字 {angel_number} 的核心意義如下：

{meanings_text}

請根據以上核心意義,為使用者提供深度、溫暖且具啟發性的解析。

【語氣要求】
使用「{tone_description}」的語氣。

【內容要求】
1. 解釋這個數字在此刻出現的深層意義
2. 闡述天使想要傳達的核心訊息（基於上述意義展開）
3. 提供對使用者生活的具體建議和指引
4. 給予溫暖的鼓勵與支持

【格式要求】
- 不使用任何 markdown 格式標記（如 **、##、- 等）
- 使用純文字和換行組織內容
- 回應長度控制在 {"400-500" if version == "paid" else "300-400"} 字左右
- 要有溫度、有深度、有啟發性
- **避免給予絕對性的預測或判斷，改用建議導向的表達**
- **禁止使用「一定會」、「絕對」、「必須」等確定性表達，請使用「建議」、「可以考慮」、「或許」等引導性語言**
- **嚴格禁止使用「因果報應」四字，若需表達相關概念，請統一改用「因果回饋分析」。**

請記住：你不只是在解釋數字,更是在傳遞來自宇宙的愛與指引。"""

        # 根據語氣設定問候語
        if conv_session.tone == "friendly":
            greeting = (
                f"{conv_session.user_name},我看到了你的天使數字 {angel_number}！✨\n\n"
            )
        elif conv_session.tone == "caring":
            greeting = f"親愛的 {conv_session.user_name},讓我為你解讀天使數字 {angel_number} 🌙\n\n"
        elif conv_session.tone == "ritual":
            greeting = f"{conv_session.user_name},{angel_number} 的神聖啟示如下 🕯️\n\n"
        else:
            greeting = f"{conv_session.user_name}，關於天使數字 {angel_number} 的解讀如下：\n\n"

        user_prompt = f"使用者的姓名是 {conv_session.user_name},他/她最近反覆看到天使數字 {angel_number}。\n\n請根據這個數字的核心意義,為 {conv_session.user_name} 提供完整、溫暖且具啟發性的解析,幫助他/她理解宇宙想要傳達的訊息。"

        try:
            client = GPTClient()
            print(f"\n{'=' * 60}")
            print(f"[DEBUG] 解析天使數字 ({version})")
            print(f"[DEBUG] Angel Number: {angel_number}")
            print(f"[DEBUG] Pattern: {angel_data.get('pattern', 'unknown')}")
            print(f"[DEBUG] User: {conv_session.user_name}")
            print(f"[DEBUG] Tone: {conv_session.tone}")
            print(f"{'=' * 60}\n")

            # 付費版使用 higher temperature for creativity
            temp = 1.0 if version == "paid" else 0.7
            max_tok = 800 if version == "paid" else 500

            final_response = client.ask(
                system_prompt, user_prompt, temperature=temp, max_tokens=max_tok
            )

            # 清理 markdown 格式標記
            final_response = (
                final_response.replace("**", "")
                .replace("__", "")
                .replace("##", "")
                .replace("###", "")
            )

            # 加上問候語
            final_response = greeting + final_response

            if version == "free":
                # 免費版：直接結束
                conv_session.state = AngelConversationState.COMPLETED
                conv_session.add_message("assistant", final_response)

                return save_and_return(
                    version,
                    session_id,
                    conv_session,
                    {
                        "session_id": session_id,
                        "response": final_response,
                        "state": conv_session.state.value,
                        "angel_number": angel_number,
                        "requires_input": False,
                    },
                )
            else:
                # 付費版：添加詢問語句並進入 ASKING_FOR_QUESTION 狀態
                if conv_session.tone == "friendly":
                    ask_question = "\n\n關於這個天使數字,你有什麼想要進一步了解的嗎？\n\n或是有什麼困惑想要詢問的呢？我很樂意繼續為你解答喔 💫"
                elif conv_session.tone == "caring":
                    ask_question = "\n\n親愛的,關於這個天使數字的訊息,\n\n你是否有任何想要深入探討的地方？\n\n或是生活中有什麼困惑想要尋求指引呢？我會陪著你一起探索 🌙"
                elif conv_session.tone == "ritual":
                    ask_question = "\n\n若您對此數字的啟示有任何疑問,\n\n或欲深入探究其中奧義,\n\n請隨時提問,我將為您揭示更深層的訊息 🕯️"
                else:
                    ask_question = (
                        "\n\n若您對此解析有任何疑問，或想深入探討，請隨時提問。"
                    )

                final_response += ask_question

                conv_session.state = AngelConversationState.ASKING_FOR_QUESTION
                conv_session.add_message("assistant", final_response)

                return save_and_return(
                    version,
                    session_id,
                    conv_session,
                    {
                        "session_id": session_id,
                        "response": final_response,
                        "state": conv_session.state.value,
                        "angel_number": angel_number,
                        "pattern": angel_data.get("pattern", "general"),
                        "requires_input": True,
                    },
                )

        except Exception as e:
            print(f"[ERROR] 解析天使數字錯誤: {e}")
            import traceback

            traceback.print_exc()

            error_response = f"抱歉,解析過程發生錯誤：{str(e)}"
            conv_session.add_message("assistant", error_response)
            return save_and_return(
                version,
                session_id,
                conv_session,
                {
                    "session_id": session_id,
                    "response": error_response,
                    "state": conv_session.state.value,
                    "requires_input": False,
                },
            )

    # 3. ASKING_FOR_QUESTION - 詢問是否有問題（付費版專屬）
    elif conv_session.state == AngelConversationState.ASKING_FOR_QUESTION:
        # 檢查使用者是否有問題
        user_input_lower = user_input.lower().strip()
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
        ]

        has_question = True
        for keyword in no_question_keywords:
            if keyword in user_input_lower:
                has_question = False
                break

        if not has_question or len(user_input.strip()) < 2:
            # 使用者沒有問題,結束對話
            if conv_session.tone == "friendly":
                response = "好的！希望這次的天使數字解讀對你有幫助 ✨\n\n如果未來又看到其他天使數字,隨時都可以回來找我喔 💫\n\n祝你一切順心～"
            elif conv_session.tone == "caring":
                response = "親愛的,很高興能為你解讀這個天使數字 🌙\n\n願這份來自宇宙的訊息能照亮你的道路 💕\n\n如果未來有其他數字想要了解,我隨時都在這裡陪伴你 🕊️"
            elif conv_session.tone == "ritual":
                response = "天使數字的啟示已完整揭示 ✨\n\n願您領受這份來自天界的智慧,踏上光明之途 🕯️\n\n若有其他數字欲解讀,請隨時再來"
            else:
                response = "感謝您的信任。願天使的指引為您帶來光明。再會。"

            conv_session.state = AngelConversationState.COMPLETED
            conv_session.add_message("assistant", response)
            return save_and_return(
                version,
                session_id,
                conv_session,
                {
                    "session_id": session_id,
                    "response": response,
                    "state": conv_session.state.value,
                    "requires_input": False,
                },
            )

        # 使用者有問題,進入持續對話狀態
        conv_session.state = AngelConversationState.CONVERSATION

        # 進入 CONVERSATION 邏輯（直接往下執行）
        pass

    # 4. CONVERSATION - 持續對話（付費版專屬）
    if conv_session.state == AngelConversationState.CONVERSATION:
        # 檢查是否要結束對話
        user_input_lower = user_input.lower().strip()
        end_keywords = [
            "謝謝",
            "谢谢",
            "感恩",
            "結束",
            "结束",
            "再見",
            "再见",
            "拜拜",
            "bye",
        ]

        wants_to_end = False
        for keyword in end_keywords:
            if keyword in user_input_lower and len(user_input) < 10:
                wants_to_end = True
                break

        # 檢查是否試圖詢問新的天使數字
        # 如果輸入純數字且與當前數字不同，提示需開啟新對話
        if not wants_to_end:
            import re

            clean_input = user_input.strip()
            # 檢查是否為 3-4 位純數字，且與當前數字不同
            if (
                clean_input.isdigit()
                and len(clean_input) in [3, 4]
                and clean_input != conv_session.angel_number
            ):
                response = "您只能針對第一次的數字提問，新的數字請開啟新的對話串呦 ✨"
                conv_session.add_message("assistant", response)
                return save_and_return(
                    version,
                    session_id,
                    conv_session,
                    {
                        "session_id": session_id,
                        "response": response,
                        "state": conv_session.state.value,
                        "requires_input": True,
                    },
                )

        if wants_to_end:
            # 結束對話
            if conv_session.tone == "friendly":
                response = "很開心能陪你探索天使數字的奧秘 ✨\n\n希望這些訊息對你有幫助～\n\n如果未來又看到其他天使數字,隨時都可以回來找我喔 💫"
            elif conv_session.tone == "caring":
                response = "親愛的,很榮幸能陪伴你這段探索之旅 🌙\n\n願天使的祝福常伴你左右 💕\n\n記得,宇宙一直都在支持著你 🕊️"
            elif conv_session.tone == "ritual":
                response = (
                    "感謝您的信任與聆聽 ✨\n\n願天使的光芒永遠照耀您的道路 🕯️\n\n再會"
                )
            else:
                response = "感謝您的信任與聆聽。願天使的光芒永遠照耀您的道路。再會。"

            conv_session.state = AngelConversationState.COMPLETED
            conv_session.add_message("assistant", response)
            return save_and_return(
                version,
                session_id,
                conv_session,
                {
                    "session_id": session_id,
                    "response": response,
                    "state": conv_session.state.value,
                    "requires_input": False,
                },
            )

        # 繼續回答問題
        angel_number = conv_session.angel_number
        name = conv_session.user_name

        # 重新獲取意義用於上下文
        use_intelligent = version == "paid"
        angel_data = get_angel_number_meaning(
            angel_number, use_intelligent_analysis=use_intelligent
        )
        meanings_text = "\n".join(angel_data["meanings"])

        tone_description = tone_prompts.get(
            conv_session.tone, tone_prompts.get("guan_yu", "friendly")
        )

        # 構建對話歷史摘要（取最近的3-4輪對話）
        recent_history = (
            conv_session.conversation_history[-6:]
            if len(conv_session.conversation_history) > 6
            else conv_session.conversation_history
        )
        history_text = "\n".join(
            [
                f"{msg['role']}: {msg['content'][:100]}..."
                if len(msg["content"]) > 100
                else f"{msg['role']}: {msg['content']}"
                for msg in recent_history
            ]
        )

        system_prompt = f"""你是一位專業的天使數字解讀師,正在與使用者 {name} 進行深度對話。

天使數字 {angel_number} 的核心意義：
{meanings_text}

【對話背景】
你們正在討論天使數字 {angel_number},以下是最近的對話內容：
{history_text}

【語氣要求】
使用「{tone_description}」的語氣。

【回答要求】
1. 基於天使數字 {angel_number} 的核心意義來回答
2. 參考對話歷史,保持對話的連貫性
3. 提供具體、實用且有啟發性的回答
4. 不使用 markdown 格式標記
5. 回應長度控制在 350-500 字,請務必完整表達完整的意思
6. **避免給予絕對性的預測或判斷，改用建議導向的表達**
7. **禁止使用「一定會」、「絕對」、「必須」等確定性表達，請使用「建議」、「可以考慮」、「或許」等引導性語言**
8. **嚴格禁止使用「因果報應」四字，若需表達相關概念，請統一改用「因果回饋分析」。**

請針對使用者的最新問題,提供有深度的回答。"""

        user_prompt = f"使用者的最新問題：{user_input}\n\n請根據對話背景和天使數字的意義,提供深度且連貫的回答。"

        try:
            client = GPTClient()
            response_text = client.ask(
                system_prompt, user_prompt, temperature=1.0, max_tokens=800
            )

            # 清理格式
            response_text = (
                response_text.replace("**", "")
                .replace("__", "")
                .replace("##", "")
                .replace("###", "")
            )

            # 添加繼續詢問的提示
            if conv_session.tone == "friendly":
                continue_prompt = "\n\n還有其他想了解的嗎？💫"
            elif conv_session.tone == "caring":
                continue_prompt = "\n\n如果還有疑問,我會繼續陪你探索 🌙"
            elif conv_session.tone == "ritual":
                continue_prompt = "\n\n若有其他疑問,請繼續提問 🕯️"
            else:
                continue_prompt = "\n\n若有其他疑問，請繼續提問。"

            response_text += continue_prompt

            conv_session.add_message("assistant", response_text)
            return save_and_return(
                version,
                session_id,
                conv_session,
                {
                    "session_id": session_id,
                    "response": response_text,
                    "state": conv_session.state.value,
                    "requires_input": True,
                },
            )

        except Exception as e:
            print(f"[ERROR] 對話回答錯誤: {e}")
            error_response = f"抱歉,回答過程發生錯誤：{str(e)}"
            conv_session.add_message("assistant", error_response)
            return save_and_return(
                version,
                session_id,
                conv_session,
                {
                    "session_id": session_id,
                    "response": error_response,
                    "state": conv_session.state.value,
                    "requires_input": True,
                },
            )

    # 5. COMPLETED - 已完成
    elif conv_session.state == AngelConversationState.COMPLETED:
        # 已完成,詢問是否要重新開始
        if conv_session.tone == "friendly":
            response = "天使數字解析完成了！✨ 如果你想解讀其他數字,可以點擊上面的「🔄 重新開始」按鈕喔 💫"
        elif conv_session.tone == "caring":
            response = "這次的天使訊息解讀就到這裡了 ☺️✨\n\n希望這些來自宇宙的指引能幫助到你 💕\n\n如果想要解讀其他天使數字,隨時點上面的「🔄 重新開始」按鈕就可以了 🌸"
        elif conv_session.tone == "ritual":
            response = "天使數字的啟示已完整揭示。\n\n若欲解讀其他數字序列,請點擊「🔄 重新開始」按鈕 🕯️"
        else:
            response = "解讀已完成。若欲解讀其他數字，請點擊重新開始。"

        conv_session.add_message("assistant", response)
        return save_and_return(
            version,
            session_id,
            conv_session,
            {
                "session_id": session_id,
                "response": response,
                "state": conv_session.state.value,
                "requires_input": False,
            },
        )

    # 預設回應
    return save_and_return(
        version,
        session_id,
        conv_session,
        {
            "session_id": session_id,
            "response": "抱歉,系統發生錯誤。請重新開始對話。",
            "state": conv_session.state.value,
            "requires_input": False,
        },
    )


def handle_reset(version: str):
    """重置會話"""
    data = request.json
    session_id = data.get("session_id")

    if session_id:
        session_store.delete(version, session_id)

    return jsonify({"success": True})


# ========== API 端點 ==========


# 免費版路由
@angelnum_bp.route("/free/api/init_with_tone", methods=["POST"])
def free_init():
    return handle_init_with_tone("free")


@angelnum_bp.route("/free/api/chat", methods=["POST"])
def free_chat():
    return handle_chat("free")


@angelnum_bp.route("/free/api/reset", methods=["POST"])
def free_reset():
    return handle_reset("free")


# 付費版路由
@angelnum_bp.route("/paid/api/init_with_tone", methods=["POST"])
def paid_init():
    return handle_init_with_tone("paid")


@angelnum_bp.route("/paid/api/chat", methods=["POST"])
def paid_chat():
    return handle_chat("paid")


@angelnum_bp.route("/paid/api/reset", methods=["POST"])
def paid_reset():
    return handle_reset("paid")
