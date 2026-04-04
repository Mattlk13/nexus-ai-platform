"""
Text-to-Speech Service using Coqui TTS
Provides Ming-Omni-TTS inspired capabilities
"""
import logging
import tempfile
import os
from typing import Optional, Dict
import torch

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service wrapper"""
    
    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load TTS model"""
        try:
            from TTS.api import TTS
            
            # Use fast English model
            self.model = TTS(
                model_name="tts_models/en/ljspeech/tacotron2-DDC",
                gpu=(self.device == "cuda")
            )
            logger.info(f"✅ TTS Model loaded on {self.device}")
        except Exception as e:
            logger.error(f"❌ TTS Model loading failed: {e}")
            self.model = None
    
    def generate_speech(
        self,
        text: str,
        output_path: Optional[str] = None,
        speaker: str = "default",
        emotion: str = "neutral",
        speed: float = 1.0
    ) -> str:
        """
        Generate speech from text
        
        Args:
            text: Text to convert to speech
            output_path: Where to save audio (auto-generated if None)
            speaker: Voice to use (currently only 'default' supported)
            emotion: Emotion to apply (not yet implemented)
            speed: Speech speed multiplier
        
        Returns:
            Path to generated audio file
        """
        if not self.model:
            raise RuntimeError("TTS model not loaded")
        
        if not text or len(text) > 1000:
            raise ValueError("Text must be between 1-1000 characters")
        
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".wav")
        
        try:
            self.model.tts_to_file(
                text=text,
                file_path=output_path
            )
            logger.info(f"Generated speech: {len(text)} chars → {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            raise
    
    def generate_notification_audio(
        self,
        notification_text: str,
        priority: str = "medium"
    ) -> str:
        """
        Generate audio for system notifications
        
        Args:
            notification_text: Notification message
            priority: Priority level (critical, high, medium, low)
        
        Returns:
            Path to audio file
        """
        # Add priority prefix
        prefixes = {
            "critical": "Critical alert: ",
            "high": "High priority: ",
            "medium": "Notification: ",
            "low": ""
        }
        
        full_text = prefixes.get(priority, "") + notification_text
        return self.generate_speech(full_text)
    
    def is_available(self) -> bool:
        """Check if TTS service is available"""
        return self.model is not None
    
    def get_voices(self) -> Dict[str, list]:
        """Get available voices"""
        # For now, return default voice
        return {
            "voices": [
                {
                    "id": "default",
                    "name": "Default English Voice",
                    "language": "en",
                    "gender": "female"
                }
            ]
        }
