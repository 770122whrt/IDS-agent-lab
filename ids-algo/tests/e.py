import sys
import json
import asyncio
from pathlib import Path

# -----------------------------------------------------------------------------
# 1. 环境配置
# -----------------------------------------------------------------------------
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from c_knowledge_base_mapping.data_structures import MappedFacet
from d_constrains.constraint_extractor import (
    ValueRestriction,
    RestrictionType,
    BoundsRestriction,
    EnumerationRestriction,
    PatternRestriction,
    LengthRestriction,
)

from e_ids_builder.entry import runIDSBuilder

# 临时文件目录
TEMP_DIR = project_root / "temp"

# -----------------------------------------------------------------------------
# 2. 辅助工具：JSON -> Constraint 对象
# -----------------------------------------------------------------------------
def reconstruct_constraint(d_dict: dict) -> ValueRestriction:
    if not isinstance(d_dict, dict):
        return None

    type_str = d_dict.get("restriction_type", "").upper()
    try:
        r_type = RestrictionType[type_str]
    except KeyError:
        # 尝试容错，如果还是找不到则忽略
        return None

    r_data = d_dict.get("restriction", {})
    restriction_obj = None

    if r_type == RestrictionType.BOUNDS:
        restriction_obj = BoundsRestriction(
            min_value=r_data.get("min_value"),
            max_value=r_data.get("max_value"),
            min_inclusive=r_data.get("min_inclusive", True),
            max_inclusive=r_data.get("max_inclusive", True),
            unit=r_data.get("unit")
        )
    elif r_type == RestrictionType.ENUMERATION:
        restriction_obj = EnumerationRestriction(
            values=r_data.get("values", [])
        )
    elif r_type == RestrictionType.PATTERN:
        restriction_obj = PatternRestriction(
            pattern=r_data.get("pattern", ""),
            description=r_data.get("description")
        )
    elif r_type == RestrictionType.LENGTH:
        restriction_obj = LengthRestriction(
            min_length=r_data.get("min_length"),
            max_length=r_data.get("max_length")
        )

    return ValueRestriction(
        restriction_type=r_type,
        restriction=restriction_obj,
        # 保证失败了也有值
        confidence=d_dict.get("confidence", 0.0),
        original_text=d_dict.get("original_text", "")
    )

# -----------------------------------------------------------------------------
# 3. 新增：加载 input.json 中的原始文本
# -----------------------------------------------------------------------------
def load_original_texts() -> dict:
    """
    读取 temp/input.json，返回 {id: text} 的字典
    """
    input_file = TEMP_DIR / "input.json"
    text_map = {}

    # 如果文件不存在，返回空字典
    if not input_file.exists():
        print(f"Warning: {input_file} not found. Original text will be empty.")
        return text_map
    # 读取文件内容
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
            # 确保是列表
            if isinstance(input_data, dict): input_data = [input_data]
            
            for item in input_data:
                # 转换为字符串ID以匹配
                entry_id = str(item.get("id", "")).strip()
                text = item.get("text", "")
                if entry_id:
                    text_map[entry_id] = text
        print(f"Loaded original texts for IDs: {list(text_map.keys())}")
    except Exception as e:
        print(f"Error loading input.json: {e}")
    
    return text_map

# -----------------------------------------------------------------------------
# 4. 核心处理逻辑
# -----------------------------------------------------------------------------
async def process_entry(entry_id: str, original_text_map: dict):
    print(f"\n▶️ Processing Entry ID: {entry_id}")
    
    file_c = TEMP_DIR / f"c{entry_id}.json"
    file_d = TEMP_DIR / f"d{entry_id}.json"
    file_e = TEMP_DIR / f"e{entry_id}.json"

    # --- Step 0: 获取原始文本 ---
    # 从预加载的字典中获取，如果找不到则为空字符串
    original_text_content = original_text_map.get(str(entry_id), "")

    # --- Step A: 加载 Facet 骨架 (C文件) dict-->MappedFacet ---
    if not file_c.exists():
        print(f"File not found: {file_c}")
        return

    facets = []
    with open(file_c, "r", encoding="utf-8") as f:
        raw_c = json.load(f)
        if isinstance(raw_c, dict): raw_c = [raw_c]
        facets = [MappedFacet.from_dict(item) for item in raw_c]
        print(f"   Loaded {len(facets)} facets from C.")

    # --- Step B: 加载 Constraints 数据 (D文件) constraints-->ValueRestriction ---
    constraints = []
    if file_d.exists():
        with open(file_d, "r", encoding="utf-8") as f:
            raw_d = json.load(f)
            if isinstance(raw_d, dict): raw_d = [raw_d]
            for item in raw_d:
                obj = reconstruct_constraint(item)
                if obj:
                    constraints.append(obj)
        print(f"    Loaded {len(constraints)} constraints from D.")
    else:
        print("     No constraints file (D) found.")

    # --- Step C: 缝合数据 (Merge) ---
    merged_count = 0
    for facet in facets:
        if facet.constraints is None:
            facet.constraints = []
        
        facet_text = (facet.original_text or "").strip().lower()

        for constr in constraints:
            constr_text = (constr.original_text or "").strip().lower()
            # 包含匹配逻辑
            if constr_text and facet_text and (constr_text in facet_text or facet_text in constr_text):
                facet.constraints.append(constr)
                merged_count += 1

    print(f"    Merged {merged_count} constraints into facets.")

    # --- Step D: 构建 IDS (Builder) ---
    try:
        # 调用 e_ids_builder/entry.py 中的 runIDSBuilder
        # 注意：这里需要传入 await，并且传入 original_text
        result_data = await runIDSBuilder(
            facets, 
            text=original_text_content,
            include_metadata= False,
        )

        # 这里的 result_data 应该是一个字典: {'specifications': [...], ...}
        specifications = result_data.get("specifications", [])

        print(f"   ✅ Generated {len(specifications)} IDS specifications.")
        
        # --- Step E: 保存结果 ---
        with open(file_e, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        print(f"   💾 Saved to {file_e}")

    except Exception as e:
        print(f"   ❌ Error building IDS: {e}")
        import traceback
        traceback.print_exc()

# -----------------------------------------------------------------------------
# 5. 主程序入口
# -----------------------------------------------------------------------------
async def main():
    # 加载所有的原始文本
    text_map = load_original_texts()

    test_ids = ["1","2"] 
    for eid in test_ids:
        await process_entry(eid, text_map)

if __name__ == "__main__":
    asyncio.run(main())