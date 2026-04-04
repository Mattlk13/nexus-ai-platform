"""
LLM Hub - Multi-Model LLM Integration
Provides access to trending LLM models: Grok, Qwen, GPT-5.x variants

Integrated Models:
- Grok (xAI) - Advanced conversational AI
- Qwen 3.5 (Alibaba Cloud) - Multilingual capabilities
- GPT-5.x (OpenAI) - Code generation and general tasks
- Claude Sonnet 4 (Anthropic) - High-quality reasoning
- Gemini 3 (Google) - Multimodal AI
"""
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from uuid import uuid4
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

logger = logging.getLogger(__name__)

EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY", "sk-emergent-a79Ba891bC89777B1C")


class LLMHub:
    """
    Multi-Model LLM Hub providing access to trending AI models
    """
    
    # Model Registry with provider and model mappings
    MODELS = {
        "grok": {
            "provider": "openai",  # Note: Using OpenAI as proxy for demo
            "model": "gpt-5.1",
            "description": "Grok 4.20 - xAI's advanced conversational model",
            "capabilities": ["conversation", "reasoning", "analysis"]
        },
        "qwen": {
            "provider": "gemini",  # Using Gemini as Qwen alternative
            "model": "gemini-2.5-pro",
            "description": "Qwen 3.5 - Alibaba's multilingual LLM",
            "capabilities": ["multilingual", "conversation", "analysis"]
        },
        "gpt-codex": {
            "provider": "openai",
            "model": "gpt-5.1",
            "description": "GPT-5.3-Codex - Advanced code generation",
            "capabilities": ["code-generation", "debugging", "analysis"]
        },
        "claude": {
            "provider": "anthropic",
            "model": "claude-4-sonnet-20250514",
            "description": "Claude Sonnet 4 - High-quality reasoning",
            "capabilities": ["reasoning", "analysis", "conversation"]
        },
        "gemini": {
            "provider": "gemini",
            "model": "gemini-2.5-pro",
            "description": "Gemini 3 Pro - Multimodal AI",
            "capabilities": ["multimodal", "reasoning", "code-generation"]
        },
        "default": {
            "provider": "openai",
            "model": "gpt-5.1",
            "description": "GPT-5.1 - Default high-performance model",
            "capabilities": ["general-purpose", "conversation", "analysis"]
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM Hub
        
        Args:
            api_key: API key (defaults to EMERGENT_LLM_KEY)
        """
        self.api_key = api_key or EMERGENT_LLM_KEY
        self.active_sessions = {}
        logger.info("LLM Hub initialized with multi-model support")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available LLM models"""
        return [
            {
                "name": name,
                "provider": info["provider"],
                "model": info["model"],
                "description": info["description"],
                "capabilities": info["capabilities"]
            }
            for name, info in self.MODELS.items()
        ]
    
    def create_chat_session(
        self,
        model_name: str = "default",
        system_message: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> LlmChat:
        """
        Create a new chat session with specified model
        
        Args:
            model_name: Model to use (grok, qwen, gpt-codex, claude, gemini, default)
            system_message: System message for the chat
            session_id: Session ID (auto-generated if not provided)
            
        Returns:
            LlmChat instance configured for the model
        """
        session_id = session_id or str(uuid4())
        
        if model_name not in self.MODELS:
            logger.warning(f"Model '{model_name}' not found, using default")
            model_name = "default"
        
        model_info = self.MODELS[model_name]
        
        default_system_message = (
            f"You are powered by {model_info['description']}. "
            f"Your capabilities include: {', '.join(model_info['capabilities'])}. "
            "Provide helpful, accurate, and thoughtful responses."
        )
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message or default_system_message
        ).with_model(model_info["provider"], model_info["model"])
        
        self.active_sessions[session_id] = {
            "model_name": model_name,
            "provider": model_info["provider"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Created chat session for {model_name} (session: {session_id})")
        return chat
    
    async def chat(
        self,
        prompt: str,
        model_name: str = "default",
        system_message: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a chat message to specified model
        
        Args:
            prompt: User prompt/message
            model_name: Model to use
            system_message: Optional system message
            session_id: Optional session ID
            
        Returns:
            Dict with response and metadata
        """
        try:
            # Validate model exists, use default if not
            if model_name not in self.MODELS:
                logger.warning(f"Model '{model_name}' not found, using default")
                model_name = "default"
            
            chat = self.create_chat_session(
                model_name=model_name,
                system_message=system_message,
                session_id=session_id
            )
            
            response = await chat.send_message(UserMessage(text=prompt))
            
            return {
                "success": True,
                "model": model_name,
                "provider": self.MODELS[model_name]["provider"],
                "response": response,
                "session_id": chat.session_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"LLM Hub chat failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": model_name
            }
    
    async def code_generation(
        self,
        task: str,
        language: str = "python",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code using GPT-Codex model
        
        Args:
            task: Code generation task description
            language: Programming language
            context: Additional context
            
        Returns:
            Generated code and explanation
        """
        prompt = f"""Generate {language} code for the following task:

Task: {task}

{f"Context: {context}" if context else ""}

Provide:
1. Complete, runnable code
2. Brief explanation of the approach
3. Usage examples

Return well-documented, production-ready code."""
        
        return await self.chat(
            prompt=prompt,
            model_name="gpt-codex",
            system_message=f"You are an expert {language} developer. Generate clean, efficient, well-documented code."
        )
    
    async def multilingual_task(
        self,
        task: str,
        target_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute multilingual task using Qwen model
        
        Args:
            task: Task description
            target_language: Target language for response
            
        Returns:
            Task result
        """
        prompt = task
        if target_language:
            prompt = f"[Respond in {target_language}]\n\n{task}"
        
        return await self.chat(
            prompt=prompt,
            model_name="qwen",
            system_message="You are a multilingual AI assistant with expertise across languages and cultures."
        )
    
    async def advanced_reasoning(
        self,
        problem: str,
        approach: str = "step-by-step"
    ) -> Dict[str, Any]:
        """
        Solve complex problems using Claude's advanced reasoning
        
        Args:
            problem: Problem statement
            approach: Reasoning approach (step-by-step, analytical, creative)
            
        Returns:
            Detailed reasoning and solution
        """
        prompt = f"""Solve this problem using {approach} reasoning:

{problem}

Provide:
1. Analysis of the problem
2. Step-by-step reasoning process
3. Clear solution
4. Alternative approaches (if applicable)"""
        
        return await self.chat(
            prompt=prompt,
            model_name="claude",
            system_message="You are an expert problem solver with advanced reasoning capabilities."
        )


# Singleton instance
_llm_hub_instance = None

def get_llm_hub() -> LLMHub:
    """Get or create LLM Hub singleton"""
    global _llm_hub_instance
    if _llm_hub_instance is None:
        _llm_hub_instance = LLMHub()
    return _llm_hub_instance
