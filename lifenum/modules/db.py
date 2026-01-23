import os
from shared.supabase_client import get_supabase_client


class LifeNumberDB:
    def __init__(self):
        self.supabase = get_supabase_client()

    def get_main_number(self, number: int):
        try:
            response = (
                self.supabase.table("lifenum_main")
                .select("*")
                .eq("number", number)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"DB Error get_main_number: {e}")
            return None

    def get_birthday_number(self, number: int):
        try:
            response = (
                self.supabase.table("lifenum_birthday")
                .select("*")
                .eq("number", number)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"DB Error get_birthday_number: {e}")
            return None

    def get_personal_year(self, number: int):
        try:
            response = (
                self.supabase.table("lifenum_personal_year")
                .select("*")
                .eq("number", number)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"DB Error get_personal_year: {e}")
            return None

    def get_grid_line(self, line_key: str):
        try:
            response = (
                self.supabase.table("lifenum_grid_lines")
                .select("*")
                .eq("line_key", line_key)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"DB Error get_grid_line: {e}")
            return None

    def get_challenge(self, number: int):
        try:
            response = (
                self.supabase.table("lifenum_challenge")
                .select("*")
                .eq("number", number)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"DB Error get_challenge: {e}")
            return None

    def get_expression(self, number: int):
        try:
            response = (
                self.supabase.table("lifenum_expression")
                .select("*")
                .eq("number", number)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"DB Error get_expression: {e}")
            return None

    def get_maturity(self, number: int):
        try:
            response = (
                self.supabase.table("lifenum_maturity")
                .select("*")
                .eq("number", number)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"DB Error get_maturity: {e}")
            return None

    def get_soul(self, number: int):
        try:
            response = (
                self.supabase.table("lifenum_soul")
                .select("*")
                .eq("number", number)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"DB Error get_soul: {e}")
            return None

    def get_personality(self, number: int):
        try:
            response = (
                self.supabase.table("lifenum_personality")
                .select("*")
                .eq("number", number)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"DB Error get_personality: {e}")
            return None

    def get_karma(self, number: int):
        try:
            response = (
                self.supabase.table("lifenum_karma")
                .select("*")
                .eq("number", number)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"DB Error get_karma: {e}")
            return None
