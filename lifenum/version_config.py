# 版本配置文件 - 所有免費版和付費版的差異都在這裡

VERSION_CONFIG = {
    'free': {
        # 可用模組（4個）
        'available_modules': ['core', 'birthday', 'year', 'grid'],
        
        # 可用語氣（3個）
        'available_tones': ['friendly', 'caring', 'ritual'],
        
        # 功能開關
        'enable_continuous_chat': False,  # 免費版不支持深度提問
        'enable_category_selection': False,  # 免費版 core 無類別選擇
        'require_english_name': False,  # 免費版不需要英文名
        
        # 模組說明
        'module_descriptions': {
            'core': '核心天賦人生方向',
            'birthday': '天生才華',
            'year': '年度運勢與連線',
            'grid': '天賦優勢與在職特質及缺的特質 九宮格'
        }
    },
    
    'paid': {
        # 可用模組（10個）
        'available_modules': [
            'core', 'birthday', 'year', 'grid',
            'soul', 'personality', 'expression', 
            'maturity', 'challenge', 'karma'
        ],
        
        # 可用語氣（10個）
        'available_tones': [
            'guan_yu', 'michael', 'gabriel', 'raphael', 'uriel',
            'zadkiel', 'jophiel', 'chamuel', 'metatron', 'ariel'
        ],
        
        # 功能開關
        'enable_continuous_chat': True,  # 付費版支持深度提問
        'enable_category_selection': True,  # 付費版 core 有類別選擇
        'require_english_name': True,  # 付費版部分模組需要英文名
        
        # 模組說明
        'module_descriptions': {
            'core': '核心天賦人生方向',
            'birthday': '天生才華',
            'year': '年度運勢與連線',
            'grid': '天賦優勢與在職特質 九宮格',
            'soul': '靈魂數 - 內心真正的渴望',
            'personality': '人格數 - 外在展現的形象',
            'expression': '表達數 - 溝通與表達方式',
            'maturity': '成熟數 - 中年後的發展',
            'challenge': '挑戰數 - 需要克服的課題',
            'karma': '業力數 - 前世今生的因果'
        }
    }
}

def get_config(version: str) -> dict:
    """獲取指定版本的配置"""
    return VERSION_CONFIG.get(version, VERSION_CONFIG['free'])
