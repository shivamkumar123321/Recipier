#!/usr/bin/env python3
"""
End-to-End Test Script for Voice Cooking Assistant

Tests the voice assistant with mock audio input/output:
1. Timer management
2. Unit conversions
3. Ingredient substitutions
4. Recipe guidance
5. WebSocket real-time interaction

This script demonstrates the complete functionality with simulated audio.
"""

import asyncio
import base64
import json
import wave
from datetime import datetime
from typing import Optional

import httpx


# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"


class Colors:
    """ANSI color codes"""
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


def create_mock_audio() -> bytes:
    """
    Create a minimal valid WAV file for testing.

    Returns:
        WAV file bytes
    """
    import io
    import struct

    # Create a 1-second silent WAV file
    sample_rate = 16000
    duration = 1  # seconds
    num_samples = sample_rate * duration

    # Create WAV file in memory
    wav_buffer = io.BytesIO()

    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        # Write silent audio (zeros)
        for _ in range(num_samples):
            wav_file.writeframes(struct.pack('<h', 0))

    return wav_buffer.getvalue()


async def authenticate() -> Optional[str]:
    """Authenticate and get JWT token."""
    print_header("1. Authentication")

    async with httpx.AsyncClient() as client:
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
                return None
        else:
            print_error(f"Authentication failed: {response.status_code}")
            return None


async def test_service_features():
    """Test voice assistant service features directly."""
    print_header("2. Voice Assistant Service Features")

    from app.services.voice_assistant_service import VoiceAssistantService, ConversationContext

    service = VoiceAssistantService()
    results = {}

    # Test timer parsing
    print_info("Testing timer command parsing...")
    timer_commands = [
        "set a timer for 10 minutes",
        "timer for 5 seconds",
        "set timer for 1 minute",
    ]

    for cmd in timer_commands:
        result = service.parse_timer_command(cmd)
        if result:
            duration, label = result
            print_success(f"Parsed '{cmd}' -> {duration}s ({label})")
            results["timer_parsing"] = True
        else:
            print_error(f"Failed to parse '{cmd}'")
            results["timer_parsing"] = False

    # Test unit conversion
    print_info("\nTesting unit conversions...")
    conversions = [
        ("how many cups in 500 ml", "cups", "ml"),
        ("convert 2 cups to ml", "ml", "cups"),
        ("how many grams in 1 pound", "grams", "pound"),
    ]

    for query, _, _ in conversions:
        result = service.parse_conversion_query(query)
        if result:
            print_success(f"'{query}' -> {result}")
            results["unit_conversion"] = True
        else:
            print_error(f"Failed: '{query}'")
            results["unit_conversion"] = False

    # Test substitutions
    print_info("\nTesting ingredient substitutions...")
    ingredients = ["butter", "milk", "egg"]

    for ing in ingredients:
        subs = service.get_substitution_suggestions(ing)
        if subs:
            print_success(f"Substitutions for {ing}:")
            for sub in subs[:2]:
                print(f"  • {sub}")
            results["substitutions"] = True
        else:
            print_error(f"No substitutions found for {ing}")
            results["substitutions"] = False

    # Test context management
    print_info("\nTesting context management...")
    context = ConversationContext()

    # Add messages
    context.add_message("user", "How do I make cookies?")
    context.add_message("assistant", "Here's how to make cookies...")

    # Set recipe
    context.set_recipe({
        "name": "Chocolate Chip Cookies",
        "ingredients": ["flour", "sugar", "butter", "eggs", "chocolate chips"],
        "current_step": "Mix dry ingredients"
    })

    # Add timer
    timer = context.add_timer(600, "Cookie timer")

    # Get summary
    summary = context.get_context_summary()
    if "Chocolate Chip Cookies" in summary and "Cookie timer" in summary:
        print_success("Context management working correctly")
        print_info(f"Context summary:\n{summary}")
        results["context_management"] = True
    else:
        print_error("Context management failed")
        results["context_management"] = False

    return results


async def test_websocket_interaction(token: str):
    """Test WebSocket cooking assistant with mock audio."""
    print_header("3. WebSocket Cooking Assistant")

    print_info("Note: WebSocket test requires websockets library")
    print_info("Install with: pip install websockets")

    try:
        import websockets

        print_info("Connecting to WebSocket...")

        ws_url = f"{WS_URL}/api/v1/ws/cooking-assistant?token={token}"

        async with websockets.connect(ws_url) as websocket:
            print_success("Connected to WebSocket!")

            # Receive welcome message
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            if welcome_data.get("type") == "connected":
                print_success(f"Server: {welcome_data.get('message')}")

            # Test 1: Send text message (simpler than audio)
            print_info("\nTest 1: Sending text message (unit conversion)...")
            await websocket.send(json.dumps({
                "type": "text",
                "message": "how many cups in 500 ml?"
            }))

            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            response_data = json.loads(response)

            if response_data.get("type") == "response":
                print_success(f"Response: {response_data.get('text')}")
                print_info(f"Audio received: {len(response_data.get('audio', ''))} bytes (base64)")

            # Test 2: Set a timer
            print_info("\nTest 2: Setting a timer...")
            await websocket.send(json.dumps({
                "type": "text",
                "message": "set a timer for 5 seconds"
            }))

            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            response_data = json.loads(response)

            if response_data.get("type") == "response":
                print_success(f"Response: {response_data.get('text')}")
                metadata = response_data.get("metadata", {})
                if metadata.get("timer_set"):
                    timer_info = metadata.get("timer", {})
                    print_success(f"Timer set: {timer_info.get('label')}")

            # Test 3: Get active timers
            print_info("\nTest 3: Getting active timers...")
            await websocket.send(json.dumps({
                "type": "get_timers"
            }))

            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            response_data = json.loads(response)

            if response_data.get("type") == "active_timers":
                timers = response_data.get("timers", [])
                print_success(f"Active timers: {len(timers)}")
                for timer in timers:
                    print_info(f"  • {timer.get('label')}: {timer.get('time_remaining_seconds')}s remaining")

            # Test 4: Wait for timer to finish
            print_info("\nTest 4: Waiting for timer to finish...")
            print_info("(This will take 5 seconds...)")

            timer_finished = False
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < 10:  # Max 10 seconds
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=6.0)
                    data = json.loads(message)

                    if data.get("type") == "timer_finished":
                        timer_info = data.get("timer", {})
                        print_success(f"Timer finished: {timer_info.get('label')}")
                        timer_finished = True
                        break
                except asyncio.TimeoutError:
                    print_info("Still waiting for timer...")

            if not timer_finished:
                print_error("Timer did not finish in expected time")

            # Test 5: Set recipe context
            print_info("\nTest 5: Setting recipe context...")
            await websocket.send(json.dumps({
                "type": "set_recipe",
                "recipe": {
                    "name": "Chocolate Chip Cookies",
                    "ingredients": ["flour", "sugar", "butter", "eggs", "chocolate chips"],
                    "instructions": [
                        "Preheat oven to 375°F",
                        "Mix dry ingredients",
                        "Cream butter and sugar",
                        "Add eggs",
                        "Combine mixtures",
                        "Bake for 10 minutes"
                    ]
                }
            }))

            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            response_data = json.loads(response)

            if response_data.get("type") == "recipe_set":
                print_success(f"Recipe set: {response_data.get('recipe_name')}")

            # Test 6: Ask about the recipe
            print_info("\nTest 6: Asking about recipe...")
            await websocket.send(json.dumps({
                "type": "text",
                "message": "What's the first step?"
            }))

            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            response_data = json.loads(response)

            if response_data.get("type") == "response":
                print_success(f"Response: {response_data.get('text')[:100]}...")

            # Test 7: Mock audio input
            print_info("\nTest 7: Sending mock audio input...")
            mock_audio = create_mock_audio()
            audio_b64 = base64.b64encode(mock_audio).decode('utf-8')

            print_info(f"Mock audio created: {len(mock_audio)} bytes")
            print_info("Note: This will likely fail transcription (mock audio is silent)")
            print_info("      But it tests the audio pipeline")

            await websocket.send(json.dumps({
                "type": "audio",
                "data": audio_b64
            }))

            # Expect transcription + response
            try:
                for _ in range(2):  # Transcription and response
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    response_data = json.loads(response)

                    if response_data.get("type") == "transcription":
                        print_info(f"Transcription: {response_data.get('text', '(empty)')}")
                    elif response_data.get("type") == "response":
                        print_info(f"Response: {response_data.get('text', '')[:50]}...")
                    elif response_data.get("type") == "error":
                        print_error(f"Error: {response_data.get('message')}")
            except asyncio.TimeoutError:
                print_error("Timeout waiting for audio response")

            # Clean up
            await websocket.send(json.dumps({"type": "cancel_timers"}))

            print_success("\n✓ All WebSocket tests completed!")
            return True

    except ImportError:
        print_error("websockets library not installed")
        print_info("Install with: pip install websockets")
        return False
    except Exception as e:
        print_error(f"WebSocket test failed: {str(e)}")
        return False


async def main():
    """Run all tests."""
    print_header("🎙️ Voice Cooking Assistant - End-to-End Tests")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Test User: {TEST_EMAIL}")
    print_info(f"Timestamp: {datetime.now().isoformat()}")

    results = {
        "authentication": False,
        "service_features": False,
        "websocket": False,
    }

    # 1. Authenticate
    token = await authenticate()
    if not token:
        print_error("\nAuthentication failed. Cannot continue with tests.")
        return
    results["authentication"] = True

    # 2. Test service features
    service_results = await test_service_features()
    results["service_features"] = all(service_results.values())

    # 3. Test WebSocket
    results["websocket"] = await test_websocket_interaction(token)

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
        print_success("\n✨ All tests passed! The voice assistant is working correctly.")
    else:
        print_error(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Review the output above.")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Voice Cooking Assistant - End-to-End Test Suite")
    print("=" * 80 + "\n")

    print("Prerequisites:")
    print("1. Backend server running on http://localhost:8000")
    print("2. Database configured and migrations applied")
    print("3. OpenAI API key configured in environment")
    print("4. websockets library installed: pip install websockets")
    print("\nStarting tests...\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
