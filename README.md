# 生命靈數後端 - 整合版本

## 專案說明

這是生命靈數系統的統一後端,同時支持免費版和付費版,並包含天使數字解讀功能。

### 🎯 架構特點

### 單一代碼庫設計
- ✅ 一個 `app.py` 統一處理所有請求
- ✅ **資料庫驅動**：所有靈數資料從 Supabase 動態讀取
- ✅ 配置驅動：所有差異在 `lifenum/version_config.py`
- ✅ 語氣配置：`lifenum/tone_config.py`
- ✅ 會話隔離：免費/付費完全獨立
- ✅ **四大模組**：生命靈數、天使數字、神諭占卜、黃道吉日

### 資料庫架構（Supabase）
本系統使用 **Supabase (PostgreSQL)** 作為主資料庫，所有生命靈數、天使數字、占卜解讀的內容都儲存在資料庫中：

**生命靈數相關資料表：**
- `lifenum_main` - 核心生命靈數 (1-9) 的詳細資料
- `lifenum_birthday` - 生日靈數解讀
- `lifenum_personal_year` - 流年運勢
- `lifenum_grid_lines` - 九宮格連線解讀
- `lifenum_grid_missing` - 九宮格缺數解讀
- `lifenum_soul` - 靈魂數
- `lifenum_personality` - 人格數
- `lifenum_expression` - 表達數
- `lifenum_maturity` - 成熟數
- `lifenum_challenge` - 挑戰數
- `lifenum_karma` - 業力數

**天使數字相關資料表：**
- `angel_number_meanings` - 天使數字 (1111-9999) 的核心意義
- `angel_number_basic_energy` - 單一數字 (0-9) 的基礎能量

**占卜相關資料表：**
- `divination_combinations` - 擲筊組合類型（10種組合：聖聖聖、聖聖陰等）
- `divination_tone_greetings` - 不同神明的問候語與語氣配置

**黃道吉日相關資料表：**
- `auspicious_calendar` - 黃曆月份資料（包含每日宜忌、沖煞、吉時等完整資訊）

### 版本差異

**免費版**：
- 4 個模組：core, birthday, year, grid
- 3 種語氣：friendly, caring, ritual
- 無深度對話
- 無類別選擇
- 不需要英文名

**付費版**：
- 10 個模組：core, birthday, year, grid, soul, personality, expression, maturity, challenge, karma
- 10 種語氣：guan_yu, michael, gabriel, raphael, uriel, zadkiel, jophiel, chamuel, metatron, ariel
- 支持持續對話（每個模組完成後可「繼續問問題」）
- core 模組有類別選擇（財運事業、家庭人際、自我成長、目標規劃）
- 部分模組需要英文名（soul, personality, expression）
- 離開時自動生成對話總結和能量調整建議（水晶、點燈推薦）

## 📋 API 端點

### 生命靈數 (Life Number)

**免費版:**
- `POST /life/free/api/init_with_tone` - 初始化（選擇語氣）
- `POST /life/free/api/chat` - 對話
- `POST /life/free/api/reset` - 重置

**付費版:**
- `POST /life/paid/api/init_with_tone` - 初始化（選擇語氣）
- `POST /life/paid/api/chat` - 對話
- `POST /life/paid/api/reset` - 重置

### 天使數字 (Angel Number)
- ✅ **免費版**:
  - `POST /angel/free/api/init_with_tone`
  - `POST /angel/free/api/chat`
  - `POST /angel/free/api/reset`
  - 支援 9 組固定天使數字 (1111-9999)
  - 3 種基礎語氣

- ✅ **付費版**:
  - `POST /angel/paid/api/init_with_tone`
  - `POST /angel/paid/api/chat`
  - `POST /angel/paid/api/reset`
  - **智能模式識別**: 支援任意數字，自動識別重複、階梯、鏡像等 8 種模式
  - **深度對話**: 可針對解讀結果進行多輪提問
  - **10 種高級語氣**: 包含關聖帝君、大天使米迦勒等
  - **完整上下文**: AI 記住對話歷史，提供連貫的指引
### 擲筊 (Divination)
- ✅ **免費版**:
  - `POST /divination/free/api/init_with_tone`
  - `POST /divination/free/api/chat`
  - `POST /divination/free/api/reset`
  - 3 種基礎語氣 (friendly, caring, ritual)
  - 隨機擲筊結果 (聖筊/笑筊/陰筊)

- ✅ **付費版**:
  - `POST /divination/paid/api/init_with_tone`
  - `POST /divination/paid/api/chat`
  - `POST /divination/paid/api/reset`
  - **9 種神明語氣**: 包含關聖帝君、媽祖、月老等
  - **三次擲筊**: 每次問神都會擲三次，綜合分析
  - **10 種組合解讀**: 根據三次結果組合（如聖聖陰、陰陰聖等）提供不同神意
  - **AI 智能解讀**: 根據神明性格、組合類型與問題進行深度解讀
  - **持續對話**: 可針對解讀結果進行多輪提問

### 黃道吉日 (Auspicious Date)
- ✅ **免費版** (已實作):
  - `POST /auspicious/free/api/init_with_tone`
  - `POST /auspicious/free/api/chat`
  - `POST /auspicious/free/api/reset`
  - **3 種基礎語氣**: friendly, caring, ritual
  - **5 種分類**: 生活日常、家庭居所、感情人際、喜慶大事、工作事業
  - **資料庫驅動**: 黃曆資料從 Supabase 查詢
  - **智能日期選擇**: 支援按鈕選擇或文字輸入日期
  - **AI 分析**: 根據黃曆「宜」「忌」欄位進行分析
  - **單次查詢**: 查詢完成後對話結束

- ✅ **付費版** (已實作):
  - `POST /auspicious/paid/api/init_with_tone`
  - `POST /auspicious/paid/api/chat`
  - `POST /auspicious/paid/api/reset`
  - **9 種神明語氣**: 包含關聖帝君、媽祖、月老等
  - **深度解讀**: 以神明性格進行個性化黃曆分析
  - **持續對話**: 查詢後可針對結果進行多輪追問
  - **智能結束**: 檢測結束關鍵詞（「謝謝」、「沒有」等），給出神明特色結束語

- `GET /health` - 健康檢查
- `GET /` - API 資訊


## 🔧 環境變數設定

在專案根目錄建立 `.env` 檔案，包含以下必要環境變數：

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o

# Supabase 資料庫
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Redis (Session 管理)
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_USERNAME=default

# 其他
PROJECT_LOCALE=zh-TW
```

## 🚀 啟動

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動服務
python app.py
```

服務將在 `http://localhost:8080` 啟動

## 🧪 測試

```bash
# 免費版測試
curl -X POST http://localhost:8080/life/free/api/init_with_tone \
  -H "Content-Type: application/json" \
  -d '{"tone": "friendly"}'

# 付費版測試
curl -X POST http://localhost:8080/life/paid/api/init_with_tone \
  -H "Content-Type: application/json" \
  -d '{"tone": "guan_yu"}'
```

## 📁 專案結構

```
Life-Number-Backend/
├── app.py                      # 主應用
├── lifenum_api.py              # 生命靈數 API Blueprint
├── angelnum_api.py             # 天使數字 API Blueprint
├── divination_api.py           # 擲筊 API Blueprint
├── lifenum/                    # 生命靈數模組
│   ├── version_config.py      # 版本配置
│   ├── tone_config.py         # 語氣配置
│   ├── agent.py               # Agent 類
│   ├── utils.py               # 工具函數
│   ├── config.py              # 環境配置
│   ├── core_information/      # 核心資訊檔案
│   └── modules/               # 10個計算模組
│       ├── core.py
│       ├── birthday.py
│       ├── personal_year.py
│       ├── grid.py
│       ├── soul_number.py
│       ├── personality.py
│       ├── expression.py
│       ├── maturity.py
│       ├── challenge.py
│       └── karma.py
├── angelnum/                   # 天使數字模組
│   ├── agent.py               # Angel Number Agent
│   └── modules/
│       └── angel_numbers.py   # 天使數字資料
├── divination/                 # 擲筊模組
│   ├── agent.py               # Divination Agent
│   └── session_store.py       # Session 管理
├── shared/                     # 共享基礎設施
│   ├── gpt_client.py          # GPT 客戶端
│   ├── redis_client.py        # Redis 連線
│   └── session_store.py       # Session 管理
├── requirements.txt
└── README.md
```

## 🔧 配置文件

### `lifenum/version_config.py`
定義免費版和付費版的所有差異：
- 可用模組列表
- 可用語氣列表
- 功能開關
- 模組說明

### `lifenum/tone_config.py`
定義所有語氣的具體表達：
- 問候語
- 繼續選項
- 完成訊息

## 🌐 部署到 Cloud Run

```bash
# 構建 Docker 映像
docker build -t life-number-backend .

# 推送到 GCP
docker tag life-number-backend gcr.io/YOUR-PROJECT/life-number-backend
docker push gcr.io/YOUR-PROJECT/life-number-backend

# 部署到 Cloud Run
gcloud run deploy life-number-backend \
  --image gcr.io/YOUR-PROJECT/life-number-backend \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated
```

## 🔄 付費版對話流程

### 完整狀態機

1. **INIT** → 初始化，選擇語氣
2. **WAITING_BASIC_INFO** → 等待用戶輸入姓名、性別、生日、英文名
3. **WAITING_MODULE_SELECTION** → 等待用戶選擇模組
4. **CORE_CATEGORY_SELECTION** → (僅 core 模組) 選擇類別
5. **WAITING_CORE_QUESTION** → (僅 core 模組) 等待用戶問題
6. **WAITING_QUESTION** → (其他模組深度對話) 等待用戶問題
7. **CONTINUE_SELECTION** → 選擇繼續選項
   - 繼續問問題 → 回到 WAITING_QUESTION
   - 其他生命靈數 → 回到 WAITING_MODULE_SELECTION
   - 離開 → COMPLETED（生成總結和能量調整建議）
8. **COMPLETED** → 完成

### Core 模組特殊流程

```
選擇 core → 選擇類別（財運事業/家庭人際/自我成長/目標規劃）→ 輸入問題 → 獲得解析 → 繼續選項
```

### 深度對話功能

每個模組完成後，可選擇「繼續問問題」進行深度對話：

```
完成模組解析 → 繼續問問題 → 輸入深度問題 → 獲得進一步解析 → 繼續選項
```

### 離開時的對話總結

當用戶選擇「離開」時，系統會：
1. 總結今天探索的所有模組
2. 根據使用的模組推薦對應的水晶和點燈商品
3. 生成符合當前語氣的祝福語

## 📝 前端調用

前端需要根據版本選擇對應的 API 路徑：

```javascript
// 免費版
const API_BASE = '/free';

// 付費版
const API_BASE = '/paid';

// API 調用
fetch(`${API_BASE}/${API_BASE}/api/chat`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: 'core', tone: 'friendly'}),
  credentials: 'include'
});
```

## ✅ 完成的功能

### 生命靈數 (Life Number)
- [x] 統一後端架構
- [x] 免費版 3 種語氣
- [x] 付費版 10 種語氣
- [x] 版本配置驅動
- [x] 會話隔離
- [x] 完整狀態機
- [x] 模組執行邏輯
- [x] 繁體中文
- [x] **付費版特殊功能**：
  - [x] Core 模組類別選擇（財運事業、家庭人際、自我成長、目標規劃）
  - [x] 深度對話功能（每個模組可繼續問問題）
  - [x] 離開時生成對話總結
  - [x] 根據使用模組推薦水晶和點燈商品

### 天使數字 (Angel Number)
- [x] 天使數字解讀功能
- [x] 支援 9 種天使數字 (1111-9999)
- [x] 3 種語氣選項 (friendly, caring, ritual)
- [x] AI 自動提取基本資訊
- [x] 完整的靈性解讀與指引
- [x] 簡化的對話流程
- [x] Redis Session 管理

### 擲筊 (Divination)
- [x] 擲筊占卜功能
- [x] 免費版 3 種語氣 (friendly, caring, ritual)
- [x] 付費版 9 種神明語氣 (關聖帝君、媽祖、月老等)
- **擲筊模組**：
  - 設計了一套結合傳統擲筊文化與 AI 解讀的系統。
  - **免費版**：提供基礎的單次擲筊體驗與固定模板回應。
  - **付費版**：提供完整的三次擲筊流程、10種組合分析、以及結合9種神明性格的 AI 深度解讀。
  - **互動式體驗**：模擬真實擲筊儀式，包含「稟報問題」->「誠心默念」->「擲筊」的完整互動流程。
- [x] AI 自動提取基本資訊
- [x] 免費版單次擲筊結果模擬
- [x] **付費版三次擲筊** + 10 種組合類型分析
- [x] AI 智能解讀神意 (付費版，根據組合類型 + 神明性格)
- [x] 持續對話功能 (付費版)
- [x] Redis Session 管理
```
