"""
Creative Studio - AI-Powered Creative Content Generation
Image generation using Nano Banana (Gemini), and creative content tools

Features:
- Nano Banana 2 (Gemini Image Generation)
- Image editing and manipulation
- Creative content generation
"""
import os
import logging
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from uuid import uuid4
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

load_dotenv()

logger = logging.getLogger(__name__)

EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY", "sk-emergent-a79Ba891bC89777B1C")


class CreativeStudio:
    """
    AI-Powered Creative Content Generation Studio
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Creative Studio
        
        Args:
            api_key: API key (defaults to EMERGENT_LLM_KEY)
        """
        self.api_key = api_key or EMERGENT_LLM_KEY
        logger.info("Creative Studio initialized with Nano Banana image generation")
    
    def _create_image_chat(self, session_id: Optional[str] = None) -> LlmChat:
        """Create chat session configured for image generation"""
        session_id = session_id or str(uuid4())
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message="You are a creative AI assistant specializing in image generation and visual creativity."
        ).with_model("gemini", "gemini-3.1-flash-image-preview").with_params(
            modalities=["image", "text"]
        )
        
        return chat
    
    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        aspect_ratio: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate image using Nano Banana (Gemini Image Generation)
        
        Args:
            prompt: Image description prompt
            style: Optional style (e.g., "photorealistic", "artistic", "anime")
            aspect_ratio: Optional aspect ratio (e.g., "16:9", "1:1", "9:16")
            
        Returns:
            Dict with generated image(s) as base64 and metadata
        """
        try:
            # Enhance prompt with style and aspect ratio
            enhanced_prompt = prompt
            if style:
                enhanced_prompt = f"{style} style: {enhanced_prompt}"
            if aspect_ratio:
                enhanced_prompt = f"{enhanced_prompt} (aspect ratio: {aspect_ratio})"
            
            chat = self._create_image_chat()
            
            msg = UserMessage(text=enhanced_prompt)
            text_response, images = await chat.send_message_multimodal_response(msg)
            
            if not images:
                return {
                    "success": False,
                    "error": "No images generated",
                    "text_response": text_response
                }
            
            # Process generated images
            generated_images = []
            for idx, img in enumerate(images):
                generated_images.append({
                    "index": idx,
                    "mime_type": img.get("mime_type", "image/png"),
                    "data_preview": img["data"][:50] + "...",  # Only preview
                    "size_bytes": len(img["data"]) if "data" in img else 0,
                    "full_data": img["data"]  # Include full base64 for download
                })
                logger.info(f"Generated image {idx}: {img.get('mime_type')}")
            
            return {
                "success": True,
                "model": "Nano Banana 2 (Gemini 3.1 Flash Image)",
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "images_count": len(images),
                "images": generated_images,
                "text_response": text_response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt
            }
    
    async def edit_image(
        self,
        reference_image_base64: str,
        edit_instruction: str
    ) -> Dict[str, Any]:
        """
        Edit an existing image using Nano Banana
        
        Args:
            reference_image_base64: Base64-encoded reference image
            edit_instruction: Instruction for how to edit the image
            
        Returns:
            Dict with edited image(s) and metadata
        """
        try:
            chat = self._create_image_chat()
            
            msg = UserMessage(
                text=edit_instruction,
                file_contents=[ImageContent(reference_image_base64)]
            )
            
            text_response, images = await chat.send_message_multimodal_response(msg)
            
            if not images:
                return {
                    "success": False,
                    "error": "No edited images generated",
                    "text_response": text_response
                }
            
            edited_images = []
            for idx, img in enumerate(images):
                edited_images.append({
                    "index": idx,
                    "mime_type": img.get("mime_type", "image/png"),
                    "data_preview": img["data"][:50] + "...",
                    "full_data": img["data"]
                })
            
            return {
                "success": True,
                "model": "Nano Banana 2 (Image Editing)",
                "instruction": edit_instruction,
                "images_count": len(images),
                "images": edited_images,
                "text_response": text_response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Image editing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "instruction": edit_instruction
            }
    
    async def create_portfolio_banner(
        self,
        creator_name: str,
        specialty: str,
        style: str = "professional and modern"
    ) -> Dict[str, Any]:
        """
        Generate a portfolio banner for creators
        
        Args:
            creator_name: Creator's name
            specialty: Creator's specialty/niche
            style: Visual style
            
        Returns:
            Generated banner image
        """
        prompt = f"""Create a stunning portfolio banner for {creator_name}, a {specialty} creator.

Style: {style}
Requirements:
- Professional and eye-catching design
- Incorporate elements related to {specialty}
- Modern aesthetic with clean typography
- High-quality, suitable for web portfolio
- 16:9 aspect ratio"""
        
        return await self.generate_image(
            prompt=prompt,
            style=style,
            aspect_ratio="16:9"
        )
    
    async def create_product_mockup(
        self,
        product_name: str,
        product_description: str,
        context: str = "professional product showcase"
    ) -> Dict[str, Any]:
        """
        Generate product mockup image
        
        Args:
            product_name: Name of the product
            product_description: Description of the product
            context: Context/environment for the mockup
            
        Returns:
            Product mockup image
        """
        prompt = f"""Create a professional product mockup for {product_name}:

Description: {product_description}
Context: {context}

Requirements:
- Photorealistic quality
- Professional lighting and composition
- Clean, modern presentation
- Suitable for marketing materials"""
        
        return await self.generate_image(
            prompt=prompt,
            style="photorealistic"
        )
    
    async def batch_generate(
        self,
        prompts: List[str],
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate multiple images in batch
        
        Args:
            prompts: List of image prompts
            style: Optional unified style for all images
            
        Returns:
            List of generated images
        """
        results = []
        
        for idx, prompt in enumerate(prompts):
            result = await self.generate_image(
                prompt=prompt,
                style=style
            )
            results.append({
                "prompt_index": idx,
                "prompt": prompt,
                "result": result
            })
        
        return {
            "success": True,
            "batch_size": len(prompts),
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Singleton instance
_creative_studio_instance = None

def get_creative_studio() -> CreativeStudio:
    """Get or create Creative Studio singleton"""
    global _creative_studio_instance
    if _creative_studio_instance is None:
        _creative_studio_instance = CreativeStudio()
    return _creative_studio_instance
