"""
Voice processing API endpoints.

Provides:
- General-purpose voice transcription
- Voice command processing (add items, query recipes, check expiration)
- Multipart file upload support for audio files
"""

import base64
import time
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.logging import get_logger
from app.db.database import get_db
from app.models.user import User
from app.schemas.voice import (
    VoiceCommandRequest,
    VoiceCommandResponse,
    VoiceFileUploadResponse,
    VoiceTranscribeRequest,
    VoiceTranscribeResponse,
)
from app.services.openai_service import OpenAIService, OpenAIServiceError
from app.services.voice_command_service import get_voice_command_service

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/transcribe",
    response_model=VoiceTranscribeResponse,
    summary="Transcribe audio to text",
    description="General-purpose audio transcription using Whisper AI",
)
async def transcribe_audio(
    request: VoiceTranscribeRequest,
    current_user: User = Depends(get_current_user),
) -> VoiceTranscribeResponse:
    """
    Transcribe audio to text using OpenAI Whisper.

    This is a general-purpose transcription endpoint that returns only the
    transcribed text without executing any commands.

    Args:
        request: Transcription request with base64 audio data
        current_user: Current authenticated user

    Returns:
        Transcribed text

    Raises:
        HTTPException: If transcription fails
    """
    logger.info(
        f"Voice transcription request from user {current_user.id}, "
        f"format: {request.audio_format}"
    )

    try:
        # Initialize OpenAI service
        openai_service = OpenAIService(api_key=settings.OPENAI_API_KEY)

        # Decode base64 audio data
        audio_bytes = base64.b64decode(request.audio_data)

        # Transcribe audio
        transcription = await openai_service.transcribe_audio(
            audio_data=audio_bytes,
            audio_format=request.audio_format,
            language=request.language,
        )

        logger.info(f"Transcription successful: {transcription[:50]}...")

        return VoiceTranscribeResponse(
            transcription=transcription,
            language_detected=request.language,
        )

    except OpenAIServiceError as e:
        logger.error(f"OpenAI transcription failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Transcription service error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transcribe audio",
        )


@router.post(
    "/transcribe/file",
    response_model=VoiceFileUploadResponse,
    summary="Transcribe audio file",
    description="Upload audio file directly for transcription (multipart/form-data)",
)
async def transcribe_audio_file(
    audio_file: UploadFile = File(..., description="Audio file to transcribe"),
    language: Optional[str] = Form(
        None, description="Language code (e.g., 'en', 'es')"
    ),
    current_user: User = Depends(get_current_user),
) -> VoiceFileUploadResponse:
    """
    Transcribe uploaded audio file.

    Accepts audio files via multipart/form-data upload. Supported formats:
    webm, mp3, wav, m4a, ogg.

    Args:
        audio_file: Uploaded audio file
        language: Optional language code
        current_user: Current authenticated user

    Returns:
        Transcription result with metadata

    Raises:
        HTTPException: If file is invalid or transcription fails
    """
    start_time = time.time()

    # Validate file type
    if not audio_file.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file content type not specified",
        )

    # Extract format from content type or filename
    content_type = audio_file.content_type.lower()
    filename = audio_file.filename.lower() if audio_file.filename else ""

    # Map content types to formats
    format_map = {
        "audio/webm": "webm",
        "audio/mpeg": "mp3",
        "audio/mp3": "mp3",
        "audio/wav": "wav",
        "audio/wave": "wav",
        "audio/x-wav": "wav",
        "audio/x-m4a": "m4a",
        "audio/m4a": "m4a",
        "audio/ogg": "ogg",
    }

    audio_format = format_map.get(content_type)

    # If not found in content type, try filename extension
    if not audio_format:
        for ext in ["webm", "mp3", "wav", "m4a", "ogg"]:
            if filename.endswith(f".{ext}"):
                audio_format = ext
                break

    if not audio_format:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format. Supported: webm, mp3, wav, m4a, ogg",
        )

    logger.info(
        f"Voice file upload from user {current_user.id}, "
        f"format: {audio_format}, size: {audio_file.size} bytes"
    )

    try:
        # Read audio file
        audio_bytes = await audio_file.read()
        file_size = len(audio_bytes)

        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Audio file too large. Max size: {max_size / 1024 / 1024}MB",
            )

        # Initialize OpenAI service
        openai_service = OpenAIService(api_key=settings.OPENAI_API_KEY)

        # Transcribe audio
        transcription = await openai_service.transcribe_audio(
            audio_data=audio_bytes,
            audio_format=audio_format,
            language=language,
        )

        processing_time = (time.time() - start_time) * 1000  # ms

        logger.info(
            f"File transcription successful in {processing_time:.0f}ms: "
            f"{transcription[:50]}..."
        )

        return VoiceFileUploadResponse(
            transcription=transcription,
            file_size_bytes=file_size,
            audio_format=audio_format,
            processing_time_ms=processing_time,
        )

    except OpenAIServiceError as e:
        logger.error(f"OpenAI transcription failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Transcription service error: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File transcription failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transcribe audio file",
        )


@router.post(
    "/command",
    response_model=VoiceCommandResponse,
    summary="Process voice command",
    description="Transcribe and execute voice commands (add items, recipes, expiration)",
)
async def process_voice_command(
    request: VoiceCommandRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VoiceCommandResponse:
    """
    Process a voice command with AI.

    Supports commands like:
    - "Add 3 apples and 2 pounds of chicken" (adds to inventory)
    - "What can I cook with chicken and rice?" (recipe suggestions)
    - "When does my milk expire?" (expiration check)
    - "Show me all vegetables" (inventory search)

    Args:
        request: Voice command request with audio data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Voice command result with execution status and data

    Raises:
        HTTPException: If processing fails
    """
    logger.info(
        f"Voice command request from user {current_user.id}, "
        f"format: {request.audio_format}"
    )

    try:
        # Initialize services
        openai_service = OpenAIService(api_key=settings.OPENAI_API_KEY)
        voice_service = get_voice_command_service()

        # Decode base64 audio data
        audio_bytes = base64.b64decode(request.audio_data)

        # Step 1: Transcribe audio
        transcription = await openai_service.transcribe_audio(
            audio_data=audio_bytes,
            audio_format=request.audio_format,
        )

        logger.info(f"Transcribed: {transcription}")

        # Step 2: Process command (if requested)
        if request.process_command:
            result = await voice_service.process_voice_command(
                transcribed_text=transcription,
                db=db,
                user_id=current_user.id,
            )

            # Convert items to dict for JSON serialization
            response_data = result.data
            if response_data and "items" in response_data:
                from app.schemas.inventory import InventoryItemResponse

                response_data["items"] = [
                    InventoryItemResponse.model_validate(item).model_dump()
                    for item in response_data["items"]
                ]

            if response_data and "recipes" in response_data:
                # Recipes are already in dict format from OpenAI
                pass

            return VoiceCommandResponse(
                transcription=transcription,
                command_type=result.command_type.value,
                success=result.success,
                message=result.message,
                data=response_data,
                error=result.error,
            )

        else:
            # Just return transcription without processing
            return VoiceCommandResponse(
                transcription=transcription,
                command_type="transcribe_only",
                success=True,
                message="Audio transcribed successfully (not executed)",
                data=None,
            )

    except OpenAIServiceError as e:
        logger.error(f"OpenAI service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Voice command processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process voice command",
        )


@router.post(
    "/command/file",
    response_model=VoiceCommandResponse,
    summary="Process voice command from file",
    description="Upload audio file and execute voice command (multipart/form-data)",
)
async def process_voice_command_file(
    audio_file: UploadFile = File(..., description="Audio file with voice command"),
    process_command: bool = Form(
        True, description="Whether to execute command or just transcribe"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VoiceCommandResponse:
    """
    Process voice command from uploaded audio file.

    Args:
        audio_file: Uploaded audio file
        process_command: Whether to execute the command
        db: Database session
        current_user: Current authenticated user

    Returns:
        Voice command result

    Raises:
        HTTPException: If processing fails
    """
    try:
        # Read and validate audio file
        audio_bytes = await audio_file.read()
        file_size = len(audio_bytes)

        # Check file size
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Audio file too large. Max size: {max_size / 1024 / 1024}MB",
            )

        # Detect audio format
        content_type = audio_file.content_type.lower() if audio_file.content_type else ""
        format_map = {
            "audio/webm": "webm",
            "audio/mpeg": "mp3",
            "audio/mp3": "mp3",
            "audio/wav": "wav",
            "audio/m4a": "m4a",
        }
        audio_format = format_map.get(content_type, "webm")

        # Convert to base64 for processing
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        # Create request and delegate to main handler
        command_request = VoiceCommandRequest(
            audio_data=audio_base64,
            audio_format=audio_format,
            process_command=process_command,
        )

        return await process_voice_command(command_request, db, current_user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice command file processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process voice command file",
        )
