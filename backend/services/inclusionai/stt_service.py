"""
Speech-to-Text Service using OpenAI Whisper
Provides Ming-UniAudio inspired capabilities
"""
import logging
import tempfile
import os
from typing import Dict, Optional
import torch

logger = logging.getLogger(__name__)


class STTService:
    """Speech-to-Text service wrapper"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize STT service
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model = None
        self.model_size = model_size
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model"""
        try:
            import whisper
            
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info(f"✅ Whisper ({self.model_size}) loaded on {self.device}")
        except Exception as e:
            logger.error(f"❌ Whisper loading failed: {e}")
            self.model = None
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict:
        """
        Transcribe audio to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (auto-detect if None)
            task: 'transcribe' or 'translate' (to English)
        
        Returns:
            Dictionary with transcription results
        """
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            options = {"task": task}
            if language:
                options["language"] = language
            
            result = self.model.transcribe(audio_path, **options)
            
            logger.info(f"Transcribed: {result['text'][:50]}...")
            
            return {
                "text": result["text"],
                "language": result.get("language"),
                "segments": result.get("segments", []),
                "duration": result.get("segments", [{}])[-1].get("end", 0) if result.get("segments") else 0
            }
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def transcribe_for_command(
        self,
        audio_path: str
    ) -> str:
        """
        Transcribe audio for voice command processing
        Returns just the text, optimized for commands
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Transcribed text
        """
        result = self.transcribe(audio_path, language="en")
        return result["text"].strip()
    
    def is_available(self) -> bool:
        """Check if STT service is available"""
        return self.model is not None
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        if not self.model:
            return []
        
        import whisper
        return list(whisper.tokenizer.LANGUAGES.keys())
