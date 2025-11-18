"""
Audio test fixtures for voice command testing.

Provides mock audio data and sample transcriptions for testing voice features.
"""

import base64


# Mock audio data (minimal WAV file header + silence)
# This is a valid minimal WAV file that can be used for testing
MOCK_WAV_AUDIO = base64.b64encode(
    b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
    b"\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
).decode()

MOCK_MP3_AUDIO = base64.b64encode(
    b"\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
).decode()


# Sample transcriptions for different command types
SAMPLE_ADD_ITEMS_TRANSCRIPTIONS = [
    "Add 3 apples and 2 pounds of chicken",
    "I bought milk, eggs, and a bag of rice",
    "Got some broccoli and frozen pizza",
    "Add five bananas, three tomatoes, and one pound of ground beef",
    "I have two gallons of milk in the fridge",
]

SAMPLE_RECIPE_QUERY_TRANSCRIPTIONS = [
    "What can I cook with chicken and rice?",
    "I have tomatoes, onions, and garlic. What can I make?",
    "Recipe ideas with leftover pasta",
    "Show me recipes using beef and potatoes",
    "What dishes can I make with salmon?",
]

SAMPLE_EXPIRATION_CHECK_TRANSCRIPTIONS = [
    "When does my milk expire?",
    "What's expiring within 3 days?",
    "Show me items expiring soon",
    "Is my chicken still good?",
    "How many days until my eggs expire?",
]

SAMPLE_SEARCH_INVENTORY_TRANSCRIPTIONS = [
    "What do I have?",
    "Show me all vegetables",
    "List all fruits in my inventory",
    "Do I have any meat?",
    "What's in my fridge?",
]

# Expected parsed items for add commands
EXPECTED_PARSED_ITEMS = {
    "Add 3 apples and 2 pounds of chicken": [
        {
            "name": "Apple",
            "quantity": 3,
            "unit": "items",
            "storage_location": "pantry",
            "category": "fruit",
        },
        {
            "name": "Chicken",
            "quantity": 2,
            "unit": "lbs",
            "storage_location": "fridge",
            "category": "protein",
        },
    ],
    "I bought milk, eggs, and a bag of rice": [
        {
            "name": "Milk",
            "quantity": 1,
            "unit": "gallon",
            "storage_location": "fridge",
            "category": "dairy",
        },
        {
            "name": "Eggs",
            "quantity": 12,
            "unit": "items",
            "storage_location": "fridge",
            "category": "protein",
        },
        {
            "name": "Rice",
            "quantity": 1,
            "unit": "bag",
            "storage_location": "pantry",
            "category": "grain",
        },
    ],
}

# Expected recipe ingredients
EXPECTED_RECIPE_INGREDIENTS = {
    "What can I cook with chicken and rice?": ["chicken", "rice"],
    "I have tomatoes, onions, and garlic. What can I make?": [
        "tomatoes",
        "onions",
        "garlic",
    ],
    "Recipe ideas with leftover pasta": ["pasta"],
}

# Expected expiration query params
EXPECTED_EXPIRATION_QUERIES = {
    "When does my milk expire?": {"item": "milk", "days": None},
    "What's expiring within 3 days?": {"item": None, "days": 3},
    "Show me items expiring soon": {"item": None, "days": 7},
    "Is my chicken still good?": {"item": "chicken", "days": None},
}


def get_mock_audio_bytes(format: str = "wav") -> bytes:
    """
    Get mock audio bytes for testing.

    Args:
        format: Audio format (wav or mp3)

    Returns:
        Raw audio bytes
    """
    if format == "mp3":
        return base64.b64decode(MOCK_MP3_AUDIO)
    return base64.b64decode(MOCK_WAV_AUDIO)


def get_mock_audio_base64(format: str = "wav") -> str:
    """
    Get base64 encoded mock audio for testing.

    Args:
        format: Audio format (wav or mp3)

    Returns:
        Base64 encoded audio string
    """
    if format == "mp3":
        return MOCK_MP3_AUDIO
    return MOCK_WAV_AUDIO
