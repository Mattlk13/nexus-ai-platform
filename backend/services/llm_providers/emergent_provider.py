"""
Emergent Universal LLM Provider
Wrapper for Emergent's universal LLM key (GPT, Claude, Gemini)
"""
import logging
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class EmergentProvider:
    """Emergent LLM integration wrapper"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('EMERGENT_LLM_KEY')
        # Pricing estimates (varies by actual usage)
        self.pricing = {
            "gpt-5.2": {"input": 75.0, "output": 150.0},  # Premium
            "gpt-5.1": {"input": 50.0, "output": 100.0},
            "claude-4-sonnet": {"input": 15.0, "output": 30.0},
            "gemini-2.5-pro": {"input": 10.0, "output": 20.0}
        }
    
    async def chat_completion(
        self,
        messages: List[Dict],
        model: str = "gpt-5.1",
        provider: str = "openai",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict:
        """
        Generate chat completion using Emergent integrations
        
        Args:
            messages: Chat history
            model: Model name
            provider: Provider (openai, anthropic, gemini)
            temperature: Randomness
            max_tokens: Max response length
        
        Returns:
            Response with text and usage
        """
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not configured")
        
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            # Initialize chat
            chat = LlmChat(
                api_key=self.api_key,
                session_id="nexus-smart-router",
                system_message=messages[0]["content"] if messages[0]["role"] == "system" else ""
            )
            
            # Set model
            chat.with_model(provider, model)
            
            # Get last user message
            user_messages = [m for m in messages if m["role"] == "user"]
            if not user_messages:
                raise ValueError("No user message found")
            
            last_message = user_messages[-1]["content"]
            
            # Send message
            user_msg = UserMessage(text=last_message)
            response_text = await chat.send_message(user_msg)
            
            # Estimate usage (no direct token count from emergentintegrations)
            estimated_input = len(last_message) // 4  # Rough estimate
            estimated_output = len(response_text) // 4
            
            cost = self._calculate_cost(
                {"prompt_tokens": estimated_input, "completion_tokens": estimated_output},
                model
            )
            
            return {
                "text": response_text,
                "model": model,
                "provider": "emergent",
                "usage": {
                    "input_tokens": estimated_input,
                    "output_tokens": estimated_output,
                    "total_tokens": estimated_input + estimated_output,
                    "cost_usd": cost
                }
            }
        
        except Exception as e:
            logger.error(f"Emergent API error: {e}")
            raise
    
    def _calculate_cost(self, usage: Dict, model: str) -> float:
        """Estimate cost (actual cost varies)"""
        rates = self.pricing.get(model, self.pricing["gpt-5.1"])
        
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]
        
        return round(input_cost + output_cost, 6)
    
    def is_available(self) -> bool:
        """Check if Emergent provider is configured"""
        return self.api_key is not None
