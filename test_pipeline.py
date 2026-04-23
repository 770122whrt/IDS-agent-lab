"""
Test script for IDS pipeline with new Anthropic endpoint
"""
import asyncio
import sys
import json
from pathlib import Path

# Add ids-algo to path
sys.path.insert(0, str(Path(__file__).parent / "ids-algo"))

from pipeline import run_ids_pipeline

# Test requirement text
TEST_REQUIREMENT = """
All IfcWall elements must have a FireRating property with a value greater than 120 minutes.
The Height property of IfcDoor should be between 2000mm and 2400mm.
"""

async def main():
    print("=" * 60)
    print("IDS Pipeline Test with Anthropic Endpoint")
    print("=" * 60)
    print(f"\nTest Requirement:\n{TEST_REQUIREMENT}")
    print("\n" + "-" * 60)

    try:
        # Run the pipeline
        result = await run_ids_pipeline(TEST_REQUIREMENT)

        print("\n" + "=" * 60)
        print("Pipeline Result:")
        print("=" * 60)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        print("\n[PASS] Pipeline test completed successfully!")
        return True

    except Exception as e:
        print(f"\n[FAIL] Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
