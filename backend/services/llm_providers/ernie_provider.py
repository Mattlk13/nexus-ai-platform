"""
Baidu ERNIE 5.0 Provider
Cost-effective multimodal LLM (99% cheaper than GPT-4)
"""
import logging
from typing import Dict, List, Optional
import httpx
import os
import base64

logger = logging.getLogger(__name__)


class ERNIEProvider:
    """ERNIE 5.0/4.5 API wrapper"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('ERNIE_API_KEY')
        # Using SiliconFlow as OpenAI-compatible proxy
        self.base_url = "https://api.siliconflow.cn/v1"
        self.models = {
            "ernie-5.0": "ERNIE-5.0-Thinking-Preview",
            "ernie-4.5-300b": "ERNIE-4.5-300B-A47B",
            "ernie-4.5-21b": "ERNIE-4.5-21B-A3B",
            "default": "ERNIE-4.5-300B-A47B"  # Best price/performance
        }
        self.pricing = {
            "ernie-5.0": {"input": 0.07, "output": 0.28},  # per 1M tokens
            "ernie-4.5-300b": {"input": 0.28, "output": 0.90},
            "ernie-4.5-21b": {"input": 0.07, "output": 0.28}
        }
    
    async def chat_completion(
        self,
        messages: List[Dict],
        model: str = "default",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict:
        """
        Generate chat completion
        
        Args:
            messages: Chat history in OpenAI format
            model: Model to use (ernie-5.0, ernie-4.5-300b, ernie-4.5-21b)
            temperature: Randomness (0-1)
            max_tokens: Max response length
        
        Returns:
            Response with text, usage, and cost
        """
        if not self.api_key:
            raise ValueError("ERNIE_API_KEY not configured")
        
        model_name = self.models.get(model, self.models["default"])
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json={
                        "model": model_name,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": False
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                response.raise_for_status()
                data = response.json()
                
                usage = data.get("usage", {})
                cost = self._calculate_cost(usage, model)
                
                return {
                    "text": data["choices"][0]["message"]["content"],
                    "model": model,
                    "provider": "ernie",
                    "usage": {
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                        "cost_usd": cost
                    },
                    "raw_response": data
                }
        
        except Exception as e:
            logger.error(f"ERNIE API error: {e}")
            raise
    
    async def multimodal_completion(
        self,
        text: str,
        image: Optional[str] = None,
        model: str = "ernie-5.0"
    ) -> Dict:
        """
        Multimodal completion (text + image)
        
        Args:
            text: Text prompt
            image: Base64 encoded image
            model: Model to use
        
        Returns:
            Response with analysis
        """
        messages = [{
            "role": "user",
            "content": []
        }]
        
        # Add text
        messages[0]["content"].append({
            "type": "text",
            "text": text
        })
        
        # Add image if provided
        if image:
            # If it's a file path, read and encode
            if not image.startswith('data:') and not image.startswith('http'):
                with open(image, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode()
                    image = f"data:image/jpeg;base64,{image_data}"
            
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {"url": image}
            })
        
        return await self.chat_completion(messages, model=model)
    
    def _calculate_cost(self, usage: Dict, model: str) -> float:
        """Calculate API cost in USD"""
        model_key = model if model in self.pricing else "ernie-4.5-300b"
        rates = self.pricing[model_key]
        
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]
        
        return round(input_cost + output_cost, 6)
    
    def is_available(self) -> bool:
        """Check if ERNIE provider is configured"""
        return self.api_key is not None
    
    def get_models(self) -> List[str]:
        """Get available models"""
        return list(self.models.keys())
