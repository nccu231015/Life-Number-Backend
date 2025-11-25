"""
GPT 客戶端（共享）
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class GPTClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None) -> None:
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4o')
        self.client = OpenAI(
            api_key=api_key or os.getenv('OPENAI_API_KEY'),
            base_url=base_url or os.getenv('OPENAI_BASE_URL'),
        )

    def ask(self, system_prompt: str, user_prompt: str, temperature: float = 0.6, max_tokens: int = 1000) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        # 準備 API 參數
        params = {
            "model": self.model,
            "messages": messages,
            "max_completion_tokens": max_tokens,
        }
        
        # 只有當 temperature 為 1.0 時才傳遞（GPT-4o 的默認值）
        # 其他值可能導致錯誤或異常行為
        if abs(temperature - 1.0) < 0.01:  # 允許浮點數誤差
            params["temperature"] = 1.0
        
        print(f"[DEBUG GPTClient] Model: {self.model}, Temperature: {temperature}, Max tokens: {max_tokens}")
        print(f"[DEBUG GPTClient] Using temperature in params: {'temperature' in params}")
        
        try:
            response = self.client.chat.completions.create(**params)
            content = response.choices[0].message.content or ""
            print(f"[DEBUG GPTClient] Response length: {len(content)}")
            return content.strip()
        except Exception as e:
            print(f"[ERROR GPTClient] API call failed: {e}")
            raise

    def structured(self, system_prompt: str, user_prompt: str, response_format: Dict[str, Any], temperature: float = 0.3, max_tokens: int = 1000) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        # 準備 API 參數
        params = {
            "model": self.model,
            "messages": messages,
            "max_completion_tokens": max_tokens,
            "response_format": response_format,
        }
        
        # 只有當 temperature 為 1 時才傳遞（有些模型只支持默認值 1）
        if temperature == 1.0:
            params["temperature"] = temperature
        
        response = self.client.chat.completions.create(**params)
        return (response.choices[0].message.content or "").strip()

