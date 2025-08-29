#!/usr/bin/env python3
"""
API Client Module
Handles external API calls (OpenRouter)
"""

import os
import asyncio
import aiohttp


class APIClient:
    def __init__(self, model="openai/gpt-oss-120b"):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = model
        
        if not self.api_key:
            print("⚠️  Warning: OPENROUTER_API_KEY not found in environment variables")

    async def get_ai_response(self, user_message, max_tokens=150, temperature=0.7):
        """Make async API call to OpenRouter"""
        if not self.api_key:
            return "Sorry, I don't have access to AI assistance right now."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Voice Assistant",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a helpful assistant. Give brief, conversational responses. limit to 3 to 5 words as possible."
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content'].strip()
                    else:
                        error_text = await response.text()
                        print(f"API Error {response.status}: {error_text}")
                        return "Sorry, I encountered an error while processing your request."
                        
        except asyncio.TimeoutError:
            print("API request timed out")
            return "Sorry, the response took too long. Please try again."
        except Exception as e:
            print(f"API call error: {e}")
            return "Sorry, I couldn't process your request right now."
