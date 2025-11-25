from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, List


def normalize_birthdate(birthdate: str) -> str:
    s = birthdate.strip()
    s = s.replace("年", "/").replace("月", "/").replace("日", "")
    s = re.sub(r"[.\\-]", "/", s)
    return s


def birthdate_to_digits_sum(birthdate: str) -> int:
    s = normalize_birthdate(birthdate)
    try:
        # Try common formats: YYYY/MM/DD, YYYY/M/D
        dt = datetime.strptime(s, "%Y/%m/%d")
    except ValueError:
        try:
            dt = datetime.strptime(s, "%Y/%m/%d")
        except ValueError:
            # Fallback: just sum digits in the string
            digits = [int(ch) for ch in re.findall(r"\d", s)]
            return sum(digits)
    digits = list(map(int, re.findall(r"\d", dt.strftime("%Y%m%d"))))
    return sum(digits)


def reduce_to_core_number(n: int) -> int:
    while n > 9:
        n = sum(int(ch) for ch in str(n))
    return n


def extract_birth_day(birthdate: str) -> int:
    s = normalize_birthdate(birthdate)
    # Try strict parsing first
    try:
        dt = datetime.strptime(s, "%Y/%m/%d")
        return dt.day
    except ValueError:
        pass
    # Heuristic: split tokens and use the last numeric as day
    tokens = [t for t in s.split("/") if t]
    numeric_tokens = [t for t in tokens if t.isdigit()]
    if len(numeric_tokens) >= 1:
        last = numeric_tokens[-1]
        if 1 <= len(last) <= 2:
            day = int(last)
            if 1 <= day <= 31:
                return day
    # If the whole string is just digits like YYYYMMDD
    digits_only = re.sub(r"\D", "", s)
    if len(digits_only) >= 8:
        day = int(digits_only[-2:])
        if 1 <= day <= 31:
            return day
    # Fallback: pick the last 1-2 digit sequence
    groups = re.findall(r"\d{1,2}", s)
    if groups:
        day = int(groups[-1])
        if 1 <= day <= 31:
            return day
    # Ultimate fallback
    return 1


def compute_birthday_number(birthdate: str) -> int:
    day = extract_birth_day(birthdate)
    return reduce_to_core_number(day)


def extract_birth_month(birthdate: str) -> int:
    s = normalize_birthdate(birthdate)
    try:
        dt = datetime.strptime(s, "%Y/%m/%d")
        return dt.month
    except ValueError:
        pass
    tokens = [t for t in s.split("/") if t]
    numeric_tokens = [t for t in tokens if t.isdigit()]
    if len(numeric_tokens) >= 2:
        month = int(numeric_tokens[-2])
        if 1 <= month <= 12:
            return month
    digits_only = re.sub(r"\D", "", s)
    if len(digits_only) >= 8:
        month = int(digits_only[-4:-2])
        if 1 <= month <= 12:
            return month
    groups = re.findall(r"\d{1,2}", s)
    if len(groups) >= 2:
        month = int(groups[-2])
        if 1 <= month <= 12:
            return month
    return 1


def compute_personal_year_number(birthdate: str, year: int | None = None) -> int:
    y = year or datetime.now().year
    year_sum = sum(int(ch) for ch in str(y))
    month = extract_birth_month(birthdate)
    day = extract_birth_day(birthdate)
    total = year_sum + month + day
    return reduce_to_core_number(total)


# --- Nine-grid helpers ---

def extract_all_digits(birthdate: str) -> List[int]:
    s = normalize_birthdate(birthdate)
    digits = [int(ch) for ch in re.findall(r"\d", s)]
    return digits


def compute_grid_counts(birthdate: str) -> Dict[int, int]:
    counts: Dict[int, int] = {i: 0 for i in range(1, 10)}
    for d in extract_all_digits(birthdate):
        if 1 <= d <= 9:
            counts[d] += 1
    return counts


GRID_LINES = {
    "123": (1, 2, 3),
    "456": (4, 5, 6),
    "789": (7, 8, 9),
    "147": (1, 4, 7),
    "258": (2, 5, 8),
    "369": (3, 6, 9),
    "159": (1, 5, 9),
    "357": (3, 5, 7),
}


def detect_present_lines(counts: Dict[int, int]) -> List[str]:
    present: List[str] = []
    for key, digits in GRID_LINES.items():
        if all(counts[d] > 0 for d in digits):
            present.append(key)
    return present


def build_ascii_grid(counts: Dict[int, int]) -> str:
    """構建九宮格顯示，顯示各數字出現次數"""
    def cell(n: int) -> str:
        c = counts[n]
        return str(c) if c > 0 else "·"

    row1 = f"{cell(1)} {cell(2)} {cell(3)}"
    row2 = f"{cell(4)} {cell(5)} {cell(6)}"
    row3 = f"{cell(7)} {cell(8)} {cell(9)}"
    return f"{row1}\n{row2}\n{row3}"


# --- Soul Number helpers ---

def extract_vowels(english_name: str) -> List[str]:
    """從英文名字中提取母音字母（A, E, I, O, U）"""
    vowels = []
    for char in english_name.upper():
        if char in 'AEIOU':
            vowels.append(char)
    return vowels


def vowel_to_number(vowel: str) -> int:
    """將母音字母轉換為對應數字"""
    vowel_map = {
        'A': 1,
        'E': 5,
        'I': 9,
        'O': 6,
        'U': 3
    }
    return vowel_map.get(vowel.upper(), 0)


def compute_soul_number(english_name: str) -> int:
    """計算靈魂數：從英文名字的母音累加至1-9"""
    vowels = extract_vowels(english_name)
    total = sum(vowel_to_number(vowel) for vowel in vowels)
    return reduce_to_core_number(total)


def extract_all_letters(english_name: str) -> list[str]:
    """從英文名字中提取所有字母（母音和子音）用於人格數計算"""
    if not english_name:
        return []
    
    letters = []
    
    # 遍歷每個字符，提取所有英文字母
    for char in english_name.upper():
        if char.isalpha():
            letters.append(char)
    
    return letters


def consonant_to_number(consonant: str) -> int:
    """將母子音字母轉換為對應數字"""
    consonant_map = {
        'A': 1, 'J': 1, 'S': 1,
        'B': 2, 'K': 2, 'T': 2,
        'C': 3, 'L': 3, 'U': 3,
        'D': 4, 'M': 4, 'V': 4,
        'E': 5, 'N': 5, 'W': 5,
        'F': 6, 'O': 6, 'X': 6,
        'G': 7, 'P': 7, 'Y': 7,
        'H': 8, 'Q': 8, 'Z': 8,
        'I': 9, 'R': 9
    }
    return consonant_map.get(consonant.upper(), 0)


def compute_personality_number(english_name: str) -> int:
    """計算人格數：從英文名字的所有字母（母音+子音）累加至1-9"""
    letters = extract_all_letters(english_name)
    total = sum(consonant_to_number(letter) for letter in letters)
    return reduce_to_core_number(total)


def compute_expression_number(english_name: str) -> int:
    """計算表達數：從英文名字的所有字母（母音+子音）累加至1-9"""
    letters = extract_all_letters(english_name)
    total = sum(consonant_to_number(letter) for letter in letters)
    return reduce_to_core_number(total)


def compute_maturity_number(birthdate: str) -> int:
    """計算成熟數：核心生命靈數 + 生日數，縮減至 1-9"""
    # 計算核心生命靈數
    core_total = birthdate_to_digits_sum(birthdate)
    core_number = reduce_to_core_number(core_total)
    
    # 計算生日數
    birthday_number = compute_birthday_number(birthdate)
    
    # 成熟數 = 核心生命靈數 + 生日數
    maturity_total = core_number + birthday_number
    return reduce_to_core_number(maturity_total)


def extract_birth_year(birthdate: str) -> int:
    """從生日中提取年份"""
    s = normalize_birthdate(birthdate)
    try:
        dt = datetime.strptime(s, "%Y/%m/%d")
        return dt.year
    except ValueError:
        pass
    # Heuristic: first token is likely the year
    tokens = [t for t in s.split("/") if t]
    numeric_tokens = [t for t in tokens if t.isdigit()]
    if len(numeric_tokens) >= 1:
        first = numeric_tokens[0]
        if len(first) == 4:
            return int(first)
    # If the whole string is just digits like YYYYMMDD
    digits_only = re.sub(r"\D", "", s)
    if len(digits_only) >= 8:
        return int(digits_only[:4])
    # Ultimate fallback
    return 2000


def compute_challenge_number(birthdate: str) -> int:
    """
    計算挑戰數：出生日月日數字計算差值
    
    正確流程：
    1. 月先加到個位數（縮減到 1-9）
    2. 日先加到個位數（縮減到 1-9）
    3. 年先加到個位數（縮減到 1-9）
    4. A = 月個位數 - 日個位數
    5. B = 日個位數 - 年個位數
    6. 挑戰數 = |A - B|
    7. 如果挑戰數 = 0，則代表 9
    8. 如果挑戰數 > 9，縮減到個位數
    
    例如1：2002/11/16
    月 = 1+1 = 2
    日 = 1+6 = 7
    年 = 2+0+0+2 = 4
    A = 2 - 7 = -5
    B = 7 - 4 = 3
    挑戰數 = |-5 - 3| = 8
    
    例如2：1990/10/10
    月 = 1+0 = 1
    日 = 1+0 = 1
    年 = 1+9+9+0 = 19 -> 1+9 = 10 -> 1+0 = 1
    A = 1 - 1 = 0
    B = 1 - 1 = 0
    挑戰數 = |0 - 0| = 0 -> 特例：0 代表 9
    """
    # 提取年月日
    year = extract_birth_year(birthdate)
    month = extract_birth_month(birthdate)
    day = extract_birth_day(birthdate)
    
    # 計算年月日的數字和，並縮減到個位數（1-9）
    year_sum = sum(int(ch) for ch in str(year))
    year_reduced = reduce_to_core_number(year_sum)
    
    month_sum = sum(int(ch) for ch in str(month))
    month_reduced = reduce_to_core_number(month_sum)
    
    day_sum = sum(int(ch) for ch in str(day))
    day_reduced = reduce_to_core_number(day_sum)
    
    # A = 月個位數 - 日個位數
    a = month_reduced - day_reduced
    
    # B = 日個位數 - 年個位數
    b = day_reduced - year_reduced
    
    # 挑戰數 = |A - B|
    challenge = abs(a - b)
    
    # 特殊規則：如果結果是 0，代表 9
    if challenge == 0:
        return 9
    
    # 如果超過 9，縮減至 1-9
    return reduce_to_core_number(challenge)


def compute_karma_number(birthdate: str) -> int:
    """
    計算業力數：優先檢查年份，再檢查年月日總和
    
    規則：
    1. 先算年份數字加總，如果是 13、14、16、19，就是業力數（不再算年月日）
    2. 如果年份數字加總不是業力數，才算年月日加總
    3. 如果年月日加總是 13、14、16、19，就是業力數
    4. 如果都不是，返回 0（表示沒有業力數）
    
    業力數意義：
    - 13: 業力輪 - 需要學習轉化負面能量、克服困難
    - 14: 自由與責任 - 需要學習在自由與責任之間找到平衡
    - 16: 業力塔 - 需要在人際關係中學習放下我執
    - 19: 業力輪的另一種形式 - 需要學習與他人合作，同時保持自我
    - 0: 沒有明顯的業力數
    
    例如：
    - 1993/5/15 -> 年份: 1+9+9+3 = 22 (非業力數) -> 年月日: 1+9+9+3+5+1+5 = 33 (非業力數) -> 0
    - 1975/8/20 -> 年份: 1+9+7+5 = 22 (非業力數) -> 年月日: 1+9+7+5+8+2+0 = 32 (非業力數) -> 0
    - 假設某年份加總為 13，則直接返回 13，不再計算年月日
    """
    # 提取年份
    year = extract_birth_year(birthdate)
    
    # 計算年份數字加總
    year_digits = [int(ch) for ch in str(year)]
    year_sum = sum(year_digits)
    
    # 業力數列表
    karma_numbers = [13, 14, 16, 19]
    
    # 先檢查年份加總是否為業力數
    if year_sum in karma_numbers:
        return year_sum
    
    # 如果年份不是業力數，再計算年月日加總
    s = normalize_birthdate(birthdate)
    all_digits = [int(ch) for ch in re.findall(r"\d", s)]
    total = sum(all_digits)
    
    # 檢查年月日加總是否為業力數
    if total in karma_numbers:
        return total
    else:
        return 0  # 沒有業力數