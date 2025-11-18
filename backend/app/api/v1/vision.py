"""
Vision API endpoints for food image recognition.

Provides:
- General-purpose food identification from images
- File upload support for images
- Nutritional information extraction
- Image storage with validation
"""

import base64
import io
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

from app.api.deps import get_current_user
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.vision import (
    IdentifiedFoodItem,
    VisionFileUploadResponse,
    VisionIdentifyRequest,
    VisionIdentifyWithNutritionResponse,
)
from app.services.image_storage_service import (
    ImageStorageError,
    image_storage_service,
)
from app.services.openai_service import OpenAIServiceError
from app.services.vision_service import get_vision_service

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/identify",
    response_model=VisionIdentifyWithNutritionResponse,
    summary="Identify food items in image",
    description="General-purpose food identification using GPT-4 Vision",
)
async def identify_food_in_image(
    request: VisionIdentifyRequest,
    current_user: User = Depends(get_current_user),
) -> VisionIdentifyWithNutritionResponse:
    """
    Identify food items in an image using AI vision.

    Analyzes the image and returns:
    - Description of what's in the image
    - List of identified food items with:
      - Name and confidence score
      - Estimated quantity and unit
      - Food category
      - Storage location recommendation
      - Estimated shelf life
    - Optional nutritional information

    Args:
        request: Vision identification request with base64 image
        current_user: Current authenticated user

    Returns:
        Identified food items with details

    Raises:
        HTTPException: If identification fails
    """
    logger.info(
        f"Food identification request from user {current_user.id}, "
        f"format: {request.image_format}, nutrition: {request.include_nutrition}"
    )

    try:
        # Get vision service
        vision_service = get_vision_service()

        # Identify food items
        result = await vision_service.identify_food_items(
            image_data=request.image_data,
            image_format=request.image_format,
            include_nutrition=request.include_nutrition,
        )

        logger.info(
            f"Identified {result['total_items_count']} items for user {current_user.id}"
        )

        return VisionIdentifyWithNutritionResponse(**result)

    except OpenAIServiceError as e:
        logger.error(f"OpenAI vision error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Vision service error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Food identification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to identify food items",
        )


@router.post(
    "/identify/file",
    response_model=VisionFileUploadResponse,
    summary="Identify food in uploaded image",
    description="Upload image file for food identification (multipart/form-data)",
)
async def identify_food_in_uploaded_image(
    image_file: UploadFile = File(..., description="Image file to analyze"),
    include_nutrition: bool = Form(
        False, description="Include nutritional information"
    ),
    save_image: bool = Form(True, description="Save image to storage"),
    current_user: User = Depends(get_current_user),
) -> VisionFileUploadResponse:
    """
    Identify food items in uploaded image file.

    Accepts image files via multipart/form-data. Supported formats:
    jpg, jpeg, png, webp.

    Features:
    - Automatic file validation (type, size, dimensions)
    - Optional image storage for later reference
    - Food identification with Vision API
    - Optional nutritional information

    Args:
        image_file: Uploaded image file
        include_nutrition: Whether to include nutrition info
        save_image: Whether to save image to storage
        current_user: Current authenticated user

    Returns:
        Identification results with image metadata

    Raises:
        HTTPException: If validation or identification fails
    """
    start_time = time.time()

    logger.info(
        f"Food identification file upload from user {current_user.id}, "
        f"filename: {image_file.filename}, save: {save_image}"
    )

    try:
        # Read image file
        image_bytes = await image_file.read()
        file_size = len(image_bytes)

        # Validate file type (will raise ImageStorageError if invalid)
        file_ext = image_storage_service.validate_file_type(
            image_file.filename or "image.jpg",
            image_file.content_type,
        )

        # Validate file size
        image_storage_service.validate_file_size(file_size)

        # Validate dimensions
        width, height = image_storage_service.validate_image_dimensions(
            image_bytes
        )

        # Convert to base64 for Vision API
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # Get vision service
        vision_service = get_vision_service()

        # Identify food items
        result = await vision_service.identify_food_items(
            image_data=image_base64,
            image_format=file_ext,
            include_nutrition=include_nutrition,
        )

        # Save image if requested
        image_url = None
        image_metadata = {
            "width": width,
            "height": height,
            "size": file_size,
            "format": file_ext,
        }

        if save_image:
            saved_image = image_storage_service.save_image(
                image_bytes=image_bytes,
                user_id=current_user.id,
                filename=image_file.filename or f"food_image.{file_ext}",
                content_type=image_file.content_type,
            )
            image_url = saved_image["url"]
            logger.info(f"Image saved: {image_url}")
        else:
            # Generate temporary URL (not saved)
            image_url = "/temp/image"

        processing_time = (time.time() - start_time) * 1000  # ms

        logger.info(
            f"Identified {result['total_items_count']} items in {processing_time:.0f}ms"
        )

        return VisionFileUploadResponse(
            description=result["description"],
            items=[IdentifiedFoodItem(**item) for item in result["items"]],
            total_items_count=result["total_items_count"],
            image_url=image_url,
            image_metadata=image_metadata,
            processing_time_ms=processing_time,
        )

    except ImageStorageError as e:
        logger.error(f"Image validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except OpenAIServiceError as e:
        logger.error(f"OpenAI vision error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Vision service error: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Food identification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process image",
        )


@router.post(
    "/estimate-portion",
    summary="Estimate portion size",
    description="Estimate food portion size using reference objects",
)
async def estimate_portion_size(
    image_file: UploadFile = File(..., description="Image with food and reference"),
    food_name: str = Form(..., description="Name of food to estimate"),
    reference_object: Optional[str] = Form(
        None, description="Reference object for scale (hand, plate, etc.)"
    ),
    current_user: User = Depends(get_current_user),
):
    """
    Estimate portion size using visual analysis.

    Useful for:
    - Calorie tracking
    - Meal logging
    - Portion control

    Args:
        image_file: Image file with food
        food_name: Name of food to estimate
        reference_object: Optional reference for scale
        current_user: Current authenticated user

    Returns:
        Portion estimate with quantity and unit
    """
    try:
        # Read and validate image
        image_bytes = await image_file.read()
        image_storage_service.validate_file_size(len(image_bytes))

        # Convert to base64
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # Get vision service
        vision_service = get_vision_service()

        # Estimate portion
        result = await vision_service.estimate_portion_size(
            image_data=image_base64,
            food_name=food_name,
            reference_object=reference_object,
        )

        return result

    except ImageStorageError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except OpenAIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Vision service error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Portion estimation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to estimate portion",
        )
