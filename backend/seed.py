"""
Database seed script with sample data.

Run this script to populate the database with test data for development.

Usage:
    python seed.py
"""

import asyncio
from datetime import date, datetime, timedelta

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal, init_db
from app.models import (
    ActivityLog,
    AIAnalysis,
    FoodCategory,
    GroceryList,
    GroceryListItem,
    InventoryItem,
    Meal,
    MealItem,
    MealPlan,
    MealPlanItem,
    Recipe,
    RecipeIngredient,
    RecipeInstruction,
    User,
    UserGoal,
    UserProfile,
    UserRecipe,
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_food_categories(db: AsyncSession) -> dict:
    """Create food categories."""
    print("Creating food categories...")

    categories_data = [
        {"name": "Fruits", "description": "Fresh and dried fruits", "icon": "🍎"},
        {"name": "Vegetables", "description": "Fresh vegetables", "icon": "🥗"},
        {"name": "Grains", "description": "Rice, pasta, bread, cereals", "icon": "🌾"},
        {"name": "Proteins", "description": "Meat, fish, eggs, tofu", "icon": "🍗"},
        {"name": "Dairy", "description": "Milk, cheese, yogurt", "icon": "🥛"},
        {"name": "Snacks", "description": "Chips, crackers, nuts", "icon": "🍿"},
        {"name": "Beverages", "description": "Drinks and juices", "icon": "🥤"},
        {"name": "Condiments", "description": "Sauces, spices, oils", "icon": "🧂"},
        {"name": "Legumes", "description": "Beans, lentils, peas", "icon": "🫘"},
        {"name": "Bakery", "description": "Bread, pastries, baked goods", "icon": "🥖"},
    ]

    categories = {}
    for cat_data in categories_data:
        category = FoodCategory(**cat_data)
        db.add(category)
        await db.flush()
        categories[cat_data["name"]] = category

    await db.commit()
    print(f"✓ Created {len(categories)} food categories")
    return categories


async def create_test_users(db: AsyncSession) -> dict:
    """Create test users with profiles and goals."""
    print("Creating test users...")

    users_data = [
        {
            "email": "john@example.com",
            "password": "password123",
            "profile": {
                "full_name": "John Doe",
                "date_of_birth": date(1990, 5, 15),
                "gender": "M",
                "height_cm": 180.0,
                "current_weight_kg": 85.0,
                "activity_level": "moderate",
                "dietary_restrictions": ["vegetarian"],
                "allergies": ["peanuts"],
                "preferences": {
                    "cuisine_preferences": ["italian", "mexican"],
                    "cooking_skill": "intermediate",
                },
            },
            "goal": {
                "goal_type": "weight_loss",
                "target_weight_kg": 75.0,
                "target_calories": 2000,
                "macro_targets": {"protein": 150, "carbs": 200, "fat": 65},
                "start_date": date.today() - timedelta(days=30),
                "target_date": date.today() + timedelta(days=90),
            },
        },
        {
            "email": "sarah@example.com",
            "password": "password123",
            "profile": {
                "full_name": "Sarah Smith",
                "date_of_birth": date(1995, 8, 22),
                "gender": "F",
                "height_cm": 165.0,
                "current_weight_kg": 60.0,
                "activity_level": "active",
                "dietary_restrictions": ["gluten_free"],
                "allergies": [],
                "preferences": {"cuisine_preferences": ["asian", "mediterranean"]},
            },
            "goal": {
                "goal_type": "muscle_gain",
                "target_weight_kg": 65.0,
                "target_calories": 2500,
                "macro_targets": {"protein": 180, "carbs": 250, "fat": 80},
                "start_date": date.today() - timedelta(days=15),
                "target_date": date.today() + timedelta(days=120),
            },
        },
    ]

    users = {}
    for user_data in users_data:
        # Create user
        user = User(
            email=user_data["email"],
            hashed_password=pwd_context.hash(user_data["password"]),
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        await db.flush()

        # Create profile
        profile = UserProfile(user_id=user.id, **user_data["profile"])
        db.add(profile)

        # Create goal
        goal = UserGoal(user_id=user.id, **user_data["goal"])
        db.add(goal)

        users[user_data["email"]] = user

    await db.commit()
    print(f"✓ Created {len(users)} test users")
    return users


async def create_inventory_items(
    db: AsyncSession, users: dict, categories: dict
) -> None:
    """Create sample inventory items."""
    print("Creating inventory items...")

    john = users["john@example.com"]

    items_data = [
        {
            "name": "Chicken Breast",
            "category": "Proteins",
            "quantity": 500,
            "unit": "g",
            "expiration_date": date.today() + timedelta(days=3),
            "storage_location": "fridge",
        },
        {
            "name": "Brown Rice",
            "category": "Grains",
            "quantity": 1000,
            "unit": "g",
            "expiration_date": date.today() + timedelta(days=365),
            "storage_location": "pantry",
        },
        {
            "name": "Broccoli",
            "category": "Vegetables",
            "quantity": 300,
            "unit": "g",
            "expiration_date": date.today() + timedelta(days=5),
            "storage_location": "fridge",
        },
        {
            "name": "Milk",
            "category": "Dairy",
            "quantity": 1,
            "unit": "L",
            "expiration_date": date.today() + timedelta(days=7),
            "storage_location": "fridge",
        },
        {
            "name": "Pasta",
            "category": "Grains",
            "quantity": 500,
            "unit": "g",
            "expiration_date": date.today() + timedelta(days=730),
            "storage_location": "pantry",
        },
    ]

    for item_data in items_data:
        category_name = item_data.pop("category")
        item = InventoryItem(
            user_id=john.id,
            category_id=categories[category_name].id,
            **item_data,
        )
        db.add(item)

    await db.commit()
    print(f"✓ Created {len(items_data)} inventory items")


async def create_meals(db: AsyncSession, users: dict) -> None:
    """Create sample meal logs."""
    print("Creating sample meals...")

    john = users["john@example.com"]

    # Today's breakfast
    breakfast = Meal(
        user_id=john.id,
        name="Oatmeal with Berries",
        meal_type="breakfast",
        description="Steel-cut oats with blueberries and almonds",
        consumed_at=datetime.now().replace(hour=8, minute=30),
        input_method="text",
        total_calories=350,
        macros={"protein": 12, "carbs": 58, "fat": 10},
    )
    db.add(breakfast)
    await db.flush()

    # Breakfast items
    breakfast_items = [
        {
            "food_name": "Oats",
            "quantity": 50,
            "unit": "g",
            "calories": 190,
            "nutrition_data": {"protein": 7, "carbs": 33, "fat": 4},
        },
        {
            "food_name": "Blueberries",
            "quantity": 100,
            "unit": "g",
            "calories": 57,
            "nutrition_data": {"protein": 1, "carbs": 14, "fat": 0.3},
        },
        {
            "food_name": "Almonds",
            "quantity": 20,
            "unit": "g",
            "calories": 115,
            "nutrition_data": {"protein": 4, "carbs": 4, "fat": 10},
        },
    ]

    for item_data in breakfast_items:
        item = MealItem(meal_id=breakfast.id, **item_data)
        db.add(item)

    # AI Analysis for breakfast
    ai_analysis = AIAnalysis(
        meal_id=breakfast.id,
        analysis="Great breakfast choice! The oats provide slow-releasing carbs, "
        "blueberries add antioxidants, and almonds provide healthy fats.",
        recommendations="Consider adding a protein source like Greek yogurt to "
        "increase satiety and hit your protein goals.",
        nutrition_breakdown={
            "calories": 350,
            "protein_percentage": 14,
            "carbs_percentage": 66,
            "fat_percentage": 26,
        },
        confidence_score=0.95,
        model_version="gpt-4-1106-preview",
    )
    db.add(ai_analysis)

    # Yesterday's lunch
    lunch = Meal(
        user_id=john.id,
        name="Grilled Chicken Salad",
        meal_type="lunch",
        consumed_at=datetime.now() - timedelta(days=1, hours=-12),
        input_method="image",
        image_url="https://example.com/meal-photos/lunch-salad.jpg",
        total_calories=450,
        macros={"protein": 35, "carbs": 25, "fat": 22},
    )
    db.add(lunch)

    await db.commit()
    print("✓ Created sample meals with items and AI analysis")


async def create_recipes(db: AsyncSession, users: dict, categories: dict) -> dict:
    """Create sample recipes."""
    print("Creating sample recipes...")

    john = users["john@example.com"]

    recipe = Recipe(
        user_id=john.id,
        name="Healthy Chicken Stir-Fry",
        description="Quick and nutritious chicken and vegetable stir-fry",
        prep_time_minutes=15,
        cook_time_minutes=15,
        servings=2,
        difficulty="easy",
        calories_per_serving=380,
        macros_per_serving={"protein": 35, "carbs": 30, "fat": 15},
        is_public=True,
        views_count=42,
        saves_count=8,
    )
    db.add(recipe)
    await db.flush()

    # Recipe ingredients
    ingredients = [
        ("Chicken Breast", "Proteins", 300, "g", 1),
        ("Broccoli", "Vegetables", 200, "g", 2),
        ("Bell Pepper", "Vegetables", 150, "g", 3),
        ("Soy Sauce", "Condiments", 2, "tbsp", 4),
        ("Garlic", "Vegetables", 2, "cloves", 5),
        ("Olive Oil", "Condiments", 1, "tbsp", 6),
    ]

    for name, cat, qty, unit, order in ingredients:
        ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            category_id=categories[cat].id,
            ingredient_name=name,
            quantity=qty,
            unit=unit,
            order_index=order,
        )
        db.add(ingredient)

    # Recipe instructions
    instructions = [
        "Cut chicken breast into bite-sized pieces and season with salt and pepper.",
        "Heat olive oil in a large pan or wok over medium-high heat.",
        "Add minced garlic and cook for 30 seconds until fragrant.",
        "Add chicken and cook for 5-6 minutes until golden brown.",
        "Add broccoli and bell pepper, stir-fry for 4-5 minutes.",
        "Add soy sauce and stir well. Cook for another 2 minutes.",
        "Serve hot over rice or enjoy on its own.",
    ]

    for i, instruction_text in enumerate(instructions, 1):
        instruction = RecipeInstruction(
            recipe_id=recipe.id,
            step_number=i,
            instruction=instruction_text,
        )
        db.add(instruction)

    # User saves this recipe
    user_recipe = UserRecipe(
        user_id=john.id,
        recipe_id=recipe.id,
        rating=5,
        notes="One of my favorite quick dinners!",
    )
    db.add(user_recipe)

    await db.commit()
    print("✓ Created sample recipe with ingredients and instructions")
    return {"stir_fry": recipe}


async def create_meal_plans(
    db: AsyncSession, users: dict, recipes: dict
) -> dict:
    """Create sample meal plans."""
    print("Creating sample meal plans...")

    john = users["john@example.com"]

    meal_plan = MealPlan(
        user_id=john.id,
        name="Week of 2025-01-15",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=7),
        target_calories=2000,
        macro_targets={"protein": 150, "carbs": 200, "fat": 65},
        status="active",
    )
    db.add(meal_plan)
    await db.flush()

    # Add meals to plan
    stir_fry = recipes["stir_fry"]

    # Schedule stir-fry for dinner today and tomorrow
    for i in range(2):
        plan_item = MealPlanItem(
            meal_plan_id=meal_plan.id,
            recipe_id=stir_fry.id,
            scheduled_date=date.today() + timedelta(days=i),
            meal_type="dinner",
            servings=1,
            is_completed=(i == 0),  # Today's is completed
        )
        db.add(plan_item)

    await db.commit()
    print("✓ Created meal plan with scheduled items")
    return {"week1": meal_plan}


async def create_grocery_lists(
    db: AsyncSession, users: dict, meal_plans: dict, categories: dict
) -> None:
    """Create sample grocery lists."""
    print("Creating sample grocery lists...")

    john = users["john@example.com"]
    week1_plan = meal_plans["week1"]

    grocery_list = GroceryList(
        user_id=john.id,
        meal_plan_id=week1_plan.id,
        name="Weekly Groceries - Jan 15",
        status="active",
    )
    db.add(grocery_list)
    await db.flush()

    # Grocery items
    items = [
        ("Chicken Breast", "Proteins", 1000, "g", False, 1),
        ("Broccoli", "Vegetables", 500, "g", True, 2),
        ("Bell Peppers", "Vegetables", 400, "g", False, 3),
        ("Soy Sauce", "Condiments", 1, "bottle", False, 4),
        ("Olive Oil", "Condiments", 500, "ml", False, 5),
        ("Brown Rice", "Grains", 1, "kg", False, 6),
    ]

    for name, cat, qty, unit, checked, order in items:
        item = GroceryListItem(
            grocery_list_id=grocery_list.id,
            category_id=categories[cat].id,
            item_name=name,
            quantity=qty,
            unit=unit,
            is_checked=checked,
            order_index=order,
        )
        db.add(item)

    await db.commit()
    print("✓ Created grocery list with items")


async def create_activity_logs(db: AsyncSession, users: dict) -> None:
    """Create sample activity logs."""
    print("Creating activity logs...")

    john = users["john@example.com"]

    logs = [
        {
            "user_id": john.id,
            "activity_type": "login",
            "entity_type": "user",
            "entity_id": john.id,
            "ip_address": "192.168.1.1",
        },
        {
            "user_id": john.id,
            "activity_type": "create",
            "entity_type": "meal",
            "entity_id": 1,
            "changes": {"action": "logged_breakfast"},
            "ip_address": "192.168.1.1",
        },
        {
            "user_id": john.id,
            "activity_type": "update",
            "entity_type": "user_profile",
            "entity_id": 1,
            "changes": {
                "before": {"current_weight_kg": 86.0},
                "after": {"current_weight_kg": 85.0},
            },
            "ip_address": "192.168.1.1",
        },
    ]

    for log_data in logs:
        log = ActivityLog(**log_data)
        db.add(log)

    await db.commit()
    print("✓ Created activity logs")


async def seed_database() -> None:
    """Main seed function."""
    print("\n🌱 Starting database seed...\n")

    # Initialize database (create tables if they don't exist)
    print("Initializing database...")
    await init_db()
    print("✓ Database initialized\n")

    async with AsyncSessionLocal() as db:
        # Create all seed data
        categories = await create_food_categories(db)
        users = await create_test_users(db)
        await create_inventory_items(db, users, categories)
        await create_meals(db, users)
        recipes = await create_recipes(db, users, categories)
        meal_plans = await create_meal_plans(db, users, recipes)
        await create_grocery_lists(db, users, meal_plans, categories)
        await create_activity_logs(db, users)

    print("\n✅ Database seeding completed successfully!")
    print("\nTest Users:")
    print("  - john@example.com (password: password123)")
    print("  - sarah@example.com (password: password123)\n")


if __name__ == "__main__":
    asyncio.run(seed_database())
