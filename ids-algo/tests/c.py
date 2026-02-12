import asyncio
import json
from c_knowledge_base_mapping import runKnowledgeBaseMapping
from c_knowledge_base_mapping import MappedFacet
from b_facet_classifier import FacetClassification
from .utils import TEMP_DIR
from .utils import createJsonTempFile
from .utils import load_input_entries


def print_knowledge_mapping_result(mapped_facets: list[MappedFacet]):
    print("\n=== 🧠 Knowledge Mapping Result ===")
    for facet in mapped_facets:
        print(f"\n📌 [{facet.facet_type.upper()}] '{facet.original_text}'")
        print(f"   🔁 Mapped To: {facet.mapped_name}")
        print(f"   📊 Confidence: {facet.confidence}")
        if facet.property_set:
            print(f"   📦 Property Set: {facet.property_set}")
        if facet.entity_name:
            print(f"   🧱 Entity Context: {facet.entity_name}")
        if facet.additional_data:
            print(f"   🧩 Additional: {facet.additional_data}")


async def process_entry(entry_id: str) -> None:
    print(f"▶️ Processing entry {entry_id}")
    target = TEMP_DIR / f"b{entry_id}.json"
    with target.open("r", encoding="utf-8") as handle:
        facet_payload = json.load(handle)
        facet_result = FacetClassification.from_dict(facet_payload)

        map_result:list[MappedFacet] = await runKnowledgeBaseMapping(facet_result)
        createJsonTempFile(map_result, f"c{entry_id}")
        #print_knowledge_mapping_result(map_result)

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
