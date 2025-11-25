# 使用官方 Python 運行時作為父鏡像
FROM python:3.12-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 設置環境變量
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# 暴露端口（Cloud Run 會自動設置 PORT 環境變量）
EXPOSE 8080

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# 使用 gunicorn 運行應用
# Cloud Run 最佳實踐：
# - 單個 worker（Cloud Run 會自動擴展實例）
# - 設置超時時間
# - 綁定到 0.0.0.0 以接受來自 Cloud Run 的請求
CMD exec gunicorn app:app \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 8 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

