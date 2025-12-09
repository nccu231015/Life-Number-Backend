"""
黃曆資料查詢模組
從 Supabase 查詢黃曆資料
"""

import os
from typing import Optional
from supabase import create_client, Client


class CalendarDB:
    """黃曆資料庫查詢"""

    def __init__(self):
        # 從環境變數讀取 Supabase 配置
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        # 使用環境變數或默認表名
        self.table_name = os.getenv("SUPABASE_CALENDAR_TABLE", "auspicious_calendar")

    def get_month_data(self, month: str) -> Optional[str]:
        """
        查詢指定月份的黃曆內容

        Args:
            month: 月份，格式 YYYY-MM

        Returns:
            黃曆內容文本，若無資料則返回 None
        """
        try:
            supabase: Client = create_client(self.supabase_url, self.supabase_key)
            response = (
                supabase.table(self.table_name)
                .select("content")
                .eq("month", month)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return response.data[0].get("content", "")

            return None

        except Exception as e:
            print(f"Error querying calendar data for {month}: {e}")
            return None

    def get_available_months(self) -> list[str]:
        """
        獲取所有可用的月份

        Returns:
            月份列表，格式 YYYY-MM
        """
        try:
            supabase: Client = create_client(self.supabase_url, self.supabase_key)
            response = supabase.table(self.table_name).select("month").execute()

            if response.data:
                months = [item["month"] for item in response.data]
                return sorted(list(set(months)))  # 去重並排序

            return []

        except Exception as e:
            print(f"Error querying available months: {e}")
            return []
