"""
擲筊模組基礎數據
定義筊杯結果和解讀模板
"""

# 筊杯結果類型
DIVINATION_RESULTS = {
    "holy": {
        "name": "聖筊",
        "symbol": "⚪⚪",
        "meaning": "神明同意，可行",
        "description": "一正一反，陰陽和合，神明應允"
    },
    "laughing": {
        "name": "笑筊",
        "symbol": "⚪⚫",
        "meaning": "再問清楚，或時機未到",
        "description": "兩筊皆正面，神明含笑，需再思量"
    },
    "negative": {
        "name": "陰筊",
        "symbol": "⚫⚫",
        "meaning": "不宜行動，需重新考慮",
        "description": "兩筊皆反面，神明不允，應當慎行"
    }
}

# 解讀提示模板
INTERPRETATION_TEMPLATES = {
    "holy": "恭喜！獲得聖筊 ⚪⚪\n神明應允了您的祈求。",
    "laughing": "得到笑筊 ⚪⚫\n神明示意需要再詳細思考。",
    "negative": "得到陰筊 ⚫⚫\n神明提醒您需要慎重考慮。"
}
