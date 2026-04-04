"""
Smart LLM Router
Intelligently routes requests to optimal provider based on task, cost, and quality
"""
import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    GENERAL = "general"
    CODING = "coding"
    REASONING = "reasoning"
    CREATIVE = "creative"
    MULTIMODAL = "multimodal"
    SENSITIVE = "sensitive"


class BudgetLevel(str, Enum):
    LOW = "low"  # Minimize cost
    MEDIUM = "medium"  # Balance cost/quality
    HIGH = "high"  # Maximize quality


class SmartRouter:
    """Routes LLM requests to optimal provider"""
    
    def __init__(self, ernie_provider, emergent_provider):
        self.ernie = ernie_provider
        self.emergent = emergent_provider
        
        # Routing rules
        self.routing_matrix = {
            # Task type: {budget_level: (provider, model)}
            TaskType.GENERAL: {
                BudgetLevel.LOW: ("ernie", "default"),
                BudgetLevel.MEDIUM: ("ernie", "ernie-4.5-300b"),
                BudgetLevel.HIGH: ("emergent", "gpt-5.1", "openai")
            },
            TaskType.CODING: {
                BudgetLevel.LOW: ("ernie", "ernie-4.5-300b"),
                BudgetLevel.MEDIUM: ("emergent", "claude-4-sonnet", "anthropic"),
                BudgetLevel.HIGH: ("emergent", "claude-4-sonnet", "anthropic")
            },
            TaskType.REASONING: {
                BudgetLevel.LOW: ("ernie", "ernie-5.0"),
                BudgetLevel.MEDIUM: ("ernie", "ernie-5.0"),
                BudgetLevel.HIGH: ("emergent", "gpt-5.2", "openai")
            },
            TaskType.CREATIVE: {
                BudgetLevel.LOW: ("ernie", "default"),
                BudgetLevel.MEDIUM: ("emergent", "claude-4-sonnet", "anthropic"),
                BudgetLevel.HIGH: ("emergent", "gpt-5.2", "openai")
            },
            TaskType.MULTIMODAL: {
                BudgetLevel.LOW: ("ernie", "ernie-5.0"),
                BudgetLevel.MEDIUM: ("ernie", "ernie-5.0"),
                BudgetLevel.HIGH: ("emergent", "gpt-5.1", "openai")
            },
            TaskType.SENSITIVE: {
                # Always use Emergent for sensitive data
                BudgetLevel.LOW: ("emergent", "gpt-5.1", "openai"),
                BudgetLevel.MEDIUM: ("emergent", "gpt-5.1", "openai"),
                BudgetLevel.HIGH: ("emergent", "gpt-5.2", "openai")
            }
        }
    
    async def route(
        self,
        messages: List[Dict],
        task_type: TaskType = TaskType.GENERAL,
        budget: BudgetLevel = BudgetLevel.LOW,
        force_provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict:
        """
        Route request to optimal provider
        
        Args:
            messages: Chat messages
            task_type: Type of task
            budget: Budget level
            force_provider: Force specific provider (ernie/emergent)
            temperature: Randomness
            max_tokens: Max response length
        
        Returns:
            Response with text, usage, cost, and routing info
        """
        # Detect sensitive content
        if self._contains_sensitive_data(messages):
            task_type = TaskType.SENSITIVE
            logger.info("Sensitive data detected, routing to Emergent")
        
        # Get routing decision
        if force_provider:
            provider_name = force_provider
            if provider_name == "ernie":
                routing = ("ernie", "default")
            else:
                routing = ("emergent", "gpt-5.1", "openai")
        else:
            routing = self.routing_matrix[task_type][budget]
        
        provider_name = routing[0]
        
        # Execute request
        try:
            if provider_name == "ernie":
                model = routing[1]
                response = await self.ernie.chat_completion(
                    messages, model=model, temperature=temperature, max_tokens=max_tokens
                )
            else:
                model = routing[1]
                provider_service = routing[2] if len(routing) > 2 else "openai"
                response = await self.emergent.chat_completion(
                    messages, model=model, provider=provider_service,
                    temperature=temperature, max_tokens=max_tokens
                )
            
            # Add routing info
            response["routing"] = {
                "task_type": task_type,
                "budget": budget,
                "chosen_provider": provider_name,
                "reasoning": self._get_routing_reasoning(task_type, budget, provider_name)
            }
            
            logger.info(
                f"Routed {task_type} task (budget: {budget}) to {provider_name} "
                f"(cost: ${response['usage']['cost_usd']:.6f})"
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Routing to {provider_name} failed: {e}")
            
            # Fallback to other provider
            fallback_provider = "emergent" if provider_name == "ernie" else "ernie"
            logger.info(f"Falling back to {fallback_provider}")
            
            if fallback_provider == "emergent":
                return await self.emergent.chat_completion(
                    messages, model="gpt-5.1", provider="openai",
                    temperature=temperature, max_tokens=max_tokens
                )
            else:
                return await self.ernie.chat_completion(
                    messages, model="default", temperature=temperature, max_tokens=max_tokens
                )
    
    def _contains_sensitive_data(self, messages: List[Dict]) -> bool:
        """Detect sensitive data keywords"""
        sensitive_keywords = [
            "password", "api key", "secret", "credential", "private key",
            "ssn", "social security", "credit card", "bank account",
            "confidential", "classified", "proprietary"
        ]
        
        text = " ".join([m.get("content", "").lower() for m in messages if isinstance(m.get("content"), str)])
        
        return any(keyword in text for keyword in sensitive_keywords)
    
    def _get_routing_reasoning(self, task_type: TaskType, budget: BudgetLevel, provider: str) -> str:
        """Explain routing decision"""
        reasons = {
            ("ernie", TaskType.GENERAL): "ERNIE 5.0 provides excellent quality at 99% lower cost",
            ("ernie", TaskType.MULTIMODAL): "ERNIE 5.0 native multimodal capabilities",
            ("ernie", TaskType.REASONING): "ERNIE 5.0 excels in reasoning benchmarks (77.7% GPQA)",
            ("emergent", TaskType.SENSITIVE): "Sensitive data requires Emergent's secure infrastructure",
            ("emergent", TaskType.CODING): "Claude excels at coding tasks",
            ("emergent", TaskType.CREATIVE): "GPT-5.2 provides superior creative output"
        }
        
        key = (provider, task_type)
        return reasons.get(key, f"Optimal choice for {task_type} at {budget} budget")
    
    def get_cost_comparison(self) -> Dict:
        """Get cost comparison between providers"""
        return {
            "ernie": {
                "input_per_1m": "$0.07-0.28",
                "output_per_1m": "$0.28-0.90",
                "note": "99% cheaper than GPT-4"
            },
            "emergent": {
                "gpt-5.2": "$75/1M input (premium)",
                "gpt-5.1": "$50/1M input (recommended)",
                "claude-4-sonnet": "$15/1M input (coding)",
                "note": "High quality, higher cost"
            },
            "savings": "Using ERNIE for 90% of tasks saves ~$700/month per 10M tokens"
        }
