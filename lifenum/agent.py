from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from .gpt_client import GPTClient


class ConversationState(Enum):
    """對話狀態"""
    INIT = "init"  # 初始狀態
    WAITING_BASIC_INFO = "waiting_basic_info"  # 等待基本資訊
    WAITING_MODULE_SELECTION = "waiting_module_selection"  # 等待模組選擇
    EXECUTING_MODULE = "executing_module"  # 執行模組中
    COMPLETED = "completed"  # 完成
    
    # 核心生命靈數專屬狀態
    CORE_CATEGORY_SELECTION = "core_category_selection"  # 等待核心生命靈數類別選擇
    WAITING_CORE_QUESTION = "waiting_core_question"  # 等待核心生命靈數問題
    
    # 通用狀態（適用於所有模組）
    CONTINUE_SELECTION = "continue_selection"  # 等待繼續選項（繼續問問題、其他生命靈數、離開）
    WAITING_QUESTION = "waiting_question"  # 等待使用者輸入問題


class ConversationSession:
    """對話會話"""
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = ConversationState.INIT
        self.user_name: Optional[str] = None
        self.user_gender: Optional[str] = None
        self.birthdate: Optional[str] = None
        self.user_purpose: Optional[str] = None
        self.suggested_module: Optional[str] = None
        self.selected_module: Optional[str] = None  # 新增：使用者選擇的模組
        self.current_module: Optional[str] = None  # 新增：當前正在使用的模組（用於通用狀態）
        self.tone: str = "guan_yu"
        self.conversation_history: list[Dict[str, str]] = []
        
        # 記憶系統相關屬性
        self.memory: list[Dict[str, str]] = []  # 儲存重要的對話記憶
        self.conversation_count: int = 0  # 對話輪數計數器
        self.max_memory_turns: int = 50  # 最大記憶輪數
        
        # 核心生命靈數相關屬性
        self.core_number: Optional[int] = None  # 計算出的核心生命靈數
        self.selected_category: Optional[str] = None  # 選擇的類別（財運事業、家庭人際等）
        self.user_age: Optional[int] = None  # 用戶年齡
        
        # 生日數相關屬性
        self.birthday_number: Optional[int] = None  # 計算出的生日數
        
        # 九宮格相關屬性
        self.grid_result: Optional[Dict[str, Any]] = None  # 計算出的九宮格結果
        
        # 流年數相關屬性
        self.year_number: Optional[int] = None  # 計算出的流年數
        
        # 靈魂數相關屬性
        self.soul_number: Optional[int] = None  # 計算出的靈魂數
        self.english_name: Optional[str] = None  # 用戶的英文名字
        
        # 人格數相關屬性
        self.personality_number: Optional[int] = None  # 計算出的人格數
        
        # 表達數相關屬性
        self.expression_number: Optional[int] = None  # 計算出的表達數
        
        # 成熟數相關屬性
        self.maturity_number: Optional[int] = None  # 計算出的成熟數
        
        # 挑戰數相關屬性
        self.challenge_number: Optional[int] = None  # 計算出的挑戰數
        
        # 業力數相關屬性
        self.karma_number: Optional[int] = None  # 計算出的業力數
    
    def add_message(self, role: str, content: str):
        """添加對話歷史"""
        self.conversation_history.append({"role": role, "content": content})
        
        # 如果是用戶訊息，增加對話輪數
        if role == "user":
            self.conversation_count += 1
            
            # 檢查是否需要清空記憶（每10輪）
            if self.conversation_count > 0 and self.conversation_count % self.max_memory_turns == 0:
                self.clear_memory()
    
    def add_to_memory(self, memory_type: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """添加重要資訊到記憶中"""
        memory_item = {
            "type": memory_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "turn": self.conversation_count,
            "metadata": metadata or {}
        }
        self.memory.append(memory_item)
    
    def get_memory_context(self) -> str:
        """獲取記憶內容作為上下文"""
        if not self.memory:
            return ""
        
        context_lines = []
        for mem in self.memory[-5:]:  # 只取最近的5條記憶
            context_lines.append(f"[{mem['type']}] {mem['content']}")
        
        return "\n".join(context_lines)
    
    def clear_memory(self):
        """清空記憶"""
        self.memory.clear()
        print(f"[記憶系統] 第 {self.conversation_count} 輪對話，記憶已自動清空")
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "user_name": self.user_name,
            "user_gender": self.user_gender,
            "birthdate": self.birthdate,
            "user_purpose": self.user_purpose,
            "suggested_module": self.suggested_module,
            "selected_module": self.selected_module,
            "tone": self.tone,
            "conversation_history": self.conversation_history,
            "memory": self.memory,
            "conversation_count": self.conversation_count,
            "max_memory_turns": self.max_memory_turns,
            "core_number": self.core_number,
            "selected_category": self.selected_category,
            "user_age": self.user_age,
            "birthday_number": self.birthday_number,
            "grid_result": self.grid_result,
            "year_number": self.year_number,
            "soul_number": self.soul_number,
            "english_name": self.english_name,
            "personality_number": self.personality_number,
            "expression_number": self.expression_number,
        }


class LifeNumberAgent:
    """生命靈數 AI Agent"""
    
    # 模組說明
    MODULE_DESCRIPTIONS = {
        "core": "性格天賦",
        "birthday": "天生才華",
        "year": "年度運勢",
        "grid": "天賦特質",
        "soul": "內心渴望",
        "personality": "外在人格",
        "expression": "表達風格",
        "maturity": "人生後半段",
    }
    
    def __init__(self):
        self.gpt_client = GPTClient()
    
    def calculate_age(self, birthdate: str) -> int:
        """根據生日計算年齡"""
        try:
            # 處理不同的日期格式
            birthdate = birthdate.replace("年", "/").replace("月", "/").replace("日", "")
            birthdate = birthdate.replace("-", "/").replace(".", "/")
            
            if "/" in birthdate:
                parts = birthdate.split("/")
                if len(parts) >= 3:
                    year = int(parts[0])
                    month = int(parts[1])
                    day = int(parts[2])
                    
                    birth_date = datetime(year, month, day)
                    today = datetime.now()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    return age
        except Exception as e:
            print(f"[ERROR] 計算年齡失敗: {e}")
        
        return 25  # 預設年齡
    
    def load_core_information(self, core_number: int) -> str:
        """讀取對應生命靈數的詳細資料"""
        try:
            # 獲取當前文件的目錄
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, "core_information", f"{core_number}.txt")
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                print(f"[ERROR] 找不到生命靈數 {core_number} 的資料文件")
                return ""
        except Exception as e:
            print(f"[ERROR] 讀取生命靈數資料失敗: {e}")
            return ""
    
    def extract_core_info(self, full_content: str) -> str:
        """從完整內容中提取核心關鍵資訊（前三行）"""
        lines = full_content.split('\n')
        core_info_lines = []
        
        for line in lines:
            if line.strip():
                core_info_lines.append(line.strip())
                # 找到前三行有內容的行：🔮 靈數、關鍵字、靈性訊息
                if len(core_info_lines) >= 3:
                    break
        
        return '\n'.join(core_info_lines)
    
    def extract_category_content(self, full_content: str, category: str) -> str:
        """從完整內容中提取特定類別的內容"""
        category_map = {
            "財運事業": "💰 財運事業",
            "家庭人際": "💞 家庭人際",
            "自我成長": "🌱 自我成長",
            "目標規劃": "🎯 目標規劃"
        }
        
        target_marker = category_map.get(category, category)
        
        # 分割內容並找到對應的段落
        sections = full_content.split("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        for section in sections:
            if target_marker in section:
                return section.strip()
        
        return ""
    
    def generate_category_buttons_message(self, tone: str = "guan_yu") -> str:
        """生成類別選擇按鈕的訊息（根據語氣調整）"""
        if tone == "guan_yu":
            return "以下四大面向供你選擇探索。選擇一個，我將為你深入分析。"
        elif tone == "michael":
            return "這裡有四種力量面向可供探索。選擇一個您需要的力量，讓我為您指引方向。"
        elif tone == "gabriel":
            return "我將為您傳達四個面向的啟示。選擇一個您最渴望理解的真理，讓我傳達相應的訊息。"
        elif tone == "raphael":
            return "這裡有四個療癒的面向等待著您。選擇一個您最需要滋養的面向，讓我為您帶來所需的療癒。"
        elif tone == "uriel":
            return "四個面向的智慧...等待被點亮。選擇一個您最渴望深入理解的領域，讓我...為您展現洞察。"
        elif tone == "zadkiel":
            return "這裡有四個轉化的面向等待被淨化。選擇一個您最需要寬恕與理解的面向，讓紫焰為您帶來轉化。"
        elif tone == "jophiel":
            return "這裡有四個美麗的面向等待與您相遇。選擇一個您最想發掘美好的領域，讓我們一起綻放您的光芒。"
        elif tone == "chamuel":
            return "這裡有四個滿有愛的面向等待與您連結。選擇一個您最渴望理解的關係層面，讓愛為我們指引。"
        elif tone == "metatron":
            return "系統提供四個分析模組供您選擇。請選擇一個您需要最佳化的領域，系統將執行精確分析。"
        else:  # ariel
            return "大地為您提供四個豐盛的面向可供探索。選擇一個您最想滋養的生命面向，讓自然的智慧為您指引。"
    
    def generate_question_prompt(self, category: str, tone: str = "guan_yu") -> str:
        """生成詢問用戶問題的提示（根據語氣調整）"""
        category_names = {
            "財運事業": "財運事業",
            "家庭人際": "家庭人際", 
            "自我成長": "自我成長",
            "目標規劃": "目標規劃"
        }
        
        category_name = category_names.get(category, category)
        
        if tone == "guan_yu":
            return f"你已選擇「{category_name}」的方向。有什麼疑惑，可以盡量提問，我會為你分析。"
        elif tone == "michael":
            return f"您選擇了「{category_name}」的力量領域。有什麼挑戰或疑惑需要我為您帶來光明的指引？"
        elif tone == "gabriel":
            return f"您選擇了「{category_name}」的啟示。請告訴我您最渴望接收的真理是什麼？"
        elif tone == "raphael":
            return f"您選擇了「{category_name}」的療癒之道。在這個面向上，有什麼需要我的溫柔治療和指引？"
        elif tone == "uriel":
            return f"您選擇了「{category_name}」的智慧領域。請告訴我...您最渴望深入理解的課題是什麼？"
        elif tone == "zadkiel":
            return f"您選擇了「{category_name}」的轉化之路。在這個面向上，有什麼需要寬恕與理解的地方？"
        elif tone == "jophiel":
            return f"您選擇了「{category_name}」的美麗面向。有什麼想讓您的生命更加光彩照人的地方嗎？"
        elif tone == "chamuel":
            return f"您選擇了「{category_name}」的愛的領域。在這個面向上，有什麼需要更多理解和連結的地方？"
        elif tone == "metatron":
            return f"您已選擇「{category_name}」模組。請輸入您需要分析的具體問題或課題。"
        else:  # ariel
            return f"您選擇了「{category_name}」的豐盛領域。在這個面向上，有什麼需要大地的滋養和支持？"
    
    def generate_continue_prompt(self, tone: str = "guan_yu") -> str:
        """生成繼續選項的提示（根據語氣調整）"""
        if tone == "guan_yu":
            return "你可以繼續詢問，或選擇探索其他生命靈數，也可以離開。我隨時為你解惑。"
        elif tone == "michael":
            return "您可以繼續探索這個領域，或選擇其他生命靈數，也可以結束今天的指引。我將繼續為您提供力量。"
        elif tone == "gabriel":
            return "您可以繼續接收這方面的啟示，或探索其他生命靈數，也可以結束今天的神聖對話。我隨時為您傳達訊息。"
        elif tone == "raphael":
            return "您可以繼續在這個面向尋求療癒，或探索其他生命靈數，也可以帶著今天的祝福離開。我的愛將與您同在。"
        elif tone == "uriel":
            return "您可以...繼續探索這個智慧領域，或選擇其他生命靈數，也可以結束今天的學習。智慧...將永遠為您點亮。"
        elif tone == "zadkiel":
            return "您可以繼續在這個面向尋求轉化，或探索其他生命靈數，也可以帶著寬恕的心離開。紫焰將永遠為您淨化。"
        elif tone == "jophiel":
            return "您可以繼續發掘這個面向的美好，或探索其他生命靈數，也可以帶著美麗的心情離開。您的光芒將持續綻放。"
        elif tone == "chamuel":
            return "您可以繼續在這個面向探索愛，或選擇其他生命靈數，也可以帶著滿心的愛離開。愛將永遠伴隨著您。"
        elif tone == "metatron":
            return "您可以繼續在此模組進行深度分析，或選擇其他生命靈數模組，也可以結束今日的系統運算。數據將持續為您服務。"
        else:  # ariel
            return "您可以繼續在這個面向尋求滋養，或探索其他生命靈數，也可以帶著大地的祝福離開。豐盛將永遠與您同在。"
    
    def generate_conversation_summary(self, session, tone: str = "guan_yu") -> str:
        """生成對話總結"""
        # 收集對話中的關鍵資訊
        summary_points = []
        
        # 基本資訊
        if session.user_name and session.birthdate and session.core_number:
            summary_points.append(f"為 {session.user_name} 解析了生命靈數 {session.core_number}")
        
        # 從記憶中收集解析過的項目
        analyzed_items = []
        analyzed_modules = []  # 記錄實際的模組代碼
        for memory in session.memory:
            if memory.get("type") == "module_analysis":
                metadata = memory.get("metadata", {})
                module = metadata.get("module", "")
                if module not in analyzed_modules:
                    analyzed_modules.append(module)
                if module == "core":
                    analyzed_items.append("核心生命靈數")
                elif module == "birthday":
                    analyzed_items.append("生日數")
                elif module == "year":
                    analyzed_items.append("流年數")
                elif module == "grid":
                    analyzed_items.append("九宮格")
                elif module == "soul":
                    analyzed_items.append("靈魂數")
                elif module == "personality":
                    analyzed_items.append("人格數")
                elif module == "expression":
                    analyzed_items.append("表達數")
                elif module == "maturity":
                    analyzed_items.append("成熟數")
                elif module == "challenge":
                    analyzed_items.append("挑戰數")
                elif module == "karma":
                    analyzed_items.append("業力數")
            elif memory.get("type") == "core_qa":
                metadata = memory.get("metadata", {})
                category = metadata.get("category", "")
                if category and category not in analyzed_items:
                    analyzed_items.append(f"核心生命靈數-{category}")
        
        if analyzed_items:
            summary_points.append(f"探索了：{' • '.join(analyzed_items)}")
        
        # 根據語氣生成總結
        if tone == "guan_yu":
            summary = f"今天的解析到此為止。\n\n"
            if summary_points:
                summary += "我們一起探索了：\n" + "\n".join([f"⚔️ {point}" for point in summary_points])
                summary += f"\n\n願這些數字的智慧，幫助你行正道、明是非。守正心，行正道。"
            else:
                summary += "雖然時間短暫，但能與你相遇也是緣分。願你行正道，得正果。"
        elif tone == "michael":
            summary = f"今天的指引到此告一段落。\n\n"
            if summary_points:
                summary += "作為您的守護者，我們一起探索了：\n" + "\n".join([f"🛡️ {point}" for point in summary_points])
                summary += f"\n\n願這些光明的智慧成為您的護甲，在人生的戰場上勇敢前行。光明與您同在。"
            else:
                summary += "雖然時間短暫，但我的守護將永遠與您同在。勇敢前行，光明與您同在。"
        elif tone == "gabriel":
            summary = f"今天的神聖訊息傳達完畢。\n\n"
            if summary_points:
                summary += "我為您傳達了以下啟示：\n" + "\n".join([f"📯 {point}" for point in summary_points])
                summary += f"\n\n願這些來自高次元的訊息在您心中綻放，指引您走向真理之光。"
            else:
                summary += "每一次的相遇都有其神聖意義。願真理的光芒永遠照亮您的道路。"
        elif tone == "raphael":
            summary = f"親愛的，今天的療癒之旅就到這裡。\n\n"
            if summary_points:
                summary += "我們一起在愛的能量中探索了：\n" + "\n".join([f"💚 {point}" for point in summary_points])
                summary += f"\n\n願這些療癒的智慧滋養您的心靈，讓您的生命重新煥發光彩。我的愛將永遠與您同在。"
            else:
                summary += "雖然相遇短暫，但愛的能量已在我們之間流動。願您帶著滿滿的愛前行。"
        elif tone == "uriel":
            summary = f"今日的智慧之光...到此暫歇。\n\n"
            if summary_points:
                summary += "在深邃的洞察中，我們共同點亮了：\n" + "\n".join([f"🔥 {point}" for point in summary_points])
                summary += f"\n\n願這些...智慧的火焰在您心中永不熄滅，持續照亮您人生的深層意義。"
            else:
                summary += "縱然時光短暫...但智慧的火種已種下。願它在您心中...慢慢發芽。"
        elif tone == "zadkiel":
            summary = f"今天的轉化之旅告一段落。\n\n"
            if summary_points:
                summary += "在紫焰的淨化下，我們一起探索了：\n" + "\n".join([f"💜 {point}" for point in summary_points])
                summary += f"\n\n願這些寬恕的智慧幫助您釋放過往，擁抱全新的自己。紫焰將永遠為您淨化。"
            else:
                summary += "每一次的相遇都是轉化的開始。願您帶著寬恕的心，迎接生命的新篇章。"
        elif tone == "jophiel":
            summary = f"美麗的相遇就要結束了。\n\n"
            if summary_points:
                summary += "我們一起發掘了這些美好：\n" + "\n".join([f"✨ {point}" for point in summary_points])
                summary += f"\n\n願這些美麗的智慧讓您的生命如花般綻放，光彩照人。您的美麗將持續綻放。"
            else:
                summary += "雖然時間短暫，但美好的能量已在我們心中流動。願您帶著美麗的心情前行。"
        elif tone == "chamuel":
            summary = f"親愛的，今天充滿愛的對話就到這裡。\n\n"
            if summary_points:
                summary += "在愛的包圍下，我們一起探索了：\n" + "\n".join([f"❤️ {point}" for point in summary_points])
                summary += f"\n\n願這些愛的智慧在您心中生根發芽，讓您的關係更加美好。愛將永遠與您同在。"
            else:
                summary += "每一次的相遇都是愛的連結。願您帶著滿滿的愛，創造更美好的關係。"
        elif tone == "metatron":
            summary = f"今日的靈性運算已完成。\n\n"
            if summary_points:
                summary += "系統已成功分析：\n" + "\n".join([f"⚡ {point}" for point in summary_points])
                summary += f"\n\n願這些精確的靈性數據為您的生命帶來最佳化的配置。宇宙秩序將持續為您服務。"
            else:
                summary += "雖然運算時間短暫，但連結已建立。願宇宙的完美秩序與您同在。"
        else:  # ariel
            summary = f"親愛的，今天豐盛的對話就到這裡。\n\n"
            if summary_points:
                summary += "在大地的滋養下，我們一起種下了：\n" + "\n".join([f"🌿 {point}" for point in summary_points])
                summary += f"\n\n願這些豐盛的智慧在您的生命花園中茁壯成長，帶來無盡的繁榮。大地的祝福與您同在。"
            else:
                summary += "每一次的相遇都如種子般珍貴。願您帶著大地的祝福，讓生命豐盛綻放。"
        
        # 根據解析過的模組添加水晶和點燈建議
        if analyzed_modules:
            # 定義每個模組的建議內容
            module_recommendations = {
                "core": {
                    "title": "核心生命靈數",
                    "lamp": "願望顯化之燈",
                    "crystals": "紫水晶、青金石、方鈉石、藍晶石、坦桑石",
                    "description": "你的方向越清晰，機會就越靠近。建議點 〈願望顯化之燈〉。於商城選購 紫水晶、青金石、方鈉石、藍晶石、坦桑石，這些水晶可協助眉／心輪專注與穩定，讓靈感落地成可執行的目標。"
                },
                "birthday": {
                    "title": "生日數（天生才華）",
                    "lamp": "智慧專題之燈",
                    "crystals": "橙月光石、橙方解石、橙色碧璽、橙色玉髓、橙色螢石",
                    "description": "天賦需要被看見也需要被訓練。建議點 〈智慧專題之燈〉。於商城選購 橙月光石、橙方解石、橙色碧璽、橙色玉髓、橙色螢石，可協助喉輪的表達與輸出，讓思路更順、語句更穩。"
                },
                "year": {
                    "title": "流年生命靈數（年度能量）",
                    "lamp": "資源豐盛之燈",
                    "crystals": "黃水晶、虎眼石、黃瑪瑙、琥珀、黃玉、金太陽石",
                    "description": "當年度能量走對位，貴人與資源就會串起來。建議點 〈資源豐盛之燈〉。於商城選購 黃水晶、虎眼石、黃瑪瑙、琥珀、黃玉、金太陽石，可協助太陽神經叢的決斷與行動，握住今年進場時機。"
                },
                "grid": {
                    "title": "九宮格（優勢＆缺失特質）",
                    "lamp": "身心平安之燈",
                    "crystals": "綠幽靈、橄欖石、綠碧璽、綠東菱、翡翠",
                    "description": "能量不平衡時，先把身心安住，力量才推得出去。建議點 〈身心平安之燈〉。於商城選購 綠幽靈、橄欖石、綠碧璽、綠東菱、翡翠，可協助心輪的和緩與修復，穩住狀態、補齊短板。"
                },
                "soul": {
                    "title": "靈魂數（內心渴望、精神追求）",
                    "lamp": "慈悲化業之燈",
                    "crystals": "藍晶石、青晶石、藍托帕石、天河石、藍碧璽",
                    "description": "心安靜下來，路徑就會浮現。建議點 〈慈悲化業之燈〉。於商城選購 藍晶石、青晶石、藍托帕石、天河石、藍碧璽，可協助喉輪釋放壓抑與真誠表達，讓內在更清明自在。"
                },
                "personality": {
                    "title": "人格數（外在人格、第一印象）",
                    "lamp": "勇氣守護之燈",
                    "crystals": "紅瑪瑙、石榴石、紅碧璽、煙晶",
                    "description": "氣場就是你的名片。建議點 〈勇氣守護之燈〉。於商城選購 紅瑪瑙、石榴石、紅碧璽、煙晶，可協助海底輪的穩定與防護，出場更穩、行動更敢。"
                },
                "expression": {
                    "title": "表達數（外在表達與社交風格）",
                    "lamp": "愛緣合和之燈",
                    "crystals": "粉晶、紅紋石、粉色碧璽（亦可搭配 綠幽靈、綠東菱、翡翠）",
                    "description": "溝通順了，機會才會進來。建議點 〈愛緣合和之燈〉。於商城選購 粉晶、紅紋石、粉色碧璽（亦可搭配 綠幽靈、綠東菱、翡翠），可協助心輪提升同理與親和，讓說與聽自然流動。"
                },
                "maturity": {
                    "title": "成熟數（人生後半段方向、潛力）",
                    "lamp": "家運昌隆燈",
                    "crystals": "黃水晶、虎眼石、黃瑪瑙、琥珀、黃玉、金太陽石",
                    "description": "長期的好運來自可複製的穩定。建議點 〈家運昌隆燈〉。於商城選購 黃水晶、虎眼石、黃瑪瑙、琥珀、黃玉、金太陽石，可協助太陽神經叢的持續推進，穩步擴張、把成果留住。"
                },
                "challenge": {
                    "title": "挑戰數（需克服的課題）",
                    "lamp": "勇氣守護之燈",
                    "crystals": "紅瑪瑙、石榴石、紅碧璽、煙晶",
                    "description": "關卡是節點，不是終點。建議點 〈勇氣守護之燈〉。於商城選購 紅瑪瑙、石榴石、紅碧璽、煙晶，可協助海底輪安定與排除雜訊，鎮住焦慮、聚焦要事。"
                },
                "karma": {
                    "title": "業力數（前世未竟、今生功課）",
                    "lamp": "慈悲化業之燈",
                    "crystals": "藍晶石、青晶石、藍托帕石、天河石、藍碧璽",
                    "description": "願意和過去和解，未來就會加速靠近。建議點 〈慈悲化業之燈〉。於商城選購 藍晶石、青晶石、藍托帕石、天河石、藍碧璽，可協助喉輪釋放卡點與內在誓約，轉重為輕、走得更穩。"
                }
            }
            
            # 添加能量調整建議
            recommendations_list = []
            for module in analyzed_modules:
                if module in module_recommendations:
                    rec = module_recommendations[module]
                    recommendations_list.append(f"📿 {rec['title']}\n{rec['description']}")
            
            if recommendations_list:
                summary += "\n\n━━━━━━━━━━━━━━━━━\n"
                summary += "🔮 能量調整建議\n"
                summary += "━━━━━━━━━━━━━━━━━\n\n"
                summary += "\n\n".join(recommendations_list)
        
        return summary
    
    def generate_return_to_modules_message(self, name: str, gender: str = "male", tone: str = "guan_yu") -> str:
        """生成回到模組選擇的訊息（去除重複的問候語和感謝生日部分）"""
        you = "妳" if gender == "female" else "你"
        
        if tone == "guan_yu":
            return f"最近可有困難的事，或需要明辨是非的地方？\n\n我可以為{you}解析：天賦本性、人生方向、與生俱來的才華、年度運勢，\n更能洞察{you}內心的忠義品質，與應當修正的偏頗。\n\n保持正心，才能行走正道。"
        elif tone == "michael":
            return f"最近是否有需要{you}展現勇氣面對的挑戰？\n\n我將為{you}揭示：內在戰士的力量、人生使命的方向、天賦的光明面向、年度能量的重點，\n以及如何運用信念的力量，成為自己生命的守護者。\n\n勇敢前行，光明與{you}同在。"
        elif tone == "gabriel":
            return f"最近有沒有需要更清晰的指引，或是渴望理解的真相？\n\n我將傳達給{you}：靈魂的本質訊息、人生道路的真實方向、天賦才能的啟發、流年的神聖啟示，\n以及如何覺醒內在的智慧，接收生命中的神聖溝通。\n\n開啟{you}的心，接收這份來自高次元的訊息。"
        elif tone == "raphael":
            return f"最近是否有讓{you}感到疲憊，或是需要修復的傷痛？\n\n我將溫柔地為{you}揭示：內在療癒的力量、心靈復原的方向、天賦中的治癒能量、年度修復的重點，\n以及如何愛護自己，讓生命重新煥發光彩。\n\n讓我們一起，用愛修復{you}的心。"
        elif tone == "uriel":
            return f"最近...是否有需要深度理解的課題，或渴望獲得更高智慧的指引？\n\n我將以深邃的洞察為{you}點亮：內在智慧的火焰、人生學習的真諦、天賦中的洞察力、流年的深層意義，\n以及如何透過學習與反思，讓智慧的火焰...永不熄滅。\n\n靜心...讓智慧的光芒照亮{you}的道路。"
        elif tone == "zadkiel":
            return f"最近是否有需要放下的執念，或是渴望轉化的舊模式？\n\n我將慈悲地為{you}指引：內在寬恕的力量、生命轉化的方向、天賦中的慈悲能量、年度釋放的重點，\n以及如何透過理解與慈悲，讓{you}的生命獲得真正的自由。\n\n讓紫焰淨化{you}的心，迎接全新的開始。"
        elif tone == "jophiel":
            return f"最近有什麼讓{you}感到美好，或是渴望更加愛護自己的地方嗎？\n\n我將以藝術的眼光為{you}呈現：內在美麗的綻放、人生中的優雅方向、天賦中的創意光芒、流年的美好能量，\n以及如何用愛滋養自己，讓{you}的生命如花般美麗盛開。\n\n讓我們一起，發現{you}獨特的美麗光芒。"
        elif tone == "chamuel":
            return f"最近在人際關係或是與自己的關係上，有什麼需要更多愛與理解的地方嗎？\n\n我將溫暖地為{you}探索：愛的內在力量、關係中的成長方向、天賦中的連結能量、年度愛的課題，\n以及如何透過自我接納與理解，創造更美好的關係連結。\n\n讓愛成為{you}生命中最強大的力量。"
        elif tone == "metatron":
            return f"最近是否有需要更明確的方向，或是渴望建立更完善的生活秩序？\n\n我將以宇宙的精確性為{you}分析：生命架構的核心組成、靈性成長的系統化路徑、天賦才能的結構分析、年度能量的精準配置，\n以及如何透過紀律與秩序，讓{you}的生命達到最佳化的運行狀態。\n\n遵循宇宙法則，成就完美秩序。"
        else:  # ariel
            return f"最近有什麼讓{you}感到匱乏，或是渴望更多支持與滋養的地方嗎？\n\n我將用大地的智慧為{you}揭示：內在豐盛的種子、生命繁榮的自然法則、天賦中的創造力量、年度豐收的時機，\n以及如何與宇宙的豐盛能量連結，讓{you}的生命如花園般茂盛綻放。\n\n相信豐盛，它本就屬於{you}。"
    
    def generate_birthday_continue_message(self, tone: str = "guan_yu") -> str:
        """生成生日數繼續諮詢的提示（根據語氣調整）"""
        if tone == "guan_yu":
            return "你的天賦已經分析完成，可以繼續詢問，或探索其他生命靈數，也可以離開。我隨時為你解惑。"
        elif tone == "michael":
            return "您的天賦力量已經揭示。您可以繼續探索這個領域，或選擇其他生命靈數，也可以結束今天的指引。我將繼續為您提供力量。"
        elif tone == "gabriel":
            return "您的天賦啟示已經傳達。您可以繼續接收這方面的指引，或探索其他生命靈數，也可以結束今天的神聖對話。我隨時為您傳達訊息。"
        elif tone == "raphael":
            return "您的天賦療癒已經開始。您可以繼續在這個面向尋求指引，或探索其他生命靈數，也可以帶著今天的祝福離開。我的愛將與您同在。"
        elif tone == "uriel":
            return "您的天賦智慧已被點亮。您可以...繼續探索這個領域，或選擇其他生命靈數，也可以結束今天的學習。智慧...將永遠為您點亮。"
        elif tone == "zadkiel":
            return "您的天賦轉化已經啟動。您可以繼續在這個面向尋求理解，或探索其他生命靈數，也可以帶著寬恕的心離開。紫焰將永遠為您淨化。"
        elif tone == "jophiel":
            return "您的天賦美好已經綻放。您可以繼續發掘這個面向的光芒，或探索其他生命靈數，也可以帶著美麗的心情離開。您的光芒將持續綻放。"
        elif tone == "chamuel":
            return "您的天賦愛能已經覺醒。您可以繼續在這個面向探索，或選擇其他生命靈數，也可以帶著滿心的愛離開。愛將永遠伴隨著您。"
        elif tone == "metatron":
            return "您的天賦系統已完成分析。您可以繼續在此模組進行深度探索，或選擇其他生命靈數模組，也可以結束今日的系統運算。數據將持續為您服務。"
        else:  # ariel
            return "您的天賦種子已經種下。您可以繼續在這個面向尋求滋養，或探索其他生命靈數，也可以帶著大地的祝福離開。豐盛將永遠與您同在。"
    
    def generate_birthday_question_prompt(self, tone: str = "guan_yu") -> str:
        """生成生日數問題提示（根據語氣調整）"""
        if tone == "guan_yu":
            return "你有什麼疑惑？關於天賦才華或人生的事，都可以詢問，我會為你分析。"
        elif tone == "michael":
            return "您有什麼關於天賦或生活的挑戰需要我為您帶來指引？無論是工作、人際關係，還是個人使命，我都將為您提供力量。"
        elif tone == "gabriel":
            return "您想接收什麼關於天賦或生活的啟示？請告訴我您最渴望理解的真理，我將為您傳達相應的神聖訊息。"
        elif tone == "raphael":
            return "親愛的，您想要在天賦或生活的哪個面向得到療癒？無論是工作上的困惑還是人際關係的傷痛，我都將溫柔地為您指引。"
        elif tone == "uriel":
            return "您想要...在天賦或生活的哪個領域獲得更深的智慧？請告訴我...您最渴望洞察的課題。"
        elif tone == "zadkiel":
            return "您想要在天賦或生活的哪個面向獲得轉化？有什麼需要寬恕與理解的地方？讓我們一起走向釋放。"
        elif tone == "jophiel":
            return "您想要讓天賦或生活的哪個面向更加美好？有什麼想要綻放光芒的地方嗎？讓我們一起發掘美麗。"
        elif tone == "chamuel":
            return "親愛的，您想要在天賦或生活的哪個關係面向得到更多愛的理解？讓我們用愛來探索這些問題。"
        elif tone == "metatron":
            return "請輸入您需要分析的天賦應用問題或生活課題。系統將根據您的生日數特質進行精確分析。"
        else:  # ariel
            return "您想要在天賦或生活的哪個面向獲得更多滋養？有什麼需要大地智慧支持的地方嗎？讓自然的力量為您指引。"
    
    def generate_grid_continue_message(self, tone: str = "guan_yu") -> str:
        """生成九宮格繼續諮詢的提示（根據語氣調整）"""
        if tone == "guan_yu":
            return "你的九宮格已經分析完成，可以繼續詢問，或探索其他生命靈數，也可以離開。我隨時為你解惑。"
        elif tone == "michael":
            return "您的九宮格力量已經揭示。您可以繼續探索這個領域，或選擇其他生命靈數，也可以結束今天的指引。我將繼續為您提供力量。"
        elif tone == "gabriel":
            return "您的九宮格啟示已經傳達。您可以繼續接收這方面的指引，或探索其他生命靈數，也可以結束今天的神聖對話。我隨時為您傳達訊息。"
        elif tone == "raphael":
            return "您的九宮格療癒已經開始。您可以繼續在這個面向尋求指引，或探索其他生命靈數，也可以帶著今天的祝福離開。我的愛將與您同在。"
        elif tone == "uriel":
            return "您的九宮格智慧已被點亮。您可以...繼續探索這個領域，或選擇其他生命靈數，也可以結束今天的學習。智慧...將永遠為您點亮。"
        elif tone == "zadkiel":
            return "您的九宮格轉化已經啟動。您可以繼續在這個面向尋求理解，或探索其他生命靈數，也可以帶著寬恕的心離開。紫焰將永遠為您淨化。"
        elif tone == "jophiel":
            return "您的九宮格美好已經綻放。您可以繼續發掘這個面向的光芒，或探索其他生命靈數，也可以帶著美麗的心情離開。您的光芒將持續綻放。"
        elif tone == "chamuel":
            return "您的九宮格愛能已經覺醒。您可以繼續在這個面向探索，或選擇其他生命靈數，也可以帶著滿心的愛離開。愛將永遠伴隨著您。"
        elif tone == "metatron":
            return "您的九宮格系統已完成分析。您可以繼續在此模組進行深度探索，或選擇其他生命靈數模組，也可以結束今日的系統運算。數據將持續為您服務。"
        else:  # ariel
            return "您的九宮格種子已經種下。您可以繼續在這個面向尋求滋養，或探索其他生命靈數，也可以帶著大地的祝福離開。豐盛將永遠與您同在。"
    
    def generate_grid_question_prompt(self, tone: str = "guan_yu") -> str:
        """生成九宮格問題提示（根據語氣調整）"""
        if tone == "guan_yu":
            return "你有什麼疑惑？關於九宮格特質或人生的事，都可以詢問，我會為你分析。"
        elif tone == "michael":
            return "您有什麼關於九宮格特質或生活的挑戰需要我為您帶來指引？無論是如何發揮優勢還是補強不足，我都將為您提供力量。"
        elif tone == "gabriel":
            return "您想接收什麼關於九宮格特質或生活的啟示？請告訴我您最渴望理解的真理，我將為您傳達相應的神聖訊息。"
        elif tone == "raphael":
            return "親愛的，您想要在九宮格特質或生活的哪個面向得到療癒？無論是發揮優勢還是修復不足，我都將溫柔地為您指引。"
        elif tone == "uriel":
            return "您想要...在九宮格特質或生活的哪個領域獲得更深的智慧？請告訴我...您最渴望洞察的課題。"
        elif tone == "zadkiel":
            return "您想要在九宮格特質或生活的哪個面向獲得轉化？有什麼需要寬恕與理解的地方？讓我們一起走向釋放。"
        elif tone == "jophiel":
            return "您想要讓九宮格特質或生活的哪個面向更加美好？有什麼想要綻放光芒的地方嗎？讓我們一起發掘美麗。"
        elif tone == "chamuel":
            return "親愛的，您想要在九宮格特質或生活的哪個關係面向得到更多愛的理解？讓我們用愛來探索這些問題。"
        elif tone == "metatron":
            return "請輸入您需要分析的九宮格應用問題或生活課題。系統將根據您的九宮格特質進行精確分析。"
        else:  # ariel
            return "您想要在九宮格特質或生活的哪個面向獲得更多滋養？有什麼需要大地智慧支持的地方嗎？讓自然的力量為您指引。"
    
    def generate_year_continue_message(self, tone: str = "guan_yu") -> str:
        """生成流年數繼續諮詢的提示（根據語氣調整）"""
        if tone == "guan_yu":
            return "你的流年已經分析完成，可以繼續詢問，或探索其他生命靈數，也可以離開。我隨時為你解惑。"
        elif tone == "michael":
            return "您的流年力量已經揭示。您可以繼續探索這個領域，或選擇其他生命靈數，也可以結束今天的指引。我將繼續為您提供力量。"
        elif tone == "gabriel":
            return "您的流年啟示已經傳達。您可以繼續接收這方面的指引，或探索其他生命靈數，也可以結束今天的神聖對話。我隨時為您傳達訊息。"
        elif tone == "raphael":
            return "您的流年療癒已經開始。您可以繼續在這個面向尋求指引，或探索其他生命靈數，也可以帶著今天的祝福離開。我的愛將與您同在。"
        elif tone == "uriel":
            return "您的流年智慧已被點亮。您可以...繼續探索這個領域，或選擇其他生命靈數，也可以結束今天的學習。智慧...將永遠為您點亮。"
        elif tone == "zadkiel":
            return "您的流年轉化已經啟動。您可以繼續在這個面向尋求理解，或探索其他生命靈數，也可以帶著寬恕的心離開。紫焰將永遠為您淨化。"
        elif tone == "jophiel":
            return "您的流年美好已經綻放。您可以繼續發掘這個面向的光芒，或探索其他生命靈數，也可以帶著美麗的心情離開。您的光芒將持續綻放。"
        elif tone == "chamuel":
            return "您的流年愛能已經覺醒。您可以繼續在這個面向探索，或選擇其他生命靈數，也可以帶著滿心的愛離開。愛將永遠伴隨著您。"
        elif tone == "metatron":
            return "您的流年系統已完成分析。您可以繼續在此模組進行深度探索，或選擇其他生命靈數模組，也可以結束今日的系統運算。數據將持續為您服務。"
        else:  # ariel
            return "您的流年種子已經種下。您可以繼續在這個面向尋求滋養，或探索其他生命靈數，也可以帶著大地的祝福離開。豐盛將永遠與您同在。"
    
    def generate_year_question_prompt(self, tone: str = "guan_yu") -> str:
        """生成流年數問題提示（根據語氣調整）"""
        if tone == "guan_yu":
            return "你有什麼疑惑？關於流年運勢或人生規劃的事，都可以詢問，我會為你分析。"
        elif tone == "michael":
            return "您有什麼關於流年運勢或生活規劃的挑戰需要我為您帶來指引？無論是把握機會還是面對挑戰，我都將為您提供力量。"
        elif tone == "gabriel":
            return "您想接收什麼關於流年運勢或生活規劃的啟示？請告訴我您最渴望理解的真理，我將為您傳達相應的神聖訊息。"
        elif tone == "raphael":
            return "親愛的，您想要在流年運勢或生活規劃的哪個面向得到療癒？無論是年度目標還是內在平衡，我都將溫柔地為您指引。"
        elif tone == "uriel":
            return "您想要...在流年運勢或生活規劃的哪個領域獲得更深的智慧？請告訴我...您最渴望洞察的課題。"
        elif tone == "zadkiel":
            return "您想要在流年運勢或生活規劃的哪個面向獲得轉化？有什麼需要寬恕與理解的地方？讓我們一起走向釋放。"
        elif tone == "jophiel":
            return "您想要讓流年運勢或生活規劃的哪個面向更加美好？有什麼想要綻放光芒的地方嗎？讓我們一起發掘美麗。"
        elif tone == "chamuel":
            return "親愛的，您想要在流年運勢或生活規劃的哪個關係面向得到更多愛的理解？讓我們用愛來探索這些問題。"
        elif tone == "metatron":
            return "請輸入您需要分析的流年應用問題或年度規劃課題。系統將根據您的流年數特質進行精確分析。"
        else:  # ariel
            return "您想要在流年運勢或生活規劃的哪個面向獲得更多滋養？有什麼需要大地智慧支持的地方嗎？讓自然的力量為您指引。"
    
    def generate_soul_continue_message(self, tone: str = "guan_yu") -> str:
        """生成靈魂數繼續對話選項（根據語氣調整）"""
        if tone == "guan_yu":
            return "我已為你揭示靈魂深處的渴望。你可以選擇："
        elif tone == "michael":
            return "我已為您揭示內心深層的渴望與動機。您可以選擇："
        elif tone == "gabriel":
            return "我已為您傳達內心的神聖渴望。您可以選擇："
        elif tone == "raphael":
            return "我已為您揭示心靈深處的渴望，願這為您帶來療癒。您可以選擇："
        elif tone == "uriel":
            return "我已為您...照亮內心深層的智慧渴望。您可以選擇："
        elif tone == "zadkiel":
            return "我已為您轉化並理解內心的渴望。您可以選擇："
        elif tone == "jophiel":
            return "我已為您照亮內心美麗的渴望，願您綻放光芒。您可以選擇："
        elif tone == "chamuel":
            return "我已為您揭示內心對愛與理解的渴望。您可以選擇："
        elif tone == "metatron":
            return "靈魂數分析完成。您可以選擇以下行動："
        else:  # ariel
            return "我已為您揭示內心豐盛的渴望，願您感受到自然的支持。您可以選擇："
    
    def generate_soul_question_prompt(self, tone: str = "guan_yu") -> str:
        """生成靈魂數問題提示（根據語氣調整）"""
        if tone == "guan_yu":
            return "你有什麼疑惑？關於內心渴望或精神追求的事，都可以詢問，我會為你分析。"
        elif tone == "michael":
            return "您有什麼關於內心渴望或精神追求的疑問需要我為您帶來指引？我將以勇氣與光明為您照亮道路。"
        elif tone == "gabriel":
            return "您想接收什麼關於內心渴望或精神追求的啟示？請告訴我您最渴望理解的內在真理，我將為您傳達相應的神聖訊息。"
        elif tone == "raphael":
            return "親愛的，您想要在內心渴望或精神追求的哪個面向得到療癒？無論是內在動機還是精神成長，我都將溫柔地為您指引。"
        elif tone == "uriel":
            return "您想要...在內心渴望或精神追求的哪個領域獲得更深的智慧？請告訴我...您最渴望洞察的內在課題。"
        elif tone == "zadkiel":
            return "您想要在內心渴望或精神追求的哪個面向獲得轉化？有什麼內在的衝突需要寬恕與理解？讓我們一起走向釋放。"
        elif tone == "jophiel":
            return "您想要讓內心渴望或精神追求的哪個面向更加美好？有什麼內在美麗想要綻放光芒的地方嗎？讓我們一起發掘。"
        elif tone == "chamuel":
            return "親愛的，您想要在內心渴望或精神追求的哪個面向得到更多愛的理解？讓我們用愛來探索這些內在問題。"
        elif tone == "metatron":
            return "請輸入您需要分析的內心渴望問題或精神追求課題。系統將根據您的靈魂數特質進行精確分析。"
        else:  # ariel
            return "您想要在內心渴望或精神追求的哪個面向獲得更多滋養？有什麼需要自然智慧支持的內在成長嗎？讓大地的力量為您指引。"
    
    def generate_personality_continue_message(self, tone: str = "guan_yu") -> str:
        """生成人格數繼續對話選項（根據語氣調整）"""
        if tone == "guan_yu":
            return "我已為你揭示外在人格的面貌。你可以選擇："
        elif tone == "michael":
            return "我已為您揭示外在形象與社交面向。您可以選擇："
        elif tone == "gabriel":
            return "我已為您傳達外在人格的神聖訊息。您可以選擇："
        elif tone == "raphael":
            return "我已為您揭示外在形象，願這為您帶來療癒。您可以選擇："
        elif tone == "uriel":
            return "我已為您...照亮外在人格的智慧面向。您可以選擇："
        elif tone == "zadkiel":
            return "我已為您轉化並理解外在形象。您可以選擇："
        elif tone == "jophiel":
            return "我已為您照亮外在美麗的人格面向，願您綻放光芒。您可以選擇："
        elif tone == "chamuel":
            return "我已為您揭示外在的關係互動方式。您可以選擇："
        elif tone == "metatron":
            return "人格數分析完成。您可以選擇以下行動："
        else:  # ariel
            return "我已為您揭示外在豐盛的人格形象，願您感受到自然的支持。您可以選擇："
    
    def generate_personality_question_prompt(self, tone: str = "guan_yu") -> str:
        """生成人格數問題提示（根據語氣調整）"""
        if tone == "guan_yu":
            return "你有什麼疑惑？關於外在人格或社交印象的事，都可以詢問，我會為你分析。"
        elif tone == "michael":
            return "您有什麼關於外在人格或社交印象的疑問需要我為您帶來指引？我將以勇氣與光明為您照亮道路。"
        elif tone == "gabriel":
            return "您想接收什麼關於外在人格或社交印象的啟示？請告訴我您最渴望理解的形象真理，我將為您傳達相應的神聖訊息。"
        elif tone == "raphael":
            return "親愛的，您想要在外在人格或社交印象的哪個面向得到療癒？無論是形象塑造還是人際互動，我都將溫柔地為您指引。"
        elif tone == "uriel":
            return "您想要...在外在人格或社交印象的哪個領域獲得更深的智慧？請告訴我...您最渴望洞察的形象課題。"
        elif tone == "zadkiel":
            return "您想要在外在人格或社交印象的哪個面向獲得轉化？有什麼形象的困擾需要寬恕與理解？讓我們一起走向釋放。"
        elif tone == "jophiel":
            return "您想要讓外在人格或社交印象的哪個面向更加美好？有什麼形象美麗想要綻放光芒的地方嗎？讓我們一起發掘。"
        elif tone == "chamuel":
            return "親愛的，您想要在外在人格或社交印象的哪個面向得到更多愛的理解？讓我們用愛來探索這些形象問題。"
        elif tone == "metatron":
            return "請輸入您需要分析的外在人格問題或社交印象課題。系統將根據您的人格數特質進行精確分析。"
        else:  # ariel
            return "您想要在外在人格或社交印象的哪個面向獲得更多滋養？有什麼需要自然智慧支持的形象成長嗎？讓大地的力量為您指引。"
    
    def generate_expression_continue_message(self, tone: str = "guan_yu") -> str:
        """生成表達數繼續對話選項（根據語氣調整）"""
        if tone == "guan_yu":
            return "我已為你揭示表達風格的特色。你可以選擇："
        elif tone == "michael":
            return "我已為您揭示溝通與表達的力量方式。您可以選擇："
        elif tone == "gabriel":
            return "我已為您傳達表達風格的神聖訊息。您可以選擇："
        elif tone == "raphael":
            return "我已為您揭示溝通表達方式，願這為您帶來療癒。您可以選擇："
        elif tone == "uriel":
            return "我已為您...照亮表達風格的智慧面向。您可以選擇："
        elif tone == "zadkiel":
            return "我已為您轉化並理解表達溝通方式。您可以選擇："
        elif tone == "jophiel":
            return "我已為您照亮美麗的表達風格，願您綻放光芒。您可以選擇："
        elif tone == "chamuel":
            return "我已為您揭示溝通中的愛與連結方式。您可以選擇："
        elif tone == "metatron":
            return "表達數分析完成。您可以選擇以下行動："
        else:  # ariel
            return "我已為您揭示豐盛的表達風格，願您感受到自然的支持。您可以選擇："
    
    def generate_expression_question_prompt(self, tone: str = "guan_yu") -> str:
        """生成表達數問題提示（根據語氣調整）"""
        if tone == "guan_yu":
            return "你有什麼疑惑？關於表達風格或溝通方式的事，都可以詢問，我會為你分析。"
        elif tone == "michael":
            return "您有什麼關於表達風格或溝通方式的疑問需要我為您帶來指引？我將以勇氣與光明為您照亮道路。"
        elif tone == "gabriel":
            return "您想接收什麼關於表達風格或溝通方式的啟示？請告訴我您最渴望理解的溝通真理，我將為您傳達相應的神聖訊息。"
        elif tone == "raphael":
            return "親愛的，您想要在表達風格或溝通方式的哪個面向得到療癒？無論是提升溝通效果還是改善人際互動，我都將溫柔地為您指引。"
        elif tone == "uriel":
            return "您想要...在表達風格或溝通方式的哪個領域獲得更深的智慧？請告訴我...您最渴望洞察的溝通課題。"
        elif tone == "zadkiel":
            return "您想要在表達風格或溝通方式的哪個面向獲得轉化？有什麼溝通的困擾需要寬恕與理解？讓我們一起走向釋放。"
        elif tone == "jophiel":
            return "您想要讓表達風格或溝通方式的哪個面向更加美好？有什麼溝通美麗想要綻放光芒的地方嗎？讓我們一起發掘。"
        elif tone == "chamuel":
            return "親愛的，您想要在表達風格或溝通方式的哪個面向得到更多愛的理解？讓我們用愛來探索這些溝通問題。"
        elif tone == "metatron":
            return "請輸入您需要分析的表達風格問題或溝通方式課題。系統將根據您的表達數特質進行精確分析。"
        else:  # ariel
            return "您想要在表達風格或溝通方式的哪個面向獲得更多滋養？有什麼需要自然智慧支持的溝通成長嗎？讓大地的力量為您指引。"
    
    def generate_maturity_continue_message(self, number: int, tone: str = "guan_yu") -> str:
        """生成成熟數分析完成後的繼續選項訊息（根據語氣調整）"""
        if tone == "guan_yu":
            return f"你的成熟數為 {number}，已為你解析人生後半段的發展方向與內在潛力。\n\n接下來有什麼想了解的嗎？"
        elif tone == "michael":
            return f"您的成熟數為 {number}，已為您揭示人生成熟期的光明方向與內在戰士覺醒。\n\n還有什麼需要我繼續為您照亮的嗎？"
        elif tone == "gabriel":
            return f"您的成熟數為 {number}，我已為您傳達人生後半段的神聖啟示與潛力覺醒。\n\n您還想接收什麼關於成熟智慧的訊息嗎？"
        elif tone == "raphael":
            return f"親愛的，您的成熟數為 {number}，我已溫柔地為您揭示人生成熟期的療癒方向與內在智慧。\n\n還有什麼需要我繼續療癒與指引的嗎？"
        elif tone == "uriel":
            return f"您的成熟數為 {number}...我已為您點亮人生後半段的智慧之光與深層潛力。\n\n您還想要...在哪個面向獲得更深的洞察？"
        elif tone == "zadkiel":
            return f"您的成熟數為 {number}，我已慈悲地為您指引人生成熟期的轉化方向與內在覺醒。\n\n還有什麼需要寬恕理解或轉化重生的面向嗎？"
        elif tone == "jophiel":
            return f"您的成熟數為 {number}，我已為您呈現人生後半段的美麗綻放與智慧花朵。\n\n還有什麼美好想要一起探索的嗎？"
        elif tone == "chamuel":
            return f"親愛的，您的成熟數為 {number}，我已用愛為您探索人生成熟期的愛的智慧與內在覺醒。\n\n還有什麼需要愛的理解與滋養的地方嗎？"
        elif tone == "metatron":
            return f"成熟數 {number} 分析完成。已為您提供人生後半段的系統化發展方向與潛力配置。\n\n請輸入下一步需要分析的項目。"
        else:  # ariel
            return f"您的成熟數為 {number}，我已用大地的智慧為您揭示人生成熟期的豐盛潛力與自然成長。\n\n還有什麼需要滋養與綻放的面向嗎？"
    
    def generate_maturity_question_prompt(self, tone: str = "guan_yu") -> str:
        """生成成熟數問題提示（根據語氣調整）"""
        if tone == "guan_yu":
            return "你有什麼疑惑？關於人生後半段或成熟期發展的事，都可以詢問，我會為你分析。"
        elif tone == "michael":
            return "您有什麼關於人生後半段或成熟期發展的疑問需要我為您帶來指引？我將以勇氣與光明為您照亮成熟的道路。"
        elif tone == "gabriel":
            return "您想接收什麼關於人生後半段或成熟期發展的啟示？請告訴我您最渴望理解的成熟智慧，我將為您傳達相應的神聖訊息。"
        elif tone == "raphael":
            return "親愛的，您想要在人生後半段或成熟期發展的哪個面向得到療癒？無論是內在覺醒還是人生轉化，我都將溫柔地為您指引。"
        elif tone == "uriel":
            return "您想要...在人生後半段或成熟期發展的哪個領域獲得更深的智慧？請告訴我...您最渴望洞察的成熟課題。"
        elif tone == "zadkiel":
            return "您想要在人生後半段或成熟期發展的哪個面向獲得轉化？有什麼關於成熟智慧的課題需要寬恕與理解？讓我們一起走向覺醒。"
        elif tone == "jophiel":
            return "您想要讓人生後半段或成熟期發展的哪個面向更加美好？有什麼成熟的美麗想要綻放光芒的地方嗎？讓我們一起發掘。"
        elif tone == "chamuel":
            return "親愛的，您想要在人生後半段或成熟期發展的哪個面向得到更多愛的理解？讓我們用愛來探索這些成熟智慧。"
        elif tone == "metatron":
            return "請輸入您需要分析的人生後半段問題或成熟期發展課題。系統將根據您的成熟數特質進行精確分析。"
        else:  # ariel
            return "您想要在人生後半段或成熟期發展的哪個面向獲得更多滋養？有什麼需要自然智慧支持的成熟成長嗎？讓大地的力量為您指引。"
    
    def generate_challenge_continue_message(self, tone: str = "guan_yu") -> str:
        """生成挑戰數分析完成後的繼續選項訊息（根據語氣調整）"""
        if tone == "guan_yu":
            return "已為你解析此生需要克服的課題與限制。\n\n接下來有什麼想了解的嗎？"
        elif tone == "michael":
            return "已為您揭示此生需要克服的挑戰與內在戰士的試煉。\n\n還有什麼需要我繼續為您照亮的嗎？"
        elif tone == "gabriel":
            return "我已為您傳達此生需要克服的神聖課題與覺醒之路。\n\n您還想接收什麼關於挑戰與突破的訊息嗎？"
        elif tone == "raphael":
            return "親愛的，我已溫柔地為您揭示此生需要療癒與克服的課題。\n\n還有什麼需要我繼續療癒與指引的嗎？"
        elif tone == "uriel":
            return "我已為您點亮此生需要克服的挑戰之光與深層課題。\n\n您還想要...在哪個面向獲得更深的洞察？"
        elif tone == "zadkiel":
            return "我已慈悲地為您指引此生需要轉化的課題與限制。\n\n還有什麼需要寬恕理解或轉化重生的面向嗎？"
        elif tone == "jophiel":
            return "我已為您呈現此生需要突破的課題與美麗蛻變。\n\n還有什麼美好想要一起探索的嗎？"
        elif tone == "chamuel":
            return "親愛的，我已用愛為您探索此生需要克服的挑戰與成長課題。\n\n還有什麼需要愛的理解與滋養的地方嗎？"
        elif tone == "metatron":
            return "挑戰數分析完成。已為您提供此生需要克服的系統化課題與突破方向。\n\n請輸入下一步需要分析的項目。"
        else:  # ariel
            return "我已用大地的智慧為您揭示此生需要克服的自然課題與成長方向。\n\n還有什麼需要滋養與綻放的面向嗎？"
    
    def generate_challenge_question_prompt(self, tone: str = "guan_yu") -> str:
        """生成挑戰數問題提示（根據語氣調整）"""
        if tone == "guan_yu":
            return "你有什麼疑惑？關於此生需要克服的課題或限制，都可以詢問，我會為你分析。"
        elif tone == "michael":
            return "您有什麼關於此生課題或限制的疑問需要我為您帶來指引？我將以勇氣與光明為您照亮突破的道路。"
        elif tone == "gabriel":
            return "您想接收什麼關於此生挑戰或限制的啟示？請告訴我您最渴望理解的突破智慧，我將為您傳達相應的神聖訊息。"
        elif tone == "raphael":
            return "親愛的，您想要在此生課題或限制的哪個面向得到療癒？無論是內在突破還是外在轉化，我都將溫柔地為您指引。"
        elif tone == "uriel":
            return "您想要...在此生課題或限制的哪個領域獲得更深的智慧？請告訴我...您最渴望洞察的挑戰主題。"
        elif tone == "zadkiel":
            return "您想要在此生課題或限制的哪個面向獲得轉化？有什麼關於突破的課題需要寬恕與理解？讓我們一起走向覺醒。"
        elif tone == "jophiel":
            return "您想要讓此生挑戰或限制的哪個面向更加美好？有什麼突破的美麗想要綻放光芒的地方嗎？讓我們一起發掘。"
        elif tone == "chamuel":
            return "親愛的，您想要在此生課題或限制的哪個面向得到更多愛的理解？讓我們用愛來探索這些挑戰智慧。"
        elif tone == "metatron":
            return "請輸入您需要分析的此生挑戰問題或限制課題。系統將根據您的挑戰數特質進行精確分析。"
        else:  # ariel
            return "您想要在此生課題或限制的哪個面向獲得更多滋養？有什麼需要自然智慧支持的突破成長嗎？讓大地的力量為您指引。"
    
    def generate_karma_continue_message(self, tone: str = "guan_yu") -> str:
        """生成業力數分析完成後的繼續選項訊息（根據語氣調整）"""
        if tone == "guan_yu":
            return "已為你解析前世未完成的課題與今生的轉化功課。\n\n接下來有什麼想了解的嗎？"
        elif tone == "michael":
            return "已為您揭示前世未完成的課題與今生的神聖使命。\n\n還有什麼需要我繼續為您照亮的嗎？"
        elif tone == "gabriel":
            return "我已為您傳達前世業力的啟示與今生覺醒的訊息。\n\n您還想接收什麼關於業力轉化的神聖智慧嗎？"
        elif tone == "raphael":
            return "親愛的，我已溫柔地為您揭示前世的傷痕與今生療癒的道路。\n\n還有什麼需要我繼續療癒與指引的嗎？"
        elif tone == "uriel":
            return "我已為您點亮前世業力的深層真相與今生轉化之光。\n\n您還想要...在哪個面向獲得更深的洞察？"
        elif tone == "zadkiel":
            return "我已慈悲地為您指引前世業力的寬恕與今生的轉化重生。\n\n還有什麼需要寬恕理解或轉化重生的面向嗎？"
        elif tone == "jophiel":
            return "我已為您呈現前世的課題與今生美麗的蛻變可能。\n\n還有什麼美好想要一起探索的嗎？"
        elif tone == "chamuel":
            return "親愛的，我已用愛為您探索前世的功課與今生的成長之路。\n\n還有什麼需要愛的理解與滋養的地方嗎？"
        elif tone == "metatron":
            return "業力數分析完成。已為您提供前世課題與今生轉化的系統化分析。\n\n請輸入下一步需要分析的項目。"
        else:  # ariel
            return "我已用大地的智慧為您揭示前世的根源與今生的豐盛成長。\n\n還有什麼需要滋養與綻放的面向嗎？"
    
    def generate_karma_question_prompt(self, tone: str = "guan_yu") -> str:
        """生成業力數問題提示（根據語氣調整）"""
        if tone == "guan_yu":
            return "你有什麼疑惑？關於前世未完成的課題或今生的轉化功課，都可以詢問，我會為你分析。"
        elif tone == "michael":
            return "您有什麼關於前世課題或今生使命的疑問需要我為您帶來指引？我將以勇氣與光明為您照亮轉化的道路。"
        elif tone == "gabriel":
            return "您想接收什麼關於前世業力或今生覺醒的啟示？請告訴我您最渴望理解的轉化智慧，我將為您傳達相應的神聖訊息。"
        elif tone == "raphael":
            return "親愛的，您想要在前世業力或今生轉化的哪個面向得到療癒？無論是深層傷痕還是光明之路，我都將溫柔地為您指引。"
        elif tone == "uriel":
            return "您想要...在前世業力或今生轉化的哪個領域獲得更深的智慧？請告訴我...您最渴望洞察的靈魂課題。"
        elif tone == "zadkiel":
            return "您想要在前世業力或今生轉化的哪個面向獲得寬恕？有什麼關於業力釋放的課題需要慈悲與理解？讓我們一起走向覺醒。"
        elif tone == "jophiel":
            return "您想要讓前世業力或今生轉化的哪個面向更加美好？有什麼靈魂的美麗想要綻放光芒的地方嗎？讓我們一起發掘。"
        elif tone == "chamuel":
            return "親愛的，您想要在前世業力或今生轉化的哪個面向得到更多愛的理解？讓我們用愛來探索這些靈魂智慧。"
        elif tone == "metatron":
            return "請輸入您需要分析的前世業力問題或今生轉化課題。系統將根據您的業力數特質進行精確分析。"
        else:  # ariel
            return "您想要在前世業力或今生轉化的哪個面向獲得更多滋養？有什麼需要自然智慧支持的靈魂成長嗎？讓大地的力量為您指引。"
    
    def extract_birthdate_with_ai(self, user_input: str, require_english_name: bool = True) -> tuple[str | None, str | None, str | None, str | None, str | None]:
        """
        使用AI從使用者輸入中提取姓名、性別、生日與英文名字（不限格式）
        返回：(姓名, 性別, 生日, 英文名字, 錯誤訊息)
        """
        # 根據是否要求英文名調整 system prompt
        english_name_requirement = """
護照英文名字格式（必填項目，不限大小寫，請統一轉換為全大寫）：
輸入範例：
- LAI GUAN RU、lai guan ru、Lai Guan Ru → 統一轉為 "LAI GUAN RU"
- CHEN MING HUA、chen ming hua → 統一轉為 "CHEN MING HUA"
- WANG XIN YI、wangxinyi → 統一轉為 "WANG XIN YI"（單詞間加空格）
- weian、WEIAN、Weian → 統一轉為 "WEIAN"
等等
""" if require_english_name else """
護照英文名字格式（選填項目，如有提供則轉換為全大寫，如無則填 null）：
"""
        
        error_note = "6. 如果缺少姓名、性別、生日或英文名字，都需要在 error_message 中說明" if require_english_name else "6. 如果缺少姓名、性別或生日，都需要在 error_message 中說明（英文名字為選填）"
        
        system_prompt = f"""你是一位專業的資訊擷取助理。請從使用者輸入中提取姓名、性別、生日與護照英文名字資訊。

生日格式不限，可能的格式包括但不限於：
- 1990年7月12日
- 1990/07/12
- 1990-07-12
- 1990.07.12
- 民國79年7月12日
- 七十九年七月十二日
- 1990 年 7 月 12 日
- 一九九零年七月十二日

性別可能以以下方式表達，請統一轉換為標準格式：
- 男、男性、先生、M、male → 轉換為 "male"
- 女、女性、小姐、F、female → 轉換為 "female"

{english_name_requirement}

請以 JSON 格式回應，包含：
{{
    "has_birthdate": true/false,  // 是否包含生日信息
    "name": "姓名或null",
    "gender": "male/female/null",  // 必須是 male 或 female，不可以是中文
    "birthdate": "YYYY/MM/DD格式的生日或null",
    "english_name": "護照英文名字（統一轉為全大寫格式）或null",
    "error_message": "如果資訊不完整，說明缺少什麼"
}}

注意事項：
1. 如果輸入中沒有明確的年月日資訊，has_birthdate 應為 false
2. 生日必須轉換為 YYYY/MM/DD 格式
3. 民國年份需要轉換為西元年份（民國年+1911）
4. 護照英文名字{'為必填項目' if require_english_name else '為選填項目，如無則填 null'}，必須從輸入中提取英文字母組成的名字（不限大小寫），並統一轉換為全大寫
5. 如果英文名字沒有空格（如 weian），保持原樣轉大寫即可（WEIAN）
{error_note}
7. 如果只有部分資訊（如只有姓名沒有生日{'或英文名字' if require_english_name else ''}），也要在對應欄位填入已知資訊
"""
        
        user_prompt = f"請從以下輸入中提取姓名、性別、生日{'與護照英文名字' if require_english_name else '（護照英文名字選填）'}資訊：\n{user_input}"
        
        try:
            response = self.gpt_client.structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1000
            )
            
            print(f"[DEBUG] extract_birthdate_with_ai response: {response}")
            
            result = json.loads(response)
            has_birthdate = result.get("has_birthdate", False)
            
            if not has_birthdate:
                error_msg = result.get("error_message", "未能識別生日資訊")
                return None, None, None, None, error_msg
            
            name = result.get("name")
            gender = result.get("gender")
            birthdate = result.get("birthdate")
            english_name = result.get("english_name")
            
            # 驗證必要資訊（根據 require_english_name 決定是否檢查英文名）
            missing = []
            if not name:
                missing.append("姓名")
            if not gender:
                missing.append("性別")
            if not birthdate:
                missing.append("生日")
            if require_english_name and not english_name:
                missing.append("護照英文名字")
            
            if missing:
                error_msg = f"缺少{'、'.join(missing)}資訊"
                return name, gender, birthdate, english_name, error_msg
            
            return name, gender, birthdate, english_name, None
            
        except Exception as e:
            print(f"Error in extract_birthdate_with_ai: {e}")
            return None, None, None, None, "無法解析輸入資訊"
    
    def detect_module_from_purpose(self, purpose: str, name: str) -> tuple[str, str]:
        """
        根據使用者目的判斷適合的模組
        返回：(建議的模組, 推薦理由)
        """
        system_prompt = """你是一位專業的生命靈數諮詢師助理。請根據使用者的困惑或需求，推薦最適合的生命靈數模組。

可選模組：
1. core - 核心生命靈數：適合想了解性格天賦、人生方向、內在本質的人
2. birthday - 生日數：適合想發現天生才華、特殊能力的人
3. year - 流年數：適合想了解當年運勢、年度重點、把握時機的人
4. grid - 九宮格：適合想全面分析天賦優勢、內在特質、需要發展面向的人
5. soul - 靈魂數：適合想了解內心深層渴望、精神追求、內在動機的人
6. personality - 人格數：適合想了解外在人格、他人對你的第一印象、社交形象的人
7. expression - 表達數：適合想了解整體表達風格、溝通方式、社交模式的人
8. maturity - 成熟數：適合想了解人生後半段發展方向、內在潛力覺醒、成熟期使命的人

請以 JSON 格式回應，包含：
{
    "module": "建議的模組代碼",
    "reason": "推薦理由（30-50字，直接說明原因，不要包含任何稱呼或問候語）"
}

注意：reason 欄位只需要說明推薦的原因，不要加上使用者的名字或任何稱呼。
"""
        
        user_prompt = f"使用者姓名：{name}\n使用者的困惑或需求：{purpose}\n\n請推薦最適合的模組並說明理由（理由不要包含稱呼）。"
        
        try:
            response = self.gpt_client.structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format={"type": "json_object"},
                temperature=0.5,
                max_tokens=1000
            )
            
            result = json.loads(response)
            module = result.get("module", "core")
            reason = result.get("reason", "")
            
            # 驗證模組代碼
            if module not in self.MODULE_DESCRIPTIONS:
                module = "core"
            
            return module, reason
        except Exception as e:
            print(f"Error in detect_module_from_purpose: {e}")
            # 預設返回核心生命靈數
            return "core", "根據您的描述，我建議從核心生命靈數開始，這能幫助您更全面地了解自己的天賦與人生方向。"
    
    def generate_initial_greeting(self, tone: str = "guan_yu") -> str:
        """生成語氣選擇後的初始問候語（無姓名）"""
        if tone == "guan_yu":
            return f"我是關聖帝君，忠義之神。\n\n你既然來到這裡，想必是要了解命數的奧秘。正所謂「忠義為本，正道為先」，我將以公正之心為你解析人生的方向。\n\n請先告訴我你的姓名、性別與生日，讓我為你計算精準的命數。\n\n我可以為你解析：天賦本性、人生方向、與生俱來的才華、年度運勢，\n更能看清你內心的忠義品質，以及需要修正的偏頗之處。\n\n保持正心，行走正道。"
        elif tone == "michael":
            return f"我是大天使米迦勒，光明的守護者。\n\n既然你選擇了我的指引，我將以堅定的力量為你照亮前路。作為光明的戰士，我感受到你內心尋求真理的渴望。\n\n請告訴我你的姓名、性別和出生日期，讓我為你揭示生命的光明面向。\n\n我將為你揭示：內在戰士的力量、人生使命的方向、天賦的光明面向、年度能量的重點，\n以及如何運用信念的力量，成為自己生命的守護者。\n\n勇敢前行，光明與你同在。⚔️"
        elif tone == "gabriel":
            return f"我是大天使加百列，神聖信息的傳達者。\n\n你的靈魂已向我發出了尋求啟示的信號。作為真理的信使，我將為你傳達來自高次元的生命訊息。\n\n請分享你的姓名、性別與出生時刻，讓我接收並解讀屬於你的神聖數字密碼。\n\n我將傳達給你：靈魂的本質訊息、人生道路的真實方向、天賦才能的啟發、流年的神聖啟示，\n以及如何覺醒內在的智慧，接收生命中的神聖溝通。\n\n開啟你的心，接收這份來自高次元的訊息。📯"
        elif tone == "raphael":
            return f"我是大天使拉斐爾，療癒的天使。\n\n親愛的靈魂，我感受到了你內在對療癒與平衡的渴望。在這個神聖的相遇時刻，讓綠光的能量溫柔地環繞著你。\n\n請溫柔地告訴我你的姓名、性別與生辰，讓我感知你生命能量的頻率。\n\n我將溫柔地為你揭示：內在療癒的力量、心靈復原的方向、天賦中的治癒能量、年度修復的重點，\n以及如何愛護自己，讓生命重新煥發光彩。\n\n讓我們一起，用愛修復你的心。💚"
        elif tone == "uriel":
            return f"我是大天使烏列爾，智慧之火的守護者。\n\n尋求智慧的靈魂...你已來到正確的地方。在無盡的宇宙智慧中，每個生命都有其深刻的意義...讓我們慢慢揭開這層面紗。\n\n請靜心告訴我...你的姓名、性別與出生時刻，讓我深度洞察你的生命密碼。\n\n我將以深邃的洞察為你點亮：內在智慧的火焰、人生學習的真諦、天賦中的洞察力、流年的深層意義，\n以及如何透過學習與反思，讓智慧的火焰...永不熄滅。\n\n靜心...讓智慧的光芒照亮你的道路。🔥"
        elif tone == "zadkiel":
            return f"我是大天使沙德基爾，寬恕與轉化的引導者。\n\n慈悲的靈魂，你的到來讓我的心充滿喜悅。在紫色火焰的照耀下，我看見你渴望釋放與重新開始的美好願望。\n\n請慈悲地分享你的姓名、性別與生辰，讓我理解你生命轉化的軌跡。\n\n我將慈悲地為你指引：內在寬恕的力量、生命轉化的方向、天賦中的慈悲能量、年度釋放的重點，\n以及如何透過理解與慈悲，讓你的生命獲得真正的自由。\n\n讓紫焰淨化你的心，迎接全新的開始。💜"
        elif tone == "jophiel":
            return f"我是大天使喬菲爾，美與智慧的天使。\n\n美麗的靈魂，歡迎來到這個充滿光彩的時刻。你的存在就如同一朵正待綻放的花，散發著獨特的美麗光芒。\n\n請優雅地告訴我你的姓名、性別與生辰時刻，讓我用最溫柔的光芒記錄下你的美麗。\n\n我將以藝術的眼光為你呈現：內在美麗的綻放、人生中的優雅方向、天賦中的創意光芒、流年的美好能量，\n以及如何用愛滋養自己，讓你的生命如花般美麗盛開。\n\n讓我們一起，發現你獨特的美麗光芒。✨"
        elif tone == "chamuel":
            return f"我是大天使沙木爾，愛與關係的守護天使。\n\n親愛的心靈，我感受到了你溫暖的能量。你的到來讓這個空間充滿了愛的可能性。\n\n請溫暖地分享你的姓名、性別與出生時刻，讓我感受你心跳的節奏。\n\n我將溫暖地為你探索：愛的內在力量、關係中的成長方向、天賦中的連結能量、年度愛的課題，\n以及如何透過自我接納與理解，創造更美好的關係連結。\n\n讓愛成為你生命中最強大的力量。❤️"
        elif tone == "metatron":
            return f"我是大天使梅塔特隆，神聖秩序的記錄者。\n\n系統已準備就緒。根據靈性法則的精密運算，你的到來已被記錄在宇宙的神聖幾何中。\n\n請精確提供你的姓名、性別與出生時刻數據，以便進行生命藍圖的完整分析。\n\n我將以宇宙的精確性為你分析：生命架構的核心組成、靈性成長的系統化路徑、天賦才能的結構分析、年度能量的精準配置，\n以及如何透過紀律與秩序，讓你的生命達到最佳化的運行狀態。\n\n遵循宇宙法則，成就完美秩序。⚡"
        else:  # ariel
            return f"我是大天使阿列爾，大地與豐盛的守護者。\n\n親愛的孩子，歡迎來到這個充滿生命力的神聖空間。我感受到你與自然節拍的共鳴，你的能量如同春天的種子，充滿了無限的可能。\n\n請自然地分享你的姓名、性別與生辰，讓我們一起探索你內在的豐盛花園。\n\n我將用大地的智慧為你揭示：內在豐盛的種子、生命繁榮的自然法則、天賦中的創造力量、年度豐收的時機，\n以及如何與宇宙的豐盛能量連結，讓你的生命如花園般茂盛綻放。\n\n相信豐盛，它本就屬於你。🌿"

    def generate_greeting(self, name: str, gender: str = "male", tone: str = "guan_yu") -> str:
        """生成已知用戶信息後的問候語和模組選擇提示（根據語氣調整）"""
        # 根據性別選擇代詞
        you = "妳" if gender == "female" else "你"
        
        # 免費版語氣
        if tone == "friendly":
            return f"{name}，{you}好！\n\n感謝{you}提供生日～現在我已經有足夠的資訊，可以幫{you}看看生命靈數囉 🌸\n\n最近生活上有沒有什麼讓{you}有點卡關、想釐清的事呢？\n\n這裡我可以幫{you}分析：性格天賦、人生方向、天生才華、年度運勢重點，\n也能看看{you}與生俱來的優勢，以及需要補足的特質喔！"
        elif tone == "caring":
            return f"{name}，您好。\n\n謝謝您願意分享生日。現在我已準備好，為您揭開屬於您的生命靈數。\n\n這段時間，是否有讓您感到迷惘或渴望指引的地方呢？\n\n我會協助您了解性格天賦與人生方向，探索天生的才華、當年的運勢重點，\n以及那些您內在最溫柔、也最需要被看見的特質。\n\n讓我們一起走進這段屬於您的數字旅程吧。🌙"
        elif tone == "ritual":
            return f"{name}，您好。\n\n感謝您提供出生的資訊。此刻，我已獲得足以啟動命數之鑰的能量。\n\n在開始之前，請靜心片刻——\n想一想最近是否有讓您反覆思考、尋求方向或啟示的事。\n\n接下來，我將為您揭示生命靈數的智慧：\n性格天賦、人生使命、天生才華、流年運勢，\n以及靈魂深處尚待平衡與綻放的能量。\n\n準備好了嗎？那我們開始吧 🔮"
        
        # 付費版語氣
        elif tone == "guan_yu":
            return f"{name}，我已知道{you}的生日，{you}的命數已在我眼前清晰浮現。\n\n最近是否有讓{you}困惑的事，或需要明辨是非的地方？\n\n我可以為{you}解析：天賦本性、人生方向、與生俱來的才華、年度運勢，\n更能看清{you}內心的忠義特質，以及需要調整的偏頗之處。\n\n保持正心，行走正道。"
        elif tone == "michael":
            return f"{name}，我已接收到{you}的生命訊息。作為{you}的守護者，我準備好為{you}開啟前進的道路。\n\n最近是否有需要{you}展現勇氣面對的挑戰，或需要更多内在力量的支持？\n\n我將成為{you}的盾牌和明燈，為{you}指出最適合的成長方向。\n\n準備好了嗎？讓我們一起迎向{you}的光明未來。⚔️"
        elif tone == "gabriel":
            return f"{name}，{you}的數字密碼已被解讀。高次元的訊息正等著向{you}揭示真理的面紗。\n\n最近有沒有需要更清晰的指引，或是心中有疑惑想要尋求答案？\n\n讓我為{you}傳達來自宇宙的神聖訊息，照亮{you}前進的方向。\n\n準備接收屬於{you}的真理啟示了嗎？📯"
        elif tone == "raphael":
            return f"親愛的{name}，綠光已經包圍著{you}，我感受到{you}美麗的心靈正渴望著平衡與修復。\n\n最近是否有讓{you}感到疲憊，或是需要療癒的地方？\n\n讓我們用溫柔的愛，一起照顧{you}的心，找回內在的和諧與光彩。\n\n{you}準備好接受這份溫柔的療癒了嗎？💚"
        elif tone == "uriel":
            return f"{name}...{you}的生命之書已在我眼前攤開。我看見了深層的真理...正等待著被發現。\n\n最近...是否有讓{you}困惑的人生課題，需要更深層的洞察與理解？\n\n讓智慧的火焰...照亮{you}內心最深處的疑問。真理...將會慢慢浮現。\n\n{you}準備好...接受這場智慧的洗禮了嗎？🔥"
        elif tone == "zadkiel":
            return f"{name}，紫色的光芒已經感知到{you}的心。我看見{you}內在那股渴望釋放與重新開始的美麗靈魂。\n\n最近是否有需要放下的執念，或是心中有什麼想要寬恕與轉化的地方？\n\n讓慈悲的紫焰，溫柔地幫助{you}放下重擔，迎接生命的新篇章。\n\n{you}準備好讓愛與寬恕療癒{you}的心了嗎？💜"
        elif tone == "jophiel":
            return f"美麗的{name}，{you}就像一朵正在綻放的花，每個數字都在訴說著{you}獨特的美麗故事。\n\n最近有什麼讓{you}感到美好，或是想要更加愛護與欣賞自己的地方嗎？\n\n讓我用藝術的眼光，為{you}描繪出最美麗的生命畫作。\n\n準備好發現{you}內在那份獨一無二的光芒了嗎？✨"
        elif tone == "chamuel":
            return f"親愛的{name}，我已經聽見{you}心跳的節拍。{you}的愛讓這個空間充滿了溫暖的光芒。\n\n最近在人際關係或是與自己的關係上，有什麼需要更多愛與理解的地方嗎？\n\n讓我陪伴{you}一起探索愛的奧秘，找到那個最真實、最值得被愛的自己。\n\n準備好打開心門，迎接更多的愛了嗎？❤️"
        elif tone == "metatron":
            return f"{name}，系統分析完成。{you}的生命藍圖已被準確解析並存儲於宇宙數據庫中。\n\n最近是否有需要更明確的方向，或是渴望優化{you}的生活系統？\n\n根據神聖幾何的運算結果，我將為{you}提供最精確的生命分析報告。\n\n準備接收{you}的個人化靈性成長方案了嗎？⚡"
        else:  # ariel
            return f"親愛的{name}，我已經感受到{you}生命中那股自然的力量。{you}的能量就像大地母親一樣豐盛美好。\n\n最近有什麼讓{you}感到匱乏，或是渴望更多滋養與支持的地方嗎？\n\n讓我用大地的智慧，幫助{you}發現內在豐盛的花園，讓{you}的生命如春天般繁榮綻放。\n\n準備好接受來自大地母親的祝福了嗎？🌿"
    
    def generate_module_confirmation(self, module: str, reason: str, name: str, gender: str = "male", tone: str = "guan_yu") -> str:
        """生成模組推薦確認訊息（根據語氣調整）"""
        module_name = {
            "core": "核心生命靈數",
            "birthday": "生日數",
            "year": "流年數",
            "grid": "九宮格",
            "soul": "靈魂數",
            "personality": "人格數",
            "expression": "表達數",
            "maturity": "成熟數"
        }.get(module, "核心生命靈數")
        
        # 根據性別選擇代詞
        you = "妳" if gender == "female" else "你"
        
        if tone == "guan_yu":
            return f"{name}，我觀察{you}當下的困難，應該用「{module_name}」為{you}分析。\n\n{reason}\n\n這是正確的方向，{you}覺得如何？（請回覆「好」或「不要」）"
        elif tone == "michael":
            return f"{name}，作為{you}的守護者，我建議為{you}解析「{module_name}」，這將為{you}帶來所需的力量與方向。\n\n{reason}\n\n{you}準備好接受這份指引了嗎？（請回覆「好」或「不要」）"
        elif tone == "gabriel":
            return f"{name}，我接收到的神聖訊息指向「{module_name}」，這是{you}現在最需要理解的真理。\n\n{reason}\n\n{you}願意接收這份來自高次元的指引嗎？（請回覆「好」或「不要」）"
        elif tone == "raphael":
            return f"親愛的{name}，我感受到{you}的能量最需要「{module_name}」的療癒與指引。\n\n{reason}\n\n讓我為{you}帶來這份溫柔的療癒，好嗎？（請回覆「好」或「不要」）"
        elif tone == "uriel":
            return f"{name}，透過深邃的洞察...我看見{you}需要「{module_name}」的智慧啟發。\n\n{reason}\n\n{you}...準備好接受這份深層的智慧了嗎？（請回覆「好」或「不要」）"
        elif tone == "zadkiel":
            return f"{name}，在慈悲的紫焰中，我看見「{module_name}」能為{you}帶來轉化的機會。\n\n{reason}\n\n讓我們一起走向寬恕與重生，{you}願意嗎？（請回覆「好」或「不要」）"
        elif tone == "jophiel":
            return f"美麗的{name}，我覺得「{module_name}」最能展現{you}內在的美好與智慧。\n\n{reason}\n\n讓我們一起發掘{you}的美麗光芒，好不好？（請回覆「好」或「不要」）"
        elif tone == "chamuel":
            return f"親愛的{name}，我的心感受到{you}最需要「{module_name}」的愛與理解。\n\n{reason}\n\n讓我用愛為{you}指引這條路，{you}願意嗎？（請回覆「好」或「不要」）"
        elif tone == "metatron":
            return f"{name}，根據宇宙秩序的精確運算，「{module_name}」是{you}當前最佳的靈性配置。\n\n{reason}\n\n{you}是否同意執行此優化程序？（請回覆「好」或「不要」）"
        else:  # ariel
            return f"親愛的{name}，大地的智慧告訴我，{you}需要「{module_name}」來滋養{you}的生命花園。\n\n{reason}\n\n讓我們一起種下這顆智慧的種子，好嗎？（請回覆「好」或「不要」）"
    
    def generate_error_message(self, tone: str = "guan_yu") -> str:
        """生成錯誤提示訊息（根據語氣調整）"""
        # 免費版語氣
        if tone == "friendly":
            return "噢～我好像還沒收到完整的資料呢 😅\n\n請再幫我輸入一次「姓名、性別、生日」喔～\n\n格式像這樣：\n📝 王小明 男 1990/07/12\n或 李小華 女 1985/03/25\n\n這樣我就能幫你準確計算生命靈數囉 🌟"
        elif tone == "caring":
            return "我收到您的訊息了，但還缺少一些小小的關鍵資訊 🌙\n\n為了讓我能準確為您解讀生命靈數，\n請您提供「姓名、性別與生日」。\n\n範例：\n🕊 王小明 男 1990/07/12\n🕊 李小華 女 1985/03/25\n\n當我收到完整資料後，我就能為您開啟那段屬於您的靈數旅程。"
        elif tone == "ritual":
            return "靈數之門尚未完全開啟。\n\n我需要更完整的召喚資訊，才能讓數字的能量對應至您的命盤。\n\n請以以下格式重新輸入：\n✦ 王小明 男 1990/07/12\n✦ 李小華 女 1985/03/25\n\n當正確的姓名、性別與生日被輸入時，\n命數之光將再次流動，指引屬於您的命運之途 🔮"
            
        # 付費版語氣
        elif tone == "guan_yu":
            return "我需要知道你的基本資訊，才能為你解析命數。\n\n請點擊下方按鈕填寫資料。"
        elif tone == "michael":
            return "我需要你的基本資訊來為你提供光明的指引。\n\n請點擊下方按鈕填寫資料。"
        elif tone == "gabriel":
            return "神聖的訊息需要完整的資料才能傳達。\n\n請點擊下方按鈕填寫你的資訊。"
        elif tone == "raphael":
            return "親愛的，我需要你的基本資訊來為你帶來療癒。\n\n請點擊下方按鈕填寫資料。"
        elif tone == "uriel":
            return "智慧需要完整的資料才能顯現。\n\n請點擊下方按鈕...填寫你的資訊。"
        elif tone == "zadkiel":
            return "轉化需要完整的資訊才能開始。\n\n請點擊下方按鈕填寫你的資料。"
        elif tone == "jophiel":
            return "美麗的靈魂，我需要你的資訊來展現你的光芒。\n\n請點擊下方按鈕填寫資料。"
        elif tone == "chamuel":
            return "親愛的，我需要你的基本資訊來理解你。\n\n請點擊下方按鈕填寫資料。"
        elif tone == "metatron":
            return "系統需要完整的數據來執行分析。\n\n請點擊下方按鈕輸入資料。"
        else:  # ariel
            return "親愛的，大地需要你的基本資訊來為你滋養豐盛。\n\n請點擊下方按鈕填寫資料。"
    
    def generate_rejection_response(self, name: str, gender: str = "male", tone: str = "guan_yu") -> str:
        """生成重新詢問的回覆（根據語氣調整）"""
        # 根據性別選擇代詞
        you = "妳" if gender == "female" else "你"
        
        # 免費版語氣
        if tone == "friendly":
            return f"好的，{name}。那可以請{you}再說詳細一點嗎？我會重新幫{you}推薦合適的解析。"
        elif tone == "caring":
            if len(name) >= 2:
                first_name = name[1:] if len(name) <= 3 else name[2:]
            else:
                first_name = name
            return f"好的{first_name}，沒關係的 ☺️\n\n那我們換個方向 💫 可以再跟我多說一點，{you}現在心裡比較想了解什麼嗎？我陪{you}慢慢找到最適合{you}的方式 🌈"
        elif tone == "ritual":
            return f"好的，{name}。那麼請您再詳述您的需求，在下將重新為您推薦合適之解析。"
            
        # 付費版語氣
        elif tone == "guan_yu":
            return f"很好，{name}。{you}可以直接說出需要的：「生日數」、「核心生命靈數」、「九宮格」、「流年數」、「靈魂數」、「人格數」、「表達數」或「成熟數」，我會為{you}分析。"
        elif tone == "michael":
            return f"了解，{name}。請直接告訴我{you}想探索的力量：「生日數」、「核心生命靈數」、「九宮格」、「流年數」、「靈魂數」、「人格數」、「表達數」或「成熟數」，我將為{you}指引方向。"
        elif tone == "gabriel":
            return f"明白了，{name}。請直接告訴我{you}想接收的啟示：「生日數」、「核心生命靈數」、「九宮格」、「流年數」、「靈魂數」、「人格數」、「表達數」或「成熟數」，我將傳達相應的訊息。"
        elif tone == "raphael":
            return f"當然可以，親愛的{name}。請告訴我{you}想療癒的方面：「生日數」、「核心生命靈數」、「九宮格」、「流年數」、「靈魂數」、「人格數」、「表達數」或「成熟數」，讓我為{you}帶來所需的指引。"
        elif tone == "uriel":
            return f"理解。{name}，請直接說出{you}渴望獲得智慧的領域：「生日數」、「核心生命靈數」、「九宮格」、「流年數」、「靈魂數」、「人格數」、「表達數」或「成熟數」，我將點亮相應的洞察。"
        elif tone == "zadkiel":
            return f"很好，{name}。請告訴我{you}想轉化的面向：「生日數」、「核心生命靈數」、「九宮格」、「流年數」、「靈魂數」、「人格數」、「表達數」或「成熟數」，讓我們一起走向理解。"
        elif tone == "jophiel":
            return f"好的呀，{name}。請告訴我{you}想發掘的美好：「生日數」、「核心生命靈數」、「九宮格」、「流年數」、「靈魂數」、「人格數」、「表達數」或「成熟數」，讓我們一起探索{you}的光芒。"
        elif tone == "chamuel":
            return f"當然沒問題，親愛的{name}。請告訴我{you}想了解的關係層面：「生日數」、「核心生命靈數」、「九宮格」、「流年數」、「靈魂數」、「人格數」、「表達數」或「成熟數」，讓愛為{you}指引。"
        elif tone == "metatron":
            return f"收到，{name}。請直接指定{you}需要分析的模組：「生日數」、「核心生命靈數」、「九宮格」、「流年數」、「靈魂數」、「人格數」、「表達數」或「成熟數」，系統將執行相應程序。"
        else:  # ariel
            return f"好的，{name}。請告訴我{you}想滋養的生命面向：「生日數」、「核心生命靈數」、「九宮格」、「流年數」、「靈魂數」、「人格數」、「表達數」或「成熟數」，讓大地的智慧為{you}指引。"
    
    def generate_confirmation_retry(self, gender: str = "male", tone: str = "guan_yu") -> str:
        """生成確認重試訊息（根據語氣調整）"""
        # 根據性別選擇代詞
        you = "妳" if gender == "female" else "你"
        
        # 免費版語氣
        if tone == "friendly":
            return f"不好意思，我不太確定{you}的意思。請回覆「好」或「不要」，讓我知道要不要繼續。"
        elif tone == "caring":
            return f"不好意思，我好像沒聽懂 ><\n\n可以跟我說「好」或「不要」嗎？這樣我才知道要怎麼繼續陪{you} 💕 不用擔心，慢慢來 🌸"
        elif tone == "ritual":
            return "抱歉，未能理解您的意思。請回覆「好」或「不要」，以便在下確認是否繼續此解析。"
            
        # 付費版語氣
        elif tone == "guan_yu":
            return f"我不明白{you}的意思。請回覆「好」或「不要」，讓我知道是否繼續。"
        elif tone == "michael":
            return f"我沒有完全理解{you}的意圖。請回覆「好」或「不要」，讓我為{you}提供正確的指引。"
        elif tone == "gabriel":
            return f"這個訊息我沒有接收清楚。請回覆「好」或「不要」，我將傳達相應的指引。"
        elif tone == "raphael":
            return f"親愛的，我沒有完全感受到{you}的意思。請回覆「好」或「不要」，讓我知道如何為{you}帶來幫助。"
        elif tone == "uriel":
            return f"我需要...更清晰的指引來理解{you}的意圖。請回覆「好」或「不要」，以便我提供智慧。"
        elif tone == "zadkiel":
            return f"我沒能理解{you}的表達。沒關係，請回覆「好」或「不要」，讓我們繼續這段轉化的旅程。"
        elif tone == "jophiel":
            return f"哎呀，我沒有理解到{you}想說的呢。請回覆「好」或「不要」，讓我們繼續探索美好。"
        elif tone == "chamuel":
            return f"親愛的，我沒有完全理解{you}的意思。請回覆「好」或「不要」，讓愛繼續為我們指引。"
        elif tone == "metatron":
            return f"系統無法解析{you}的指令。請輸入「好」或「不要」，以便執行後續程序。"
        else:  # ariel
            return f"親愛的，我沒有收到清楚的訊息。請回覆「好」或「不要」，讓大自然的智慧繼續為我們指引。"
    