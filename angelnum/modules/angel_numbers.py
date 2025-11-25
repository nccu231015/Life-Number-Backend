"""天使數字模組 - 天使數字的意義與解析"""

# 單位數字的基礎能量（1-9）- 用於智能模式識別
BASIC_ENERGY = {
    "1": "開創、行動、領導、顯化起點",
    "2": "和諧、合作、平衡、信任",
    "3": "表達、創造、靈感、成長",
    "4": "結構、穩定、秩序、責任",
    "5": "變化、自由、探索、突破",
    "6": "愛、家庭、治癒、服務",
    "7": "靈性、智慧、內省、覺醒",
    "8": "財富、力量、循環、豐盛",
    "9": "完成、釋放、轉化、慈悲",
    "0": "無限、原點、靈性重置、全域"
}

# 特殊數字的固定意義
SPECIAL_NUMBERS = {
    "0000": "全域重置與靈性原點",
    "1010": "覺醒與新循環開端",
    "2020": "遠景校準、目標對焦",
    "3030": "創意的週期性爆發",
    "4040": "在混亂中重建秩序",
    "5050": "自由與責任的平衡",
    "6060": "愛與照顧的互惠循環",
    "7070": "內在導師覺醒",
    "8080": "財富循環與權力平衡",
    "9090": "完成一輪學習、迎接新旅程"
}

# 天使數字的核心意義（免費版固定意義，1111-9999）
ANGEL_NUMBERS = {
    "1111": {
        "title": "1111 - 新開始與精神覺醒",
        "meanings": [
            "新開始與精神覺醒：象徵全新旅程的開啟,提醒專注當下,與生命使命保持一致。",
            "思維具化與宇宙支持：思想正在快速具現化,宇宙回應你保持正向思考。",
            "領導力爆發與自我實現：代表行動與成就的時刻來臨,展現獨特才華。"
        ],
        "keywords": ["新開始", "精神覺醒", "思維具化", "領導力", "自我實現"],
        "pattern": "repetition"
    },
    "2222": {
        "title": "2222 - 和諧與平衡",
        "meanings": [
            "和諧、平衡與精神支援：提醒你維持內在與人際的穩定與寧靜。",
            "持續進展與成功軌道：努力的成果正在累積,正走在通往成功的路上。",
            "人際連結與情感平衡：象徵愛情與關係的穩定,甚至預示靈魂伴侶的出現。"
        ],
        "keywords": ["和諧", "平衡", "持續進展", "人際連結", "情感平衡"],
        "pattern": "repetition"
    },
    "3333": {
        "title": "3333 - 成長與創意",
        "meanings": [
            "成長與擴展：代表個人成長、視野拓展與新機會的到來。",
            "創意與自我表達：鼓勵釋放創造力、真實表達自我。",
            "靈性引導與支援：暗示天使與高等力量的陪伴與引導。"
        ],
        "keywords": ["成長", "擴展", "創意", "自我表達", "靈性引導"],
        "pattern": "repetition"
    },
    "4444": {
        "title": "4444 - 穩定與守護",
        "meanings": [
            "穩定與堅實基礎：提醒築基與耐心,強調長遠的穩固發展。",
            "感恩與內在力量：要以感恩之心面對生活,並善用自身韌性。",
            "神聖守護與正路同行：天使在守護,確認你正走在正確的方向上。"
        ],
        "keywords": ["穩定", "堅實基礎", "感恩", "神聖守護", "正確方向"],
        "pattern": "repetition"
    },
    "5555": {
        "title": "5555 - 重大轉變",
        "meanings": [
            "重大轉變與成長：象徵人生進入劇烈變化的階段,迎接新挑戰。",
            "積極變革與正向演化：雖然變動,但方向朝更好的未來前進。",
            "自由與靈性覺醒：呼喚你擁抱真實自我,追求內在的自由。"
        ],
        "keywords": ["重大轉變", "成長", "變革", "自由", "靈性覺醒"],
        "pattern": "repetition"
    },
    "6666": {
        "title": "6666 - 愛與和諧",
        "meanings": [
            "愛與家庭的和諧：強調家庭、情感與內心的平衡。",
            "愛的回歸與支持：象徵同理心與支持網絡的重要性。",
            "平衡物質與靈性：提醒兼顧精神層次與現實生活。"
        ],
        "keywords": ["愛", "家庭和諧", "支持", "平衡", "物質與靈性"],
        "pattern": "repetition"
    },
    "7777": {
        "title": "7777 - 靈性覺醒",
        "meanings": [
            "靈性覺醒與神聖引導：象徵靈性開啟與信任直覺。",
            "啟迪、堅持與智慧：鼓勵勇敢、持續並擁抱成長。",
            "療癒結束與靈魂突破：暗示困境將結束,靈魂進入新週期。"
        ],
        "keywords": ["靈性覺醒", "神聖引導", "智慧", "療癒", "靈魂突破"],
        "pattern": "repetition"
    },
    "8888": {
        "title": "8888 - 豐盛與財富",
        "meanings": [
            "豐盛與財富臨近：象徵財運與繁榮即將到來。",
            "無限豐盈的能量：提醒你把握機會,吸引成功。",
            "自我成長與指引：代表進入新的自我探索與提升階段。"
        ],
        "keywords": ["豐盛", "財富", "繁榮", "無限能量", "自我成長"],
        "pattern": "repetition"
    },
    "9999": {
        "title": "9999 - 完成與新旅程",
        "meanings": [
            "完成與迎向新旅程：象徵一段使命的圓滿結束,準備展開新篇章。",
            "靈性任務完成、迎接革新：意味重要目標已達成,新的方向即將出現。",
            "循環完結與心靈轉化：提醒你一個階段結束,進入靈性蛻變。"
        ],
        "keywords": ["完成", "新旅程", "圓滿", "革新", "心靈轉化"],
        "pattern": "repetition"
    }
}


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
            "keywords": []
        }
    
    # 檢查是否為特殊數字
    if number in SPECIAL_NUMBERS:
        return {
            "pattern": "special",
            "title": f"{number} - {SPECIAL_NUMBERS[number]}",
            "meanings": [SPECIAL_NUMBERS[number]],
            "keywords": ["特殊能量", "循環", "轉化"]
        }
    
    digits = list(number)
    unique_digits = list(set(digits))
    
    # 1. 檢查重複數模板（如 111, 2222, 3333）
    if len(unique_digits) == 1 and digits[0] != "0":
        digit = digits[0]
        energy = BASIC_ENERGY.get(digit, "神聖能量")
        repetition_power = "極強" if len(digits) >= 4 else "強烈"
        return {
            "pattern": "repetition",
            "title": f"{number} - {energy}的{repetition_power}放大",
            "meanings": [
                f"重複數表示「放大能量」與「強化訊息」,數字 {digit} 的核心能量是：{energy}。",
                f"重複 {len(digits)} 次表示宇宙訊息{repetition_power},「顯化之門」正在開啟。",
                "這是立即採取行動的訊號,能量倍增、宇宙同步的時刻。"
            ],
            "keywords": ["能量放大", "強化訊息", "顯化之門", energy]
        }
    
    # 2. 檢查階梯數模板（如 123, 234, 1234）
    is_ascending = all(int(digits[i]) == int(digits[i-1]) + 1 for i in range(1, len(digits)))
    if is_ascending:
        energies = [BASIC_ENERGY.get(d, d) for d in digits]
        return {
            "pattern": "ascending",
            "title": f"{number} - 循序成長的能量階梯",
            "meanings": [
                "階梯數象徵能量循序提升、學習進化、階段成長。",
                f"能量從 {energies[0]} 逐步發展到 {energies[-1]},每一步都在為未來鋪路。",
                "你正穩步向上成長,人生階段正在循序推進,請保持耐心與信心。"
            ],
            "keywords": ["循序成長", "階段進化", "穩步向前"] + energies
        }
    
    # 3. 檢查對稱交錯模板（如 121, 232, 343）- 3位數特定模式
    if len(digits) == 3 and digits[0] == digits[2] and digits[0] != digits[1]:
        outer = digits[0]
        center = digits[1]
        energy_outer = BASIC_ENERGY.get(outer, outer)
        energy_center = BASIC_ENERGY.get(center, center)
        return {
            "pattern": "symmetric_center",
            "title": f"{number} - 以{energy_center}為核心的覺醒",
            "meanings": [
                f"對稱交錯象徵中心覺醒、聚焦核心,數字 {center} 的能量（{energy_center}）是關鍵。",
                f"外在的 {outer}（{energy_outer}）環繞著內在核心,提醒你專注於核心本質。",
                "外在世界的變化只是映照你內心的焦點,向內探尋才是關鍵。"
            ],
            "keywords": ["中心覺醒", "聚焦核心", energy_center, energy_outer]
        }
    
    # 4. 檢查雙重組合模板（如 1212, 1313, 1414）- 4位數 ABAB 模式
    if len(digits) == 4 and digits[0] == digits[2] and digits[1] == digits[3] and digits[0] != digits[1]:
        digit_a = digits[0]
        digit_b = digits[1]
        energy_a = BASIC_ENERGY.get(digit_a, digit_a)
        energy_b = BASIC_ENERGY.get(digit_b, digit_b)
        return {
            "pattern": "dual_alternating",
            "title": f"{number} - {energy_a}與{energy_b}的反覆磨合",
            "meanings": [
                f"雙重組合象徵兩種能量的反覆磨合：{energy_a}（{digit_a}）與 {energy_b}（{digit_b}）。",
                "結構為 A-B-A-B,象徵平衡與互補,兩股力量在你生命中交替出現。",
                f"在{energy_b}中{energy_a},在{energy_a}中尋找{energy_b}。"
            ],
            "keywords": ["能量磨合", "平衡互補", energy_a, energy_b]
        }
    
    # 5. 檢查交疊遞進模板（如 1122, 2233, 3344）- 4位數 AABB 模式
    if len(digits) == 4 and digits[0] == digits[1] and digits[2] == digits[3] and digits[0] != digits[2]:
        first_pair = digits[0]
        second_pair = digits[2]
        energy_first = BASIC_ENERGY.get(first_pair, first_pair)
        energy_second = BASIC_ENERGY.get(second_pair, second_pair)
        return {
            "pattern": "transition",
            "title": f"{number} - 從{energy_first}邁向{energy_second}",
            "meanings": [
                f"交疊遞進象徵階段轉換與能量交接,從 {energy_first} 過渡到 {energy_second}。",
                "前半與後半為不同能量,表示你正從一種狀態邁入另一種狀態。",
                f"這是轉化的時刻,放下過去的{energy_first},迎接即將到來的{energy_second}。"
            ],
            "keywords": ["階段轉換", "能量交接", energy_first, energy_second]
        }
    
    # 6. 檢查鏡像數模板（如 1221, 2112）- 通用對稱模式
    if len(digits) >= 2 and digits == digits[::-1]:
        return {
            "pattern": "mirror",
            "title": f"{number} - 內外平衡的鏡像能量",
            "meanings": [
                "鏡像數象徵互為映照、內外平衡、靈魂共振。",
                "結構對稱代表「內在與外在世界對話」,常與人際、愛情、靈魂伴侶課題有關。",
                "你與他人的能量正在對齊,關係是自我投射的鏡子,內在和諧將映照於外。"
            ],
            "keywords": ["內外平衡", "靈魂共振", "對稱映照", "關係鏡像"]
        }
    
    # 7. 多層混合模板（複雜數字）
    if len(unique_digits) >= 3:
        energies = [BASIC_ENERGY.get(d, d) for d in unique_digits]
        return {
            "pattern": "complex_integration",
            "title": f"{number} - 多重能量的整合與協奏",
            "meanings": [
                f"這個數字融合了多種能量：{' + '.join(energies)}。",
                "複合進化象徵跨領域整合,你正在整合不同面向的能量。",
                "形成全新的生命節奏,多元能量將匯聚成獨特的智慧與力量。"
            ],
            "keywords": ["能量整合", "多元融合", "跨領域發展"] + energies
        }
    
    # 8. 通用解析（使用單位數字的組合）
    energies = [BASIC_ENERGY.get(d, d) for d in digits]
    return {
        "pattern": "general",
        "title": f"{number} - 天使的特殊訊息",
        "meanings": [
            f"這個數字包含了 {' + '.join(energies)} 的能量組合。",
            "每個數字都是宇宙給你的指引,請用心感受這些能量如何在你生命中流動。",
            "天使正透過這組數字向你傳遞專屬的訊息,請保持開放的心接收。"
        ],
        "keywords": ["神聖指引", "能量組合"] + energies
    }


def get_angel_number_meaning(number: str, use_intelligent_analysis: bool = False) -> dict:
    """
    取得天使數字的意義
    
    Args:
        number: 天使數字字串 (例如: "1111")
        use_intelligent_analysis: 是否使用智能分析（付費版功能）
        
    Returns:
        包含標題、意義和關鍵字的字典
    """
    # 如果使用智能分析,或者數字不在固定列表中,使用模式分析
    if use_intelligent_analysis or number not in ANGEL_NUMBERS:
        return analyze_angel_number_pattern(number)
    
    # 否則返回固定意義（免費版）
    return ANGEL_NUMBERS.get(number, {
        "title": f"{number} - 天使數字",
        "meanings": ["此數字正在對你傳遞獨特的訊息,請用心感受。"],
        "keywords": ["覺醒", "指引", "成長"],
        "pattern": "general"
    })


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
