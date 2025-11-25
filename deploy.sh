#!/bin/bash
# GCP Cloud Run 部署腳本

set -e  # 遇到錯誤立即退出

# ============================================
# 配置區域（請根據需要修改）
# ============================================
PROJECT_ID="crm-llm-api-463205"  # GCP Project ID
REGION="asia-east1"  # 亞洲東部（台灣）
SERVICE_NAME="life-number-backend"

# ============================================
# 顏色輸出
# ============================================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 開始部署到 GCP Cloud Run...${NC}\n"

# ============================================
# 1. 檢查 gcloud 是否安裝
# ============================================
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI 未安裝${NC}"
    echo "請先安裝: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo -e "${GREEN}✅ gcloud CLI 已安裝${NC}"

# ============================================
# 2. 設置 GCP 項目
# ============================================
echo -e "\n${YELLOW}📝 設置 GCP 項目: ${PROJECT_ID}${NC}"
gcloud config set project ${PROJECT_ID}

# ============================================
# 3. 啟用必要的 API
# ============================================
echo -e "\n${YELLOW}🔧 啟用必要的 GCP API...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    secretmanager.googleapis.com \
    containerregistry.googleapis.com

# ============================================
# 4. 創建 Secret Manager 密鑰（如果不存在）
# ============================================
echo -e "\n${YELLOW}🔐 設置 Secret Manager...${NC}"

# 從 .env 文件讀取環境變量
if [ -f ".env" ]; then
    source .env
    
    # 檢查必要的環境變量
    REQUIRED_VARS=("OPENAI_API_KEY" "REDIS_HOST" "REDIS_PORT" "REDIS_PASSWORD" "REDIS_USERNAME")
    MISSING_VARS=0
    
    for VAR in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!VAR}" ]; then
            echo -e "${RED}❌ 錯誤: .env 文件中缺少 ${VAR}${NC}"
            MISSING_VARS=1
        fi
    done
    
    if [ $MISSING_VARS -eq 1 ]; then
        exit 1
    fi
    
    # 創建或更新 OPENAI_API_KEY
    if gcloud secrets describe OPENAI_API_KEY --project=${PROJECT_ID} &>/dev/null; then
        echo "更新 OPENAI_API_KEY..."
        echo -n "${OPENAI_API_KEY}" | gcloud secrets versions add OPENAI_API_KEY --data-file=-
    else
        echo "創建 OPENAI_API_KEY..."
        echo -n "${OPENAI_API_KEY}" | gcloud secrets create OPENAI_API_KEY --data-file=- --replication-policy="automatic"
    fi
    
    # 創建或更新 Redis 相關密鑰
    echo "設置 Redis 配置..."
    
    # REDIS_HOST
    if gcloud secrets describe REDIS_HOST --project=${PROJECT_ID} &>/dev/null; then
        echo -n "${REDIS_HOST}" | gcloud secrets versions add REDIS_HOST --data-file=-
    else
        echo -n "${REDIS_HOST}" | gcloud secrets create REDIS_HOST --data-file=- --replication-policy="automatic"
    fi
    
    # REDIS_PORT
    if gcloud secrets describe REDIS_PORT --project=${PROJECT_ID} &>/dev/null; then
        echo -n "${REDIS_PORT}" | gcloud secrets versions add REDIS_PORT --data-file=-
    else
        echo -n "${REDIS_PORT}" | gcloud secrets create REDIS_PORT --data-file=- --replication-policy="automatic"
    fi
    
    # REDIS_PASSWORD
    if gcloud secrets describe REDIS_PASSWORD --project=${PROJECT_ID} &>/dev/null; then
        echo -n "${REDIS_PASSWORD}" | gcloud secrets versions add REDIS_PASSWORD --data-file=-
    else
        echo -n "${REDIS_PASSWORD}" | gcloud secrets create REDIS_PASSWORD --data-file=- --replication-policy="automatic"
    fi
    
    # REDIS_USERNAME
    if gcloud secrets describe REDIS_USERNAME --project=${PROJECT_ID} &>/dev/null; then
        echo -n "${REDIS_USERNAME}" | gcloud secrets versions add REDIS_USERNAME --data-file=-
    else
        echo -n "${REDIS_USERNAME}" | gcloud secrets create REDIS_USERNAME --data-file=- --replication-policy="automatic"
    fi
    
    echo -e "${GREEN}✅ Secrets 設置完成${NC}"
else
    echo -e "${RED}❌ 找不到 .env 文件${NC}"
    echo "請確保根目錄下有 .env 文件，並包含以下變量："
    echo "OPENAI_API_KEY, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_USERNAME"
    exit 1
fi

# ============================================
# 5. 構建並部署
# ============================================
echo -e "\n${YELLOW}🏗️  構建 Docker 鏡像...${NC}"

# 生成構建標籤（使用時間戳）
BUILD_TAG=$(date +%Y%m%d-%H%M%S)
echo -e "構建標籤: ${BUILD_TAG}"

# 執行構建（使用替換變量）
gcloud builds submit --config=cloudbuild.yaml \
    --substitutions=COMMIT_SHA=${BUILD_TAG}

echo -e "\n${GREEN}✅ 部署完成！${NC}"

# ============================================
# 6. 設置公開訪問（允許未經身份驗證的請求）
# ============================================
echo -e "\n${YELLOW}🔓 設置公開訪問權限...${NC}"
gcloud run services add-iam-policy-binding ${SERVICE_NAME} \
    --region=${REGION} \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --project=${PROJECT_ID}

echo -e "${GREEN}✅ 已允許公開訪問${NC}"

# ============================================
# 7. 獲取服務 URL
# ============================================
echo -e "\n${YELLOW}📍 獲取服務 URL...${NC}"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --format='value(status.url)')

echo -e "\n${GREEN}🎉 部署成功！${NC}"
echo -e "\n服務 URL: ${GREEN}${SERVICE_URL}${NC}"
echo -e "\n測試 API:"
echo -e "  ${YELLOW}curl ${SERVICE_URL}/health${NC}"
echo -e "\n查看日誌:"
echo -e "  ${YELLOW}gcloud run services logs read ${SERVICE_NAME} --region=${REGION}${NC}"

