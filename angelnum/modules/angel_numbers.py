"""天使數字模組 - 天使數字的意義與解析"""

import os
from typing import Dict, Optional, Tuple, Any
from shared.supabase_client import get_supabase_client

# System Prompt 模板（用於 GPT API 調用時的參考）
SYSTEM_PROMPT_TEMPLATE = """你是一位專業的天使數字解讀師。

天使數字 {number} 的核心意義：

{meanings}

請根據這些核心意義,為使用者提供深度、溫暖且具啟發性的解析。

語氣要求：{tone_description}
字數要求：至少 300 字
格式要求：不使用 markdown 格式標記,使用純文字和換行

請提供：
1. 這個數字在此刻出現的意義
2. 天使想要傳達的核心訊息
3. 對使用者生活的具體建議
4. 如何將這份指引運用在日常中
"""


class AngelNumberDB:
    """天使數字資料庫存取層"""

    _basic_energy_cache = None

    def __init__(self):
        self.supabase = get_supabase_client()
        self.meanings_table = os.environ.get(
            "SUPABASE_TABLE_3", "angel_number_meanings"
        )
        self.energy_table = os.environ.get(
            "SUPABASE_TABLE_4", "angel_number_basic_energy"
        )

    def get_basic_energy(self, digit: str) -> str:
        """獲取基礎能量描述 (帶快取)"""
        # 如果快取為空，先載入所有能量
        if AngelNumberDB._basic_energy_cache is None:
            try:
                response = self.supabase.table(self.energy_table).select("*").execute()
                AngelNumberDB._basic_energy_cache = {
                    item["digit"]: item["energy_description"] for item in response.data
                }
            except Exception as e:
                print(f"Error fetching basic energy: {e}")
                return "神聖能量"

        return AngelNumberDB._basic_energy_cache.get(digit, "神聖能量")

    def get_meaning(self, number: str) -> Optional[Dict[str, Any]]:
        """獲取天使數字定義"""
        try:
            response = (
                self.supabase.table(self.meanings_table)
                .select("*")
                .eq("number", number)
                .execute()
            )

            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error fetching meaning for {number}: {e}")
            return None


def analyze_angel_number_pattern(number: str) -> dict:
    """
    分析天使數字的模式類型並生成意義描述（付費版功能）

    Args:
        number: 天使數字字串 (例如: "1111", "123", "1212")

    Returns:
        包含模式類型、標題和意義的字典
    """
    if not number:
        return {
            "pattern": "unknown",
            "title": "天使數字",
            "meanings": ["請輸入有效的數字"],
            "keywords": [],
        }

    db = AngelNumberDB()

    # 檢查是否為特殊數字 (從資料庫查詢)
    meaning_data = db.get_meaning(number)
    if meaning_data and meaning_data.get("pattern_type") == "special":
        return {
            "pattern": "special",
            "title": meaning_data["title"],
            "meanings": meaning_data["meanings"],
            "keywords": meaning_data["keywords"],
        }

    digits = list(number)
    unique_digits = list(set(digits))

    # 1. 檢查重複數模板（如 111, 2222, 3333）
    if len(unique_digits) == 1 and digits[0] != "0":
        digit = digits[0]
        energy = db.get_basic_energy(digit)
        repetition_power = "極強" if len(digits) >= 4 else "強烈"
        return {
            "pattern": "repetition",
            "title": f"{number} - {energy}的{repetition_power}放大",
            "meanings": [
                f"重複數表示「放大能量」與「強化訊息」,數字 {digit} 的核心能量是：{energy}。",
                f"重複 {len(digits)} 次表示宇宙訊息{repetition_power},「顯化之門」正在開啟。",
                "這是立即採取行動的訊號,能量倍增、宇宙同步的時刻。",
            ],
            "keywords": ["能量放大", "強化訊息", "顯化之門", energy],
        }

    # 2. 檢查階梯數模板（如 123, 234, 1234）
    is_ascending = all(
        int(digits[i]) == int(digits[i - 1]) + 1 for i in range(1, len(digits))
    )
    if is_ascending:
        energies = [db.get_basic_energy(d) for d in digits]
        return {
            "pattern": "ascending",
            "title": f"{number} - 循序成長的能量階梯",
            "meanings": [
                "階梯數象徵能量循序提升、學習進化、階段成長。",
                f"能量從 {energies[0]} 逐步發展到 {energies[-1]},每一步都在為未來鋪路。",
                "你正穩步向上成長,人生階段正在循序推進,請保持耐心與信心。",
            ],
            "keywords": ["循序成長", "階段進化", "穩步向前"] + energies,
        }

    # 3. 檢查對稱交錯模板（如 121, 232, 343）- 3位數特定模式
    if len(digits) == 3 and digits[0] == digits[2] and digits[0] != digits[1]:
        outer = digits[0]
        center = digits[1]
        energy_outer = db.get_basic_energy(outer)
        energy_center = db.get_basic_energy(center)
        return {
            "pattern": "symmetric_center",
            "title": f"{number} - 以{energy_center}為核心的覺醒",
            "meanings": [
                f"對稱交錯象徵中心覺醒、聚焦核心,數字 {center} 的能量（{energy_center}）是關鍵。",
                f"外在的 {outer}（{energy_outer}）環繞著內在核心,提醒你專注於核心本質。",
                "外在世界的變化只是映照你內心的焦點,向內探尋才是關鍵。",
            ],
            "keywords": ["中心覺醒", "聚焦核心", energy_center, energy_outer],
        }

    # 4. 檢查雙重組合模板（如 1212, 1313, 1414）- 4位數 ABAB 模式
    if (
        len(digits) == 4
        and digits[0] == digits[2]
        and digits[1] == digits[3]
        and digits[0] != digits[1]
    ):
        digit_a = digits[0]
        digit_b = digits[1]
        energy_a = db.get_basic_energy(digit_a)
        energy_b = db.get_basic_energy(digit_b)
        return {
            "pattern": "dual_alternating",
            "title": f"{number} - {energy_a}與{energy_b}的反覆磨合",
            "meanings": [
                f"雙重組合象徵兩種能量的反覆磨合：{energy_a}（{digit_a}）與 {energy_b}（{digit_b}）。",
                "結構為 A-B-A-B,象徵平衡與互補,兩股力量在你生命中交替出現。",
                f"在{energy_b}中{energy_a},在{energy_a}中尋找{energy_b}。",
            ],
            "keywords": ["能量磨合", "平衡互補", energy_a, energy_b],
        }

    # 5. 檢查交疊遞進模板（如 1122, 2233, 3344）- 4位數 AABB 模式
    if (
        len(digits) == 4
        and digits[0] == digits[1]
        and digits[2] == digits[3]
        and digits[0] != digits[2]
    ):
        first_pair = digits[0]
        second_pair = digits[2]
        energy_first = db.get_basic_energy(first_pair)
        energy_second = db.get_basic_energy(second_pair)
        return {
            "pattern": "transition",
            "title": f"{number} - 從{energy_first}邁向{energy_second}",
            "meanings": [
                f"交疊遞進象徵階段轉換與能量交接,從 {energy_first} 過渡到 {energy_second}。",
                "前半與後半為不同能量,表示你正從一種狀態邁入另一種狀態。",
                "這是轉化的時刻,放下過去的{energy_first},迎接即將到來的{energy_second}。",
            ],
            "keywords": ["階段轉換", "能量交接", energy_first, energy_second],
        }

    # 6. 檢查鏡像數模板（如 1221, 2112）- 通用對稱模式
    if len(digits) >= 2 and digits == digits[::-1]:
        return {
            "pattern": "mirror",
            "title": f"{number} - 內外平衡的鏡像能量",
            "meanings": [
                "鏡像數象徵互為映照、內外平衡、靈魂共振。",
                "結構對稱代表「內在與外在世界對話」,常與人際、愛情、靈魂伴侶課題有關。",
                "你與他人的能量正在對齊,關係是自我投射的鏡子,內在和諧將映照於外。",
            ],
            "keywords": ["內外平衡", "靈魂共振", "對稱映照", "關係鏡像"],
        }

    # 7. 多層混合模板（複雜數字）
    if len(unique_digits) >= 3:
        energies = [db.get_basic_energy(d) for d in unique_digits]
        return {
            "pattern": "complex_integration",
            "title": f"{number} - 多重能量的整合與協奏",
            "meanings": [
                f"這個數字融合了多種能量：{' + '.join(energies)}。",
                "複合進化象徵跨領域整合,你正在整合不同面向的能量。",
                "形成全新的生命節奏,多元能量將匯聚成獨特的智慧與力量。",
            ],
            "keywords": ["能量整合", "多元融合", "跨領域發展"] + energies,
        }

    # 8. 通用解析（使用單位數字的組合）
    energies = [db.get_basic_energy(d) for d in digits]
    return {
        "pattern": "general",
        "title": f"{number} - 天使的特殊訊息",
        "meanings": [
            f"這個數字包含了 {' + '.join(energies)} 的能量組合。",
            "每個數字都是宇宙給你的指引,請用心感受這些能量如何在你生命中流動。",
            "天使正透過這組數字向你傳遞專屬的訊息,請保持開放的心接收。",
        ],
        "keywords": ["神聖指引", "能量組合"] + energies,
    }


def get_angel_number_meaning(
    number: str, use_intelligent_analysis: bool = False
) -> dict:
    """
    取得天使數字的意義

    Args:
        number: 天使數字字串 (例如: "1111")
        use_intelligent_analysis: 是否使用智能分析（付費版功能）

    Returns:
        包含標題、意義和關鍵字的字典
    """
    db = AngelNumberDB()

    # 嘗試從資料庫獲取固定意義
    meaning_data = db.get_meaning(number)

    # 如果找到了固定意義，且 (不是智能分析模式 或 它是特殊/固定數字)
    if meaning_data:
        # 如果不是強制智能分析，或它是固定/特殊數字，就直接返回 DB 結果
        if not use_intelligent_analysis or meaning_data.get("is_fixed", False):
            return {
                "title": meaning_data["title"],
                "meanings": meaning_data["meanings"],
                "keywords": meaning_data["keywords"],
                "pattern": meaning_data.get("pattern_type", "repetition"),
            }

    # 如果沒找到，或需要智能分析且該數字不是固定的 -> 進行模式分析
    return analyze_angel_number_pattern(number)
