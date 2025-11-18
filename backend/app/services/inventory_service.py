"""
Inventory service for managing pantry/fridge items.

Handles:
- Manual item addition
- Voice-based item addition
- Image-based item scanning
- Item updates and deletion
- Expiration tracking
- Category management
"""

import base64
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.core.logging import get_logger
from app.models.inventory import InventoryItem
from app.repositories.inventory_repository import (
    food_category_repository,
    inventory_repository,
)
from app.schemas.inventory import (
    CategorySummary,
    ImageScanResponse,
    InventoryItemCreate,
    InventoryItemUpdate,
    VoiceAddResponse,
)
from app.services.openai_service import openai_service

logger = get_logger(__name__)


class InventoryService:
    """Service for inventory management operations."""

    async def create_item(
        self,
        db: AsyncSession,
        item_data: InventoryItemCreate,
        user_id: int,
    ) -> InventoryItem:
        """
        Create a new inventory item.

        Args:
            db: Database session
            item_data: Item creation data
            user_id: User ID

        Returns:
            Created inventory item

        Raises:
            ValidationException: If validation fails
        """
        # Validate category if provided
        if item_data.category_id:
            category = await food_category_repository.get(db, item_data.category_id)
            if not category:
                raise ValidationException(
                    f"Category with ID {item_data.category_id} not found",
                    error_code="CATEGORY_NOT_FOUND",
                )

        # Create item
        item_dict = item_data.model_dump()
        item = await inventory_repository.create(
            db,
            {**item_dict, "user_id": user_id},
        )

        await db.commit()
        await db.refresh(item, ["category"])

        logger.info(f"Created inventory item: {item.name} for user {user_id}")

        return item

    async def add_items_from_voice(
        self,
        db: AsyncSession,
        audio_data_base64: str,
        audio_format: str,
        user_id: int,
    ) -> VoiceAddResponse:
        """
        Add inventory items from voice transcription.

        Args:
            db: Database session
            audio_data_base64: Base64 encoded audio data
            audio_format: Audio format (webm, mp3, wav, m4a)
            user_id: User ID

        Returns:
            Voice add response with transcription and added items

        Raises:
            ValidationException: If transcription or parsing fails
        """
        try:
            # Decode audio data
            audio_bytes = base64.b64decode(audio_data_base64)

            # Transcribe audio
            transcription = await openai_service.transcribe_audio(
                audio_bytes,
                audio_format,
            )

            logger.info(f"Transcribed voice input: {transcription}")

            # Parse items from transcription
            parsed_items = await openai_service.parse_inventory_from_text(transcription)

            # Create inventory items
            items_added = []
            for item_data in parsed_items:
                # Find or create category
                category_id = None
                if "category" in item_data and item_data["category"]:
                    category = await food_category_repository.get_by_name(
                        db,
                        item_data["category"],
                    )
                    if category:
                        category_id = category.id

                # Create item
                item = await inventory_repository.create(
                    db,
                    {
                        "user_id": user_id,
                        "name": item_data.get("name", "Unknown Item"),
                        "quantity": float(item_data.get("quantity", 1.0)),
                        "unit": item_data.get("unit", "pieces"),
                        "storage_location": item_data.get("storage_location"),
                        "category_id": category_id,
                    },
                )
                items_added.append(item)

            await db.commit()

            # Refresh items with relationships
            for item in items_added:
                await db.refresh(item, ["category"])

            logger.info(f"Added {len(items_added)} items from voice input")

            return VoiceAddResponse(
                transcription=transcription,
                items_added=items_added,
                message=f"Successfully added {len(items_added)} item(s) from voice input",
            )

        except Exception as e:
            logger.error(f"Failed to add items from voice: {e}")
            raise ValidationException(
                f"Failed to process voice input: {str(e)}",
                error_code="VOICE_PROCESSING_FAILED",
            )

    async def add_items_from_image(
        self,
        db: AsyncSession,
        image_data_base64: str,
        image_format: str,
        user_id: int,
    ) -> ImageScanResponse:
        """
        Add inventory items from image recognition.

        Args:
            db: Database session
            image_data_base64: Base64 encoded image data
            image_format: Image format (jpeg, jpg, png, webp)
            user_id: User ID

        Returns:
            Image scan response with identified items and added items

        Raises:
            ValidationException: If image analysis fails
        """
        try:
            # Analyze image
            analysis = await openai_service.analyze_food_image(
                image_data_base64,
                image_format,
            )

            logger.info(f"Analyzed food image: {analysis.get('description', '')}")

            description = analysis.get("description", "Food items detected")
            identified_items = analysis.get("items", [])

            # Create inventory items
            items_added = []
            items_identified_names = []

            for item_data in identified_items:
                items_identified_names.append(item_data.get("name", "Unknown"))

                # Calculate expiration date if shelf life provided
                expiration_date = None
                shelf_life_days = item_data.get("estimated_shelf_life_days")
                if shelf_life_days:
                    expiration_date = date.today() + timedelta(days=shelf_life_days)

                # Create item
                item = await inventory_repository.create(
                    db,
                    {
                        "user_id": user_id,
                        "name": item_data.get("name", "Unknown Item"),
                        "quantity": float(item_data.get("quantity", 1.0)),
                        "unit": item_data.get("unit", "pieces"),
                        "storage_location": item_data.get("storage_location"),
                        "expiration_date": expiration_date,
                    },
                )
                items_added.append(item)

            await db.commit()

            # Refresh items with relationships
            for item in items_added:
                await db.refresh(item, ["category"])

            logger.info(f"Added {len(items_added)} items from image scan")

            return ImageScanResponse(
                description=description,
                items_identified=items_identified_names,
                items_added=items_added,
                message=f"Successfully added {len(items_added)} item(s) from image",
            )

        except Exception as e:
            logger.error(f"Failed to add items from image: {e}")
            raise ValidationException(
                f"Failed to process image: {str(e)}",
                error_code="IMAGE_PROCESSING_FAILED",
            )

    async def get_user_inventory(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        storage_location: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[InventoryItem], int]:
        """
        Get user's inventory with filtering and pagination.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records
            category_id: Filter by category
            storage_location: Filter by storage location
            search: Search by item name
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)

        Returns:
            Tuple of (items list, total count)
        """
        return await inventory_repository.get_by_user(
            db,
            user_id,
            skip=skip,
            limit=limit,
            category_id=category_id,
            storage_location=storage_location,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def get_item_by_id(
        self,
        db: AsyncSession,
        item_id: int,
        user_id: int,
    ) -> InventoryItem:
        """
        Get inventory item by ID.

        Args:
            db: Database session
            item_id: Item ID
            user_id: User ID

        Returns:
            Inventory item

        Raises:
            NotFoundException: If item not found
        """
        item = await inventory_repository.get_by_id_and_user(db, item_id, user_id)

        if not item:
            raise NotFoundException(
                f"Inventory item with ID {item_id} not found",
                error_code="ITEM_NOT_FOUND",
            )

        return item

    async def update_item(
        self,
        db: AsyncSession,
        item_id: int,
        item_data: InventoryItemUpdate,
        user_id: int,
    ) -> InventoryItem:
        """
        Update inventory item.

        Args:
            db: Database session
            item_id: Item ID
            item_data: Update data
            user_id: User ID

        Returns:
            Updated inventory item

        Raises:
            NotFoundException: If item not found
            ValidationException: If validation fails
        """
        # Get existing item
        item = await self.get_item_by_id(db, item_id, user_id)

        # Validate category if being updated
        if item_data.category_id is not None:
            category = await food_category_repository.get(db, item_data.category_id)
            if not category:
                raise ValidationException(
                    f"Category with ID {item_data.category_id} not found",
                    error_code="CATEGORY_NOT_FOUND",
                )

        # Update item
        update_dict = item_data.model_dump(exclude_unset=True)
        updated_item = await inventory_repository.update(db, item, update_dict)

        await db.commit()
        await db.refresh(updated_item, ["category"])

        logger.info(f"Updated inventory item {item_id} for user {user_id}")

        return updated_item

    async def delete_item(
        self,
        db: AsyncSession,
        item_id: int,
        user_id: int,
    ) -> bool:
        """
        Soft delete inventory item.

        Args:
            db: Database session
            item_id: Item ID
            user_id: User ID

        Returns:
            True if deleted successfully

        Raises:
            NotFoundException: If item not found
        """
        # Verify ownership
        await self.get_item_by_id(db, item_id, user_id)

        # Soft delete
        await inventory_repository.soft_delete(db, item_id)

        await db.commit()

        logger.info(f"Deleted inventory item {item_id} for user {user_id}")

        return True

    async def get_expiring_items(
        self,
        db: AsyncSession,
        user_id: int,
        days: int = 7,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[InventoryItem], int]:
        """
        Get items expiring within specified days.

        Args:
            db: Database session
            user_id: User ID
            days: Number of days
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Tuple of (items list, total count)
        """
        return await inventory_repository.get_expiring_soon(
            db,
            user_id,
            days=days,
            skip=skip,
            limit=limit,
        )

    async def get_items_by_category(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> List[CategorySummary]:
        """
        Get inventory items grouped by category.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of category summaries with items
        """
        grouped = await inventory_repository.get_by_categories(db, user_id)

        summaries = []
        for category_id, category_name, items in grouped:
            total_items = sum(item.quantity for item in items)

            summaries.append(
                CategorySummary(
                    category_id=category_id,
                    category_name=category_name or "Uncategorized",
                    item_count=len(items),
                    total_items=int(total_items),
                    items=items,
                )
            )

        return summaries


# Singleton instance
inventory_service = InventoryService()
