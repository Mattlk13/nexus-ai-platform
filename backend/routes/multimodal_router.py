"""
Multimodal AI API Router
Text-to-Speech, Speech-to-Text, and Vision services
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import tempfile
import os
import logging

# Import services
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.inclusionai import TTSService, STTService, VisionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/multimodal", tags=["multimodal"])

# Initialize services (lazy loading)
_tts_service = None
_stt_service = None
_vision_service = None


def get_tts_service() -> TTSService:
    """Get or create TTS service instance"""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service


def get_stt_service() -> STTService:
    """Get or create STT service instance"""
    global _stt_service
    if _stt_service is None:
        _stt_service = STTService(model_size="base")
    return _stt_service


def get_vision_service() -> VisionService:
    """Get or create vision service instance"""
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service


# Request models
class TTSRequest(BaseModel):
    text: str
    speaker: str = "default"
    emotion: str = "neutral"
    speed: float = 1.0


class VoiceNotificationRequest(BaseModel):
    message: str
    priority: str = "medium"  # critical, high, medium, low


class ImageAnalysisRequest(BaseModel):
    labels: Optional[List[str]] = None


# ============== TEXT-TO-SPEECH ENDPOINTS ==============

@router.post("/tts/generate")
async def generate_speech(request: TTSRequest):
    """Generate speech from text"""
    tts = get_tts_service()
    
    if not tts.is_available():
        raise HTTPException(status_code=503, detail="TTS service unavailable")
    
    try:
        audio_path = tts.generate_speech(
            text=request.text,
            speaker=request.speaker,
            emotion=request.emotion,
            speed=request.speed
        )
        
        return FileResponse(
            audio_path,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts/notification")
async def generate_notification_audio(request: VoiceNotificationRequest):
    """Generate audio for system notification"""
    tts = get_tts_service()
    
    if not tts.is_available():
        raise HTTPException(status_code=503, detail="TTS service unavailable")
    
    try:
        audio_path = tts.generate_notification_audio(
            notification_text=request.message,
            priority=request.priority
        )
        
        return FileResponse(
            audio_path,
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename=notification_{request.priority}.wav"}
        )
    except Exception as e:
        logger.error(f"Notification TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tts/voices")
async def get_available_voices():
    """Get list of available TTS voices"""
    tts = get_tts_service()
    
    if not tts.is_available():
        raise HTTPException(status_code=503, detail="TTS service unavailable")
    
    return tts.get_voices()


# ============== SPEECH-TO-TEXT ENDPOINTS ==============

@router.post("/stt/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = None
):
    """Transcribe audio to text"""
    stt = get_stt_service()
    
    if not stt.is_available():
        raise HTTPException(status_code=503, detail="STT service unavailable")
    
    # Validate file type
    if file.content_type not in ["audio/wav", "audio/mp3", "audio/mpeg", "audio/ogg", "audio/webm"]:
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Transcribe
        result = stt.transcribe(tmp_path, language=language)
        
        # Cleanup
        os.unlink(tmp_path)
        
        return result
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stt/voice-command")
async def process_voice_command(file: UploadFile = File(...)):
    """Process voice command (optimized for short commands)"""
    stt = get_stt_service()
    
    if not stt.is_available():
        raise HTTPException(status_code=503, detail="STT service unavailable")
    
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Transcribe for command
        command_text = stt.transcribe_for_command(tmp_path)
        
        # Cleanup
        os.unlink(tmp_path)
        
        # Parse command (basic implementation)
        intent = parse_command_intent(command_text)
        
        return {
            "text": command_text,
            "intent": intent["action"],
            "parameters": intent["params"],
            "confidence": "high"
        }
    except Exception as e:
        logger.error(f"Voice command error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stt/languages")
async def get_supported_languages():
    """Get list of supported languages for STT"""
    stt = get_stt_service()
    
    if not stt.is_available():
        raise HTTPException(status_code=503, detail="STT service unavailable")
    
    languages = stt.get_supported_languages()
    return {"languages": languages}


# ============== VISION ENDPOINTS ==============

@router.post("/vision/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    labels: Optional[str] = None
):
    """Analyze image with AI vision"""
    vision = get_vision_service()
    
    if not vision.is_available():
        raise HTTPException(status_code=503, detail="Vision service unavailable")
    
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Unsupported image format")
    
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Parse labels if provided
        label_list = labels.split(",") if labels else None
        
        # Analyze
        result = vision.analyze_image(tmp_path, candidate_labels=label_list)
        
        # Cleanup
        os.unlink(tmp_path)
        
        return result
    except Exception as e:
        logger.error(f"Vision error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vision/diagnose-error")
async def diagnose_error_screenshot(file: UploadFile = File(...)):
    """Analyze error screenshot and provide diagnosis"""
    vision = get_vision_service()
    
    if not vision.is_available():
        raise HTTPException(status_code=503, detail="Vision service unavailable")
    
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Unsupported image format")
    
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Analyze error
        result = vision.analyze_error_screenshot(tmp_path)
        
        # Cleanup
        os.unlink(tmp_path)
        
        return result
    except Exception as e:
        logger.error(f"Error diagnosis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== MULTIMODAL PIPELINE ==============

@router.post("/pipeline/voice-to-voice")
async def voice_to_voice_pipeline(file: UploadFile = File(...)):
    """Complete voice-to-voice pipeline: Audio in → Text → Process → Audio out"""
    stt = get_stt_service()
    tts = get_tts_service()
    
    if not stt.is_available() or not tts.is_available():
        raise HTTPException(status_code=503, detail="Services unavailable")
    
    try:
        # Step 1: Save input audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            contents = await file.read()
            tmp.write(contents)
            input_path = tmp.name
        
        # Step 2: Transcribe
        command_text = stt.transcribe_for_command(input_path)
        
        # Step 3: Process (echo for now)
        response_text = f"You said: {command_text}"
        
        # Step 4: Generate response audio
        output_path = tts.generate_speech(response_text)
        
        # Cleanup input
        os.unlink(input_path)
        
        return FileResponse(
            output_path,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=response.wav"}
        )
    except Exception as e:
        logger.error(f"Voice pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== STATUS ENDPOINTS ==============

@router.get("/status")
async def get_services_status():
    """Get status of all multimodal services"""
    return {
        "tts": {
            "available": get_tts_service().is_available(),
            "service": "Coqui TTS"
        },
        "stt": {
            "available": get_stt_service().is_available(),
            "service": "OpenAI Whisper"
        },
        "vision": {
            "available": get_vision_service().is_available(),
            "service": "CLIP"
        }
    }


# ============== HELPER FUNCTIONS ==============

def parse_command_intent(text: str) -> dict:
    """Parse voice command to extract intent and parameters"""
    text_lower = text.lower().strip()
    
    # Simple intent matching
    intents = {
        "show": ["show", "display", "view"],
        "create": ["create", "make", "add", "new"],
        "search": ["search", "find", "lookup"],
        "start": ["start", "begin", "launch"],
        "stop": ["stop", "end", "terminate"],
        "status": ["status", "check", "health"]
    }
    
    detected_intent = "unknown"
    for intent, keywords in intents.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_intent = intent
            break
    
    return {
        "action": detected_intent,
        "params": {
            "raw_text": text
        }
    }


def get_multimodal_router():
    """Get the multimodal router"""
    return router
