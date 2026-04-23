"""
Test script for Anthropic API endpoint connectivity
"""
import os
from anthropic import Anthropic

# Configuration
API_KEY = "sk-d2c34707eb1a890aa86061cd84ccd8574ee13da991963d01459a3e4095744c17"
BASE_URL = "https://cc-vibe.com"
MODEL = "claude-sonnet-4-5-20250929"

def test_anthropic_endpoint():
    """Test basic connectivity to Anthropic endpoint"""
    print(f"Testing Anthropic endpoint: {BASE_URL}")
    print(f"Model: {MODEL}")
    print("-" * 50)

    try:
        # Initialize client
        client = Anthropic(api_key=API_KEY, base_url=BASE_URL)
        print("[OK] Client initialized successfully")

        # Send a simple test message
        print("\nSending test message...")
        response = client.messages.create(
            model=MODEL,
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Please respond with 'Connection successful' if you receive this message."
                }
            ]
        )

        print("[OK] Response received!")
        print(f"\nResponse content:")
        print(response.content[0].text)
        print(f"\nModel used: {response.model}")
        print(f"Tokens used: {response.usage.input_tokens} input, {response.usage.output_tokens} output")

        return True

    except Exception as e:
        print(f"[ERROR] Error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_anthropic_endpoint()
    print("\n" + "=" * 50)
    if success:
        print("[PASS] Test PASSED - Endpoint is working correctly")
    else:
        print("[FAIL] Test FAILED - Please check the error messages above")
