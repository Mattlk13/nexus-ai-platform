"""
Hybrid Integrations API Routes
Routes for trending AI models and creative tools
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from services.hybrid_integrations.llm_hub import get_llm_hub
from services.hybrid_integrations.creative_studio import get_creative_studio

logger = logging.getLogger(__name__)


# Request Models
class ChatRequest(BaseModel):
    prompt: str
    model: str = "default"
    system_message: Optional[str] = None
    session_id: Optional[str] = None


class CodeGenRequest(BaseModel):
    task: str
    language: str = "python"
    context: Optional[str] = None


class ImageGenRequest(BaseModel):
    prompt: str
    style: Optional[str] = None
    aspect_ratio: Optional[str] = None


class ImageEditRequest(BaseModel):
    reference_image_base64: str
    edit_instruction: str


class PortfolioBannerRequest(BaseModel):
    creator_name: str
    specialty: str
    style: str = "professional and modern"


class ProductMockupRequest(BaseModel):
    product_name: str
    product_description: str
    context: str = "professional product showcase"


class MultilingualRequest(BaseModel):
    task: str
    target_language: Optional[str] = None


class ReasoningRequest(BaseModel):
    problem: str
    approach: str = "step-by-step"


def get_hybrid_integrations_router():
    """Get hybrid integrations router"""
    router = APIRouter(prefix="/api/hybrid", tags=["hybrid-integrations"])
    
    llm_hub = get_llm_hub()
    creative_studio = get_creative_studio()
    
    # ========== LLM Hub Endpoints ==========
    
    @router.get("/llm/models")
    async def list_available_models():
        """List all available LLM models"""
        return {
            "success": True,
            "models": llm_hub.get_available_models(),
            "total_models": len(llm_hub.MODELS)
        }
    
    @router.post("/llm/chat")
    async def chat_with_llm(request: ChatRequest):
        """
        Chat with any available LLM model
        
        Models: grok, qwen, gpt-codex, claude, gemini, default
        """
        try:
            result = await llm_hub.chat(
                prompt=request.prompt,
                model_name=request.model,
                system_message=request.system_message,
                session_id=request.session_id
            )
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("error"))
            
            return result
            
        except Exception as e:
            logger.error(f"LLM chat failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/llm/code-generation")
    async def generate_code(request: CodeGenRequest):
        """
        Generate code using GPT-Codex model
        
        Supports: Python, JavaScript, TypeScript, Go, Rust, etc.
        """
        try:
            result = await llm_hub.code_generation(
                task=request.task,
                language=request.language,
                context=request.context
            )
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("error"))
            
            return result
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/llm/multilingual")
    async def multilingual_task(request: MultilingualRequest):
        """
        Execute multilingual task using Qwen model
        
        Supports multiple languages with cultural context
        """
        try:
            result = await llm_hub.multilingual_task(
                task=request.task,
                target_language=request.target_language
            )
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("error"))
            
            return result
            
        except Exception as e:
            logger.error(f"Multilingual task failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/llm/reasoning")
    async def advanced_reasoning(request: ReasoningRequest):
        """
        Advanced problem solving using Claude Sonnet 4
        
        Approaches: step-by-step, analytical, creative
        """
        try:
            result = await llm_hub.advanced_reasoning(
                problem=request.problem,
                approach=request.approach
            )
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("error"))
            
            return result
            
        except Exception as e:
            logger.error(f"Reasoning task failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ========== Creative Studio Endpoints ==========
    
    @router.post("/creative/generate-image")
    async def generate_image(request: ImageGenRequest):
        """
        Generate image using Nano Banana 2 (Gemini Image Generation)
        
        Styles: photorealistic, artistic, anime, abstract, professional
        Aspect ratios: 16:9, 1:1, 9:16, 4:3
        """
        try:
            result = await creative_studio.generate_image(
                prompt=request.prompt,
                style=request.style,
                aspect_ratio=request.aspect_ratio
            )
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("error"))
            
            return result
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/creative/edit-image")
    async def edit_image(request: ImageEditRequest):
        """
        Edit existing image using Nano Banana 2
        
        Provide base64-encoded reference image and edit instructions
        """
        try:
            result = await creative_studio.edit_image(
                reference_image_base64=request.reference_image_base64,
                edit_instruction=request.edit_instruction
            )
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("error"))
            
            return result
            
        except Exception as e:
            logger.error(f"Image editing failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/creative/portfolio-banner")
    async def create_portfolio_banner(request: PortfolioBannerRequest):
        """
        Generate professional portfolio banner for creators
        
        Automatically creates branded banner with creator info
        """
        try:
            result = await creative_studio.create_portfolio_banner(
                creator_name=request.creator_name,
                specialty=request.specialty,
                style=request.style
            )
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("error"))
            
            return result
            
        except Exception as e:
            logger.error(f"Portfolio banner generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/creative/product-mockup")
    async def create_product_mockup(request: ProductMockupRequest):
        """
        Generate product mockup image
        
        Creates photorealistic product mockups for marketing
        """
        try:
            result = await creative_studio.create_product_mockup(
                product_name=request.product_name,
                product_description=request.product_description,
                context=request.context
            )
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("error"))
            
            return result
            
        except Exception as e:
            logger.error(f"Product mockup generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ========== Status & Info Endpoints ==========
    
    @router.get("/status")
    async def hybrid_integrations_status():
        """Get status of all hybrid integrations"""
        return {
            "status": "active",
            "integrations": {
                "llm_hub": {
                    "status": "active",
                    "models": len(llm_hub.MODELS),
                    "features": [
                        "Multi-model chat (Grok, Qwen, GPT, Claude, Gemini)",
                        "Code generation (GPT-Codex)",
                        "Multilingual tasks (Qwen)",
                        "Advanced reasoning (Claude)"
                    ]
                },
                "creative_studio": {
                    "status": "active",
                    "model": "Nano Banana 2 (Gemini 3.1 Flash Image)",
                    "features": [
                        "Image generation from text",
                        "Image editing with reference",
                        "Portfolio banners",
                        "Product mockups"
                    ]
                }
            },
            "version": "1.0.0"
        }
    
    @router.get("/demo")
    async def demo_hybrid_integrations():
        """Demo hybrid integrations capabilities"""
        return {
            "demo": "NEXUS Hybrid AI Integrations",
            "trending_models": [
                "Grok 4.20 (xAI)",
                "Qwen 3.5 (Alibaba Cloud)",
                "GPT-5.3-Codex (OpenAI)",
                "Claude Sonnet 4 (Anthropic)",
                "Gemini 3 Pro (Google)",
                "Nano Banana 2 (Gemini Image Gen)"
            ],
            "example_endpoints": {
                "llm_chat": "POST /api/hybrid/llm/chat",
                "code_gen": "POST /api/hybrid/llm/code-generation",
                "multilingual": "POST /api/hybrid/llm/multilingual",
                "reasoning": "POST /api/hybrid/llm/reasoning",
                "image_gen": "POST /api/hybrid/creative/generate-image",
                "image_edit": "POST /api/hybrid/creative/edit-image",
                "portfolio_banner": "POST /api/hybrid/creative/portfolio-banner",
                "product_mockup": "POST /api/hybrid/creative/product-mockup"
            },
            "quick_start": {
                "1_chat_with_grok": {
                    "endpoint": "/api/hybrid/llm/chat",
                    "payload": {
                        "prompt": "Explain quantum computing in simple terms",
                        "model": "grok"
                    }
                },
                "2_generate_code": {
                    "endpoint": "/api/hybrid/llm/code-generation",
                    "payload": {
                        "task": "Create a REST API for user authentication",
                        "language": "python"
                    }
                },
                "3_create_image": {
                    "endpoint": "/api/hybrid/creative/generate-image",
                    "payload": {
                        "prompt": "A futuristic AI marketplace with holographic interfaces",
                        "style": "photorealistic"
                    }
                }
            }
        }
    
    return router
