"""
Vision Service using CLIP
Provides Ming-Flash-Omni inspired vision capabilities
"""
import logging
from typing import Dict, List, Optional
from PIL import Image
import io
import torch

logger = logging.getLogger(__name__)


class VisionService:
    """Vision analysis service wrapper"""
    
    def __init__(self):
        self.clip_model = None
        self.clip_processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load CLIP model"""
        try:
            from transformers import CLIPProcessor, CLIPModel
            
            model_name = "openai/clip-vit-base-patch32"
            self.clip_model = CLIPModel.from_pretrained(model_name).to(self.device)
            self.clip_processor = CLIPProcessor.from_pretrained(model_name)
            
            logger.info(f"✅ CLIP Model loaded on {self.device}")
        except Exception as e:
            logger.error(f"❌ CLIP loading failed: {e}")
    
    def analyze_image(
        self,
        image_path: str,
        candidate_labels: Optional[List[str]] = None
    ) -> Dict:
        """
        Analyze image content
        
        Args:
            image_path: Path to image file
            candidate_labels: List of possible labels to classify
        
        Returns:
            Analysis results with labels and scores
        """
        if not self.clip_model:
            raise RuntimeError("CLIP model not loaded")
        
        # Default labels for error screenshots
        if candidate_labels is None:
            candidate_labels = [
                "error message",
                "system dashboard",
                "code editor",
                "terminal window",
                "database interface",
                "network diagram",
                "server status",
                "application interface"
            ]
        
        try:
            # Load and process image
            image = Image.open(image_path).convert("RGB")
            
            # Prepare inputs
            inputs = self.clip_processor(
                images=image,
                text=candidate_labels,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)[0]
            
            # Format results
            results = {
                label: float(score)
                for label, score in zip(candidate_labels, probs)
            }
            
            # Sort by score
            sorted_results = dict(
                sorted(results.items(), key=lambda x: x[1], reverse=True)
            )
            
            logger.info(f"Image analyzed: {image.size}, top: {list(sorted_results.keys())[0]}")
            
            return {
                "size": image.size,
                "format": image.format,
                "predictions": sorted_results,
                "top_prediction": list(sorted_results.keys())[0],
                "confidence": list(sorted_results.values())[0]
            }
        
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            raise
    
    def analyze_error_screenshot(
        self,
        image_path: str
    ) -> Dict:
        """
        Specialized analysis for error screenshots
        
        Args:
            image_path: Path to screenshot
        
        Returns:
            Analysis with error-specific insights
        """
        error_labels = [
            "database connection error",
            "404 not found error",
            "500 server error",
            "authentication error",
            "network timeout",
            "syntax error",
            "permission denied",
            "service unavailable"
        ]
        
        result = self.analyze_image(image_path, error_labels)
        
        # Add diagnosis suggestions
        top_error = result["top_prediction"]
        suggestions = self._get_error_suggestions(top_error)
        
        return {
            **result,
            "error_type": top_error,
            "suggestions": suggestions
        }
    
    def _get_error_suggestions(self, error_type: str) -> List[str]:
        """Get troubleshooting suggestions for error type"""
        suggestions_map = {
            "database connection error": [
                "Check MongoDB is running: sudo systemctl status mongodb",
                "Verify MONGO_URL in .env file",
                "Check network connectivity",
                "Review MongoDB logs"
            ],
            "500 server error": [
                "Check backend logs: tail -f /var/log/supervisor/backend.err.log",
                "Verify all environment variables are set",
                "Check for recent code changes",
                "Review API endpoint implementation"
            ],
            "404 not found error": [
                "Verify API route is registered",
                "Check frontend API endpoint URL",
                "Ensure backend is running",
                "Review nginx/proxy configuration"
            ],
            "authentication error": [
                "Check session token/cookie",
                "Verify Google OAuth credentials",
                "Clear browser cookies and retry",
                "Check auth middleware configuration"
            ]
        }
        
        return suggestions_map.get(
            error_type,
            ["Review error logs", "Check system status", "Consult documentation"]
        )
    
    def is_available(self) -> bool:
        """Check if vision service is available"""
        return self.clip_model is not None
