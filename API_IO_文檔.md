# 生命靈數 API I/O 規格文檔

> 📡 **部署狀態**: 可部署至 GCP Cloud Run  
> 🔐 **安全性**: HTTPS + Secret Manager  
> 💾 **Session 存儲**: Redis (12小時 TTL)  
> 🌍 **區域**: Asia East 1 (台灣)

---

## 🚀 快速開始

### 步驟 1：取得 API URL
部署完成後，執行以下指令取得服務 URL：
```bash
gcloud run services describe life-number-backend \
  --region=asia-east1 \
  --format='value(status.url)'
```

### 步驟 2：測試健康檢查
```bash
curl https://your-service-url.a.run.app/health
```

### 步驟 3：初始化 Session
```bash
curl -X POST https://your-service-url.a.run.app/life/free/api/init_with_tone \
  -H "Content-Type: application/json" \
  -d '{"tone": "friendly"}'
```

### 步驟 4：開始對話
使用返回的 `session_id` 進行後續對話。

---

## 📋 總體設計原則

### 統一的 Session 管理機制
1. **後端生成 `session_id`**：所有版本（免費/付費）都由後端在 `init_with_tone` 時生成唯一的 `session_id`
2. **前端保存並傳遞**：前端收到 `session_id` 後保存，之後所有請求都必須帶上這個 `session_id`
3. **無需區分用戶類型**：不需要 `user_id`，所有用戶統一使用 `session_id` 機制
4. **自動過期**：Session 在 12 小時後自動過期（Redis TTL）

### 技術架構
- **後端框架**: Flask + Gunicorn
- **AI 引擎**: OpenAI GPT-4o
- **Session 存儲**: Redis Cloud
- **部署平台**: GCP Cloud Run
- **容器化**: Docker

---

## 🔌 API 端點

### 基礎 URL

#### 🌐 生產環境（GCP Cloud Run）
部署後，您的 API 將運行在 GCP Cloud Run 上：
```
https://life-number-backend-<hash>-<region-code>.a.run.app
```

> 📝 **注意**：部署完成後，Cloud Run 會提供完整的服務 URL。請記錄下來並在前端配置中使用。

#### 🖥️ 本地開發環境
```
http://localhost:8080
```

### 完整端點列表

| 端點路徑 | 方法 | 說明 |
|---------|------|------|
| `/health` | GET | 健康檢查 |
| `/life/free/api/init_with_tone` | POST | 免費版 - 初始化對話 |
| `/life/free/api/chat` | POST | 免費版 - 發送訊息 |
| `/life/free/api/reset` | POST | 免費版 - 重置會話 |
| `/life/paid/api/init_with_tone` | POST | 付費版 - 初始化對話 |
| `/life/paid/api/chat` | POST | 付費版 - 發送訊息 |
| `/life/paid/api/reset` | POST | 付費版 - 重置會話 |

---

## 1️⃣ 初始化對話

### **POST** `/life/{version}/api/init_with_tone`

**完整路徑：**
- 免費版：`/life/free/api/init_with_tone`
- 付費版：`/life/paid/api/init_with_tone`

#### Request Body
```json
{
  "tone": "string"  // 語氣選擇
}
```

**語氣選項：**

**免費版（3種）：**
- `friendly` - 親切版
- `caring` - 貼心版
- `ritual` - 儀式版

**付費版（10種）：**
- `guan_yu` - 關聖帝君
- `michael` - 大天使米迦勒
- `gabriel` - 大天使加百列
- `raphael` - 大天使拉斐爾
- `uriel` - 大天使烏列爾
- `zadkiel` - 大天使沙德基爾
- `jophiel` - 大天使喬菲爾
- `chamuel` - 大天使沙木爾
- `metatron` - 大天使梅塔特隆
- `ariel` - 大天使阿列爾

#### Response
```json
{
  "session_id": "uuid-string",  // ⭐ 後端生成的會話ID，前端必須保存
  "response": "問候語內容",
  "state": "waiting_basic_info",
  "current_module": null
}
```

#### 範例

**生產環境：**
```bash
# Request
curl -X POST https://your-service-url.a.run.app/life/free/api/init_with_tone \
  -H "Content-Type: application/json" \
  -d '{"tone": "friendly"}'

# Response
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "response": "嗨！歡迎來到生命靈數的世界～",
  "state": "waiting_basic_info",
  "current_module": null
}
```

**本地開發：**
```bash
# Request
curl -X POST http://localhost:8080/life/free/api/init_with_tone \
  -H "Content-Type: application/json" \
  -d '{"tone": "friendly"}'
```

---

## 2️⃣ 對話互動

### **POST** `/life/{version}/api/chat`

**完整路徑：**
- 免費版：`/life/free/api/chat`
- 付費版：`/life/paid/api/chat`

#### Request Body
```json
{
  "session_id": "string",  // ⭐ 必須：由 init_with_tone 返回的會話ID
  "message": "string"      // 必須：用戶輸入內容
}
```

#### Response
```json
{
  "session_id": "string",       // 回傳原session_id
  "response": "AI回應內容",
  "state": "當前狀態",
  "current_module": "當前模組"  // 如有
}
```

#### 可能的狀態值
- `waiting_basic_info` - 等待基本資訊
- `waiting_module_selection` - 等待模組選擇
- `core_category_selection` - 核心模組類別選擇（⚠️ 僅 core 模組，付費版專屬）
- `waiting_core_question` - 等待核心模組問題（付費版）
- `waiting_question` - 等待深度問題（付費版）
- `continue_selection` - 繼續選項
- `completed` - 已完成

> 📝 **重要**：`core_category_selection` 狀態只會在付費版選擇 `core` 模組時出現。其他模組（birthday, year, grid, soul, personality, expression, maturity, challenge, karma）不會進入此狀態，會直接執行模組分析。

---

## 🔀 完整對話流程說明

### 付費版完整流程

```
步驟 1: 初始化（init_with_tone）
    ↓
步驟 2: 提交基本資訊（姓名、性別、生日、英文名）
    ↓
步驟 3: 系統顯示 10 個可用模組
    ├─ core（核心天賦人生方向）
    ├─ birthday（天生才華）
    ├─ year（年度運勢與連線）
    ├─ grid（九宮格）
    ├─ soul（靈魂數）
    ├─ personality（人格數）
    ├─ expression（表達數）
    ├─ maturity（成熟數）
    ├─ challenge（挑戰數）
    └─ karma（業力數）
    ↓
步驟 4: 用戶選擇其中一個模組
    ↓
    ├─ 如果選擇 【core】→ 特殊流程 ─┐
    │                                  │
    └─ 如果選擇 【其他模組】→ 標準流程 │
                                       │
┌──────────────────────────────────────┘
│
├─【core 特殊流程】─────────────────────┐
│  進入 core_category_selection 狀態     │
│      ↓                                │
│  選擇類別（四選一）：                   │
│    • 財運事業                          │
│    • 家庭人際                          │
│    • 自我成長                          │
│    • 目標規劃                          │
│      ↓                                │
│  進入 waiting_core_question 狀態       │
│      ↓                                │
│  用戶提交具體問題                      │
│      ↓                                │
│  獲得分析結果                          │
│      ↓                                │
│  進入 continue_selection 狀態          │
└───────────────────────────────────────┘
│
├─【其他模組標準流程】──────────────────┐
│  直接執行模組分析                      │
│      ↓                                │
│  獲得完整分析結果                      │
│      ↓                                │
│  進入 continue_selection 狀態          │
└───────────────────────────────────────┘
    ↓
步驟 5: 在 continue_selection 狀態，用戶可選擇：
    ├─ 繼續問問題（深度提問，付費版專屬）
    ├─ 其他生命靈數（回到步驟 3）
    └─ 離開（生成對話總結，含產品推薦）
```

> ⚠️ **關鍵重點**：
> 1. 提交基本資訊後，**一定會先讓用戶從 10 個模組中選擇一個**
> 2. 類別選擇（財運事業等）**不是模組選擇**，而是**只在選擇 core 模組後才出現的額外步驟**
> 3. 其他 9 個模組（birthday, year, grid, soul 等）選擇後直接給分析，無類別選擇

---

## 📝 完整對話流程範例

### **免費版流程**

#### 步驟 1：初始化
```json
POST /life/free/api/init_with_tone
Request: {"tone": "friendly"}
Response: {
  "session_id": "session-123",
  "response": "嗨！歡迎來到生命靈數～",
  "state": "waiting_basic_info"
}
```

#### 步驟 2：提交基本資訊
```json
POST /life/free/api/chat
Request: {
  "session_id": "session-123",
  "message": "王小明 male 1990/07/12"
}
Response: {
  "session_id": "session-123",
  "response": "王先生您好！...\n\n請選擇您想了解的生命靈數：\n1. core - 核心天賦人生方向\n2. birthday - 天生才華\n3. year - 年度運勢與連線\n4. grid - 九宮格",
  "state": "waiting_module_selection"
}
```
> 📌 **免費版有 4 個模組可選，且 core 模組沒有類別選擇**

#### 步驟 3：從 4 個模組中選擇一個（例如：core）
```json
POST /life/free/api/chat
Request: {
  "session_id": "session-123",
  "message": "core"
}
Response: {
  "session_id": "session-123",
  "response": "您的核心生命靈數是 5...\n\n（完整分析內容）",
  "state": "continue_selection",
  "current_module": "core",
  "number": 5
}
```
> 📌 **免費版：直接給出完整分析，沒有類別選擇**

#### 步驟 4：選擇離開
```json
POST /life/free/api/chat
Request: {
  "session_id": "session-123",
  "message": "離開"
}
Response: {
  "session_id": "session-123",
  "response": "感謝使用！",
  "state": "completed"
}
```

---

### **付費版流程（含付費功能）**

#### 步驟 1：初始化
```json
POST /life/paid/api/init_with_tone
Request: {"tone": "guan_yu"}
Response: {
  "session_id": "session-456",
  "response": "本君在此，準備為汝解惑...",
  "state": "waiting_basic_info"
}
```

#### 步驟 2：提交基本資訊（含英文名）
```json
POST /life/paid/api/chat
Request: {
  "session_id": "session-456",
  "message": "李小華 female 1985/03/25 LEE XIAO HUA"
}
Response: {
  "session_id": "session-456",
  "response": "李女士，本君已悉知汝之生辰...\n\n請選擇您想了解的生命靈數：\n1. core - 核心天賦人生方向\n2. birthday - 天生才華\n3. year - 年度運勢與連線\n4. grid - 九宮格\n5. soul - 靈魂數\n6. personality - 人格數\n7. expression - 表達數\n8. maturity - 成熟數\n9. challenge - 挑戰數\n10. karma - 業力數",
  "state": "waiting_module_selection"
}
```
> 📌 **此時用戶需要從 10 個模組中選擇一個**

#### 步驟 3：從 10 個模組中選擇 core（觸發類別選擇）
```json
POST /life/paid/api/chat
Request: {
  "session_id": "session-456",
  "message": "core"
}
Response: {
  "session_id": "session-456",
  "response": "您選擇了核心生命靈數。請選擇您想了解的類別：\n1. 財運事業\n2. 家庭人際\n3. 自我成長\n4. 目標規劃",
  "state": "core_category_selection",
  "current_module": "core",
  "show_category_buttons": true,
  "categories": ["財運事業", "家庭人際", "自我成長", "目標規劃"]
}
```
> 📌 **因為選擇了 core 模組，所以進入類別選擇（這是 core 專屬的額外步驟）**

#### 步驟 4：從 4 個類別中選擇一個（例如：財運事業）
```json
POST /life/paid/api/chat
Request: {
  "session_id": "session-456",
  "message": "財運事業"
}
Response: {
  "session_id": "session-456",
  "response": "請問你具體想了解什麼？",
  "state": "waiting_core_question",
  "current_module": "core",
  "category": "財運事業"
}
```

#### 步驟 5：提交問題
```json
POST /life/paid/api/chat
Request: {
  "session_id": "session-456",
  "message": "我今年適合創業嗎？"
}
Response: {
  "session_id": "session-456",
  "response": "根據您的核心生命靈數 8...",
  "state": "continue_selection",
  "current_module": "core",
  "number": 8
}
```

#### 步驟 6：選擇繼續問問題（付費版專屬）
```json
POST /life/paid/api/chat
Request: {
  "session_id": "session-456",
  "message": "繼續問問題"
}
Response: {
  "session_id": "session-456",
  "response": "請問您還想了解什麼？",
  "state": "waiting_question",
  "current_module": "core"
}
```

#### 步驟 7：提交深度問題
```json
POST /life/paid/api/chat
Request: {
  "session_id": "session-456",
  "message": "創業時機該如何選擇？"
}
Response: {
  "session_id": "session-456",
  "response": "根據您的流年數...",
  "state": "continue_selection",
  "current_module": "core"
}
```

#### 步驟 8：選擇其他生命靈數
```json
POST /life/paid/api/chat
Request: {
  "session_id": "session-456",
  "message": "其他生命靈數"
}
Response: {
  "session_id": "session-456",
  "response": "李女士，想了解其他面向嗎？",
  "state": "waiting_module_selection",
  "current_module": null
}
```

#### 步驟 9：離開（生成對話總結）
```json
POST /life/paid/api/chat
Request: {
  "session_id": "session-456",
  "message": "離開"
}
Response: {
  "session_id": "session-456",
  "response": "今天為您解析了...（含水晶和點燈推薦）",
  "state": "completed"
}
```

---

### **付費版流程（非 core 模組示例）**

> 📌 **說明**：當從 10 個模組中選擇 core 以外的模組時，不會有類別選擇，直接執行模組分析。

#### 步驟 1：初始化（同上）
（省略）

#### 步驟 2：提交基本資訊
```json
POST /life/paid/api/chat
Request: {
  "session_id": "session-789",
  "message": "李小華 female 1985/03/25 LEE XIAO HUA"
}
Response: {
  "session_id": "session-789",
  "response": "李女士，本君已悉知汝之生辰...\n\n請選擇您想了解的生命靈數：\n1. core - 核心天賦人生方向\n2. birthday - 天生才華\n3. year - 年度運勢與連線\n...\n10. karma - 業力數",
  "state": "waiting_module_selection"
}
```
> 📌 **系統顯示 10 個可選模組**

#### 步驟 3：從 10 個模組中選擇 birthday（非 core 模組）
```json
POST /life/paid/api/chat
Request: {
  "session_id": "session-789",
  "message": "birthday"
}
Response: {
  "session_id": "session-789",
  "response": "您的生日靈數是 3，代表著創造力與表達能力...",
  "state": "continue_selection",
  "current_module": "birthday",
  "number": 3
}
```
> ⚠️ **注意**：直接進入 `continue_selection` 狀態，沒有 `core_category_selection` 階段

#### 步驟 4：繼續問問題（付費版專屬）
```json
POST /life/paid/api/chat
Request: {
  "session_id": "session-789",
  "message": "繼續問問題"
}
Response: {
  "session_id": "session-789",
  "response": "請問您對生日靈數還有什麼想了解的？",
  "state": "waiting_question",
  "current_module": "birthday"
}
```

#### 步驟 5：提問深度問題
```json
POST /life/paid/api/chat
Request: {
  "session_id": "session-789",
  "message": "生日靈數 3 在職場上該如何發揮優勢？"
}
Response: {
  "session_id": "session-789",
  "response": "生日靈數 3 的您在職場上...",
  "state": "continue_selection",
  "current_module": "birthday"
}
```

#### 步驟 6：選擇其他生命靈數
```json
POST /life/paid/api/chat
Request: {
  "session_id": "session-789",
  "message": "其他生命靈數"
}
Response: {
  "session_id": "session-789",
  "response": "李女士，想了解其他面向嗎？",
  "state": "waiting_module_selection",
  "current_module": null
}
```

---

## 3️⃣ 重置會話

### **POST** `/life/{version}/api/reset`

**完整路徑：**
- 免費版：`/life/free/api/reset`
- 付費版：`/life/paid/api/reset`

#### Request Body
```json
{
  "session_id": "string"  // 可選：要刪除的會話ID
}
```

#### Response
```json
{
  "success": true
}
```

---

## 🔑 關鍵特點

### ✅ Session ID 機制
- **後端生成**：`init_with_tone` 時由後端創建唯一 UUID
- **前端保存**：前端必須保存並在所有後續請求中傳遞
- **會話隔離**：不同用戶使用不同的 `session_id`，互不干擾
- **無需登入**：免費用戶和付費用戶都使用相同機制，無需額外的 `user_id`

### 🆓 免費版特點

**可用模組（4個）：**
- `core` - 核心天賦人生方向
- `birthday` - 天生才華
- `year` - 年度運勢與連線
- `grid` - 天賦優勢與在職特質及缺的特質 九宮格

**可用語氣（3個）：**
- `friendly` - 親切版
- `caring` - 貼心版
- `ritual` - 儀式版

**功能限制：**
- ❌ 不需要英文名
- ❌ 單次對話，無深度提問功能
- ❌ 無核心模組類別選擇
- ❌ 無對話總結與產品推薦

### 💎 付費版特點

**可用模組（10個）：**
- `core` - 核心天賦人生方向
- `birthday` - 天生才華
- `year` - 年度運勢與連線
- `grid` - 天賦優勢與在職特質 九宮格
- `soul` - 靈魂數 - 內心真正的渴望
- `personality` - 人格數 - 外在展現的形象
- `expression` - 表達數 - 溝通與表達方式
- `maturity` - 成熟數 - 中年後的發展
- `challenge` - 挑戰數 - 需要克服的課題
- `karma` - 業力數 - 前世今生的因果

**可用語氣（10個）：**
- `guan_yu` - 關聖帝君
- `michael` - 大天使米迦勒
- `gabriel` - 大天使加百列
- `raphael` - 大天使拉斐爾
- `uriel` - 大天使烏列爾
- `zadkiel` - 大天使沙德基爾
- `jophiel` - 大天使喬菲爾
- `chamuel` - 大天使沙木爾
- `metatron` - 大天使梅塔特隆
- `ariel` - 大天使阿列爾

**獨家功能：**
- ✅ **必須提供英文名**（用於靈魂、人格、表達數計算）
- ✅ **核心模組（core）專屬類別選擇**
  - 只有選擇 `core` 模組時才會觸發類別選擇
  - 四大類別：財運事業、家庭人際、自我成長、目標規劃
  - 其他模組（birthday, year, grid, soul 等）無類別選擇
- ✅ **深度對話功能**：支持「繼續問問題」
- ✅ **對話總結**：離開時生成完整總結，包含水晶和點燈推薦

---

## ⚠️ 錯誤處理

### 缺少 session_id
```json
{
  "error": "缺少 session_id",
  "message": "請先調用 init_with_tone 初始化會話"
}
```
**HTTP Status**: 400

### 會話不存在或已過期
```json
{
  "error": "會話不存在或已過期",
  "message": "請重新調用 init_with_tone 初始化會話",
  "session_id": "原session_id"
}
```
**HTTP Status**: 404

### Redis 連線錯誤
```json
{
  "error": "Session 存儲服務暫時不可用",
  "message": "請稍後再試"
}
```
**HTTP Status**: 503

### OpenAI API 錯誤
```json
{
  "error": "AI 服務暫時不可用",
  "message": "請稍後再試"
}
```
**HTTP Status**: 503

### 請求超時
Cloud Run 預設超時為 120 秒，超過此時間將返回：
```json
{
  "error": "Request timeout",
  "message": "請求處理時間過長，請重試"
}
```
**HTTP Status**: 504

### 服務冷啟動
當服務實例從 0 擴展時，首次請求可能需要較長時間（5-10秒）。後續請求將快速響應。

---

## 🧪 測試指令

### 本地開發測試
```bash
# 啟動本地服務
python app.py

# 運行完整測試（需要服務運行中）
python test_complete_all.py
```

### 生產環境測試
部署後，可使用以下指令測試生產環境 API：

```bash
# 設定服務 URL
export API_URL="https://your-service-url.a.run.app"

# 測試健康檢查
curl $API_URL/health

# 測試免費版初始化
curl -X POST $API_URL/life/free/api/init_with_tone \
  -H "Content-Type: application/json" \
  -d '{"tone": "friendly"}'

# 測試付費版初始化
curl -X POST $API_URL/life/paid/api/init_with_tone \
  -H "Content-Type: application/json" \
  -d '{"tone": "guan_yu"}'
```

### 測試配置
- `TRUNCATE_RESPONSE = False`：顯示完整API回應
- `TRUNCATE_RESPONSE = True`：截斷長回應至300字元

### 負載測試
使用 Apache Bench 進行負載測試：
```bash
# 測試 100 個請求，10 個並發
ab -n 100 -c 10 -H "Content-Type: application/json" \
  -p health_check.json \
  https://your-service-url.a.run.app/health
```

---

## 🚀 部署資訊

### GCP Cloud Run 部署

#### 部署區域
- **預設區域**: `asia-east1` (台灣)
- **可選區域**: `asia-northeast1` (東京)、`us-west1` (奧勒岡)

#### 資源配置
- **Memory**: 512Mi
- **CPU**: 1 vCPU
- **並發數**: 80 個請求
- **超時時間**: 120 秒
- **最小實例**: 0（按需啟動）
- **最大實例**: 10

#### 環境變量（透過 Secret Manager 管理）
部署時，以下環境變量會從 GCP Secret Manager 自動注入：

| 變量名稱 | 說明 | 範例值 |
|---------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 金鑰 | `sk-proj-...` |
| `OPENAI_MODEL` | GPT 模型版本 | `gpt-4o` |
| `PROJECT_LOCALE` | 專案語言 | `zh-TW` |
| `REDIS_HOST` | Redis 主機地址 | `redis-xxxxx.cloud.redislabs.com` |
| `REDIS_PORT` | Redis 端口 | `11330` |
| `REDIS_PASSWORD` | Redis 密碼 | `******` |
| `REDIS_USERNAME` | Redis 用戶名 | `default` |
| `SESSION_TTL` | Session 過期時間（秒） | `43200`（12小時） |

#### 部署指令
```bash
# 執行部署腳本
cd /path/to/Life\ Number\ Backend
./deploy.sh

# 或使用 gcloud 手動部署
gcloud builds submit --config cloudbuild.yaml
```

#### 取得服務 URL
部署完成後，使用以下指令取得服務 URL：
```bash
gcloud run services describe life-number-backend \
  --region=asia-east1 \
  --format='value(status.url)'
```

#### 健康檢查端點
```bash
# 檢查服務狀態
curl https://your-service-url.a.run.app/health

# 預期回應
{
  "status": "healthy",
  "timestamp": "2025-11-24T12:00:00.000Z"
}
```

### CORS 配置
API 已啟用 CORS，允許跨域請求：
- ✅ 所有來源 (`*`)
- ✅ 支援 POST、GET、OPTIONS 方法
- ✅ 支援 Content-Type、Authorization 標頭

### 安全性
- 🔐 敏感資料（API 金鑰、密碼）存放於 GCP Secret Manager
- 🔐 生產模式運行（`debug=False`）
- 🔐 HTTPS 加密傳輸（自動由 Cloud Run 提供）
- 🔐 Session 資料加密存儲於 Redis（12 小時 TTL）

### 前端整合範例

#### JavaScript/Fetch API
```javascript
// 設定 API 基礎 URL
const API_BASE_URL = 'https://your-service-url.a.run.app';

// 免費版初始化
async function initFreeSession(tone) {
  const response = await fetch(`${API_BASE_URL}/life/free/api/init_with_tone`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tone })
  });
  const data = await response.json();
  // 保存 session_id
  localStorage.setItem('session_id', data.session_id);
  return data;
}

// 發送對話訊息
async function sendMessage(message, version = 'free') {
  const sessionId = localStorage.getItem('session_id');
  const response = await fetch(`${API_BASE_URL}/life/${version}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message })
  });
  return await response.json();
}
```

#### Python/Requests
```python
import requests

API_BASE_URL = 'https://your-service-url.a.run.app'

# 付費版初始化
def init_paid_session(tone):
    response = requests.post(
        f'{API_BASE_URL}/life/paid/api/init_with_tone',
        json={'tone': tone}
    )
    data = response.json()
    session_id = data['session_id']  # 保存此 ID
    return data

# 發送對話訊息
def send_message(session_id, message):
    response = requests.post(
        f'{API_BASE_URL}/life/paid/api/chat',
        json={'session_id': session_id, 'message': message}
    )
    return response.json()
```

### 監控與日誌

#### 查看即時日誌
```bash
# 查看最新日誌
gcloud run services logs read life-number-backend \
  --region=asia-east1 \
  --limit=50

# 即時追蹤日誌
gcloud run services logs tail life-number-backend \
  --region=asia-east1
```

#### 監控指標
在 GCP Console 可查看：
- 請求數量與延遲
- 錯誤率
- 實例數量
- CPU 與記憶體使用率

---

## 📌 版本資訊
- **API Version**: 1.0.0
- **Last Updated**: 2025-11-24
- **部署平台**: GCP Cloud Run
- **文檔維護**: 每次 API 變更時同步更新

