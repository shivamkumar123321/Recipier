"""
Voice-related Pydantic schemas for request/response validation.
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

from app.schemas.base import BaseSchema
from app.schemas.inventory import InventoryItemResponse


# Voice Transcription Schemas
class VoiceTranscribeRequest(BaseSchema):
    """Schema for general-purpose voice transcription request."""

    audio_data: str = Field(
        ...,
        description="Base64 encoded audio data",
    )
    audio_format: str = Field(
        default="webm",
        pattern="^(webm|mp3|wav|m4a|ogg)$",
        description="Audio format (webm, mp3, wav, m4a, ogg)",
    )
    language: Optional[str] = Field(
        None,
        max_length=10,
        description="Language code (e.g., 'en', 'es', 'fr')",
    )


class VoiceTranscribeResponse(BaseSchema):
    """Schema for voice transcription response."""

    transcription: str = Field(..., description="Transcribed text from audio")
    language_detected: Optional[str] = Field(
        None,
        description="Detected language code",
    )
    duration_seconds: Optional[float] = Field(
        None,
        description="Audio duration in seconds",
    )


# Voice Command Schemas
class VoiceCommandRequest(BaseSchema):
    """Schema for processing voice commands."""

    audio_data: str = Field(
        ...,
        description="Base64 encoded audio data",
    )
    audio_format: str = Field(
        default="webm",
        pattern="^(webm|mp3|wav|m4a|ogg)$",
        description="Audio format",
    )
    process_command: bool = Field(
        default=True,
        description="Whether to execute the command or just transcribe",
    )


class RecipeSuggestion(BaseSchema):
    """Schema for recipe suggestion."""

    name: str
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    difficulty: Optional[str] = None
    ingredients: List[Dict[str, Any]] = []
    instructions: List[str] = []


class VoiceCommandResponse(BaseSchema):
    """Schema for voice command response."""

    transcription: str = Field(..., description="Transcribed text")
    command_type: str = Field(..., description="Type of command detected")
    success: bool = Field(..., description="Whether command executed successfully")
    message: str = Field(..., description="Human-readable result message")
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Command-specific data (items, recipes, etc.)",
    )
    error: Optional[str] = Field(None, description="Error message if failed")


# Multipart File Upload Schemas (for file upload support)
class VoiceFileUploadResponse(BaseSchema):
    """Response for voice file upload."""

    transcription: str
    file_size_bytes: int
    audio_format: str
    processing_time_ms: float
