#!/usr/bin/env python3
"""
End-to-End Test Script for Intelligent Meal Planning and Coaching

Tests all implemented features:
1. POST /api/meal-plans/generate-intelligent - Intelligent meal plan generation
2. POST /api/coaching/advice - Context-aware nutrition advice
3. POST /api/recipes/generate - Custom recipe generation
4. WebSocket /ws/meal-plan-generation - Streaming meal plan generation

This script demonstrates the complete functionality without requiring pytest.
"""

import asyncio
import json
from datetime import datetime

import httpx


# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

# Test credentials (you'll need to use real credentials)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_json(data):
    print(json.dumps(data, indent=2))


async def authenticate():
    """Authenticate and get JWT token"""
    print_header("1. Authentication")

    async with httpx.AsyncClient() as client:
        # Try to login
        print_info("Attempting to login...")
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )

        if response.status_code == 200:
            token = response.json()["access_token"]
            print_success("Login successful!")
            return token
        elif response.status_code == 404:
            print_info("User not found, attempting registration...")
            # Register new user
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/register",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD,
                    "full_name": "Test User"
                }
            )

            if response.status_code == 201:
                print_success("Registration successful!")
                # Login again
                response = await client.post(
                    f"{BASE_URL}/api/v1/auth/login",
                    json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
                )
                token = response.json()["access_token"]
                print_success("Login successful!")
                return token
            else:
                print_error(f"Registration failed: {response.status_code}")
                print_json(response.json())
                return None
        else:
            print_error(f"Authentication failed: {response.status_code}")
            print_json(response.json())
            return None


async def test_intelligent_meal_plan(token):
    """Test intelligent meal plan generation endpoint"""
    print_header("2. Intelligent Meal Plan Generation (REST API)")

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=60.0) as client:
        print_info("Generating 3-day meal plan with dietary restrictions...")

        params = {
            "days": 3,
            "dietary_restrictions": "vegetarian,gluten-free",
            "target_calories": 2000
        }

        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/meal-plans/generate-intelligent",
                headers=headers,
                params=params
            )

            if response.status_code == 201:
                print_success("Meal plan generated successfully!")
                plan = response.json()

                print_info(f"Plan Name: {plan.get('name', 'N/A')}")
                print_info(f"Description: {plan.get('description', 'N/A')}")
                print_info(f"Total Days: {plan.get('total_days', 'N/A')}")

                if 'days' in plan and len(plan['days']) > 0:
                    first_day = plan['days'][0]
                    print_info(f"\nFirst Day Sample:")
                    print_info(f"  Date: {first_day.get('date', 'N/A')}")

                    if 'meals' in first_day and len(first_day['meals']) > 0:
                        first_meal = first_day['meals'][0]
                        print_info(f"  First Meal: {first_meal.get('recipe_name', 'N/A')}")
                        print_info(f"  Type: {first_meal.get('meal_type', 'N/A')}")

                if 'shopping_list' in plan:
                    print_info(f"\nShopping List Items: {len(plan['shopping_list'])}")

                return True
            else:
                print_error(f"Failed to generate meal plan: {response.status_code}")
                print_json(response.json())
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False


async def test_coaching_advice(token):
    """Test context-aware nutrition coaching endpoint"""
    print_header("3. Context-Aware Nutrition Coaching")

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        print_info("Getting personalized nutrition advice...")

        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/coaching/advice",
                headers=headers,
                json={
                    "specific_question": "What healthy meals can I make with my current inventory?"
                }
            )

            if response.status_code == 200:
                print_success("Coaching advice retrieved successfully!")
                advice = response.json()

                print_info("\nCoaching Message:")
                print(f"  {advice.get('coaching_message', 'N/A')}")

                if 'quick_tips' in advice and len(advice['quick_tips']) > 0:
                    print_info("\nQuick Tips:")
                    for tip in advice['quick_tips'][:3]:
                        print(f"  • {tip}")

                if 'motivation' in advice:
                    print_info(f"\nMotivation: {advice['motivation']}")

                return True
            else:
                print_error(f"Failed to get coaching advice: {response.status_code}")
                print_json(response.json())
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False


async def test_custom_recipe_generation(token):
    """Test custom recipe generation from ingredients"""
    print_header("4. Custom Recipe Generation")

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=60.0) as client:
        print_info("Generating custom recipe from available ingredients...")

        recipe_request = {
            "available_ingredients": [
                "Chicken Breast",
                "Broccoli",
                "Garlic",
                "Olive Oil",
                "Lemon"
            ],
            "dietary_restrictions": ["gluten-free"],
            "cuisine_type": "mediterranean",
            "meal_type": "dinner"
        }

        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/recipes/generate",
                headers=headers,
                json=recipe_request
            )

            if response.status_code == 201:
                print_success("Custom recipe generated successfully!")
                recipe = response.json()

                print_info(f"\nRecipe Name: {recipe.get('recipe_name', 'N/A')}")
                print_info(f"Description: {recipe.get('description', 'N/A')}")
                print_info(f"Servings: {recipe.get('servings', 'N/A')}")
                print_info(f"Difficulty: {recipe.get('difficulty', 'N/A')}")
                print_info(f"Prep Time: {recipe.get('prep_time_minutes', 'N/A')} min")
                print_info(f"Cook Time: {recipe.get('cook_time_minutes', 'N/A')} min")

                if 'nutrition_per_serving' in recipe:
                    nutrition = recipe['nutrition_per_serving']
                    print_info(f"\nNutrition (per serving):")
                    print_info(f"  Calories: {nutrition.get('calories', 'N/A')}")
                    print_info(f"  Protein: {nutrition.get('protein_grams', 'N/A')}g")
                    print_info(f"  Carbs: {nutrition.get('carbohydrates_grams', 'N/A')}g")
                    print_info(f"  Fat: {nutrition.get('fat_grams', 'N/A')}g")

                if 'ingredients' in recipe and len(recipe['ingredients']) > 0:
                    print_info(f"\nIngredients: {len(recipe['ingredients'])} items")

                if 'instructions' in recipe and len(recipe['instructions']) > 0:
                    print_info(f"Instructions: {len(recipe['instructions'])} steps")

                return True
            else:
                print_error(f"Failed to generate recipe: {response.status_code}")
                print_json(response.json())
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False


async def test_websocket_streaming(token):
    """Test WebSocket streaming meal plan generation"""
    print_header("5. WebSocket Streaming Meal Plan Generation")

    print_info("Note: WebSocket test requires websockets library")
    print_info("Install with: pip install websockets")

    try:
        import websockets

        print_info("Connecting to WebSocket...")

        ws_url = f"{WS_URL}/api/v1/ws/meal-plan-generation?token={token}&days=3&dietary_restrictions=vegetarian&target_calories=2000"

        async with websockets.connect(ws_url) as websocket:
            print_success("Connected to WebSocket!")

            # Receive messages
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(message)

                    msg_type = data.get('type')

                    if msg_type == 'connected':
                        print_success(f"WebSocket: {data.get('message')}")

                    elif msg_type == 'progress':
                        stage = data.get('stage', 'unknown')
                        progress = data.get('progress', 0)
                        msg = data.get('message', '')
                        print_info(f"[{progress:3d}%] {stage}: {msg}")

                    elif msg_type == 'complete':
                        print_success(f"WebSocket: {data.get('message')}")
                        print_success("Meal plan generation completed!")

                        if 'meal_plan' in data:
                            plan = data['meal_plan']
                            print_info(f"Generated Plan: {plan.get('name', 'N/A')}")

                        # Send ping to keep connection alive
                        await websocket.send(json.dumps({"type": "ping"}))

                        # Wait for pong and then close
                        pong = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        pong_data = json.loads(pong)
                        if pong_data.get('type') == 'pong':
                            print_info("Ping/pong successful")

                        break

                    elif msg_type == 'error':
                        print_error(f"WebSocket Error: {data.get('message')}")
                        break

                except asyncio.TimeoutError:
                    print_error("WebSocket timeout")
                    break
                except Exception as e:
                    print_error(f"WebSocket error: {str(e)}")
                    break

        return True

    except ImportError:
        print_error("websockets library not installed")
        print_info("Install with: pip install websockets")
        return False
    except Exception as e:
        print_error(f"WebSocket test failed: {str(e)}")
        return False


async def test_proactive_suggestions(token):
    """Test proactive nutrition suggestions"""
    print_header("6. Proactive Nutrition Suggestions")

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        print_info("Getting proactive suggestions...")

        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/coaching/suggestions",
                headers=headers,
                json={}
            )

            if response.status_code == 200:
                print_success("Proactive suggestions retrieved successfully!")
                suggestions = response.json()

                print_info(f"\nUrgency: {suggestions.get('urgency', 'N/A')}")
                print_info(f"Primary Suggestion: {suggestions.get('primary_suggestion', 'N/A')}")

                if 'reasons' in suggestions and len(suggestions['reasons']) > 0:
                    print_info("\nReasons:")
                    for reason in suggestions['reasons']:
                        print(f"  • {reason}")

                if 'action_steps' in suggestions and len(suggestions['action_steps']) > 0:
                    print_info("\nAction Steps:")
                    for step in suggestions['action_steps']:
                        print(f"  • {step}")

                return True
            else:
                print_error(f"Failed to get suggestions: {response.status_code}")
                print_json(response.json())
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False


async def main():
    """Run all tests"""
    print_header("🧪 Intelligent Meal Planning & Coaching - End-to-End Tests")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Test User: {TEST_EMAIL}")
    print_info(f"Timestamp: {datetime.now().isoformat()}")

    # Track results
    results = {
        "authentication": False,
        "intelligent_meal_plan": False,
        "coaching_advice": False,
        "custom_recipe": False,
        "websocket_streaming": False,
        "proactive_suggestions": False
    }

    # 1. Authenticate
    token = await authenticate()
    if not token:
        print_error("\nAuthentication failed. Cannot continue with tests.")
        return
    results["authentication"] = True

    # 2. Test intelligent meal plan generation
    results["intelligent_meal_plan"] = await test_intelligent_meal_plan(token)

    # 3. Test coaching advice
    results["coaching_advice"] = await test_coaching_advice(token)

    # 4. Test custom recipe generation
    results["custom_recipe"] = await test_custom_recipe_generation(token)

    # 5. Test WebSocket streaming
    results["websocket_streaming"] = await test_websocket_streaming(token)

    # 6. Test proactive suggestions
    results["proactive_suggestions"] = await test_proactive_suggestions(token)

    # Summary
    print_header("📊 Test Summary")

    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        color = Colors.OKGREEN if result else Colors.FAIL
        print(f"{color}{status:6s}{Colors.ENDC} - {test_name.replace('_', ' ').title()}")

    print(f"\n{Colors.BOLD}Results: {passed_tests}/{total_tests} tests passed{Colors.ENDC}")

    if passed_tests == total_tests:
        print_success("\n✨ All tests passed! The implementation is working correctly.")
    else:
        print_error(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Review the output above.")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Intelligent Meal Planning & Coaching - End-to-End Test Suite")
    print("=" * 80 + "\n")

    print("Prerequisites:")
    print("1. Backend server running on http://localhost:8000")
    print("2. Database configured and migrations applied")
    print("3. OpenAI API key configured in environment")
    print("4. Redis server running (for caching)")
    print("\nStarting tests...\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
