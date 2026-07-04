# 🌟 生命靈數後端 API 文檔

## 📖 系統架構

本系統是一個**資料庫驅動**的生命靈數平台，整合了三大核心模組：

### 🎯 核心模組
1. **生命靈數 (Life Number)** - 完整的生命靈數計算與解讀系統
2. **天使數字 (Angel Number)** - 天使數字訊息解讀
3. **神諭占卜 (Divination)** - 擲筊占卜與神明指引
4. **黃道吉日 (Auspicious Date)** - 黃曆查詢與吉日推薦

### 💾 資料庫架構

系統使用 **Supabase (PostgreSQL)** 作為資料來源，所有靈數內容、天使訊息、神諭解讀都動態從資料庫讀取：

**優勢：**
- ✅ **內容易更新**：直接在資料庫修改解讀內容，無需重新部署
- ✅ **一致性保證**：所有用戶獲得相同版本的最新內容
- ✅ **擴充性強**：輕鬆新增更多靈數、天使數字或占卜組合
- ✅ **多語言支持**：資料庫可輕鬆擴充多語言內容

**資料表結構：**
- **全域規則**：1 個資料表（ai_global_rules - AI 全域回答規則）
- **生命靈數**：11 個資料表（main, birthday, year, grid, soul, personality, expression, maturity, challenge, karma, grid_lines）
- **天使數字**：2 個資料表（meanings, basic_energy）
- **占卜系統**：2 個資料表（combinations, tone_greetings）
- **黃道吉日**：1 個資料表（auspicious_calendar - 月份黃曆資料）

### ☁️ 免費版雲端服務用量與限制

本系統依賴兩種雲端資料服務：**Supabase**（主要內容資料庫）與 **Redis Cloud**（Session 暫存）。以下為免費方案的用量限制與閒置處置規則，供維運與成本評估參考。

---

#### 一、Supabase 免費版

提供完整的 Postgres 資料庫與後端服務，資源給得相當大方，但也因此對閒置資源的控管較為嚴格。

**用量與限制**

| 項目 | 限制 |
|------|------|
| 資料庫容量 | 500 MB（Shared CPU） |
| 檔案儲存空間 | 1 GB |
| 身分驗證 (Auth) | 每月 50,000 名活躍用戶 (MAU) |
| 網路傳輸 | 每月 5 GB（另有 5 GB 緩存傳輸量） |
| 專案數量限制 | 每個帳號最多 2 個活躍專案 |

**閒置規則與處置**

| 項目 | 說明 |
|------|------|
| 閒置判定 | 連續 **7 天**沒有對資料庫進行真實的「查詢或寫入」。單純登入 Supabase 網頁後台**不會**重置計時器。 |
| 處置方式（暫停） | 運算實例會被關閉（Pause），但資料、Schema 與備份都會完整保留。 |
| 重啟影響 | 專案收到下一次真實請求或從後台手動開啟時，會自動喚醒。但會有約 **30 秒**的冷啟動延遲 (Cold-start latency)。 |

> 📝 **對本系統的影響**：Supabase 暫停後，API 仍可回應 `/health`，但所有需讀取靈數內容、神諭解讀的端點會失敗，直到 Supabase 被喚醒。

---

#### 二、Redis Cloud 免費版（官方服務）

Redis 官方託管的雲端服務，免費額度較小，且對閒置資源的清理非常嚴格。

**用量與限制**

| 項目 | 限制 |
|------|------|
| 資料庫容量 | 30 MB |
| 連線數限制 | 最多 30 個並行連線 (Concurrent connections) |
| 可用性 | 單一可用區 (Single AZ)，無高可用性備援 |
| 資料庫數量限制 | 每個帳號最多只能擁有 **1 個**免費資料庫 |

**閒置規則與處置**

| 項目 | 說明 |
|------|------|
| 閒置判定 | 連續 **14 天**沒有對資料庫進行真實的指令操作（例如 GET、SET 等）。登入網頁後台**無法**重置此計時器。 |
| 處置方式（廢棄） | 整個資料庫與內部儲存的資料會被**永久刪除**，無法復原。 |
| 重建影響 | 系統刪除資料庫後，帳號會殘留一個「空的訂閱 (Empty Subscription)」。必須在後台**手動將該空訂閱徹底刪除**，系統才會允許重新建立新的免費資料庫。 |

> ⚠️ **對本系統的影響**：Redis 被廢棄後，所有對話 API 的 Session 管理會失效（回傳 503），用戶需重新 `init_with_tone` 建立新 Session。Session 資料本身為暫存（12 小時 TTL），重建 Redis 不影響 Supabase 中的靈數內容。

---

## 📡 I/O 規格文檔

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
| **生命靈數 (Life Number)** |
| `/life/free/api/init_with_tone` | POST | 免費版 - 初始化對話 |
| `/life/free/api/chat` | POST | 免費版 - 發送訊息 |
| `/life/free/api/reset` | POST | 免費版 - 重置會話 |
| `/life/paid/api/init_with_tone` | POST | 付費版 - 初始化對話 |
| `/life/paid/api/chat` | POST | 付費版 - 發送訊息 |
| `/life/paid/api/reset` | POST | 付費版 - 重置會話 |
| **天使數字 (Angel Number)** |
| `/angel/free/api/init_with_tone` | POST | 天使數字 - 免費版初始化 |
| `/angel/free/api/chat` | POST | 天使數字 - 免費版對話 |
| `/angel/free/api/reset` | POST | 天使數字 - 免費版重置 |
| `/angel/paid/api/init_with_tone` | POST | 天使數字 - 付費版初始化 |
| `/angel/paid/api/chat` | POST | 天使數字 - 付費版對話 |
| `/angel/paid/api/reset` | POST | 天使數字 - 付費版重置 |
| **擲筊 (Divination)** |
| `/divination/free/api/init_with_tone` | POST | 擲筊 - 免費版初始化 |
| `/divination/free/api/chat` | POST | 擲筊 - 免費版對話 |
| `/divination/free/api/reset` | POST | 擲筊 - 免費版重置 |
| `/divination/paid/api/init_with_tone` | POST | 擲筊 - 付費版初始化 |
| `/divination/paid/api/chat` | POST | 擲筊 - 付費版對話 |
| `/divination/paid/api/reset` | POST | 擲筊 - 付費版重置 |
| **黃道吉日 (Auspicious Date)** |
| `/auspicious/free/api/init_with_tone` | POST | 黃道吉日 - 免費版初始化 |
| `/auspicious/free/api/chat` | POST | 黃道吉日 - 免費版對話 |
| `/auspicious/free/api/reset` | POST | 黃道吉日 - 免費版重置 |
| `/auspicious/paid/api/init_with_tone` | POST | 黃道吉日 - 付費版初始化 |
| `/auspicious/paid/api/chat` | POST | 黃道吉日 - 付費版對話 |
| `/auspicious/paid/api/reset` | POST | 黃道吉日 - 付費版重置 |

---

## 4️⃣ 天使數字 API (Angel Number)

天使數字模組提供免費版和付費版兩種體驗。

### 🌟 版本差異

| 功能 | 免費版 | 付費版 |
|------|--------|--------|
| **語氣選擇** | 3 種 (friendly, caring, ritual) | 10 種 (包含關聖帝君、大天使等) |
| **數字支援** | 僅限 4 位重複數 (如 1111, 2222) | 支援任意數字 (如 123, 1212, 888) |
| **智能分析** | 固定含義 | 智能模式識別 (重複、階梯、鏡像等 8 種模式) |
| **對話深度** | 單次解讀即結束 | 支援深度對話 (提問 -> 回答 -> 繼續) |
| **輸入方式** | 選擇器 (UI) | 文字輸入 |

### 📡 端點說明

#### 初始化對話
`POST /angel/{version}/api/init_with_tone`

**Request:**
```jsonc
{
  "tone": "string" // friendly, caring, ritual, guan_yu, michael...
}
```

**Response:**
```jsonc
{
  "session_id": "uuid",
  "response": "問候語",
  "state": "waiting_basic_info"
}
```

#### 對話互動
`POST /angel/{version}/api/chat`

**Request:**
```jsonc
{
  "session_id": "uuid",
  "message": "string"
}
```

**Response:**
```jsonc
{
  "session_id": "uuid",
  "response": "AI回應",
  "state": "waiting_angel_number | asking_for_question | conversation | completed",
  "angel_number": "123", // 僅在解讀完成時返回
  "pattern": "ascending" // 僅付費版返回
}
```

### 🔄 對話流程

#### 免費版流程
1. **初始化**：選擇語氣
2. **基本資訊**：輸入姓名、性別、生日
3. **選擇數字**：從列表中選擇 (如 1111)
4. **解讀**：獲得解讀結果，對話結束

#### 付費版流程
1. **初始化**：選擇語氣 (預設 guan_yu)
2. **基本資訊**：輸入姓名、性別、生日
3. **輸入數字**：輸入任意數字 (如 123)
4. **智能解讀**：AI 分析數字模式並解讀
5. **深度提問**：系統詢問是否有問題
   - **有問題**：進入對話模式，針對該數字進行深入問答
   - **沒問題**：對話結束
6. **持續對話**：可多輪提問，直到用戶說謝謝/結束
   > 💡 **進階功能**：在 `asking_for_question` 或 `conversation` 狀態下，若用戶輸入新的 1~4 位**純數字**（例如直接輸入 `444`，不可含文字如「那 444 呢？」），且與目前分析中的數字不同，系統會自動將狀態重置回 `waiting_angel_number`，重新啟動新數字的分析，無需另外開啟新對話串。

---

## 5️⃣ 擲筊 API (Divination)

擲筊模組提供免費版和付費版兩種體驗。

### 🌟 版本差異

| 功能 | 免費版 | 付費版 |
|------|--------|--------|
| **語氣選擇** | 3 種 (friendly, caring, ritual) | 9 種 (關聖帝君、媽祖、月老等) |
| **擲筊次數** | 單次擲筊 | **三次擲筊** |
| **解讀方式** | 固定模板 | **AI 智能解讀** + **行動建議** (根據神明性格 + 10 種組合) |
| **對話深度** | 單次擲筊即結束 | 支援深度對話 (提問 -> 擲筊 -> 解讀 -> 追問) |
| **結果生成** | 隨機 (聖/笑/陰) | **三次隨機** + 組合分析 + AI 解讀 |

### 📡 端點說明

#### 初始化對話
`POST /divination/{version}/api/init_with_tone`

**Request:**
```jsonc
{
  "tone": "string" // friendly, caring, ritual, guan_gong, mazu...
}
```

**Response:**
```jsonc
{
  "session_id": "uuid",
  "response": "問候語",
  "state": "waiting_basic_info"
}
```

#### 對話互動
`POST /divination/{version}/api/chat`

**Request:**
```jsonc
{
  "session_id": "uuid",
  "message": "string", // 一般對話訊息
  // ⚠️ 在 divining 狀態下，必須傳入以下欄位之一：
  "divination_result": "string", // 免費版 (holy/laughing/negative)
  "divination_results": ["string", "string", "string"] // 付費版，三個結果的數組
}
```

> **注意**：系統不再自動隨機生成結果。前端必須先執行擲筊動畫，然後將動畫產生的最終結果傳遞給後端進行解讀。

**狀態流轉說明：**
1. `waiting_basic_info`: 等待用戶輸入姓名、性別、生日
2. `waiting_question`: 等待用戶輸入問題
3. `divining`: 用戶輸入問題後，系統回傳引導文案，進入此狀態。用戶需發送請求（如 message="cast"）來觸發擲筊。
4. `completed` (免費版) / `asking_for_question` (付費版): 擲筊完成，回傳結果解讀。

> ⚠️ **注意：敏感詞過濾**
> 在 `waiting_question` 狀態，若用戶輸入的問題涉及**高風險關鍵詞**（如股票、期貨、樂透、賭博、保明牌），系統才會拒絕服務。
> **注意**：對於**買房、置產、創業、薪資**等一般性金融或生涯規劃話題，**不再**視為敏感詞，系統將照常提供分析。
> - State: 保持在 `waiting_question` 或結束（視實現而定，目前保持原狀態或允許重新提問）。

**免費版 Response:**
```jsonc
{
  "session_id": "uuid",
  "response": "AI回應",
  "state": "waiting_question | divining | completed",
  "question": "用戶問題",
  "divination_result": "holy"  // 僅在 completed 狀態回傳：holy(聖筊), laughing(笑筊), negative(陰筊)
}
```

**免費版 Divining 狀態 Response 範例：**
```jsonc
{
  "session_id": "uuid",
  "response": "收到你的問題。請誠心默念，然後按下按鈕擲筊。",
  "state": "divining"
}
```

**付費版 Response:**
```jsonc
{
  "session_id": "uuid",
  "response": "AI回應",
  "state": "waiting_question | divining | asking_for_question | completed",
  "question": "用戶問題",
  "divination_results": ["holy", "laughing", "negative"],  // 僅在 asking_for_question/completed 狀態回傳
  "combination_type": "holy_holy_laughing",
  "divination_result": "holy_holy_laughing"
}
```

**付費版 Divining 狀態 Response 範例：**
```jsonc
{
  "session_id": "uuid",
  "response": "收到，王小明。請誠心默念問題三次，準備好後點擊擲筊。",
  "state": "divining"
}
```

**付費版組合類型：**
- `holy_holy_holy` - 三次聖筊（全然支持）
- `negative_negative_negative` - 三次陰筊（時運不合）
- `laughing_laughing_laughing` - 三次笑筊（無需執著）
- `holy_holy_negative` - 兩允一止（需補不足）
- `holy_holy_laughing` - 兩允一笑（放輕心態）
- `negative_negative_holy` - 兩止一允（轉機已現）
- `negative_negative_laughing` - 兩止一笑（不宜強求）
- `laughing_laughing_holy` - 兩笑一允（專注核心）
- `laughing_laughing_negative` - 兩笑一止（順其自然）
- `mixed_all_three` - 聖陰笑齊聚（彈性面對）

### 🔄 對話流程

#### 免費版流程
1. **初始化**：選擇語氣
2. **基本資訊**：輸入姓名、性別、生日
3. **提交問題**：輸入想問的問題
4. **擲筊**：系統隨機擲筊（單次）並使用模板解讀，對話結束

#### 付費版流程
1. **初始化**：選擇語氣 (如關聖帝君)
2. **基本資訊**：輸入姓名、性別、生日
3. **提交問題**：輸入想問的問題
4. **擲筊三次**：系統進行三次擲筊
5. **AI 綜合解讀**：根據三次結果的組合類型（10 種）+ 神明性格 + 用戶問題，生成個性化解讀
6. **持續對話**：系統詢問是否有其他疑問
   - **有問題**：用戶追問，AI 繼續以神明口吻回答
   - **沒問題**：對話結束

---

## 6️⃣ 黃道吉日 API (Auspicious Date)

黃道吉日模組提供基於傳統黃曆的吉日查詢服務。

### 🌟 版本差異

| 功能 | 免費版 | 付費版 |
|------|--------|--------|
| **語氣選擇** | 3 種 (friendly, caring, ritual) | 8 種神明語氣（關聖帝君、五路財神、文昌帝君、月老、觀音、媽祖、九天娘娘、福德正神） |
| **分類查詢** | 5 種分類（生活日常、家庭居所、感情人際、喜慶大事、工作事業） | 相同 |
| **輸入方式** | 按鈕選擇 + 文字輸入 | 相同 |
| **解讀方式** | 基於黃曆「宜」「忌」欄位的 AI 分析 | 以神明性格進行深度解讀 |
| **對話深度** | 單次查詢即結束 | **持續對話**：可追問更多細節，AI 以神明口吻回答 |

### 📋 對話流程

#### 免費版流程
1. **初始化**：選擇語氣（friendly/caring/ritual）
2. **基本資訊**：輸入姓名、性別、生日、生肖
3. **選擇分類和日期**：選擇分類（如「感情人際」）+ 日期
4. **描述事項**：具體說明要做的事（如「結婚」）
5. **查詢結果**：AI 分析黃曆並給出建議，對話結束

#### 付費版流程
1. **初始化**：選擇神明語氣（如月老星君）
2. **基本資訊**：輸入姓名、性別、生日、生肖
3. **選擇分類和日期**：選擇分類 + 日期
4. **描述事項**：具體說明要做的事
5. **查詢結果**：神明以其性格進行深度解讀
6. **持續對話**：系統詢問是否有其他疑問
   - **有問題**：用戶追問，AI 以神明口吻繼續回答
   - **沒問題**：用戶說「謝謝」或「沒有」，神明給出結束語，對話結束

### 📡 端點說明

#### 初始化對話
`POST /auspicious/{version}/api/init_with_tone`

**Request:**
```jsonc
{
  "tone": "string" // 免費版: friendly, caring, ritual | 付費版: yue_lao, guan_gong, wealth_god, 等
}
```

**Response:**
```jsonc
{
  "session_id": "uuid",
  "response": "問候語",
  "state": "waiting_basic_info"
}
```

#### 對話互動
`POST /auspicious/{version}/api/chat`

**Request - 階段 1（提交基本資訊）:**
```jsonc
{
  "session_id": "uuid",
  "message": "王小明 男 1990/07/12 屬馬"
}
```

**Response:**
```jsonc
{
  "session_id": "uuid",
  "response": "好的！接下來請選擇你想查詢的分類，並選擇一個日期...",
  "state": "waiting_category_and_date",
  "categories": {
    "daily_life": { "name": "生活日常", "examples": "..." },
    "family_home": { "name": "家庭居所", "examples": "..." },
    "relationship": { "name": "感情人際", "examples": "..." },
    "celebration": { "name": "喜慶大事", "examples": "..." },
    "work_career": { "name": "工作事業", "examples": "..." }
  }
}
```

**Request - 階段 2（選擇分類和日期）:**

方式一：前端按鈕直接傳遞
```jsonc
{
  "session_id": "uuid",
  "category": "family_home",
  "selected_date": "2025-12-15"
}
```

方式二：文字輸入
```jsonc
{
  "session_id": "uuid",
  "message": "家庭居所，2025-12-15"
}
```

**分類對應：**
| Key | 中文名稱 | 黃曆對應 |
|-----|---------|---------|
| `daily_life` | 生活日常 | 出行、出火、捕捉、畋獵、取魚、結網、沐浴、會親友等 |
| `family_home` | 家庭居所` | 入宅、安床、作灶、動土、上樑、裁衣、破屋壞垣 |
| `relationship` | 感情人際 | 納采、嫁娶、冠笄 |
| `celebration` | 喜慶大事 | 祭祀、祈福、開光、設醮、齋醮、安香 |
| `work_career` | 工作事業 | 開市、交車 |

**Response:**
```jsonc
{
  "session_id": "uuid",
  "response": "好的！你選擇了「家庭居所」，日期是「2025-12-15」...",
  "state": "waiting_specific_question",
  "category": "family_home",
  "selected_date": "2025-12-15"
}
```

**Request - 階段 3（描述具體事項）:**
```jsonc
{
  "session_id": "uuid",
  "message": "我想搬家到新家"
}
```

**Response (免費版):**
```jsonc
{
  "session_id": "uuid",
  "response": "根據黃曆分析...[AI 解讀內容]...",
  "state": "completed",
  "specific_question": "我想搬家到新家"
}
```

**Response (付費版):**
```jsonc
{
  "session_id": "uuid",
  "response": "[神明解讀]...\n\n如果您對選擇的日期或建議有任何疑問，歡迎繼續提問。我會為您詳細解答。",
  "state": "asking_for_question",  // 付費版進入持續對話狀態
  "specific_question": "我想搬家到新家"
}
```

**Request - 階段 4（僅付費版：追問）:**
```jsonc
{
  "session_id": "uuid",
  "message": "那有什麼需要特別注意的嗎？"
}
```

**Response (付費版持續對話):**
```jsonc
{
  "session_id": "uuid",
  "response": "[神明以其性格回答用戶的追問]...",
  "state": "asking_for_question"  // 仍在持續對話中
}
```

**Request - 階段 5（僅付費版：結束對話）:**
```jsonc
{
  "session_id": "uuid",
  "message": "謝謝"  // 或「沒有」、「不用了」等結束關鍵詞
}
```

**Response (付費版結束):**
```jsonc
{
  "session_id": "uuid",
  "response": "[神明特色結束語，如月老：「既然沒有其他問題，那就祝你良緣早至，幸福美滿。」]",
  "state": "completed"
}
```


### 🔄 重置會話
`POST /auspicious/{version}/api/reset`

**Request:**
```jsonc
{
  "session_id": "uuid"
}
```

**Response:**
```jsonc
{
  "success": true,
  "message": "會話已重置"
}
```

---

## 1️⃣ 初始化對話

### **POST** `/life/{version}/api/init_with_tone`

**完整路徑：**
- 免費版：`/life/free/api/init_with_tone`
- 付費版：`/life/paid/api/init_with_tone`

#### Request Body
```jsonc
{
  "tone": "string"  // 語氣選擇
}
```

**語氣選項：**

**1. 生命靈數 (Life Number)**
- **免費版**: `friendly`, `caring`, `ritual`
- **付費版**: `guan_yu` (關聖帝君), `michael` (大天使米迦勒) 等 10 種大天使與神明

**2. 天使數字 (Angel Number)**
- **免費版**: `friendly`, `caring`, `ritual`
- **付費版**: 
  - `guan_yu` (關聖帝君)
  - `michael` (大天使米迦勒)
  - `gabriel` (大天使加百列)
  - `raphael` (大天使拉斐爾)
  - `uriel` (大天使烏列爾)
  - `zadkiel` (大天使沙德基爾)
  - `jophiel` (大天使喬菲爾)
  - `chamuel` (大天使沙木爾)
  - `metatron` (大天使梅塔特隆)
  - `ariel` (大天使阿列爾)

**3. 擲筊 (Divination)**
- **免費版**: `friendly`, `caring`, `ritual`
- **付費版**:
  - `guan_gong` (關聖帝君)
  - `wealth_god` (五路財神)
  - `wen_chang` (文昌帝君)
  - `yue_lao` (月老星君)
  - `guanyin` (觀世音菩薩)
  - `mazu` (媽祖)
  - `jiutian` (九天娘娘)
  - `fude` (福德正神)

**4. 黃道吉日 (Auspicious Date)**
- **免費版**: `friendly` (親切), `caring` (貼心), `ritual` (儀式)
- **付費版**: 待規劃

#### Response
```jsonc
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
```jsonc
{
  "session_id": "string",  // ⭐ 必須：由 init_with_tone 返回的會話ID
  "message": "string"      // 必須：用戶輸入內容
}
```

#### Response
```jsonc
{
  "session_id": "string",       // 回傳原session_id
  "response": "AI回應內容",
  "state": "當前狀態",
  "current_module": "當前模組",  // 如有
  "number": 5                   // ⚠️ 僅在模組初次計算完成時回傳（可能為整數、字串或字串列表，見下方說明）
}
```

> ⚠️ **關於 `number` 參數**：
> 1. 此參數僅在 **模組選定並完成初次計算** 的 Response 中出現（即當 state 從 `waiting_module_selection` 轉變為 `continue_selection` 或 `core_category_selection` 時）。
> 2. 後續的深度對話（如 `waiting_core_question` 的回應）**不會**再次回傳此參數。
> 3. **Grid (九宮格)** 模組回傳的是 **字串列表**，例如 `["123", "456"]`。若無連線則回傳 `["none"]`。
> 4. 一般模組（core, birthday, year, maturity, challenge 等）回傳 **整數**（如 `5`、`8`）。
> 5. **特殊情況 — 計算結果為 0**：`soul`（靈魂數）、`personality`（人格數）、`expression`（表達數）、`karma`（業力數）在無法計算或無特定業力時，回傳字串 `"無"` 而非 `0`。常見原因：未提供英文姓名（靈魂/人格/表達數），或生日無 13/14/16/19 業力數（業力數）。

#### 可能的狀態值
- `waiting_basic_info` - 等待基本資訊
- `waiting_module_selection` - 等待模組選擇
- `core_category_selection` - 核心模組類別選擇（⚠️ 僅 core 模組，付費版專屬）
- `waiting_core_question` - 等待核心模組問題（付費版）
- `waiting_question` - 等待深度問題（付費版）
- `continue_selection` - 繼續選項
- `completed` - 已完成

**黃道吉日專屬：**
- `waiting_category_and_date` - 等待分類與日期選擇
- `waiting_specific_question` - 等待具體問題
- `providing_dates` - 提供吉日建議

> 📝 **重要**：`core_category_selection` 狀態只會在付費版選擇 `core` 模組時出現。
其他模組（birthday, year, grid, soul, personality, expression, maturity, challenge, karma）不會進入此狀態，會直接執行模組分析。

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
│  執行核心生命靈數計算 ⭐                │
│      ↓                                │
│  顯示完整分析結果（含生命靈數數字）     │
│      +                                │
│  顯示類別選擇按鈕                      │
│      ↓                                │
│  進入 core_category_selection 狀態     │
│      ↓                                │
│  用戶選擇類別：                        │
│    • 財運事業                          │
│    • 家庭人際                          │
│    • 自我成長                          │
│    • 目標規劃                          │
│      ↓                                │
│  進入 waiting_core_question 狀態       │
│      ↓                                │
│  用戶提交具體問題                      │
│      ↓                                │
│  根據核心生命靈數 + 類別 + 問題        │
│  提供深度個性化分析                    │
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
```jsonc
POST /life/free/api/init_with_tone
Request: {"tone": "friendly"}
Response: {
  "session_id": "session-123",
  "response": "嗨！歡迎來到生命靈數～",
  "state": "waiting_basic_info"
}
```

#### 步驟 2：提交基本資訊
```jsonc
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
```jsonc
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
```jsonc
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
```jsonc
POST /life/paid/api/init_with_tone
Request: {"tone": "guan_yu"}
Response: {
  "session_id": "session-456",
  "response": "本君在此，準備為汝解惑...",
  "state": "waiting_basic_info"
}
```

#### 步驟 2：提交基本資訊（含英文名）
```jsonc
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

#### 步驟 3：從 10 個模組中選擇 core（立即計算並顯示結果 + 類別選擇）
```jsonc
POST /life/paid/api/chat
Request: {
  "session_id": "session-456",
  "message": "core"
}
Response: {
  "session_id": "session-456",
  "response": "李女士，您好。根據您的生辰資訊，您的核心生命靈數是 8。\n\n生命靈數 8 的人具有強大的領導力和商業頭腦，天生擁有掌控全局的能力...\n\n（完整的核心生命靈數分析）\n\n以下四大面向供你選擇探索。選擇一個，我將為你深入分析。\n\n1. 財運事業\n2. 家庭人際\n3. 自我成長\n4. 目標規劃",
  "state": "core_category_selection",
  "current_module": "core",
  "number": 8,
  "show_category_buttons": true,
  "categories": ["財運事業", "家庭人際", "自我成長", "目標規劃"]
}
```
> ✨ **關鍵重點**：
> 1. **立即計算並顯示核心生命靈數結果**（數字 + 完整分析）
> 2. **然後**在結果後面顯示類別選擇
> 3. 用戶可以根據已知的核心生命靈數，選擇想深入探討的面向

#### 步驟 4：從 4 個類別中選擇一個（例如：財運事業）
```jsonc
POST /life/paid/api/chat
Request: {
  "session_id": "session-456",
  "message": "財運事業"
}
Response: {
  "session_id": "session-456",
  "response": "在財運事業這個面向，你有什麼具體想了解的問題嗎？",
  "state": "waiting_core_question",
  "current_module": "core",
  "category": "財運事業"
}
```
> 📌 **選擇類別後，系統要求用戶提出具體問題**

#### 步驟 5：提交問題（根據類別和核心生命靈數提供針對性分析）
```jsonc
POST /life/paid/api/chat
Request: {
  "session_id": "session-456",
  "message": "我今年適合創業嗎？"
}
Response: {
  "session_id": "session-456",
  "response": "根據您的核心生命靈數 8 以及財運事業這個面向，讓我為您分析...\n\n生命靈數 8 在創業方面具有天生的優勢。您的領導力、商業頭腦和掌控全局的能力，都是創業成功的關鍵要素...\n\n（針對創業問題的深度分析，基於核心生命靈數 8 和財運事業類別）",
  "state": "continue_selection",
  "current_module": "core",
  "number": 8
}
```
> ✨ **根據已計算的核心生命靈數（8）、選擇的類別（財運事業）和用戶的具體問題，提供深度個性化分析**

#### 步驟 6：選擇繼續問問題（付費版專屬）
```jsonc
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
```jsonc
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
```jsonc
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
```jsonc
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
```jsonc
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
```jsonc
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
```jsonc
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
```jsonc
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
```jsonc
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
```jsonc
{
  "session_id": "string"  // 可選：要刪除的會話ID
}
```

#### Response
```jsonc
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
- `grid` - 天賦優勢與在職特質 九宮格 (若無連線，將提供替代指引建議)
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

---

## 🎨 前端 UI 顯示指南 (Frontend UI Guide)

本節說明在不同狀態下，前端應顯示的 UI 元件與互動方式。

### 1. 生命靈數 (Life Number)

| 狀態 (`state`) | 說明 | 建議 UI 顯示 |
|---|---|---|
| `waiting_basic_info` | 等待基本資訊 | **表單輸入**：<br>- 姓名 (Text)<br>- 性別 (Select: 男/女)<br>- 生日 (Date Picker)<br>- 英文名 (Text, 僅付費版) |
| `waiting_module_selection` | 等待模組選擇 | **按鈕列表**：<br>- 免費版：顯示 4 個模組按鈕 (Core, Birthday, Year, Grid)<br>- 付費版：顯示 10 個模組按鈕 |
| `core_category_selection` | 核心模組類別選擇<br>(僅付費版 Core) | **按鈕列表**：<br>- 財運事業<br>- 家庭人際<br>- 自我成長<br>- 目標規劃 |
| `waiting_core_question` | 等待核心模組問題<br>(僅付費版 Core) | **文字輸入框**：<br>- 提示語：「請輸入您想了解的具體問題...」<br>- 發送按鈕 |
| `waiting_question` | 等待深度問題<br>(付費版深度對話) | **文字輸入框**：<br>- 提示語：「請輸入您的問題...」<br>- 發送按鈕 |
| `continue_selection` | 繼續選項 | **操作按鈕**：<br>- 「繼續問問題」(僅付費版)<br>- 「選擇其他生命靈數」<br>- 「離開」 |
| `completed` | 已完成 | **結束畫面**：<br>- 顯示總結與祝福<br>- 「重新開始」按鈕 |

### 2. 天使數字 (Angel Number)

| 狀態 (`state`) | 說明 | 建議 UI 顯示 |
|---|---|---|
| `waiting_basic_info` | 等待基本資訊 | **表單輸入**：<br>- 姓名 (Text)<br>- 性別 (Select: 男/女)<br>- 生日 (Date Picker) |
| `waiting_angel_number` | 等待天使數字 | **免費版**：下拉選單或按鈕 (1111, 2222... 9999)<br>**付費版**：數字輸入框 (Number Input) |
| `asking_for_question` | 詢問是否有問題<br>(僅付費版) | **對話介面**：<br>- 文字輸入框 (輸入問題)<br>- 「沒有問題/謝謝」按鈕 (結束對話)<br>- **提示**：可輸入 1~4 位純數字切換新天使數字 |
| `conversation` | 持續深度對話<br>(僅付費版) | **對話介面**：<br>- 文字輸入框 (輸入追問)<br>- 「沒有問題/謝謝」按鈕 (結束對話)<br>- **提示**：可輸入 1~4 位純數字切換新天使數字 |
| `completed` | 已完成 | **結束畫面**：<br>- 顯示完整解讀<br>- 「重新開始」按鈕 |

### 3. 擲筊 (Divination)

| 狀態 (`state`) | 說明 | 建議 UI 顯示 |
|---|---|---|
| `waiting_basic_info` | 等待基本資訊 | **表單輸入**：<br>- 姓名 (Text)<br>- 性別 (Select: 男/女)<br>- 生日 (Date Picker) |
| `waiting_question` | 等待提問 | **文字輸入框**：<br>- 提示語：「請誠心輸入您的問題...」<br>- 「開始擲筊」按鈕 |
| `divining` | 擲筊中 (過渡狀態) | **動畫效果**：<br>- 顯示擲筊動畫或 Loading 效果<br>- 隨後自動顯示結果 |
| `asking_for_question` | 持續提問<br>(僅付費版) | **對話介面**：<br>- 文字輸入框 (輸入追問)<br>- 「沒有問題/謝謝」按鈕 (結束對話) |
| `completed` | 已完成 | **結束畫面**：<br>- 免費版：顯示單次擲筊結果 (聖/笑/陰) 與解讀<br>- 付費版：顯示三次擲筊結果（如「聖筊 → 笑筊 → 陰筊」）+ 組合類型 + AI 解讀<br>- 「重新開始」按鈕 |

### 4. 黃道吉日 (Auspicious Date)

| 狀態 (`state`) | 說明 | 建議 UI 顯示 |
|---|---|---|
| `waiting_basic_info` | 等待基本資訊 | **表單輸入**：<br>- 姓名 (Text)<br>- 性別 (Select: 男/女)<br>- 生日 (Date Picker)<br>- 生肖 (Select: 鼠/牛/虎/兔/龍/蛇/馬/羊/猴/雞/狗/豬) |
| `waiting_category_and_date` | 等待分類與日期選擇 | **方式一（推薦）**：<br>- **分類選擇器**：5 個按鈕或下拉選單<br>  - 生活日常 (`daily_life`)<br>  - 家庭居所 (`family_home`)<br>  - 感情人際 (`relationship`)<br>  - 喜慶大事 (`celebration`)<br>  - 工作事業 (`work_career`)<br>- **日期選擇器**：日曆元件 (Calendar Picker)<br><br>**方式二（彈性）**：<br>- 文字輸入框：允許輸入「家庭居所，2025-12-15」 |
| `waiting_specific_question` | 等待具體事項描述 | **文字輸入框**：<br>- 提示語：「請描述您具體想做的事情...」<br>- 範例：「我要搬新家」、「簽約買房」<br>- 發送按鈕 |
| `providing_dates` | 提供吉日建議 | **結果顯示**：<br>- 顯示所選日期的黃曆資訊<br>- 顯示「宜」「忌」事項<br>- AI 建議與注意事項<br>- 是否沖生肖提醒 |
| `asking_for_question` | 詢問是否有其他問題<br>(僅付費版) | **對話介面**：<br>- 顯示神明的黃曆解讀結果<br>- 文字輸入框（輸入追問，如「有什麼需要注意的？」）<br>- 「沒有問題/謝謝」按鈕（結束對話）<br>- **提示**：AI 會以神明口吻繼續回答 |
| `completed` | 已完成 | **結束畫面**：<br>- **免費版**：顯示完整吉日分析<br>- **付費版**：顯示完整分析 + 神明結束語<br>- 「重新開始」按鈕 |

---

## ⚠️ 錯誤處理

### 缺少 session_id
```jsonc
{
  "error": "缺少 session_id",
  "message": "請先調用 init_with_tone 初始化會話"
}
```
**HTTP Status**: 400

### 會話不存在或已過期
```jsonc
{
  "error": "會話不存在或已過期",
  "message": "請重新調用 init_with_tone 初始化會話",
  "session_id": "原session_id"
}
```
**HTTP Status**: 404

### Redis 連線錯誤
```jsonc
{
  "error": "Session 存儲服務暫時不可用",
  "message": "請稍後再試"
}
```
**HTTP Status**: 503

### OpenAI API 錯誤
```jsonc
{
  "error": "AI 服務暫時不可用",
  "message": "請稍後再試"
}
```
**HTTP Status**: 503

### 請求超時
Cloud Run 預設超時為 120 秒，超過此時間將返回：
```jsonc
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

## 🔮 天使數字 API (Angel Number)

### 功能說明

天使數字 API 提供天使數字解讀服務。當使用者反覆看到相同的數字(如 1111、2222 等),系統會透過 AI 解讀其背後的靈性意義。

**特色：**
- 支援 9 種天使數字(1111-9999)
- 3 種語氣選項(friendly, caring, ritual)
- 簡化的對話流程
- 使用 AI 自動提取基本資訊
- 完整的靈性解讀與指引

---

### 天使數字端點

#### **POST** `/angel/free/api/init_with_tone`

初始化天使數字對話並選擇語氣。

**Request Body:**
```jsonc
{
  "tone": "string"  // 語氣選擇: friendly, caring, ritual
}
```

**Response:**
```jsonc
{
  "session_id": "uuid-string",  // 會話ID,前端必須保存
  "response": "問候語內容",
  "state": "waiting_basic_info",
  "requires_input": true
}
```

**範例:**
```bash
curl -X POST http://localhost:8080/angel/free/api/init_with_tone \
  -H "Content-Type: application/json" \
  -d '{"tone": "friendly"}'
```

---

#### **POST** `/angel/free/api/chat`

天使數字對話互動。

**Request Body:**
```jsonc
{
  "session_id": "string",  // 必須：由 init_with_tone 返回的會話ID
  "message": "string"      // 必須：用戶輸入內容
}
```

**Response:**
```jsonc
{
  "session_id": "string",
  "response": "AI回應內容",
  "state": "當前狀態",
  "angel_number": "1111",  // 如有
  "show_angel_number_selector": true,  // 如需顯示選單
  "requires_input": true/false
}
```

**可能的狀態值:**
- `waiting_basic_info` - 等待基本資訊(姓名、性別、生日)
- `waiting_angel_number` - 等待天使數字選擇
- `completed` - 已完成

---

#### **POST** `/angel/paid/api/init_with_tone`

付費版初始化，Request/Response 格式同免費版，但 `tone` 可選 10 種高級語氣（如 `guan_yu`、`michael` 等）。

**範例:**
```bash
curl -X POST http://localhost:8080/angel/paid/api/init_with_tone \
  -H "Content-Type: application/json" \
  -d '{"tone": "guan_yu"}'
```

---

#### **POST** `/angel/paid/api/chat`

付費版對話互動，Request 格式同免費版。

**Response 額外欄位:**
```jsonc
{
  "session_id": "string",
  "response": "AI回應內容",
  "state": "當前狀態",
  "angel_number": "123",       // 解讀完成時回傳
  "pattern": "ascending",      // 智能模式識別結果（如 repetition, ascending, mirror 等）
  "requires_input": true/false
}
```

**可能的狀態值:**
- `waiting_basic_info` - 等待基本資訊
- `waiting_angel_number` - 等待天使數字輸入（支援任意 1~4 位數字）
- `asking_for_question` - 解讀完成，詢問是否有問題
- `conversation` - 持續深度對話中
- `completed` - 已完成

> 💡 **動態切換數字**：在 `asking_for_question` 或 `conversation` 狀態下，用戶輸入 1~4 位純數字（且與目前數字不同）即可切換至新數字分析，無需重新初始化 Session。

---

#### **POST** `/angel/paid/api/reset`

付費版重置會話，格式同免費版 `/angel/free/api/reset`。

---

#### **POST** `/angel/free/api/reset`

重置天使數字會話。

**Request Body:**
```jsonc
{
  "session_id": "string"  // 可選：要刪除的會話ID
}
```

**Response:**
```jsonc
{
  "success": true
}
```

---

### 天使數字對話流程

```
步驟 1: 初始化（init_with_tone）
    ↓
步驟 2: 提交基本資訊（姓名、性別、生日）
    ↓ (AI 自動解析)
步驟 3: 選擇天使數字（1111-9999）
    ↓
步驟 4: 獲得完整解讀
    ↓
步驟 5: 完成（可重新開始）
```

---

### 完整對話範例

#### 步驟 1：初始化
```bash
curl -X POST http://localhost:8080/angel/free/api/init_with_tone \
  -H "Content-Type: application/json" \
  -d '{"tone": "friendly"}'
```

**Response:**
```json
{
  "session_id": "abc-123",
  "response": "嗨～歡迎來到 天使數字 AI 對話空間 💫\n\n你是不是最近也常常看到某個數字一直出現呢？...",
  "state": "waiting_basic_info",
  "requires_input": true
}
```

#### 步驟 2：提交基本資訊
```bash
curl -X POST http://localhost:8080/angel/free/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123",
    "message": "王小明 男 1990/07/12"
  }'
```

**Response:**
```json
{
  "session_id": "abc-123",
  "response": "王小明,你好呀～我這邊已經收到你的資料囉 ✨\n\n接下來想請你告訴我...",
  "state": "waiting_angel_number",
  "show_angel_number_selector": true,
  "requires_input": false
}
```

#### 步驟 3：選擇天使數字
```bash
curl -X POST http://localhost:8080/angel/free/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123",
    "message": "1111"
  }'
```

**Response:**
```json
{
  "session_id": "abc-123",
  "response": "王小明,我看到了你的天使數字 1111！✨\n\n（完整的天使數字解讀內容...）",
  "state": "completed",
  "angel_number": "1111",
  "requires_input": false
}
```

---

### 支援的天使數字

| 數字 | 標題 | 核心意義 |
|------|------|----------|
| 1111 | 新開始與精神覺醒 | 新開始、思維具化、領導力爆發 |
| 2222 | 和諧與平衡 | 和諧平衡、持續進展、人際連結 |
| 3333 | 成長與創意 | 成長擴展、創意表達、靈性引導 |
| 4444 | 穩定與守護 | 穩定基礎、感恩、神聖守護 |
| 5555 | 重大轉變 | 重大轉變、積極變革、靈性覺醒 |
| 6666 | 愛與和諧 | 愛與家庭、支持、平衡物質與靈性 |
| 7777 | 靈性覺醒 | 靈性覺醒、智慧、療癒與突破 |
| 8888 | 豐盛與財富 | 豐盛財富、無限能量、自我成長 |
| 9999 | 完成與新旅程 | 完成、新旅程、心靈轉化 |

---

### 語氣選項說明

**friendly (親切版):**
- 輕鬆友善,像朋友聊天
- 使用「你」稱呼
- 語調活潑自然

**caring (貼心版):**
- 溫暖關懷,像靈性導師
- 使用「你」或「您」稱呼
- 充滿同理心與溫柔

**ritual (儀式版):**
- 莊重神聖,充滿儀式感
- 使用「您」稱呼
- 帶有神性與靈性氛圍

---

## 🎯 AI 全域規則系統

### 概述

所有四個模組（生命靈數、天使數字、擲筊、黃道吉日）共用一套**動態載入的全域規則**，這些規則從 Supabase `ai_global_rules` 表中讀取，業主可以隨時新增或修改規則，系統會自動在 5 分鐘內更新。

### 設計目標

1. **統一管理**：所有模組的回答原則、禁語、內容限制統一在一個地方管理
2. **動態更新**：無需重新部署，直接在 Supabase UI 修改即可生效
3. **容錯機制**：當資料庫不可用時，使用硬編碼的 fallback 規則
4. **性能優化**：使用 5 分鐘緩存，減少資料庫查詢

### 資料表結構：`ai_global_rules`

| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| `id` | BIGINT | 主鍵，自動遞增 |
| `created_at` | TIMESTAMP | 創建時間，自動生成 |
| `rule_key` | TEXT | 規則標識（例如：`avoid_absolute_statements`） |
| `rule_name` | TEXT | 規則名稱（例如：`避免絕對性判斷`） |
| `rule_content` | TEXT | 規則的完整文字內容，會直接添加到 LLM prompt 中 |

### 當前全域規則

系統預設包含以下三個全域規則：

#### 1. 避免絕對性判斷
```
rule_key: avoid_absolute_statements
rule_name: 避免絕對性判斷
rule_content:
【回答原則】避免給予絕對性的判斷，改用建議導向的表達：
- 禁止使用「你一定會」、「你絕對不該」、「必須」、「千萬不要」等絕對性表達
- 請使用「建議」、「可以考慮」、「值得留意」、「或許」等引導性語言
- 提供多種可能性和方向，而非單一確定的結論
```

#### 2. 禁止「因果報應」
```
rule_key: forbid_karma_punishment
rule_name: 禁止使用「因果報應」
rule_content:
【禁語要求】
- **嚴格禁止使用「因果報應」四字，若需表達相關概念，請統一改用「因果回饋分析」或「業力課題」。**
```

#### 3. 敏感內容過濾
```
rule_key: filter_sensitive_content
rule_name: 敏感內容過濾
rule_content:
【內容限制】嚴格禁止提供以下類型的建議或解讀：
- 投資、買賣、獲利、股票、期貨相關建議
- 彩券、樂透、賭博、博弈相關指引
- 任何保證成功、一定賺錢的承諾

若用戶詢問上述內容，請回應：「本平台不提供投資、賭博或保證獲利等相關建議。我們只能提供一般的文化與資料說明。如果你有其他生活上的事項想查詢，歡迎重新詢問！」
```

### 技術實現

#### 規則載入機制

**文件**: `shared/rule_loader.py`

**主要函數**:
- `load_global_rules()`: 從資料庫載入所有規則並組合成字符串
- `get_fallback_rules()`: 當資料庫不可用時的備用規則
- `clear_rules_cache()`: 手動清除緩存（用於測試）

**緩存策略**:
- 緩存有效期：5 分鐘
- 自動刷新：緩存過期後下一次請求時自動重新載入
- 強制刷新：調用 `load_global_rules(force_refresh=True)`

#### 各模組整合情況

| 模組 | 文件 | 整合位置 |
|------|------|----------|
| **生命靈數** | `lifenum_api.py` | `execute_module()` 函數的 system prompt |
| **天使數字** | `angelnum_api.py` | `WAITING_BASIC_INFO` 和 `CONVERSATION` 狀態 |
| **擲筊** | `divination/agent.py` | `generate_interpretation()`、`generate_followup_response()`、`generate_three_cast_interpretation()` |
| **黃道吉日** | `auspicious_api.py` | `WAITING_SPECIFIC_QUESTION` 和 `ASKING_FOR_QUESTION` 狀態 |

### 管理指南

#### 如何新增規則

1. 登入 Supabase Dashboard
2. 進入 `ai_global_rules` 表
3. 點擊「Insert Row」
4. 填寫以下欄位：
   - `rule_key`: 規則的英文標識（snake_case）
   - `rule_name`: 規則的中文名稱
   - `rule_content`: 規則的完整內容（會直接添加到 prompt）
5. 儲存後，系統會在 5 分鐘內自動載入新規則

#### 如何修改規則

1. 在 Supabase 中找到對應的規則行
2. 直接編輯 `rule_content` 欄位
3. 儲存後，系統會在 5 分鐘內自動更新

#### 如何停用規則

1. 直接刪除對應的規則行
2. 系統會在 5 分鐘內停止使用該規則

#### 立即生效（開發環境）

如需立即測試規則變更，可以重啟服務：
```bash
# 本地開發
pkill -f "python app.py"
python app.py

# GCP Cloud Run 會在下次冷啟動時自動刷新
```

### 容錯機制

**情境 1：Supabase 暫時不可用**
- ✅ 系統自動使用硬編碼的 fallback 規則
- ✅ AI 回應仍然包含基本的規則限制
- ⚠️ 新增的自定義規則暫時不會生效

**情境 2：資料表為空**
- ✅ 系統使用 fallback 規則
- ⚠️ 會在日誌中記錄警告訊息

**情境 3：緩存過期但資料庫查詢失敗**
- ✅ 保留上一次成功載入的緩存
- ✅ 直到資料庫恢復為止

### 最佳實踐

1. **測試新規則**：在非高峰時段新增或修改規則
2. **規則內容格式**：
   - 使用清晰的標題（如：【回答原則】、【禁語要求】）
   - 使用列表格式增加可讀性
   - 避免過長的單行文字
3. **規則順序**：規則按 `id` 升序排列，較早的規則會先出現在 prompt 中
4. **避免重複**：不要在多個規則中重複相同的限制

---

## 📌 版本資訊
- **API Version**: 1.0.0
- **Last Updated**: 2026-01-26
- **部署平台**: GCP Cloud Run
- **文檔維護**: 每次 API 變更時同步更新
- **新增功能**: AI 全域規則動態載入系統

