"""
Tests for voice processing API endpoints.
"""

import io
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import AsyncClient

from app.models.user import User
from tests.fixtures.audio_samples import (
    EXPECTED_PARSED_ITEMS,
    EXPECTED_RECIPE_INGREDIENTS,
    MOCK_WAV_AUDIO,
    SAMPLE_ADD_ITEMS_TRANSCRIPTIONS,
    SAMPLE_RECIPE_QUERY_TRANSCRIPTIONS,
    get_mock_audio_bytes,
)


@pytest.mark.asyncio
async def test_transcribe_audio_success(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test successful audio transcription."""
    with patch("app.api.v1.voice.OpenAIService") as mock_openai:
        # Mock OpenAI service
        mock_service = Mock()
        mock_service.transcribe_audio = AsyncMock(
            return_value="I have 3 apples and 2 bananas"
        )
        mock_openai.return_value = mock_service

        response = await client.post(
            "/api/v1/voice/transcribe",
            headers=verified_auth_headers,
            json={
                "audio_data": MOCK_WAV_AUDIO,
                "audio_format": "wav",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["transcription"] == "I have 3 apples and 2 bananas"


@pytest.mark.asyncio
async def test_transcribe_audio_with_language(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test audio transcription with language specification."""
    with patch("app.api.v1.voice.OpenAIService") as mock_openai:
        mock_service = Mock()
        mock_service.transcribe_audio = AsyncMock(
            return_value="Tengo tres manzanas"
        )
        mock_openai.return_value = mock_service

        response = await client.post(
            "/api/v1/voice/transcribe",
            headers=verified_auth_headers,
            json={
                "audio_data": MOCK_WAV_AUDIO,
                "audio_format": "wav",
                "language": "es",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "manzanas" in data["transcription"]
        assert data["language_detected"] == "es"


@pytest.mark.asyncio
async def test_transcribe_audio_file_upload(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test audio file upload for transcription."""
    with patch("app.api.v1.voice.OpenAIService") as mock_openai:
        mock_service = Mock()
        mock_service.transcribe_audio = AsyncMock(
            return_value="Add milk and eggs"
        )
        mock_openai.return_value = mock_service

        # Create mock audio file
        audio_bytes = get_mock_audio_bytes("wav")
        files = {
            "audio_file": ("test.wav", io.BytesIO(audio_bytes), "audio/wav")
        }

        response = await client.post(
            "/api/v1/voice/transcribe/file",
            headers=verified_auth_headers,
            files=files,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["transcription"] == "Add milk and eggs"
        assert data["audio_format"] == "wav"
        assert "file_size_bytes" in data
        assert "processing_time_ms" in data


@pytest.mark.asyncio
async def test_transcribe_audio_file_invalid_format(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test audio file upload with invalid format."""
    # Create mock file with unsupported content type
    files = {
        "audio_file": ("test.txt", io.BytesIO(b"not audio"), "text/plain")
    }

    response = await client.post(
        "/api/v1/voice/transcribe/file",
        headers=verified_auth_headers,
        files=files,
    )

    assert response.status_code == 400
    assert "Unsupported audio format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_transcribe_audio_file_too_large(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test audio file upload that exceeds size limit."""
    # Create large mock file (> 10MB)
    large_audio = b"x" * (11 * 1024 * 1024)
    files = {
        "audio_file": ("test.wav", io.BytesIO(large_audio), "audio/wav")
    }

    response = await client.post(
        "/api/v1/voice/transcribe/file",
        headers=verified_auth_headers,
        files=files,
    )

    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_process_voice_command_add_items(
    client: AsyncClient,
    verified_auth_headers: dict,
    db,
):
    """Test voice command to add items."""
    transcription = SAMPLE_ADD_ITEMS_TRANSCRIPTIONS[0]

    with patch("app.api.v1.voice.OpenAIService") as mock_openai, \
         patch("app.api.v1.voice.get_voice_command_service") as mock_voice_service:

        # Mock OpenAI transcription
        mock_openai_instance = Mock()
        mock_openai_instance.transcribe_audio = AsyncMock(
            return_value=transcription
        )
        mock_openai.return_value = mock_openai_instance

        # Mock voice command service
        from app.services.voice_command_service import VoiceCommandResult, VoiceCommandType

        mock_result = VoiceCommandResult(
            command_type=VoiceCommandType.ADD_ITEMS,
            success=True,
            data={"items": []},
            message="Successfully added 2 items to your inventory.",
        )

        mock_service = Mock()
        mock_service.process_voice_command = AsyncMock(return_value=mock_result)
        mock_voice_service.return_value = mock_service

        response = await client.post(
            "/api/v1/voice/command",
            headers=verified_auth_headers,
            json={
                "audio_data": MOCK_WAV_AUDIO,
                "audio_format": "wav",
                "process_command": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["transcription"] == transcription
        assert data["command_type"] == "add_items"
        assert data["success"] is True
        assert "added" in data["message"].lower()


@pytest.mark.asyncio
async def test_process_voice_command_recipe_query(
    client: AsyncClient,
    verified_auth_headers: dict,
    db,
):
    """Test voice command for recipe query."""
    transcription = SAMPLE_RECIPE_QUERY_TRANSCRIPTIONS[0]

    with patch("app.api.v1.voice.OpenAIService") as mock_openai, \
         patch("app.api.v1.voice.get_voice_command_service") as mock_voice_service:

        mock_openai_instance = Mock()
        mock_openai_instance.transcribe_audio = AsyncMock(
            return_value=transcription
        )
        mock_openai.return_value = mock_openai_instance

        from app.services.voice_command_service import VoiceCommandResult, VoiceCommandType

        mock_result = VoiceCommandResult(
            command_type=VoiceCommandType.QUERY_RECIPES,
            success=True,
            data={
                "ingredients": ["chicken", "rice"],
                "recipes": [
                    {"name": "Chicken Rice Bowl", "prep_time_minutes": 20}
                ],
            },
            message="Found 1 recipe(s) using chicken, rice.",
        )

        mock_service = Mock()
        mock_service.process_voice_command = AsyncMock(return_value=mock_result)
        mock_voice_service.return_value = mock_service

        response = await client.post(
            "/api/v1/voice/command",
            headers=verified_auth_headers,
            json={
                "audio_data": MOCK_WAV_AUDIO,
                "audio_format": "wav",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["command_type"] == "query_recipes"
        assert data["success"] is True
        assert "recipes" in data["data"]


@pytest.mark.asyncio
async def test_process_voice_command_transcribe_only(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test voice command with transcribe_only mode."""
    with patch("app.api.v1.voice.OpenAIService") as mock_openai:
        mock_openai_instance = Mock()
        mock_openai_instance.transcribe_audio = AsyncMock(
            return_value="Add 5 apples"
        )
        mock_openai.return_value = mock_openai_instance

        response = await client.post(
            "/api/v1/voice/command",
            headers=verified_auth_headers,
            json={
                "audio_data": MOCK_WAV_AUDIO,
                "audio_format": "wav",
                "process_command": False,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["transcription"] == "Add 5 apples"
        assert data["command_type"] == "transcribe_only"
        assert data["success"] is True
        assert data["data"] is None


@pytest.mark.asyncio
async def test_process_voice_command_file_upload(
    client: AsyncClient,
    verified_auth_headers: dict,
    db,
):
    """Test voice command from file upload."""
    with patch("app.api.v1.voice.OpenAIService") as mock_openai, \
         patch("app.api.v1.voice.get_voice_command_service") as mock_voice_service:

        mock_openai_instance = Mock()
        mock_openai_instance.transcribe_audio = AsyncMock(
            return_value="Show me all vegetables"
        )
        mock_openai.return_value = mock_openai_instance

        from app.services.voice_command_service import VoiceCommandResult, VoiceCommandType

        mock_result = VoiceCommandResult(
            command_type=VoiceCommandType.SEARCH_INVENTORY,
            success=True,
            data={"items": [], "query": "vegetables", "total": 0},
            message="Found 0 item(s) matching 'vegetables'.",
        )

        mock_service = Mock()
        mock_service.process_voice_command = AsyncMock(return_value=mock_result)
        mock_voice_service.return_value = mock_service

        audio_bytes = get_mock_audio_bytes("wav")
        files = {
            "audio_file": ("test.wav", io.BytesIO(audio_bytes), "audio/wav")
        }
        data = {"process_command": "true"}

        response = await client.post(
            "/api/v1/voice/command/file",
            headers=verified_auth_headers,
            files=files,
            data=data,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["command_type"] == "search_inventory"
        assert response_data["success"] is True


@pytest.mark.asyncio
async def test_voice_command_unauthorized(
    client: AsyncClient,
):
    """Test voice command without authentication."""
    response = await client.post(
        "/api/v1/voice/command",
        json={
            "audio_data": MOCK_WAV_AUDIO,
            "audio_format": "wav",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_transcribe_audio_openai_error(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test transcription with OpenAI service error."""
    with patch("app.api.v1.voice.OpenAIService") as mock_openai:
        from app.services.openai_service import OpenAIServiceError

        mock_service = Mock()
        mock_service.transcribe_audio = AsyncMock(
            side_effect=OpenAIServiceError("Rate limit exceeded")
        )
        mock_openai.return_value = mock_service

        response = await client.post(
            "/api/v1/voice/transcribe",
            headers=verified_auth_headers,
            json={
                "audio_data": MOCK_WAV_AUDIO,
                "audio_format": "wav",
            },
        )

        assert response.status_code == 502
        assert "Transcription service error" in response.json()["detail"]


# Integration tests with inventory

@pytest.mark.asyncio
async def test_inventory_voice_add_file_endpoint(
    client: AsyncClient,
    verified_auth_headers: dict,
    db,
):
    """Test inventory voice-add with file upload."""
    with patch("app.services.inventory_service.OpenAIService") as mock_openai:
        # Mock OpenAI service for inventory service
        mock_service = Mock()
        mock_service.transcribe_audio = AsyncMock(
            return_value="Add 3 apples"
        )
        mock_service.parse_inventory_from_speech = AsyncMock(
            return_value=[
                {
                    "name": "Apple",
                    "quantity": 3,
                    "unit": "items",
                    "storage_location": "pantry",
                }
            ]
        )
        mock_openai.return_value = mock_service

        audio_bytes = get_mock_audio_bytes("wav")
        files = {
            "audio_file": ("test.wav", io.BytesIO(audio_bytes), "audio/wav")
        }

        response = await client.post(
            "/api/v1/inventory/voice-add/file",
            headers=verified_auth_headers,
            files=files,
        )

        assert response.status_code == 201
        data = response.json()
        assert "transcription" in data
        assert "items_added" in data


@pytest.mark.asyncio
async def test_inventory_voice_add_file_too_large(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test inventory voice-add with oversized file."""
    large_audio = b"x" * (11 * 1024 * 1024)
    files = {
        "audio_file": ("test.wav", io.BytesIO(large_audio), "audio/wav")
    }

    response = await client.post(
        "/api/v1/inventory/voice-add/file",
        headers=verified_auth_headers,
        files=files,
    )

    assert response.status_code == 413
