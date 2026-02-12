import asyncio
import json
from b_facet_classifier import FacetClassification
from b_facet_classifier import runFacetClassifier
from a_structured_parser import StructuredParseResult
from .utils import TEMP_DIR
from .utils import createJsonTempFile
from .utils import load_input_entries

async def process_entry(entry_id: str) -> None:
    print(f"▶️ Processing entry {entry_id}")
    target = TEMP_DIR / f"a{entry_id}.json"
    with target.open("r", encoding="utf-8") as handle:
        parser_payload = json.load(handle)
        parser_result = StructuredParseResult.from_dict(parser_payload)
        facet_result: FacetClassification = await runFacetClassifier(parser_result)
        createJsonTempFile(facet_result, f"b{entry_id}")

async def main() -> None:
    try:
        entries = load_input_entries("input.json")
        for entry in entries:
            entry_id = str(entry.get("id", "")).strip()
            await process_entry(entry_id)
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
