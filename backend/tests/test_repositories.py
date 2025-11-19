"""
Comprehensive tests for repository layer (database operations).

Tests CRUD operations for all major entities:
- Users
- Inventory items
- Recipes
- Meal plans
- Grocery lists
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.inventory import InventoryItem, FoodCategory
from app.models.recipe import Recipe, RecipeIngredient
from app.models.meal_plan import MealPlan, MealPlanItem
from app.models.grocery_list import GroceryList, GroceryListItem
from app.repositories.user_repository import user_repository
from app.repositories.inventory_repository import inventory_repository
from app.repositories.recipe_repository import recipe_repository
from app.repositories.meal_plan_repository import meal_plan_repository
from app.repositories.grocery_list_repository import grocery_list_repository


class TestUserRepository:
    """Test user repository operations."""

    @pytest.mark.asyncio
    async def test_create_user(self, db: AsyncSession):
        """Test creating a new user."""
        user_data = {
            "email": "newuser@test.com",
            "hashed_password": "hashed_password",
            "is_active": True,
        }

        user = await user_repository.create(db, user_data)
        await db.commit()
        await db.refresh(user)

        assert user.id is not None
        assert user.email == "newuser@test.com"
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, db: AsyncSession, test_user: User):
        """Test retrieving user by ID."""
        user = await user_repository.get(db, test_user.id)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, db: AsyncSession, test_user: User):
        """Test retrieving user by email."""
        user = await user_repository.get_by_email(db, test_user.email)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.asyncio
    async def test_update_user(self, db: AsyncSession, test_user: User):
        """Test updating user information."""
        updated_user = await user_repository.update(
            db,
            test_user,
            {"full_name": "Updated Name"}
        )
        await db.commit()
        await db.refresh(updated_user)

        assert updated_user.full_name == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete_user(self, db: AsyncSession, test_user: User):
        """Test deleting a user."""
        await user_repository.delete(db, test_user.id)
        await db.commit()

        deleted_user = await user_repository.get(db, test_user.id)
        assert deleted_user is None


class TestInventoryRepository:
    """Test inventory repository operations."""

    @pytest.mark.asyncio
    async def test_create_inventory_item(
        self,
        db: AsyncSession,
        test_user: User
    ):
        """Test creating an inventory item."""
        item_data = {
            "user_id": test_user.id,
            "name": "Chicken Breast",
            "quantity": 500.0,
            "unit": "g",
            "category": FoodCategory.MEAT,
            "location": "fridge",
        }

        item = await inventory_repository.create(db, item_data)
        await db.commit()
        await db.refresh(item)

        assert item.id is not None
        assert item.name == "Chicken Breast"
        assert item.quantity == 500.0
        assert item.category == FoodCategory.MEAT

    @pytest.mark.asyncio
    async def test_get_user_inventory(
        self,
        db: AsyncSession,
        test_user: User
    ):
        """Test retrieving all inventory items for a user."""
        # Create multiple items
        for i in range(3):
            item_data = {
                "user_id": test_user.id,
                "name": f"Item {i}",
                "quantity": 100.0,
                "unit": "g",
                "category": FoodCategory.PANTRY,
            }
            await inventory_repository.create(db, item_data)

        await db.commit()

        items = await inventory_repository.get_by_user(db, test_user.id)

        assert len(items) >= 3
        assert all(item.user_id == test_user.id for item in items)

    @pytest.mark.asyncio
    async def test_update_inventory_quantity(
        self,
        db: AsyncSession,
        test_user: User
    ):
        """Test updating inventory item quantity."""
        item_data = {
            "user_id": test_user.id,
            "name": "Rice",
            "quantity": 1000.0,
            "unit": "g",
            "category": FoodCategory.PANTRY,
        }
        item = await inventory_repository.create(db, item_data)
        await db.commit()
        await db.refresh(item)

        # Update quantity
        updated_item = await inventory_repository.update(
            db,
            item,
            {"quantity": 500.0}
        )
        await db.commit()
        await db.refresh(updated_item)

        assert updated_item.quantity == 500.0

    @pytest.mark.asyncio
    async def test_filter_by_category(
        self,
        db: AsyncSession,
        test_user: User
    ):
        """Test filtering inventory by category."""
        # Create items in different categories
        categories = [FoodCategory.MEAT, FoodCategory.PRODUCE, FoodCategory.MEAT]
        for i, category in enumerate(categories):
            item_data = {
                "user_id": test_user.id,
                "name": f"Item {i}",
                "quantity": 100.0,
                "unit": "g",
                "category": category,
            }
            await inventory_repository.create(db, item_data)

        await db.commit()

        # Filter by MEAT category
        meat_items = await inventory_repository.get_by_category(
            db,
            test_user.id,
            FoodCategory.MEAT
        )

        assert len(meat_items) == 2
        assert all(item.category == FoodCategory.MEAT for item in meat_items)

    @pytest.mark.asyncio
    async def test_filter_expiring_soon(
        self,
        db: AsyncSession,
        test_user: User
    ):
        """Test filtering items expiring soon."""
        # Create item expiring in 2 days
        item_data = {
            "user_id": test_user.id,
            "name": "Milk",
            "quantity": 1000.0,
            "unit": "ml",
            "category": FoodCategory.DAIRY,
            "expiry_date": datetime.utcnow() + timedelta(days=2),
        }
        await inventory_repository.create(db, item_data)

        # Create item expiring in 10 days
        item_data2 = {
            "user_id": test_user.id,
            "name": "Cheese",
            "quantity": 200.0,
            "unit": "g",
            "category": FoodCategory.DAIRY,
            "expiry_date": datetime.utcnow() + timedelta(days=10),
        }
        await inventory_repository.create(db, item_data2)

        await db.commit()

        # Get items expiring within 3 days
        expiring_items = await inventory_repository.get_expiring_soon(
            db,
            test_user.id,
            days=3
        )

        assert len(expiring_items) >= 1
        assert all(
            item.expiry_date <= datetime.utcnow() + timedelta(days=3)
            for item in expiring_items
            if item.expiry_date
        )


class TestRecipeRepository:
    """Test recipe repository operations."""

    @pytest.mark.asyncio
    async def test_create_recipe(self, db: AsyncSession):
        """Test creating a recipe."""
        recipe_data = {
            "name": "Pasta Carbonara",
            "description": "Classic Italian pasta",
            "prep_time": 10,
            "cook_time": 15,
            "total_time": 25,
            "servings": 4,
            "difficulty": "medium",
            "cuisine": "italian",
            "calories_per_serving": 450,
            "protein_per_serving": 20.0,
            "carbs_per_serving": 50.0,
            "fat_per_serving": 15.0,
        }

        recipe = await recipe_repository.create(db, recipe_data)
        await db.commit()
        await db.refresh(recipe)

        assert recipe.id is not None
        assert recipe.name == "Pasta Carbonara"
        assert recipe.difficulty == "medium"

    @pytest.mark.asyncio
    async def test_search_recipes_by_name(self, db: AsyncSession):
        """Test searching recipes by name."""
        # Create multiple recipes
        recipes_data = [
            {"name": "Chicken Curry", "difficulty": "medium", "cuisine": "indian"},
            {"name": "Chicken Salad", "difficulty": "easy", "cuisine": "american"},
            {"name": "Beef Stew", "difficulty": "hard", "cuisine": "american"},
        ]

        for data in recipes_data:
            data.update({
                "prep_time": 10,
                "cook_time": 20,
                "total_time": 30,
                "servings": 4,
                "calories_per_serving": 400,
                "protein_per_serving": 30.0,
                "carbs_per_serving": 40.0,
                "fat_per_serving": 10.0,
            })
            await recipe_repository.create(db, data)

        await db.commit()

        # Search for "chicken"
        results = await recipe_repository.search(db, query="chicken")

        assert len(results) >= 2
        assert all("chicken" in recipe.name.lower() for recipe in results)

    @pytest.mark.asyncio
    async def test_filter_recipes_by_cuisine(self, db: AsyncSession):
        """Test filtering recipes by cuisine."""
        # Create recipes with different cuisines
        cuisines = ["italian", "mexican", "italian"]
        for i, cuisine in enumerate(cuisines):
            recipe_data = {
                "name": f"Recipe {i}",
                "difficulty": "easy",
                "cuisine": cuisine,
                "prep_time": 10,
                "cook_time": 20,
                "total_time": 30,
                "servings": 4,
                "calories_per_serving": 400,
                "protein_per_serving": 30.0,
                "carbs_per_serving": 40.0,
                "fat_per_serving": 10.0,
            }
            await recipe_repository.create(db, recipe_data)

        await db.commit()

        # Filter by Italian cuisine
        italian_recipes = await recipe_repository.filter_by_cuisine(
            db,
            cuisine="italian"
        )

        assert len(italian_recipes) >= 2
        assert all(recipe.cuisine == "italian" for recipe in italian_recipes)

    @pytest.mark.asyncio
    async def test_filter_recipes_by_difficulty(self, db: AsyncSession):
        """Test filtering recipes by difficulty."""
        # Create recipes with different difficulties
        difficulties = ["easy", "hard", "easy"]
        for i, difficulty in enumerate(difficulties):
            recipe_data = {
                "name": f"Recipe {i}",
                "difficulty": difficulty,
                "cuisine": "american",
                "prep_time": 10,
                "cook_time": 20,
                "total_time": 30,
                "servings": 4,
                "calories_per_serving": 400,
                "protein_per_serving": 30.0,
                "carbs_per_serving": 40.0,
                "fat_per_serving": 10.0,
            }
            await recipe_repository.create(db, recipe_data)

        await db.commit()

        # Filter by easy difficulty
        easy_recipes = await recipe_repository.filter_by_difficulty(
            db,
            difficulty="easy"
        )

        assert len(easy_recipes) >= 2
        assert all(recipe.difficulty == "easy" for recipe in easy_recipes)


class TestMealPlanRepository:
    """Test meal plan repository operations."""

    @pytest.mark.asyncio
    async def test_create_meal_plan(
        self,
        db: AsyncSession,
        test_user: User
    ):
        """Test creating a meal plan."""
        meal_plan_data = {
            "user_id": test_user.id,
            "name": "Weekly Plan",
            "start_date": datetime.utcnow().date(),
            "end_date": (datetime.utcnow() + timedelta(days=7)).date(),
            "total_days": 7,
            "goal": "weight_loss",
            "target_calories": 1800,
        }

        meal_plan = await meal_plan_repository.create(db, meal_plan_data)
        await db.commit()
        await db.refresh(meal_plan)

        assert meal_plan.id is not None
        assert meal_plan.name == "Weekly Plan"
        assert meal_plan.total_days == 7

    @pytest.mark.asyncio
    async def test_get_user_meal_plans(
        self,
        db: AsyncSession,
        test_user: User
    ):
        """Test retrieving user's meal plans."""
        # Create multiple meal plans
        for i in range(2):
            meal_plan_data = {
                "user_id": test_user.id,
                "name": f"Plan {i}",
                "start_date": datetime.utcnow().date(),
                "end_date": (datetime.utcnow() + timedelta(days=7)).date(),
                "total_days": 7,
                "goal": "maintenance",
            }
            await meal_plan_repository.create(db, meal_plan_data)

        await db.commit()

        plans = await meal_plan_repository.get_by_user(db, test_user.id)

        assert len(plans) >= 2
        assert all(plan.user_id == test_user.id for plan in plans)

    @pytest.mark.asyncio
    async def test_get_active_meal_plan(
        self,
        db: AsyncSession,
        test_user: User
    ):
        """Test retrieving active meal plan."""
        # Create active meal plan
        meal_plan_data = {
            "user_id": test_user.id,
            "name": "Active Plan",
            "start_date": datetime.utcnow().date(),
            "end_date": (datetime.utcnow() + timedelta(days=7)).date(),
            "total_days": 7,
            "is_active": True,
        }
        await meal_plan_repository.create(db, meal_plan_data)
        await db.commit()

        active_plan = await meal_plan_repository.get_active(db, test_user.id)

        assert active_plan is not None
        assert active_plan.is_active is True
        assert active_plan.user_id == test_user.id


class TestGroceryListRepository:
    """Test grocery list repository operations."""

    @pytest.mark.asyncio
    async def test_create_grocery_list(
        self,
        db: AsyncSession,
        test_user: User
    ):
        """Test creating a grocery list."""
        list_data = {
            "user_id": test_user.id,
            "name": "Weekly Shopping",
            "is_active": True,
        }

        grocery_list = await grocery_list_repository.create(db, list_data)
        await db.commit()
        await db.refresh(grocery_list)

        assert grocery_list.id is not None
        assert grocery_list.name == "Weekly Shopping"
        assert grocery_list.is_active is True

    @pytest.mark.asyncio
    async def test_add_items_to_list(
        self,
        db: AsyncSession,
        test_user: User
    ):
        """Test adding items to grocery list."""
        # Create grocery list
        list_data = {
            "user_id": test_user.id,
            "name": "Shopping List",
        }
        grocery_list = await grocery_list_repository.create(db, list_data)
        await db.commit()
        await db.refresh(grocery_list)

        # Add items
        items_data = [
            {
                "grocery_list_id": grocery_list.id,
                "name": "Milk",
                "quantity": 2,
                "unit": "L",
                "category": "dairy",
                "order_index": 1,
            },
            {
                "grocery_list_id": grocery_list.id,
                "name": "Bread",
                "quantity": 1,
                "unit": "unit",
                "category": "bakery",
                "order_index": 2,
            },
        ]

        for item_data in items_data:
            item = GroceryListItem(**item_data)
            db.add(item)

        await db.commit()

        # Retrieve list with items
        grocery_list = await grocery_list_repository.get(db, grocery_list.id)

        assert len(grocery_list.items) == 2

    @pytest.mark.asyncio
    async def test_mark_item_purchased(
        self,
        db: AsyncSession,
        test_user: User
    ):
        """Test marking grocery item as purchased."""
        # Create list and item
        list_data = {
            "user_id": test_user.id,
            "name": "Shopping",
        }
        grocery_list = await grocery_list_repository.create(db, list_data)
        await db.commit()
        await db.refresh(grocery_list)

        item = GroceryListItem(
            grocery_list_id=grocery_list.id,
            name="Eggs",
            quantity=12,
            unit="unit",
            category="dairy",
            is_purchased=False,
            order_index=1,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)

        # Mark as purchased
        item.is_purchased = True
        await db.commit()
        await db.refresh(item)

        assert item.is_purchased is True

    @pytest.mark.asyncio
    async def test_get_completed_lists(
        self,
        db: AsyncSession,
        test_user: User
    ):
        """Test retrieving completed grocery lists."""
        # Create completed list
        list_data = {
            "user_id": test_user.id,
            "name": "Completed Shopping",
            "is_completed": True,
        }
        await grocery_list_repository.create(db, list_data)
        await db.commit()

        completed_lists = await grocery_list_repository.get_completed(
            db,
            test_user.id
        )

        assert len(completed_lists) >= 1
        assert all(lst.is_completed for lst in completed_lists)
