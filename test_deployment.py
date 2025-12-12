"""
部署驗證測試腳本
完整測試已部署的 Cloud Run 服務的 3 個主要模組（Life Number, Angel Number, Divination）
每個模組測試免費版和付費版的完整流程
"""

import requests
import sys
import time
import json

# 部署的服務 URL - 請在運行前修改為實際的服務 URL
SERVICE_URL = "https://life-number-backend-354905615311.asia-east1.run.app"
# SERVICE_URL = "http://localhost:8080"


# 顏色輸出
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{message:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'=' * 70}{Colors.RESET}\n")


def print_step(message):
    print(f"{Colors.CYAN}➜ {message}{Colors.RESET}")


def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def print_info(message, indent=2):
    print(f"{' ' * indent}{Colors.CYAN}{message}{Colors.RESET}")


def run_flow(module_name, version, flow_steps):
    """
    執行完整的測試流程

    Args:
        module_name: 模組名稱 (Life Number, Angel Number, Divination)
        version: 版本 (free/paid)
        flow_steps: 測試步驟列表 [(步驟名稱, URL後綴, payload函數或字典), ...]

    Returns:
        bool: 測試是否通過
    """
    print_header(f"{module_name} - {version.upper()} 版本測試")
    session_id = None
    step_count = 0
    total_steps = len(flow_steps)
    previous_state = None

    for step_name, url_suffix, payload_func in flow_steps:
        step_count += 1
        print_step(f"[{step_count}/{total_steps}] {step_name}")

        url = f"{SERVICE_URL}{url_suffix}"

        # 準備 payload
        if callable(payload_func):
            payload = payload_func(session_id)
        else:
            payload = payload_func

        print_info(f"URL: {url_suffix}", 4)
        print_info(f"Payload keys: {list(payload.keys())}", 4)

        try:
            response = requests.post(url, json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()
                print_success(f"{step_name} - 成功")

                # 更新 session_id
                if "session_id" in data:
                    session_id = data["session_id"]
                    print_info(f"Session ID: {session_id[:20]}...", 4)

                # 🔥 顯示狀態變化（重點）
                if "state" in data:
                    current_state = data["state"]
                    if previous_state != current_state:
                        print_info(
                            f"State: {Colors.BOLD}{Colors.YELLOW}{previous_state or 'N/A'}{Colors.RESET} → {Colors.BOLD}{Colors.GREEN}{current_state}{Colors.RESET}",
                            4,
                        )
                        previous_state = current_state
                    else:
                        print_info(
                            f"State: {Colors.BOLD}{current_state}{Colors.RESET} (未變)",
                            4,
                        )

                # 檢查回應內容
                if "response" in data:
                    resp_len = len(data["response"])
                    print_info(f"回應長度: {resp_len} 字", 4)
                    if resp_len > 0:
                        # 顯示回應的前100字
                        preview = data["response"][:100].replace("\n", " ")
                        print_info(f"內容預覽: {preview}...", 4)
                    else:
                        print_warning("回應內容為空")

                # 檢查特定欄位
                if "number" in data:
                    print_info(f"計算結果: {data['number']}", 4)
                if "angel_number" in data:
                    print_info(f"天使數字: {data['angel_number']}", 4)
                if "divination_result" in data:
                    print_info(f"占卜結果: {data['divination_result']}", 4)
                if "divination_results" in data:
                    print_info(f"三次擲筊: {data['divination_results']}", 4)

                time.sleep(0.5)  # 避免請求過快

            else:
                print_error(f"{step_name} - 失敗 (HTTP {response.status_code})")
                print_info(f"錯誤訊息: {response.text[:300]}", 4)
                return False

        except requests.exceptions.Timeout:
            print_error(f"{step_name} - 請求超時")
            return False
        except requests.exceptions.ConnectionError:
            print_error(f"{step_name} - 無法連接服務")
            return False
        except Exception as e:
            print_error(f"{step_name} - 發生錯誤: {str(e)}")
            return False

    print(
        f"\n{Colors.BOLD}{Colors.GREEN}✨ {module_name} ({version}) 完整流程測試通過 ✨{Colors.RESET}\n"
    )
    return True


def test_health_check():
    """測試健康檢查端點"""
    print_header("健康檢查")
    try:
        resp = requests.get(f"{SERVICE_URL}/health", timeout=10)
        if resp.status_code == 200:
            print_success("服務健康狀態正常")
            data = resp.json()
            print_info(f"回應: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print_error(f"健康檢查失敗 (HTTP {resp.status_code})")
            return False
    except Exception as e:
        print_error(f"無法連接服務: {e}")
        return False


def test_home_page():
    """測試首頁"""
    print_header("首頁測試")
    try:
        resp = requests.get(f"{SERVICE_URL}/", timeout=10)
        if resp.status_code == 200:
            print_success("首頁訪問成功")
            data = resp.json()
            print_info(f"模組狀態:")
            for module, status in data.get("modules", {}).items():
                status_icon = "✓" if status else "✗"
                print_info(f"  {status_icon} {module}: {status}", 4)
            return True
        else:
            print_error(f"首頁訪問失敗 (HTTP {resp.status_code})")
            return False
    except Exception as e:
        print_error(f"首頁訪問錯誤: {e}")
        return False


def main():
    """主測試函數"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}")
    print(f"{'🚀 Life Number Backend - 完整部署測試 🚀':^70}")
    print(f"{'=' * 70}{Colors.RESET}\n")
    print(f"{Colors.YELLOW}測試服務: {SERVICE_URL}{Colors.RESET}\n")

    results = []

    # 0. 預備檢查
    if not test_health_check():
        print_error("健康檢查失敗，終止測試")
        sys.exit(1)

    if not test_home_page():
        print_warning("首頁測試失敗，但繼續執行其他測試")

    # ==========================================
    # 1. 生命靈數 (Life Number)
    # ==========================================

    # 1.1 免費版
    results.append(
        (
            "Life Number Free",
            run_flow(
                "生命靈數",
                "free",
                [
                    (
                        "初始化會話",
                        "/life/free/api/init_with_tone",
                        {"tone": "caring"},
                    ),
                    (
                        "提交基本資訊",
                        "/life/free/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "賴冠儒 男 2002/11/28",
                        },
                    ),
                    (
                        "選擇挑戰數模組",
                        "/life/free/api/chat",
                        lambda sid: {"session_id": sid, "message": "challenge"},
                    ),
                    (
                        "離開",
                        "/life/free/api/chat",
                        lambda sid: {"session_id": sid, "message": "離開"},
                    ),
                ],
            ),
        )
    )

    # 1.2 付費版 - 完整流程（包含類別選擇和深度提問）
    results.append(
        (
            "Life Number Paid",
            run_flow(
                "生命靈數",
                "paid",
                [
                    (
                        "初始化會話",
                        "/life/paid/api/init_with_tone",
                        {"tone": "metatron"},
                    ),
                    (
                        "提交基本資訊（含英文名）",
                        "/life/paid/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "李大華 男 1985/05/05 LEE DA HUA",
                        },
                    ),
                    (
                        "選擇核心模組",
                        "/life/paid/api/chat",
                        lambda sid: {"session_id": sid, "message": "core"},
                    ),
                    (
                        "選擇類別-財運事業",
                        "/life/paid/api/chat",
                        lambda sid: {"session_id": sid, "message": "財運事業"},
                    ),
                    (
                        "提出具體問題",
                        "/life/paid/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "我適合創業還是上班？",
                        },
                    ),
                    (
                        "繼續問問題",
                        "/life/paid/api/chat",
                        lambda sid: {"session_id": sid, "message": "繼續問問題"},
                    ),
                    (
                        "深度提問",
                        "/life/paid/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "創業的時機應該怎麼選擇？",
                        },
                    ),
                    (
                        "離開",
                        "/life/paid/api/chat",
                        lambda sid: {"session_id": sid, "message": "離開"},
                    ),
                ],
            ),
        )
    )

    # ==========================================
    # 2. 天使數字 (Angel Number)
    # ==========================================

    # 2.1 免費版
    results.append(
        (
            "Angel Number Free",
            run_flow(
                "天使數字",
                "free",
                [
                    (
                        "初始化會話",
                        "/angel/free/api/init_with_tone",
                        {"tone": "caring"},
                    ),
                    (
                        "提交基本資訊",
                        "/angel/free/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "張小美 女 2000/03/15",
                        },
                    ),
                    (
                        "選擇天使數字",
                        "/angel/free/api/chat",
                        lambda sid: {"session_id": sid, "message": "1111"},
                    ),
                ],
            ),
        )
    )

    # 2.2 付費版 - 包含持續對話
    results.append(
        (
            "Angel Number Paid",
            run_flow(
                "天使數字",
                "paid",
                [
                    (
                        "初始化會話",
                        "/angel/paid/api/init_with_tone",
                        {"tone": "michael"},
                    ),
                    (
                        "提交基本資訊",
                        "/angel/paid/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "Alice 女 1995/12/25",
                        },
                    ),
                    (
                        "輸入天使數字",
                        "/angel/paid/api/chat",
                        lambda sid: {"session_id": sid, "message": "4444"},
                    ),
                    (
                        "提出問題",
                        "/angel/paid/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "這個數字對我的感情有什麼啟示？",
                        },
                    ),
                    (
                        "繼續提問",
                        "/angel/paid/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "那我應該主動還是被動？",
                        },
                    ),
                    (
                        "結束對話",
                        "/angel/paid/api/chat",
                        lambda sid: {"session_id": sid, "message": "謝謝"},
                    ),
                ],
            ),
        )
    )

    # ==========================================
    # 3. 神諭占卜 (Divination)
    # ==========================================

    # 3.1 免費版 - 單次擲筊
    results.append(
        (
            "Divination Free",
            run_flow(
                "神諭占卜",
                "free",
                [
                    (
                        "初始化會話",
                        "/divination/free/api/init_with_tone",
                        {"tone": "ritual"},
                    ),
                    (
                        "提交基本資訊",
                        "/divination/free/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "王小明 男 1990/07/12",
                        },
                    ),
                    (
                        "提交問題",
                        "/divination/free/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "我最近應該換工作嗎？",
                        },
                    ),
                    (
                        "執行擲筊",
                        "/divination/free/api/chat",
                        lambda sid: {"session_id": sid, "message": "擲筊"},
                    ),
                ],
            ),
        )
    )

    # 3.2 付費版 - 三次擲筊 + 持續提問
    results.append(
        (
            "Divination Paid",
            run_flow(
                "神諭占卜",
                "paid",
                [
                    (
                        "初始化會話",
                        "/divination/paid/api/init_with_tone",
                        {"tone": "yue_lao"},
                    ),
                    (
                        "提交基本資訊",
                        "/divination/paid/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "李四 女 1988/09/20",
                        },
                    ),
                    (
                        "提交問題",
                        "/divination/paid/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "我和男友的感情會有結果嗎？",
                        },
                    ),
                    (
                        "執行擲筊（三次）",
                        "/divination/paid/api/chat",
                        lambda sid: {"session_id": sid, "message": "擲筊"},
                    ),
                    (
                        "追問",
                        "/divination/paid/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "那我應該主動還是等待？",
                        },
                    ),
                    (
                        "結束",
                        "/divination/paid/api/chat",
                        lambda sid: {"session_id": sid, "message": "謝謝，沒有問題了"},
                    ),
                ],
            ),
        )
    )

    # ==========================================
    # 4. 黃道吉日 (Auspicious Date)
    # ==========================================

    # 4.1 免費版 - 完整流程
    results.append(
        (
            "Auspicious Date Free",
            run_flow(
                "黃道吉日",
                "free",
                [
                    (
                        "初始化會話",
                        "/auspicious/free/api/init_with_tone",
                        {"tone": "friendly"},
                    ),
                    (
                        "提交基本資訊",
                        "/auspicious/free/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "汪大東 男 1995/10/10 屬馬",
                        },
                    ),
                    (
                        "選擇分類和日期",
                        "/auspicious/free/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "category": "family_home",
                            "selected_date": "2025-12-11",
                        },
                    ),
                    (
                        "描述事項",
                        "/auspicious/free/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "我要結婚，想知道這天好不好",
                        },
                    ),
                ],
            ),
        )
    )

    # 4.2 付費版 - 包含持續對話
    results.append(
        (
            "Auspicious Date Paid",
            run_flow(
                "黃道吉日",
                "paid",
                [
                    (
                        "初始化會話",
                        "/auspicious/paid/api/init_with_tone",
                        {"tone": "yue_lao"},
                    ),
                    (
                        "提交基本資訊",
                        "/auspicious/paid/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "李小美 女 1995/05/20 屬豬",
                        },
                    ),
                    (
                        "選擇分類和日期",
                        "/auspicious/paid/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "category": "relationship",
                            "selected_date": "2025-12-25",
                        },
                    ),
                    (
                        "描述事項",
                        "/auspicious/paid/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "我想訂婚，想知道這天適合嗎",
                        },
                    ),
                    (
                        "追問",
                        "/auspicious/paid/api/chat",
                        lambda sid: {
                            "session_id": sid,
                            "message": "那有什麼需要特別注意的嗎？",
                        },
                    ),
                    (
                        "結束對話",
                        "/auspicious/paid/api/chat",
                        lambda sid: {"session_id": sid, "message": "謝謝月老"},
                    ),
                ],
            ),
        )
    )

    # ==========================================
    # 測試結果統計
    # ==========================================
    print_header("測試結果統計")

    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed

    print(f"{Colors.BOLD}總測試數: {len(results)}{Colors.RESET}")
    print(f"{Colors.GREEN}✓ 通過: {passed}{Colors.RESET}")
    print(f"{Colors.RED}✗ 失敗: {failed}{Colors.RESET}\n")

    print(f"{Colors.BOLD}詳細結果:{Colors.RESET}")
    for name, result in results:
        status = (
            f"{Colors.GREEN}✓ PASS{Colors.RESET}"
            if result
            else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        )
        print(f"  {status} - {name}")

    print(f"\n{'=' * 70}\n")

    if failed == 0:
        print(
            f"{Colors.BOLD}{Colors.GREEN}🎉 恭喜！所有測試都通過了！ 🎉{Colors.RESET}\n"
        )
        return 0
    else:
        print(
            f"{Colors.BOLD}{Colors.RED}⚠️  有 {failed} 個測試失敗，請檢查服務狀態 ⚠️{Colors.RESET}\n"
        )
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}測試被用戶中斷{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}測試執行時發生嚴重錯誤: {e}{Colors.RESET}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
