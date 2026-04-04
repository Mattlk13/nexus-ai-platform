"""
Smart LLM Router API
Endpoints for intelligent LLM provider routing
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging

# Import LLM providers
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.llm_providers import ERNIEProvider, EmergentProvider, SmartRouter
from services.llm_providers.smart_router import TaskType, BudgetLevel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/llm", tags=["llm"])

# Initialize providers (lazy loading)
_ernie_provider = None
_emergent_provider = None
_smart_router = None


def get_providers():
    """Get or create provider instances"""
    global _ernie_provider, _emergent_provider, _smart_router
    
    if _ernie_provider is None:
        _ernie_provider = ERNIEProvider()
    
    if _emergent_provider is None:
        _emergent_provider = EmergentProvider()
    
    if _smart_router is None:
        _smart_router = SmartRouter(_ernie_provider, _emergent_provider)
    
    return _ernie_provider, _emergent_provider, _smart_router


# Request models
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    task_type: str = "general"
    budget: str = "low"
    force_provider: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


class MultimodalRequest(BaseModel):
    text: str
    image: Optional[str] = None  # Base64 or file path


# ============== SMART ROUTER ENDPOINTS ==============

@router.post("/chat")
async def smart_chat(request: ChatRequest):
    """
    Smart chat completion with automatic provider routing
    
    Routes to ERNIE 5.0 for cost optimization or Emergent for sensitive/premium tasks
    """
    _, _, router_instance = get_providers()
    
    try:
        # Convert messages
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        # Convert task_type and budget to enums
        try:
            task_type = TaskType(request.task_type.lower())
        except ValueError:
            task_type = TaskType.GENERAL
        
        try:
            budget = BudgetLevel(request.budget.lower())
        except ValueError:
            budget = BudgetLevel.LOW
        
        # Route request
        response = await router_instance.route(
            messages=messages,
            task_type=task_type,
            budget=budget,
            force_provider=request.force_provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Smart chat error: { e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/providers/ernie/chat")
async def ernie_chat(request: ChatRequest):
    """Direct ERNIE 5.0 chat completion"""
    ernie, _, _ = get_providers()
    
    if not ernie.is_available():
        raise HTTPException(
            status_code=503,
            detail="ERNIE provider not configured. Please set ERNIE_API_KEY in .env"
        )
    
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        response = await ernie.chat_completion(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return response
    
    except Exception as e:
        logger.error(f"ERNIE chat error: { e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/providers/emergent/chat")
async def emergent_chat(request: ChatRequest):
    """Direct Emergent universal key chat completion"""
    _, emergent, _ = get_providers()
    
    if not emergent.is_available():
        raise HTTPException(
            status_code=503,
            detail="Emergent provider not configured"
        )
    
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        response = await emergent.chat_completion(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return response
    
    except Exception as e:
        logger.error(f"Emergent chat error: { e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/providers/ernie/multimodal")
async def ernie_multimodal(request: MultimodalRequest):
    """ERNIE 5.0 multimodal analysis (text + image)"""
    ernie, _, _ = get_providers()
    
    if not ernie.is_available():
        raise HTTPException(status_code=503, detail="ERNIE provider not configured")
    
    try:
        response = await ernie.multimodal_completion(
            text=request.text,
            image=request.image
        )
        return response
    
    except Exception as e:
        logger.error(f"ERNIE multimodal error: { e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== STATUS & INFO ENDPOINTS ==============

@router.get("/providers/status")
async def get_providers_status():
    """Get status of all LLM providers"""
    ernie, emergent, _ = get_providers()
    
    return {
        "ernie": {
            "available": ernie.is_available(),
            "models": ernie.get_models() if ernie.is_available() else [],
            "pricing": "$0.07-0.90 per 1M tokens (99% cheaper than GPT-4)"
        },
        "emergent": {
            "available": emergent.is_available(),
            "models": ["gpt-5.2", "gpt-5.1", "claude-4-sonnet", "gemini-2.5-pro"],
            "pricing": "$10-75 per 1M tokens (premium quality)"
        }
    }


@router.get("/routing/rules")
async def get_routing_rules():
    """Get smart routing rules"""
    return {
        "task_types": [t.value for t in TaskType],
        "budget_levels": [b.value for b in BudgetLevel],
        "routing_strategy": {
            "general": "ERNIE 5.0 for cost optimization (99% savings)",
            "coding": "Claude for complex code, ERNIE for simple",
            "reasoning": "ERNIE 5.0 (beats GPT-4 in benchmarks)",
            "multimodal": "ERNIE 5.0 native multimodal",
            "sensitive": "Always Emergent (secure infrastructure)"
        },
        "sensitive_detection": "Auto-routes sensitive data to Emergent"
    }


@router.get("/cost/comparison")
async def get_cost_comparison():
    """Get cost comparison between providers"""
    _, _, router_instance = get_providers()
    return router_instance.get_cost_comparison()


@router.get("/cost/calculator")
async def calculate_cost(
    tokens: int = 10000000,  # 10M tokens
    provider: str = "both"
):
    """Calculate cost for given token count"""
    ernie_cost = (tokens / 1_000_000) * 0.28  # Average ERNIE cost
    gpt4_cost = (tokens / 1_000_000) * 75.0  # GPT-4 cost
    
    savings = gpt4_cost - ernie_cost
    savings_percent = (savings / gpt4_cost) * 100
    
    return {
        "tokens": tokens,
        "costs": {
            "ernie_5_0": f"${ernie_cost:.2f}",
            "gpt_4": f"${gpt4_cost:.2f}",
            "savings": f"${savings:.2f}",
            "savings_percent": f"{savings_percent:.1f}%"
        },
        "recommendation": "Use ERNIE 5.0 for 90% of tasks to maximize savings"
    }


def get_llm_router():
    """Get the LLM router"""
    return router
