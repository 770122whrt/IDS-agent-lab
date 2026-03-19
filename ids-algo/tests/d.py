import asyncio
import json
from .utils import TEMP_DIR, createJsonTempFile, load_input_entries
from d_constrains import MappedFacet, runConstraintExtraction


async def process_entry(entry_id: str) -> None:
    print(f"▶️ Processing entry {entry_id}")
    target = TEMP_DIR / f"c{entry_id}.json"

    try:
        with target.open("r", encoding="utf-8") as handle:
            raw_data = json.load(handle)
    except Exception as e:
        print(f"Failed to load file {target}: {e}")
        return

    # 支持单个对象或对象列表
    if isinstance(raw_data, list):
        facet_list = raw_data
    elif isinstance(raw_data, dict):
        facet_list = [raw_data]
    else:
        print(f"Unexpected data type in {target}")
        return

    all_constraints = []

    for facet_data in facet_list:
        try:
            mapped = MappedFacet.from_dict(facet_data)
            constraints = runConstraintExtraction([mapped])  #正确传入列表
            if isinstance(constraints, list):
                all_constraints.extend(constraints)
            else:
                all_constraints.append(constraints)
        except Exception as e:
            print(f"Error processing facet: {e}")

    print(f" Extracted {len(all_constraints)} constraint(s) from entry {entry_id}")
    #手动转换为 JSON 友好的 dict 结构

    def safe_to_dict(obj, seen=None):
        if seen is None:
            seen = set()

        obj_id = id(obj)
        if obj_id in seen:
            return f"<circular {type(obj).__name__}>"

        seen.add(obj_id)

        # 基础类型
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj

        # Enum → 转成 value
        import enum
        if isinstance(obj, enum.Enum):
            return obj.value

        # list
        if isinstance(obj, list):
            return [safe_to_dict(i, seen) for i in obj]

        # dict
        if isinstance(obj, dict):
            return {k: safe_to_dict(v, seen) for k, v in obj.items()}

        # dataclass 或普通对象
        if hasattr(obj, "__dict__"):
            return {k: safe_to_dict(v, seen) for k, v in vars(obj).items()}

        return str(obj)

    json_friendly_constraints = [safe_to_dict(c) for c in all_constraints]
    createJsonTempFile(json_friendly_constraints, f"d{entry_id}")  # 保存为临时 JSON 文件


async def main() -> None:
    try:
        entries = load_input_entries("input.json")  # 默认加载 temp/input.json
        for entry in entries:
            entry_id = str(entry.get("id", "")).strip()
            if entry_id:
                await process_entry(entry_id)
            else:
                print("⚠️ Skipping entry with no ID")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
