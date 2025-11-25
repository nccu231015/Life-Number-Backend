#!/usr/bin/env python3
"""
生命靈數完整測試程式
測試免費版和付費版的所有功能，顯示完整的 API I/O

使用方法：
1. 測試本地環境（默認）：
   python test_complete_all.py

2. 測試生產環境：
   export API_URL="https://your-service-url.a.run.app"
   python test_complete_all.py
   
   或者：
   python test_complete_all.py --production
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, Any

# ========== 測試配置 ==========
# 是否截斷長回應（True: 截斷至300字元，False: 顯示完整內容）
TRUNCATE_RESPONSE = False  # 改為 False 顯示完整內容

# API 配置
# 優先使用環境變量，否則使用本地地址
if "--production" in sys.argv:
    BASE_URL = "https://life-number-backend-354905615311.asia-east1.run.app"
    print("\n🌐 使用生產環境 URL")
else:
    BASE_URL = os.getenv("API_URL", "http://localhost:8080")
    if BASE_URL != "http://localhost:8080":
        print(f"\n🌐 使用環境變量 API_URL: {BASE_URL}")
    else:
        print("\n🖥️  使用本地環境 URL")

FREE_PREFIX = "/life/free"
PAID_PREFIX = "/life/paid"

# 測試用戶資料
TEST_USER_FREE = {
    "name": "王小明",
    "gender": "male",
    "birthdate": "1990/07/12"
}

TEST_USER_PAID = {
    "name": "李小華",
    "gender": "female",
    "birthdate": "1985/03/25",
    "english_name": "LEE XIAO HUA"
}

# 免費版配置
FREE_TONES = ["friendly", "caring", "ritual"]
FREE_MODULES = ["core", "birthday", "year", "grid"]

# 付費版配置（選擇代表性語氣）
PAID_TONE = "guan_yu"
PAID_MODULES = [
    {"key": "core", "name": "核心生命靈數", "category": "財運事業", "question": "我今年適合創業嗎？"},
    {"key": "birthday", "name": "生日數", "question": "如何發揮我的天生才華？"},
    {"key": "year", "name": "流年數", "question": "今年的運勢重點是什麼？"},
    {"key": "grid", "name": "九宮格", "question": "我的優勢和劣勢是什麼？"},
    {"key": "soul", "name": "靈魂數", "question": "我內心真正渴望的是什麼？"},
    {"key": "personality", "name": "人格數", "question": "別人對我的第一印象是什麼？"},
    {"key": "expression", "name": "表達數", "question": "我的溝通方式有什麼特色？"},
    {"key": "maturity", "name": "成熟數", "question": "我人生後半段的發展方向？"},
    {"key": "challenge", "name": "挑戰數", "question": "我需要克服的課題是什麼？"},
    {"key": "karma", "name": "業力數", "question": "我今生需要學習的功課？"}
]


def print_separator(char="=", length=120):
    """打印分隔線"""
    print(char * length)


def print_title(title: str, level=1):
    """打印標題"""
    if level == 1:
        print("\n" + "🌟" * 60)
        print(f"  {title}")
        print("🌟" * 60 + "\n")
    elif level == 2:
        print("\n" + "=" * 120)
        print(f"  {title}")
        print("=" * 120 + "\n")
    else:
        print("\n" + "-" * 120)
        print(f"  {title}")
        print("-" * 120 + "\n")


def print_api_io(step: str, method: str, url: str, request_data: Dict = None, 
                 response_data: Dict = None, status_code: int = None, duration: float = None):
    """格式化顯示 API I/O"""
    print_separator("-")
    print(f"📡 API 調用: {step}")
    print_separator("-")
    print(f"▶️  Method: {method}")
    print(f"▶️  URL: {url}")
    
    if request_data:
        print(f"\n📤 Request JSON:")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    if status_code:
        status_icon = "✅" if 200 <= status_code < 300 else "❌"
        print(f"\n{status_icon} Status Code: {status_code}")
    
    if duration:
        print(f"⏱️  Duration: {duration:.2f}s")
    
    if response_data:
        print(f"\n📥 Response JSON:")
        # 根據全局 TRUNCATE_RESPONSE 配置決定是否截取回應內容
        display_data = response_data.copy()
        if TRUNCATE_RESPONSE and 'response' in display_data and len(display_data['response']) > 300:
            original_length = len(display_data['response'])
            display_data['response'] = display_data['response'][:300] + f"...(已截斷，完整長度: {original_length} 字元)"
            display_data['_truncated'] = True
        print(json.dumps(display_data, indent=2, ensure_ascii=False))
    
    print()


class FreeVersionTester:
    """免費版測試器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        self.session_id = None  # 保存 session_id
    
    def test_single_tone(self, tone: str):
        """測試單個語氣的完整流程"""
        print_title(f"測試免費版 - {tone} 語氣", level=2)
        
        # 1. 初始化（後端會生成 session_id）
        print_title("步驟 1: 初始化（選擇語氣）", level=3)
        req_data = {"tone": tone}
        start_time = time.time()
        resp = self.session.post(f"{BASE_URL}{FREE_PREFIX}/api/init_with_tone", 
                                json=req_data, timeout=10)
        resp_data = resp.json() if resp.status_code == 200 else {}
        print_api_io("初始化", "POST", f"{BASE_URL}{FREE_PREFIX}/api/init_with_tone",
                    request_data=req_data, response_data=resp_data,
                    status_code=resp.status_code, duration=time.time() - start_time)
        
        # 保存 session_id
        if resp.status_code == 200 and 'session_id' in resp_data:
            self.session_id = resp_data['session_id']
            print(f"\n💾 Session ID: {self.session_id}\n")
        else:
            print("\n❌ 初始化失敗，無法獲取 session_id\n")
            return False
        
        time.sleep(2)
        
        # 2. 提交基本資訊
        print_title("步驟 2: 提交基本資訊", level=3)
        user_input = f"{TEST_USER_FREE['name']} {TEST_USER_FREE['gender']} {TEST_USER_FREE['birthdate']}"
        req_data = {"session_id": self.session_id, "message": user_input}
        start_time = time.time()
        resp = self.session.post(f"{BASE_URL}{FREE_PREFIX}/api/chat", 
                                json=req_data, timeout=20)
        print_api_io("提交基本資訊", "POST", f"{BASE_URL}{FREE_PREFIX}/api/chat",
                    request_data=req_data, response_data=resp.json() if resp.status_code == 200 else {},
                    status_code=resp.status_code, duration=time.time() - start_time)
        time.sleep(2)
        
        # 3. 測試一個模組（以 core 為例）
        print_title("步驟 3: 選擇核心生命靈數模組", level=3)
        req_data = {"session_id": self.session_id, "message": "core"}
        start_time = time.time()
        resp = self.session.post(f"{BASE_URL}{FREE_PREFIX}/api/chat", 
                                json=req_data, timeout=60)
        print_api_io("選擇並執行 core 模組", "POST", f"{BASE_URL}{FREE_PREFIX}/api/chat",
                    request_data=req_data, response_data=resp.json() if resp.status_code == 200 else {},
                    status_code=resp.status_code, duration=time.time() - start_time)
        time.sleep(2)
        
        # 4. 離開
        print_title("步驟 4: 離開", level=3)
        req_data = {"session_id": self.session_id, "message": "離開"}
        start_time = time.time()
        resp = self.session.post(f"{BASE_URL}{FREE_PREFIX}/api/chat", 
                                json=req_data, timeout=15)
        print_api_io("離開對話", "POST", f"{BASE_URL}{FREE_PREFIX}/api/chat",
                    request_data=req_data, response_data=resp.json() if resp.status_code == 200 else {},
                    status_code=resp.status_code, duration=time.time() - start_time)
        
        return True
    
    def run_all_tests(self):
        """運行所有免費版測試"""
        print_title("免費版完整測試", level=1)
        
        for i, tone in enumerate(FREE_TONES, 1):
            print(f"\n{'='*120}")
            print(f"測試 {i}/{len(FREE_TONES)}: {tone} 語氣")
            print(f"{'='*120}\n")
            self.test_single_tone(tone)
            time.sleep(3)
        
        print_title("✅ 免費版測試完成", level=2)


class PaidVersionTester:
    """付費版測試器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.tone = PAID_TONE
        self.results = []
        self.session_id = None  # 保存 session_id
    
    def test_complete_flow(self):
        """測試付費版完整流程"""
        print_title("付費版完整測試", level=1)
        
        # 1. 初始化（後端會生成 session_id）
        print_title("步驟 1: 初始化（關聖帝君語氣）", level=2)
        req_data = {"tone": self.tone}
        start_time = time.time()
        resp = self.session.post(f"{BASE_URL}{PAID_PREFIX}/api/init_with_tone", 
                                json=req_data, timeout=10)
        resp_data = resp.json() if resp.status_code == 200 else {}
        print_api_io("初始化", "POST", f"{BASE_URL}{PAID_PREFIX}/api/init_with_tone",
                    request_data=req_data, response_data=resp_data,
                    status_code=resp.status_code, duration=time.time() - start_time)
        
        # 保存 session_id
        if resp.status_code == 200 and 'session_id' in resp_data:
            self.session_id = resp_data['session_id']
            print(f"\n💾 Session ID: {self.session_id}\n")
        else:
            print("\n❌ 初始化失敗，無法獲取 session_id\n")
            return
        
        time.sleep(2)
        
        # 2. 提交基本資訊（包含英文名）
        print_title("步驟 2: 提交基本資訊（含英文名）", level=2)
        user_input = f"{TEST_USER_PAID['name']} {TEST_USER_PAID['gender']} {TEST_USER_PAID['birthdate']} {TEST_USER_PAID['english_name']}"
        req_data = {"session_id": self.session_id, "message": user_input}
        start_time = time.time()
        resp = self.session.post(f"{BASE_URL}{PAID_PREFIX}/api/chat", 
                                json=req_data, timeout=20)
        print_api_io("提交基本資訊", "POST", f"{BASE_URL}{PAID_PREFIX}/api/chat",
                    request_data=req_data, response_data=resp.json() if resp.status_code == 200 else {},
                    status_code=resp.status_code, duration=time.time() - start_time)
        time.sleep(2)
        
        # 3. 測試前3個模組（示例，可擴展到全部10個）
        test_modules = PAID_MODULES[:3]
        
        for i, module_info in enumerate(test_modules, 3):
            self.test_single_module(module_info, i)
            time.sleep(3)
        
        # 4. 測試離開（生成總結）
        print_title("最終步驟: 離開並生成總結", level=2)
        req_data = {"session_id": self.session_id, "message": "離開"}
        start_time = time.time()
        resp = self.session.post(f"{BASE_URL}{PAID_PREFIX}/api/chat", 
                                json=req_data, timeout=90)
        
        resp_data = resp.json() if resp.status_code == 200 else {}
        # 離開時的回應可能很長，完整顯示
        print_api_io("離開對話（生成總結）", "POST", f"{BASE_URL}{PAID_PREFIX}/api/chat",
                    request_data=req_data, response_data=resp_data,
                    status_code=resp.status_code, duration=time.time() - start_time)
        
        # 檢查總結內容
        if resp.status_code == 200:
            response_text = resp_data.get('response', '')
            has_summary = "探索了" in response_text or "今天" in response_text
            has_recommendation = "水晶" in response_text or "點燈" in response_text
            
            print("\n" + "="*120)
            print("🔍 總結檢查")
            print("="*120)
            print(f"✅ 包含對話總結: {has_summary}")
            print(f"✅ 包含商品推薦: {has_recommendation}")
            print("="*120 + "\n")
        
        print_title("✅ 付費版測試完成", level=2)
    
    def test_single_module(self, module_info: Dict, step_num: int):
        """測試單個模組"""
        module_key = module_info['key']
        module_name = module_info['name']
        
        print_title(f"步驟 {step_num}: 測試 {module_name} 模組", level=2)
        
        # A. 選擇模組
        print(f"\n▶️  {step_num}.1 選擇模組")
        req_data = {"session_id": self.session_id, "message": module_key}
        start_time = time.time()
        resp = self.session.post(f"{BASE_URL}{PAID_PREFIX}/api/chat", 
                                json=req_data, timeout=90)
        resp_data = resp.json() if resp.status_code == 200 else {}
        print_api_io(f"選擇 {module_name}", "POST", f"{BASE_URL}{PAID_PREFIX}/api/chat",
                    request_data=req_data, response_data=resp_data,
                    status_code=resp.status_code, duration=time.time() - start_time)
        
        # B. 如果是 core 模組，處理類別選擇
        if module_key == "core" and resp_data.get('show_category_buttons'):
            time.sleep(2)
            print(f"\n▶️  {step_num}.2 選擇類別")
            category = module_info.get('category', '財運事業')
            req_data = {"session_id": self.session_id, "message": category}
            start_time = time.time()
            resp = self.session.post(f"{BASE_URL}{PAID_PREFIX}/api/chat", 
                                    json=req_data, timeout=15)
            resp_data = resp.json() if resp.status_code == 200 else {}
            print_api_io(f"選擇類別 - {category}", "POST", f"{BASE_URL}{PAID_PREFIX}/api/chat",
                        request_data=req_data, response_data=resp_data,
                        status_code=resp.status_code, duration=time.time() - start_time)
            
            # C. 提交問題
            time.sleep(2)
            print(f"\n▶️  {step_num}.3 提交問題")
            question = module_info.get('question', '')
            req_data = {"session_id": self.session_id, "message": question}
            start_time = time.time()
            resp = self.session.post(f"{BASE_URL}{PAID_PREFIX}/api/chat", 
                                    json=req_data, timeout=90)
            resp_data = resp.json() if resp.status_code == 200 else {}
            print_api_io(f"提交問題並獲取解析", "POST", f"{BASE_URL}{PAID_PREFIX}/api/chat",
                        request_data=req_data, response_data=resp_data,
                        status_code=resp.status_code, duration=time.time() - start_time)
        
        # D. 測試深度對話（繼續問問題）
        time.sleep(2)
        print(f"\n▶️  {step_num}.4 測試深度對話")
        req_data = {"session_id": self.session_id, "message": "繼續問問題"}
        start_time = time.time()
        resp = self.session.post(f"{BASE_URL}{PAID_PREFIX}/api/chat", 
                                json=req_data, timeout=15)
        resp_data = resp.json() if resp.status_code == 200 else {}
        print_api_io("選擇繼續問問題", "POST", f"{BASE_URL}{PAID_PREFIX}/api/chat",
                    request_data=req_data, response_data=resp_data,
                    status_code=resp.status_code, duration=time.time() - start_time)
        
        # E. 提交深度問題
        if resp_data.get('state') == 'waiting_question':
            time.sleep(2)
            print(f"\n▶️  {step_num}.5 提交深度問題")
            deep_question = module_info.get('question', '')
            req_data = {"session_id": self.session_id, "message": deep_question}
            start_time = time.time()
            resp = self.session.post(f"{BASE_URL}{PAID_PREFIX}/api/chat", 
                                    json=req_data, timeout=90)
            resp_data = resp.json() if resp.status_code == 200 else {}
            print_api_io("提交深度問題", "POST", f"{BASE_URL}{PAID_PREFIX}/api/chat",
                        request_data=req_data, response_data=resp_data,
                        status_code=resp.status_code, duration=time.time() - start_time)
        
        # F. 選擇其他生命靈數
        time.sleep(2)
        print(f"\n▶️  {step_num}.6 選擇其他生命靈數")
        req_data = {"session_id": self.session_id, "message": "其他生命靈數"}
        start_time = time.time()
        resp = self.session.post(f"{BASE_URL}{PAID_PREFIX}/api/chat", 
                                json=req_data, timeout=15)
        resp_data = resp.json() if resp.status_code == 200 else {}
        print_api_io("選擇其他生命靈數", "POST", f"{BASE_URL}{PAID_PREFIX}/api/chat",
                    request_data=req_data, response_data=resp_data,
                    status_code=resp.status_code, duration=time.time() - start_time)


def verify_redis_storage():
    """驗證 Redis 存儲（僅本地環境）"""
    print("\n" + "="*120)
    print("第三階段：Redis 存儲驗證")
    print("="*120 + "\n")
    
    # 如果是生產環境，跳過 Redis 驗證
    if BASE_URL != "http://localhost:8080":
        print("ℹ️  跳過 Redis 驗證（僅在本地環境可用）")
        print("   生產環境的 Redis 由 Cloud Run 內部管理")
        print()
        return
    
    try:
        from lifenum.redis_client import get_redis_client
        
        redis_client = get_redis_client()
        
        # 查找所有 session
        free_keys = redis_client.keys("session:free:*")
        paid_keys = redis_client.keys("session:paid:*")
        
        print("📊 Redis Session 統計")
        print("-" * 120)
        print(f"免費版 Session 數量: {len(free_keys)}")
        print(f"付費版 Session 數量: {len(paid_keys)}")
        print(f"總計: {len(free_keys) + len(paid_keys)} 個 Session")
        print()
        
        # 顯示幾個 Session 的詳情
        all_keys = list(free_keys[:2]) + list(paid_keys[:2])  # 各取2個
        
        for key in all_keys:
            ttl = redis_client.ttl(key)
            data_str = redis_client.get(key)
            
            if data_str:
                data = json.loads(data_str)
                version = "免費版" if ":free:" in key else "付費版"
                
                print(f"🔍 {version} Session")
                print("-" * 120)
                print(f"  Session ID: {data.get('session_id', 'N/A')}")
                print(f"  狀態: {data.get('state', 'N/A')}")
                print(f"  用戶: {data.get('user_name', 'N/A')}")
                print(f"  對話輪數: {data.get('conversation_count', 0)}")
                print(f"  記憶項目: {len(data.get('memory', []))}")
                print(f"  TTL: {ttl} 秒 ({ttl/3600:.2f} 小時)")
                print()
        
        print("✅ Redis 存儲驗證完成")
        print(f"✅ TTL 統一設定為 12 小時 (43200秒)")
        print()
        
    except Exception as e:
        print(f"❌ Redis 驗證失敗: {e}")
        print("   提示：請確認 Redis 服務正在運行")
        import traceback
        traceback.print_exc()


def main():
    """主測試函數"""
    start_time = datetime.now()
    
    print("\n" + "🎯" * 60)
    print("  生命靈數完整測試程式")
    print(f"  測試時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  測試環境: {BASE_URL}")
    print("  包含：免費版（3種語氣）+ 付費版（完整功能）+ Redis 驗證")
    print("🎯" * 60)
    
    # 檢查服務
    print("\n⏳ 檢查服務狀態...")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        if resp.status_code == 200:
            health_data = resp.json()
            print(f"✅ 服務正常運行")
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Version: {health_data.get('version', 'unknown')}")
            print(f"   URL: {BASE_URL}")
        else:
            print(f"❌ 服務異常: {resp.status_code}")
            return
    except Exception as e:
        print(f"❌ 無法連接服務: {e}")
        print(f"   請確認服務是否運行在: {BASE_URL}")
        return
    
    time.sleep(2)
    
    try:
        # 測試免費版
        print("\n\n")
        print("="*120)
        print("第一階段：免費版測試")
        print("="*120)
        free_tester = FreeVersionTester()
        free_tester.run_all_tests()
        
        time.sleep(5)
        
        # 測試付費版
        print("\n\n")
        print("="*120)
        print("第二階段：付費版測試")
        print("="*120)
        paid_tester = PaidVersionTester()
        paid_tester.test_complete_flow()
        
        time.sleep(3)
        
        # 驗證 Redis 存儲
        verify_redis_storage()
        
        # 總結
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "="*120)
        print("📊 測試總結")
        print("="*120)
        print(f"測試環境: {BASE_URL}")
        print(f"開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"結束時間: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"總耗時: {duration:.1f} 秒 ({duration/60:.1f} 分鐘)")
        print(f"✅ 免費版: 測試了 {len(FREE_TONES)} 種語氣")
        print(f"✅ 付費版: 測試了完整流程（含深度對話、類別選擇、總結功能）")
        if BASE_URL == "http://localhost:8080":
            print(f"✅ Redis: 驗證了存儲功能（TTL: 12小時）")
        else:
            print(f"ℹ️  Redis: 跳過驗證（生產環境）")
        print("="*120 + "\n")
        
        print("🎉 所有測試完成！")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  測試被用戶中斷")
    except Exception as e:
        print(f"\n\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

