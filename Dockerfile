
# 使用官方 Python 3.9 slim 映像檔作為基礎
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式程式碼
COPY . .

# 暴露端口
EXPOSE 8080

# 使用 Gunicorn 啟動應用
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
