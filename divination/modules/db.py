import os
from typing import Dict, Any, Optional
from shared.supabase_client import get_supabase_client


class DivinationDB:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.results_table = os.environ.get("SUPABASE_TABLE_1", "divination_results")
        self.combinations_table = os.environ.get(
            "SUPABASE_TABLE_2", "divination_combinations"
        )

    def get_divination_result(self, result_key: str) -> Optional[Dict[str, Any]]:
        """
        從資料庫獲取單次擲筊結果（聖筊/笑筊/陰筊）

        Args:
            result_key: 'holy', 'laughing', 'negative'
        """
        try:
            response = (
                self.supabase.table(self.results_table)
                .select("*")
                .eq("result_key", result_key)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error fetching divination result for {result_key}: {e}")
            return None

    def get_combination_interpretation(
        self, combination_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        從資料庫獲取三次擲筊組合的解讀

        Args:
            combination_key: e.g. 'holy_holy_holy'
        """
        try:
            response = (
                self.supabase.table(self.combinations_table)
                .select("*")
                .eq("combination_key", combination_key)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(
                f"Error fetching combination interpretation for {combination_key}: {e}"
            )
            return None
