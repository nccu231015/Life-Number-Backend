"""
生命靈數 API Blueprint
支持免費版和付費版的所有功能
"""

from flask import Blueprint, request, jsonify
import uuid

from lifenum.modules.core import SYSTEM_PROMPT as CORE_PROMPT
from lifenum.modules.birthday import SYSTEM_PROMPT as BIRTHDAY_PROMPT
from lifenum.modules.personal_year import SYSTEM_PROMPT as YEAR_PROMPT
from lifenum.modules.grid import SYSTEM_PROMPT as GRID_PROMPT
from lifenum.modules.soul_number import SYSTEM_PROMPT as SOUL_PROMPT
from lifenum.modules.personality import SYSTEM_PROMPT as PERSONALITY_PROMPT
from lifenum.modules.expression import SYSTEM_PROMPT as EXPRESSION_PROMPT
from lifenum.modules.maturity import SYSTEM_PROMPT as MATURITY_PROMPT
from lifenum.modules.challenge import SYSTEM_PROMPT as CHALLENGE_PROMPT
from lifenum.modules.karma import SYSTEM_PROMPT as KARMA_PROMPT

from lifenum.gpt_client import GPTClient
from lifenum.agent import LifeNumberAgent, ConversationSession, ConversationState
from lifenum.version_config import get_config
from lifenum.tone_config import get_tone_config
from lifenum.session_store import get_session_store
from lifenum.utils import (
    birthdate_to_digits_sum,
    reduce_to_core_number,
    compute_birthday_number,
    compute_personal_year_number,
    compute_grid_counts,
    detect_present_lines,
    compute_soul_number,
    compute_personality_number,
    compute_expression_number,
    compute_maturity_number,
    compute_challenge_number,
    compute_karma_number,
    build_ascii_grid,
)

# 創建 Blueprint
lifenum_bp = Blueprint('lifenum', __name__, url_prefix='/life')

# Session 存儲管理器（使用 Redis）
session_store = get_session_store()

# Agent 實例
agent = LifeNumberAgent()

# 免費版語氣提示
FREE_TONE_PROMPTS = {
    "friendly": "請使用親切、輕鬆的語氣，像普通朋友聊天一樣，適合日常對話場景。後續稱呼使用「你」或「妳」。",
    "caring": "請使用貼心、溫暖、關懷的語氣，像家人或閨蜜關心一樣，比親切版更加溫柔體貼，適合需要被理解的人。後續稱呼使用「你」或「妳」。",
    "ritual": "請使用莊重、神聖、充滿儀式感的語氣，適合需做重大決策的場景。保持正式且尊重的態度，使用「您」、「在下」等文言用詞。",
}

# 付費版語氣提示
PAID_TONE_PROMPTS = {
    "guan_yu": "請使用關聖帝君的莊嚴、正直語氣，帶有沉穩節奏。關鍵語彙：忠義、正道、守信、因果、明辨是非。**嚴格警告：禁止使用任何文言文詞彙（汝、吾、乃、之、於、若、然、故、是以、當、須、方能、焉、矣、已為汝析得、為汝、汝之等），必須100%使用現代中文（你、我、的、在、如果、因此、應該、需要、能夠、已為你分析、為你、你的）。語調莊重威嚴但完全現代化表達。**",
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

# ========== 工具函數 ==========
def get_session_by_id(version: str, session_id: str):
    """
    根據 session_id 從 Redis 獲取會話
    """
    if not session_id:
        return None
    
    return session_store.load_session(version, session_id)


def save_and_return(version: str, session_id: str, conv_session: ConversationSession, response_data: dict):
    """
    保存會話到 Redis 並返回 JSON 響應
    """
    # 保存會話到 Redis
    session_store.save_session(version, session_id, conv_session)
    
    # 返回響應
    return jsonify(response_data)

def execute_module(version: str, module_type: str, birthdate: str, name: str, gender: str, tone: str, user_purpose: str = "", english_name: str = "", category: str = "") -> dict:
    """執行指定的模組計算（統一版本，支持免費和付費）"""
    year = None
    
    try:
        # 根據模組類型計算
        if module_type == "core":
            total = birthdate_to_digits_sum(birthdate)
            number = reduce_to_core_number(total)
            system_prompt = CORE_PROMPT
            extra_info = f"加總：{total}\n"
            
            # 付費版：載入預先準備的類別內容
            category_content = ""
            if version == 'paid' and category:
                full_content = agent.load_core_information(number)
                if full_content:
                    category_content = agent.extract_category_content(full_content, category)
                    if category_content:
                        extra_info += f"類別：{category}\n預先準備的內容：\n{category_content}\n\n"
        elif module_type == "birthday":
            number = compute_birthday_number(birthdate)
            system_prompt = BIRTHDAY_PROMPT
            extra_info = ""
        elif module_type == "year":
            number = compute_personal_year_number(birthdate, year)
            system_prompt = YEAR_PROMPT
            extra_info = f"指定年份：{year if year else '當年'}\n"
        elif module_type == "grid":
            counts = compute_grid_counts(birthdate)
            lines = detect_present_lines(counts)
            grid_display = build_ascii_grid(counts)
            system_prompt = GRID_PROMPT
            number = len(lines)
            extra_info = f"九宮格：\n{grid_display}\n連線：{lines}\n"
        elif module_type == "soul":
            number = compute_soul_number(english_name)
            system_prompt = SOUL_PROMPT
            extra_info = f"計算依據：姓名母音分析\n"
        elif module_type == "personality":
            number = compute_personality_number(english_name)
            system_prompt = PERSONALITY_PROMPT
            extra_info = f"計算依據：姓名子音分析\n"
        elif module_type == "expression":
            number = compute_expression_number(english_name)
            system_prompt = EXPRESSION_PROMPT
            extra_info = f"計算依據：姓名完整字母分析\n"
        elif module_type == "maturity":
            number = compute_maturity_number(birthdate)
            system_prompt = MATURITY_PROMPT
            extra_info = ""
        elif module_type == "challenge":
            number = compute_challenge_number(birthdate)
            system_prompt = CHALLENGE_PROMPT
            extra_info = ""
        elif module_type == "karma":
            number = compute_karma_number(birthdate)
            system_prompt = KARMA_PROMPT
            extra_info = ""
        else:
            return {"error": "不支援的模組類型"}
    except Exception as e:
        return {"error": f"計算錯誤：{str(e)}"}
    
    # 根據版本和語氣決定稱呼格式
    if version == 'free':
        if tone == "friendly":
            greeting = f"哈囉{name}！\n\n"
        elif tone == "caring":
            if len(name) >= 2:
                first_name = name[1:] if len(name) <= 3 else name[2:]
            else:
                first_name = name
            greeting = f"嗨{first_name}\n\n"
        else:  # ritual
            title = "先生" if gender == "male" else "小姐"
            greeting = f"{name}{title}您好\n\n"
        
        tone_instruction = FREE_TONE_PROMPTS.get(tone, FREE_TONE_PROMPTS["friendly"])
    else:  # paid
        greeting = ""  # 付費版由語氣決定，通常不用固定格式
        tone_instruction = PAID_TONE_PROMPTS.get(tone, PAID_TONE_PROMPTS["guan_yu"])
    
    # 組合完整的 system prompt
    # 如果有英文名字資訊，添加隱私保護指示
    privacy_note = "\n【隱私要求】計算過程中使用的英文名字僅供數字計算使用，請勿在回覆內容中直接顯示或提及英文名字本身。" if english_name else ""
    
    full_system_prompt = f"""{system_prompt}

【語氣要求】{tone_instruction}
【稱呼要求】請在回應開頭使用「{greeting.strip()}」作為稱呼，然後繼續提供完整的詳細解析內容。稱呼只是開頭，主要內容是生命靈數的深度解析。
【內容要求】除了稱呼外，必須提供至少300字以上的完整生命靈數解析，包含性格分析、優勢說明、人生方向建議等詳細內容。絕不可只有稱呼就結束。
【格式要求】請使用純文字回覆，不要使用任何 markdown 格式標記（如 **、__、#、- 等），直接以清楚的文字和換行組織內容。{privacy_note}
"""
    
    # 建立 user prompt
    if user_purpose:
        user_prompt = f"生日：{birthdate}\n{extra_info}計算結果數字：{number}\n\n【使用者的問題】\n{user_purpose}\n\n請根據計算結果提供完整詳細的生命靈數解析，包含性格底色、優勢、人生方向等完整內容，並針對使用者的問題給予相應的指引與建議。回應必須包含指定的稱呼開頭，但更重要的是提供至少300字以上的深度解析內容。"
    else:
        user_prompt = f"生日：{birthdate}\n{extra_info}計算結果數字：{number}\n\n請提供完整詳細的生命靈數解析，包含性格底色、優勢、人生方向等所有相關內容。回應必須包含指定的稱呼開頭，但主要重點是提供至少300字以上的深度解析內容，絕不可只有稱呼就結束。"
    
    # 調用 GPT API
    try:
        client = GPTClient()
        final_response = client.ask(full_system_prompt, user_prompt, temperature=1.0, max_tokens=2000)
        
        # 清理 markdown 格式標記
        final_response = final_response.replace("**", "").replace("__", "").replace("##", "").replace("###", "")
        
        # 確保回應包含正確的稱呼
        if greeting and not final_response.startswith(greeting.strip()[:3]):
            final_response = greeting + final_response
        
        # 檢查回應是否太短
        if len(final_response.strip()) < 50:
            return {"error": f"AI 回應異常（太短），請重試"}
        
        return {
            "response": final_response,
            "number": number
        }
    except Exception as e:
        print(f"[ERROR] execute_module 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"計算過程發生錯誤：{str(e)}"}

# ========== 通用處理函數 ==========
def handle_init_with_tone(version: str):
    """初始化對話"""
    data = request.json
    tone = data.get("tone", "friendly" if version == "free" else "guan_yu")
    
    config = get_config(version)
    
    # 驗證語氣
    if tone not in config['available_tones']:
        tone = config['available_tones'][0]
    
    # 創建新會話，統一由後端生成 session_id
    session_id = str(uuid.uuid4())
    conv_session = ConversationSession(session_id)
    conv_session.tone = tone
    conv_session.state = ConversationState.WAITING_BASIC_INFO
    
    # 獲取語氣配置並生成問候
    tone_cfg = get_tone_config(version, tone)
    response = tone_cfg['greeting']
    
    conv_session.add_message("assistant", response)
    
    # 保存會話到 Redis
    session_store.save_session(version, session_id, conv_session)
    
    print(f"[Init] 創建新會話: {session_id}, 版本: {version}")
    
    return jsonify({
        "session_id": session_id,  # 返回給前端保存
        "response": response,
        "state": conv_session.state.value,
        "current_module": None
    })

def handle_chat(version: str):
    """主對話處理"""
    data = request.json
    user_input = data.get("message", "").strip()
    session_id = data.get("session_id")
    tone = data.get("tone")
    
    # 驗證 session_id
    if not session_id:
        return jsonify({
            "error": "缺少 session_id",
            "message": "請先調用 init_with_tone 初始化會話"
        }), 400
    
    # 獲取會話
    config = get_config(version)
    conv_session = get_session_by_id(version, session_id)
    
    if not conv_session:
        return jsonify({
            "error": "會話不存在或已過期",
            "message": "請重新調用 init_with_tone 初始化會話",
            "session_id": session_id
        }), 404
    
    # 如果提供了 tone，更新會話的 tone（通常前端不需要傳）
    if tone and tone in config['available_tones']:
        conv_session.tone = tone
    
    conv_session.add_message("user", user_input)
    
    # ========== 狀態機處理 ==========
    
    # 1. WAITING_BASIC_INFO - 等待基本資訊
    if conv_session.state == ConversationState.WAITING_BASIC_INFO:
        # 使用 AI 解析基本資訊（根據版本決定是否要求英文名）
        require_english = config.get('require_english_name', False)
        name, gender, birthdate, english_name, error_msg = agent.extract_birthdate_with_ai(user_input, require_english_name=require_english)
            
        print(f"[DEBUG] extract result: name={name}, gender={gender}, birthdate={birthdate}, error={error_msg}")
        
        if error_msg:
            # 使用 agent 的錯誤訊息生成函數
            response = agent.generate_error_message(tone)
            conv_session.add_message("assistant", response)
            return save_and_return(version, session_id, conv_session, {
                "session_id": session_id,
                "response": response,
                "state": conv_session.state.value,
                "current_module": None
            })
        
        # 保存基本資訊
        conv_session.user_name = name
        conv_session.user_gender = gender
        conv_session.birthdate = birthdate
        conv_session.english_name = english_name
        
        # 使用 agent 生成問候
        response = agent.generate_greeting(name, gender, tone)
        conv_session.state = ConversationState.WAITING_MODULE_SELECTION
        conv_session.add_message("assistant", response)
        
        return save_and_return(version, session_id, conv_session, {
            "session_id": session_id,
            "response": response,
            "state": conv_session.state.value,
            "current_module": None
        })
    
    # 2. WAITING_MODULE_SELECTION - 等待模組選擇
    elif conv_session.state == ConversationState.WAITING_MODULE_SELECTION:
        # 使用 AI 判斷用戶意圖
        module_key, reason = agent.detect_module_from_purpose(user_input, conv_session.user_name)
        print(f"[DEBUG] WAITING_MODULE_SELECTION Detected module: {module_key}, reason: {reason}")
        
        # 識別選擇的模組
        selected_module = module_key
        
        if not selected_module or selected_module not in config['available_modules']:
            response = "抱歉，我不太確定你想選擇哪個模組。請點選下方的按鈕，或直接告訴我想了解的方向。"
            conv_session.add_message("assistant", response)
            return save_and_return(version, session_id, conv_session, {
                "session_id": session_id,
                "response": response,
                "state": conv_session.state.value,
                "current_module": None
            })
        
        # 設置當前模組
        conv_session.current_module = selected_module
        
        # 執行模組計算（所有模組都要先計算）
        result = execute_module(
            version,
            selected_module,
            conv_session.birthdate,
            conv_session.user_name,
            conv_session.user_gender,
            conv_session.tone,
            "",
            conv_session.english_name or "",
            ""  # 其他模組不需要類別
        )
        
        # 檢查是否有錯誤
        if "error" in result:
            error_message = result["error"]
            conv_session.add_message("assistant", error_message)
            return save_and_return(version, session_id, conv_session, {
                "session_id": session_id,
                "response": error_message,
                "state": conv_session.state.value,
                "current_module": conv_session.current_module
            })
        
        # 付費版 core 模組：在結果後加上類別選擇
        if version == 'paid' and selected_module == 'core' and config.get('enable_category_selection', False):
            # 生成類別選擇提示
            category_prompt = agent.generate_category_buttons_message(tone)
            # 合併：核心生命靈數結果 + 類別選擇
            enhanced_response = f"{result['response']}\n\n{category_prompt}"
            
            conv_session.state = ConversationState.CORE_CATEGORY_SELECTION
            conv_session.add_message("assistant", enhanced_response)
            
            # 記錄到 memory
            conv_session.add_to_memory(
                "module_analysis",
                f"已完成核心生命靈數計算，結果為 {result.get('number')}",
                {"module": "core", "number": result.get("number")}
            )
            
            return save_and_return(version, session_id, conv_session, {
                "session_id": session_id,
                "response": enhanced_response,
                "state": conv_session.state.value,
                "current_module": selected_module,
                "number": result.get("number"),
                "show_category_buttons": True,
                "categories": ["財運事業", "家庭人際", "自我成長", "目標規劃"]
            })
        
        # 其他模組：計算完成後進入繼續選項狀態
        conv_session.state = ConversationState.CONTINUE_SELECTION
        conv_session.add_message("assistant", result["response"])
        
        # 記錄到 memory（用於離開時生成總結）
        conv_session.add_to_memory(
            "module_analysis",
            f"已完成 {selected_module} 模組分析，結果為 {result.get('number')}",
            {"module": selected_module, "number": result.get("number")}
        )
        
        return save_and_return(version, session_id, conv_session, {
            "session_id": session_id,
            "response": result["response"],
            "state": conv_session.state.value,
            "current_module": conv_session.current_module,
            "number": result.get("number")
        })
    
    # 3. CORE_CATEGORY_SELECTION - 核心生命靈數類別選擇（付費版專屬）
    elif conv_session.state == ConversationState.CORE_CATEGORY_SELECTION:
        # 識別類別
        category = None
        if "財運" in user_input or "事業" in user_input:
            category = "財運事業"
        elif "家庭" in user_input or "人際" in user_input:
            category = "家庭人際"
        elif "自我" in user_input or "成長" in user_input:
            category = "自我成長"
        elif "目標" in user_input or "規劃" in user_input:
            category = "目標規劃"
        
        if not category:
            response = "抱歉，我不太確定您想選擇哪個類別。請點選下方的按鈕，或直接告訴我想了解的方向。"
            conv_session.add_message("assistant", response)
            return save_and_return(version, session_id, conv_session, {
                "session_id": session_id,
                "response": response,
                "state": conv_session.state.value,
                "current_module": "core",
                "show_category_buttons": True,
                "categories": ["財運事業", "家庭人際", "自我成長", "目標規劃"]
            })
        
        # 保存選擇的類別
        conv_session.selected_category = category
        
        # 生成詢問問題的提示
        conv_session.state = ConversationState.WAITING_CORE_QUESTION
        response = agent.generate_question_prompt(category, tone)
        conv_session.add_message("assistant", response)
        
        return save_and_return(version, session_id, conv_session, {
            "session_id": session_id,
            "response": response,
            "state": conv_session.state.value,
            "current_module": "core",
            "category": category
        })
    
    # 4. WAITING_CORE_QUESTION - 等待核心生命靈數問題（付費版專屬）
    elif conv_session.state == ConversationState.WAITING_CORE_QUESTION:
        user_question = user_input
        
        # 執行 core 模組，帶上用戶問題和類別
        result = execute_module(
            version,
            "core",
            conv_session.birthdate,
            conv_session.user_name,
            conv_session.user_gender,
            conv_session.tone,
            user_question,  # 傳入用戶問題
            conv_session.english_name or "",
            conv_session.selected_category or ""  # 傳入選擇的類別
        )
        
        if "error" in result:
            error_message = result["error"]
            conv_session.add_message("assistant", error_message)
            return save_and_return(version, session_id, conv_session, {
                "session_id": session_id,
                "response": error_message,
                "state": conv_session.state.value,
                "current_module": "core"
            })
        
        # 進入繼續選項狀態
        conv_session.state = ConversationState.CONTINUE_SELECTION
        conv_session.add_message("assistant", result["response"])
        
        # 記錄到 memory（用於離開時生成總結）
        conv_session.add_to_memory(
            "core_qa",
            f"已完成核心生命靈數分析，結果為 {result.get('number')}，類別：{conv_session.selected_category}",
            {"module": "core", "number": result.get("number"), "category": conv_session.selected_category}
        )
        
        return save_and_return(version, session_id, conv_session, {
            "session_id": session_id,
            "response": result["response"],
            "state": conv_session.state.value,
            "current_module": "core",
            "number": result.get("number")
        })
    
    # 5. WAITING_QUESTION - 等待深度提問（付費版所有模組）
    elif conv_session.state == ConversationState.WAITING_QUESTION:
        user_question = user_input
        current_module = conv_session.current_module
        
        if not current_module:
            response = "請先選擇一個模組。"
            conv_session.state = ConversationState.WAITING_MODULE_SELECTION
            conv_session.add_message("assistant", response)
            return save_and_return(version, session_id, conv_session, {
                "session_id": session_id,
                "response": response,
                "state": conv_session.state.value,
                "current_module": None
            })
        
        # 執行當前模組，帶上用戶問題
        result = execute_module(
            version,
            current_module,
            conv_session.birthdate,
            conv_session.user_name,
            conv_session.user_gender,
            conv_session.tone,
            user_question,
            conv_session.english_name or "",
            conv_session.selected_category if current_module == "core" else ""  # core 模組傳入類別
        )
        
        if "error" in result:
            error_message = result["error"]
            conv_session.add_message("assistant", error_message)
            return save_and_return(version, session_id, conv_session, {
                "session_id": session_id,
                "response": error_message,
                "state": conv_session.state.value,
                "current_module": current_module
            })
        
        # 回到繼續選項狀態
        conv_session.state = ConversationState.CONTINUE_SELECTION
        conv_session.add_message("assistant", result["response"])
        
        return save_and_return(version, session_id, conv_session, {
            "session_id": session_id,
            "response": result["response"],
            "state": conv_session.state.value,
            "current_module": current_module,
            "number": result.get("number")
        })
    
    # 6. CONTINUE_SELECTION - 繼續選項
    elif conv_session.state == ConversationState.CONTINUE_SELECTION:
        # 付費版：支持「繼續問問題」
        if version == 'paid' and config.get('enable_continuous_chat', False):
            if "繼續" in user_input or "問問題" in user_input or "提問" in user_input:
                # 進入深度提問狀態
                conv_session.state = ConversationState.WAITING_QUESTION
                
                # 根據當前模組生成對應的提示
                current_module = conv_session.current_module
                if current_module == "birthday":
                    response = agent.generate_birthday_question_prompt(tone)
                elif current_module == "grid":
                    response = agent.generate_grid_question_prompt(tone)
                elif current_module == "year":
                    response = agent.generate_year_question_prompt(tone)
                elif current_module == "soul":
                    response = agent.generate_soul_question_prompt(tone)
                elif current_module == "personality":
                    response = agent.generate_personality_question_prompt(tone)
                elif current_module == "expression":
                    response = agent.generate_expression_question_prompt(tone)
                elif current_module == "maturity":
                    response = agent.generate_maturity_question_prompt(tone)
                elif current_module == "challenge":
                    response = agent.generate_challenge_question_prompt(tone)
                elif current_module == "karma":
                    response = agent.generate_karma_question_prompt(tone)
                else:
                    response = "請問你想了解什麼？"
                
                conv_session.add_message("assistant", response)
                return save_and_return(version, session_id, conv_session, {
                    "session_id": session_id,
                    "response": response,
                    "state": conv_session.state.value,
                    "current_module": current_module
                })
        
        # 選擇其他生命靈數
        if "其他生命靈數" in user_input or "其他模組" in user_input:
            conv_session.state = ConversationState.WAITING_MODULE_SELECTION
            conv_session.current_module = None
            
            # 免費版使用簡單訊息
            if version == 'free':
                if tone == "friendly":
                    response = "好的！請選擇你想了解的其他模組～"
                elif tone == "caring":
                    response = "當然可以 ✨ 請選擇你想了解的其他模組吧～"
                else:  # ritual
                    response = "好的。請選擇您想了解的其他模組。"
            else:
                # 付費版使用 agent 訊息
                response = agent.generate_return_to_modules_message(
                    conv_session.user_name,
                    conv_session.user_gender,
                    tone
                )
            
            conv_session.add_message("assistant", response)
            return save_and_return(version, session_id, conv_session, {
                "session_id": session_id,
                "response": response,
                "state": conv_session.state.value,
                "current_module": None
            })
        
        # 離開
        elif "離開" in user_input:
            conv_session.state = ConversationState.COMPLETED
            
            # 付費版生成完整的對話總結（包含水晶和點燈推薦）
            if version == 'paid':
                response = agent.generate_conversation_summary(conv_session, tone)
            else:
                # 免費版使用簡單訊息
                tone_cfg = get_tone_config(version, tone)
                response = tone_cfg.get('completed', "感謝使用！")
            
            conv_session.add_message("assistant", response)
            return save_and_return(version, session_id, conv_session, {
                "session_id": session_id,
                "response": response,
                "state": conv_session.state.value,
                "current_module": conv_session.current_module
            })
        
        else:
            # 未識別的輸入
            tone_cfg = get_tone_config(version, tone)
            if version == 'paid' and config.get('enable_continuous_chat', False):
                options = tone_cfg.get('continue_options', ['繼續問問題', '其他生命靈數', '離開'])
            else:
                options = tone_cfg.get('continue_options', ['其他生命靈數', '離開'])
            response = f"請選擇：{' / '.join(options)}"
            
            conv_session.add_message("assistant", response)
            return save_and_return(version, session_id, conv_session, {
                "session_id": session_id,
                "response": response,
                "state": conv_session.state.value,
                "current_module": conv_session.current_module
            })
    
    # 7. COMPLETED - 已完成
    elif conv_session.state == ConversationState.COMPLETED:
        tone_cfg = get_tone_config(version, tone)
        response = tone_cfg.get('completed', "感謝使用！")
        conv_session.add_message("assistant", response)
        
        return save_and_return(version, session_id, conv_session, {
            "session_id": session_id,
            "response": response,
            "state": conv_session.state.value,
            "current_module": conv_session.current_module
        })
    
    # 默認回應
    return save_and_return(version, session_id, conv_session, {
        "session_id": session_id,
        "response": "未知狀態，請重新開始。",
        "state": conv_session.state.value,
        "current_module": conv_session.current_module
    })

def handle_reset(version: str):
    """重置會話"""
    data = request.json or {}
    session_id = data.get("session_id")
    
    if session_id:
        # 從 Redis 刪除會話
        session_store.delete(version, session_id)
        print(f"[Reset] 刪除會話: {session_id}, 版本: {version}")
    
    return jsonify({"success": True})

# ========== 路由 ==========
# 免費版路由
@lifenum_bp.route("/free/api/init_with_tone", methods=["POST"])
def free_init():
    return handle_init_with_tone('free')

@lifenum_bp.route("/free/api/chat", methods=["POST"])
def free_chat():
    return handle_chat('free')

@lifenum_bp.route("/free/api/reset", methods=["POST"])
def free_reset():
    return handle_reset('free')

# 付費版路由
@lifenum_bp.route("/paid/api/init_with_tone", methods=["POST"])
def paid_init():
    return handle_init_with_tone('paid')

@lifenum_bp.route("/paid/api/chat", methods=["POST"])
def paid_chat():
    return handle_chat('paid')

@lifenum_bp.route("/paid/api/reset", methods=["POST"])
def paid_reset():
    return handle_reset('paid')

