"""
Inventory management endpoints.

Provides:
- Manual item addition
- Voice-based item addition
- Image-based item scanning
- Item CRUD operations
- Expiration tracking
- Category filtering
"""

import base64
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_current_user
from app.core.logging import get_logger
from app.db.database import get_db
from app.models.user import User
from app.schemas.inventory import (
    CategorySummary,
    ImageScanRequest,
    ImageScanResponse,
    InventoryItemCreate,
    InventoryItemListResponse,
    InventoryItemResponse,
    InventoryItemUpdate,
    VoiceAddRequest,
    VoiceAddResponse,
)
from app.services.inventory_service import inventory_service

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/items",
    response_model=InventoryItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add item manually",
    description="Manually add a single inventory item",
)
async def create_inventory_item(
    item_data: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InventoryItemResponse:
    """
    Add a new item to inventory manually.

    Args:
        item_data: Item creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created inventory item
    """
    item = await inventory_service.create_item(
        db=db,
        item_data=item_data,
        user_id=current_user.id,
    )

    return item


@router.post(
    "/voice-add",
    response_model=VoiceAddResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add items via voice",
    description="Add inventory items via voice transcription using Whisper AI",
)
async def add_items_via_voice(
    request: VoiceAddRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VoiceAddResponse:
    """
    Add items to inventory via voice input.

    The audio will be transcribed using OpenAI Whisper, then parsed to extract
    inventory items with quantities and other details.

    Args:
        request: Voice add request with base64 audio data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Voice add response with transcription and added items
    """
    response = await inventory_service.add_items_from_voice(
        db=db,
        audio_data_base64=request.audio_data,
        audio_format=request.audio_format,
        user_id=current_user.id,
    )

    return response


@router.post(
    "/voice-add/file",
    response_model=VoiceAddResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add items via voice file upload",
    description="Add inventory items via audio file upload (multipart/form-data)",
)
async def add_items_via_voice_file(
    audio_file: UploadFile = File(..., description="Audio file to transcribe"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VoiceAddResponse:
    """
    Add items to inventory via voice file upload.

    Accepts audio files via multipart/form-data. Supported formats:
    webm, mp3, wav, m4a, ogg.

    Args:
        audio_file: Uploaded audio file
        db: Database session
        current_user: Current authenticated user

    Returns:
        Voice add response with transcription and added items

    Raises:
        HTTPException: If file is invalid or processing fails
    """
    from fastapi import HTTPException

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

    # Detect audio format from content type or filename
    content_type = audio_file.content_type.lower() if audio_file.content_type else ""
    filename = audio_file.filename.lower() if audio_file.filename else ""

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

    # Try filename extension if content type doesn't match
    if not audio_format:
        for ext in ["webm", "mp3", "wav", "m4a", "ogg"]:
            if filename.endswith(f".{ext}"):
                audio_format = ext
                break

    if not audio_format:
        audio_format = "webm"  # Default fallback

    # Convert to base64 and delegate to existing service
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

    response = await inventory_service.add_items_from_voice(
        db=db,
        audio_data_base64=audio_base64,
        audio_format=audio_format,
        user_id=current_user.id,
    )

    return response


@router.post(
    "/scan",
    response_model=ImageScanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add items via image scan",
    description="Add inventory items via image recognition using GPT-4 Vision",
)
async def scan_food_image(
    request: ImageScanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ImageScanResponse:
    """
    Add items to inventory by scanning food images.

    The image will be analyzed using GPT-4 Vision to identify food items,
    estimate quantities, and suggest storage locations.

    Args:
        request: Image scan request with base64 image data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Image scan response with identified items and added items
    """
    response = await inventory_service.add_items_from_image(
        db=db,
        image_data_base64=request.image_data,
        image_format=request.image_format,
        user_id=current_user.id,
    )

    return response


@router.post(
    "/scan/file",
    response_model=ImageScanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add items via image file upload",
    description="Upload image file for food recognition and inventory addition (multipart/form-data)",
)
async def scan_food_image_file(
    image_file: UploadFile = File(..., description="Food image to scan"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ImageScanResponse:
    """
    Scan uploaded food image and add items to inventory.

    Accepts image files via multipart/form-data. Supported formats:
    jpg, jpeg, png, webp.

    The image will be:
    1. Validated (file type, size, dimensions)
    2. Analyzed using GPT-4 Vision
    3. Food items identified with quantities
    4. Items automatically added to inventory
    5. Image saved to user's storage

    Args:
        image_file: Uploaded image file
        db: Database session
        current_user: Current authenticated user

    Returns:
        Image scan response with identified and added items

    Raises:
        HTTPException: If validation or processing fails
    """
    from app.services.image_storage_service import (
        ImageStorageError,
        image_storage_service,
    )

    try:
        # Read image file
        image_bytes = await image_file.read()

        # Validate file
        file_ext = image_storage_service.validate_file_type(
            image_file.filename or "image.jpg",
            image_file.content_type,
        )
        image_storage_service.validate_file_size(len(image_bytes))
        image_storage_service.validate_image_dimensions(image_bytes)

        # Convert to base64 for processing
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # Delegate to existing service
        response = await inventory_service.add_items_from_image(
            db=db,
            image_data_base64=image_base64,
            image_format=file_ext,
            user_id=current_user.id,
        )

        return response

    except ImageStorageError as e:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        from fastapi import HTTPException

        logger = get_logger(__name__)
        logger.error(f"Image scan failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to scan image",
        )


@router.get(
    "/items",
    response_model=InventoryItemListResponse,
    summary="List all inventory items",
    description="Get all inventory items with filtering, sorting, and pagination",
)
async def get_inventory_items(
    pagination: PaginationParams = Depends(),
    category_id: int = Query(None, description="Filter by category ID"),
    storage_location: str = Query(
        None,
        regex="^(pantry|fridge|freezer)$",
        description="Filter by storage location",
    ),
    search: str = Query(
        None,
        min_length=1,
        max_length=100,
        description="Search by item name",
    ),
    sort_by: str = Query(
        "created_at",
        regex="^(created_at|name|quantity|expiration_date)$",
        description="Field to sort by",
    ),
    sort_order: str = Query(
        "desc",
        regex="^(asc|desc)$",
        description="Sort order",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InventoryItemListResponse:
    """
    Get all inventory items for the current user.

    Supports:
    - Pagination (skip, limit)
    - Filtering by category and storage location
    - Search by item name
    - Sorting by multiple fields

    Args:
        pagination: Pagination parameters
        category_id: Optional category filter
        storage_location: Optional storage location filter
        search: Optional name search
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of inventory items
    """
    items, total = await inventory_service.get_user_inventory(
        db=db,
        user_id=current_user.id,
        skip=pagination.skip,
        limit=pagination.limit,
        category_id=category_id,
        storage_location=storage_location,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return InventoryItemListResponse(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/items/{item_id}",
    response_model=InventoryItemResponse,
    summary="Get single item",
    description="Get a single inventory item by ID",
)
async def get_inventory_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InventoryItemResponse:
    """
    Get a single inventory item by ID.

    Args:
        item_id: Item ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Inventory item

    Raises:
        NotFoundException: If item not found or not owned by user
    """
    item = await inventory_service.get_item_by_id(
        db=db,
        item_id=item_id,
        user_id=current_user.id,
    )

    return item


@router.patch(
    "/items/{item_id}",
    response_model=InventoryItemResponse,
    summary="Update item",
    description="Update inventory item (quantity, expiration, etc.)",
)
async def update_inventory_item(
    item_id: int,
    item_data: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InventoryItemResponse:
    """
    Update an existing inventory item.

    Can update any field including:
    - Name
    - Quantity
    - Unit
    - Expiration date
    - Storage location
    - Category

    Args:
        item_id: Item ID
        item_data: Update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated inventory item

    Raises:
        NotFoundException: If item not found
        ValidationException: If validation fails
    """
    item = await inventory_service.update_item(
        db=db,
        item_id=item_id,
        item_data=item_data,
        user_id=current_user.id,
    )

    return item


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete item",
    description="Remove item from inventory (soft delete)",
)
async def delete_inventory_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete an inventory item (soft delete).

    Args:
        item_id: Item ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        NotFoundException: If item not found
    """
    await inventory_service.delete_item(
        db=db,
        item_id=item_id,
        user_id=current_user.id,
    )


@router.get(
    "/expiring",
    response_model=InventoryItemListResponse,
    summary="Get expiring items",
    description="Get items expiring within specified days",
)
async def get_expiring_items(
    days: int = Query(
        7,
        ge=1,
        le=90,
        description="Number of days to check for expiration",
    ),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InventoryItemListResponse:
    """
    Get items expiring within the specified number of days.

    Useful for:
    - Expiration alerts
    - Meal planning with soon-to-expire items
    - Reducing food waste

    Args:
        days: Number of days to check (default: 7)
        pagination: Pagination parameters
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of expiring items sorted by expiration date
    """
    items, total = await inventory_service.get_expiring_items(
        db=db,
        user_id=current_user.id,
        days=days,
        skip=pagination.skip,
        limit=pagination.limit,
    )

    return InventoryItemListResponse(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/categories",
    response_model=List[CategorySummary],
    summary="Get items grouped by category",
    description="Get all inventory items grouped by food category",
)
async def get_items_by_category(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CategorySummary]:
    """
    Get inventory items grouped by category.

    Returns all items organized by food category with summary information:
    - Number of unique items per category
    - Total quantity across all items
    - List of items in each category

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of category summaries with items
    """
    summaries = await inventory_service.get_items_by_category(
        db=db,
        user_id=current_user.id,
    )

    return summaries
