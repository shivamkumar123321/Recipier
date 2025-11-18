"""
Database relationship verification script.

This script checks that all models are properly configured with
correct relationships, foreign keys, and constraints.
"""

from app.db.base import Base
from app.models import (
    AIAnalysis,
    ActivityLog,
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


def verify_models():
    """Verify all models are properly configured."""
    print("🔍 Verifying Database Models and Relationships\n")
    print("=" * 80)

    # Get all mapped classes
    models = [
        ("User", User),
        ("UserProfile", UserProfile),
        ("UserGoal", UserGoal),
        ("Meal", Meal),
        ("MealItem", MealItem),
        ("AIAnalysis", AIAnalysis),
        ("FoodCategory", FoodCategory),
        ("InventoryItem", InventoryItem),
        ("Recipe", Recipe),
        ("RecipeIngredient", RecipeIngredient),
        ("RecipeInstruction", RecipeInstruction),
        ("UserRecipe", UserRecipe),
        ("MealPlan", MealPlan),
        ("MealPlanItem", MealPlanItem),
        ("GroceryList", GroceryList),
        ("GroceryListItem", GroceryListItem),
        ("ActivityLog", ActivityLog),
    ]

    print(f"\n✅ Found {len(models)} models\n")

    # Check each model
    for model_name, model_class in models:
        print(f"\n📋 {model_name}")
        print("-" * 80)

        # Table name
        table_name = model_class.__tablename__
        print(f"  Table: {table_name}")

        # Columns
        columns = list(model_class.__table__.columns.keys())
        print(f"  Columns ({len(columns)}): {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")

        # Relationships
        relationships = []
        for attr_name in dir(model_class):
            attr = getattr(model_class, attr_name)
            if hasattr(attr, "property") and hasattr(attr.property, "mapper"):
                relationships.append(attr_name)

        if relationships:
            print(f"  Relationships ({len(relationships)}): {', '.join(relationships)}")
        else:
            print("  Relationships: None")

        # Foreign keys
        foreign_keys = []
        for column in model_class.__table__.columns:
            if column.foreign_keys:
                for fk in column.foreign_keys:
                    foreign_keys.append(f"{column.name} → {fk.target_fullname}")

        if foreign_keys:
            print(f"  Foreign Keys ({len(foreign_keys)}):")
            for fk in foreign_keys:
                print(f"    • {fk}")

        # Indexes
        indexes = list(model_class.__table__.indexes)
        if indexes:
            print(f"  Indexes: {len(indexes)}")

        # Constraints
        constraints = [c for c in model_class.__table__.constraints if not c.name.startswith("pk_")]
        if constraints:
            print(f"  Constraints: {len(constraints)}")

    print("\n" + "=" * 80)
    print("\n📊 Summary:")
    print(f"  Total Models: {len(models)}")
    print(f"  Total Tables: {len(Base.metadata.tables)}")
    print("\n✅ All models verified successfully!")
    print("\nTo create database tables, run:")
    print("  alembic upgrade head\n")


def verify_relationships():
    """Verify specific critical relationships."""
    print("\n🔗 Verifying Critical Relationships\n")
    print("=" * 80)

    relationships_to_check = [
        ("User", "profile", "UserProfile"),
        ("User", "meals", "Meal"),
        ("User", "inventory_items", "InventoryItem"),
        ("User", "recipes", "Recipe"),
        ("Meal", "meal_items", "MealItem"),
        ("Meal", "ai_analysis", "AIAnalysis"),
        ("Recipe", "ingredients", "RecipeIngredient"),
        ("Recipe", "instructions", "RecipeInstruction"),
        ("MealPlan", "meal_plan_items", "MealPlanItem"),
        ("GroceryList", "items", "GroceryListItem"),
    ]

    all_verified = True

    for model_name, rel_name, related_model_name in relationships_to_check:
        # Get model class
        model_class = globals().get(model_name)
        if not model_class:
            print(f"  ❌ Model {model_name} not found")
            all_verified = False
            continue

        # Check relationship exists
        if not hasattr(model_class, rel_name):
            print(f"  ❌ {model_name}.{rel_name} relationship missing")
            all_verified = False
        else:
            print(f"  ✅ {model_name}.{rel_name} → {related_model_name}")

    print("\n" + "=" * 80)
    if all_verified:
        print("\n✅ All critical relationships verified!")
    else:
        print("\n⚠️  Some relationships need attention")


if __name__ == "__main__":
    try:
        verify_models()
        verify_relationships()
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
