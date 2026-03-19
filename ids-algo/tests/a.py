import asyncio
from a_structured_parser import format_result_as_markdown
from a_structured_parser import runStructuredParser
from .utils import createJsonTempFile
from .utils import createMdInOutput
from .utils import load_input_entries

async def main() -> None:
    try:
        entries = load_input_entries("input.json")
        for entry in entries:
            text = str(entry.get("text", "")).strip()
            entry_id = str(entry.get("id", "")).strip()
            print(f"▶️ Processing entry {entry_id}")
            result = await runStructuredParser(text)
            createJsonTempFile(result, f"a{entry_id}")
            # createMdInOutput(format_result_as_markdown(result, text), entry_id)
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
