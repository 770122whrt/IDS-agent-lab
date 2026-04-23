"""
更新entity_db.json中的桥梁实体定义
使用从官方IFC4X3文档获取的完整定义和predefined types
"""
import json
from pathlib import Path

# 更新的实体定义
UPDATED_ENTITIES = {
    "IfcBridge": {
        "definition": "A bridge is a civil engineering works that affords passage to pedestrians, animals, vehicles, and services above obstacles or between two points at a height above ground. IfcBridge defines the occurrence of a bridge.",
        "predefined_types": ["ARCHED", "CABLE_STAYED", "CANTILEVER", "CULVERT", "FRAMEWORK", "GIRDER", "SUSPENSION", "TRUSS", "USERDEFINED", "NOTDEFINED"]
    },
    "IfcBridgePart": {
        "definition": "A bridge part is a major functional part of a bridge which can be used to provide a specific kind of bridge construction information. IfcBridgePart is used to represent the major parts of a bridge, such as abutment, deck, foundation, pier, pylon, substructure, and superstructure.",
        "predefined_types": ["ABUTMENT", "DECK", "DECK_SEGMENT", "FOUNDATION", "PIER", "PIER_SEGMENT", "PYLON", "SUBSTRUCTURE", "SUPERSTRUCTURE", "SURFACESTRUCTURE", "USERDEFINED", "NOTDEFINED"]
    },
    "IfcAlignment": {
        "definition": "An alignment is a positioning and layout representation of a linear infrastructure facility, such as a road, railway, or bridge. The alignment is defined by a horizontal alignment, a vertical alignment, and optionally a cant alignment.",
        "predefined_types": ["USERDEFINED", "NOTDEFINED"]
    }
}

def update_entity_definitions():
    """更新entity_db.json中的实体定义"""

    db_path = Path(__file__).parent / "c_knowledge_base_mapping" / "resources" / "entity_db.json"

    print(f"Loading database from: {db_path}")
    with open(db_path, 'r', encoding='utf-8') as f:
        db_data = json.load(f)

    updated_count = 0
    for item in db_data['items']:
        if item['name'] in UPDATED_ENTITIES:
            old_def = item['definition']
            old_types = item.get('predefined_types', [])

            # 更新定义和predefined types
            item['definition'] = UPDATED_ENTITIES[item['name']]['definition']
            item['predefined_types'] = UPDATED_ENTITIES[item['name']]['predefined_types']
            item['ifc_version'] = 'IFC4X3'  # 确保版本正确

            print(f"\n[UPDATED] {item['name']}")
            print(f"  Old definition: {old_def[:80]}...")
            print(f"  New definition: {item['definition'][:80]}...")
            print(f"  Old predefined_types: {old_types}")
            print(f"  New predefined_types: {item['predefined_types']}")

            updated_count += 1

    # 更新元数据
    db_data['metadata']['updated_at'] = "2026-04-21T00:30:00.000000"

    # 创建备份
    backup_path = db_path.with_suffix('.json.backup2')
    print(f"\n[BACKUP] Creating backup at: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

    # 保存更新后的数据库
    print(f"[SAVE] Saving updated database to: {db_path}")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] Updated {updated_count} entities")
    print("=" * 80)
    print("IMPORTANT: The vector database needs to be reloaded for changes to take effect.")
    print("Restart the application or clear the vector cache.")

if __name__ == "__main__":
    update_entity_definitions()
