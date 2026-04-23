"""
扩展知识库 - 添加IFC4X3桥梁领域实体

基于官方文档添加IfcBridge、IfcBridgePart、IfcAlignment等实体
"""

import json
import logging
from pathlib import Path
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# IFC4X3桥梁实体定义（基于官方文档）
BRIDGE_ENTITIES = [
    {
        "name": "IfcBridge",
        "definition": "A bridge is a civil engineering works that affords passage to pedestrians, animals, vehicles, and services above obstacles or between two points at a height above ground. IfcBridge defines the occurrence of a bridge.",
        "ifc_version": "IFC4X3",
        "item_type": "entity",
        "predefined_types": [
            "ARCHED", "CABLE_STAYED", "CANTILEVER", "CULVERT",
            "FRAMEWORK", "GIRDER", "SUSPENSION", "TRUSS", "USERDEFINED", "NOTDEFINED"
        ]
    },
    {
        "name": "IfcBridgePart",
        "definition": "A bridge part is a major functional part of a bridge which can be used to provide a specific kind of bridge construction information. IfcBridgePart is used to represent the major parts of a bridge, such as abutment, deck, foundation, pier, pylon, substructure, and superstructure.",
        "ifc_version": "IFC4X3",
        "item_type": "entity",
        "predefined_types": [
            "ABUTMENT", "DECK", "DECK_SEGMENT", "FOUNDATION",
            "PIER", "PIER_SEGMENT", "PYLON", "SUBSTRUCTURE",
            "SUPERSTRUCTURE", "SURFACESTRUCTURE", "USERDEFINED", "NOTDEFINED"
        ]
    },
    {
        "name": "IfcAlignment",
        "definition": "An alignment is a positioning and layout representation of a linear infrastructure facility, such as a road, railway, or bridge. The alignment is defined by a horizontal alignment, a vertical alignment, and optionally a cant alignment.",
        "ifc_version": "IFC4X3",
        "item_type": "entity",
        "predefined_types": ["USERDEFINED", "NOTDEFINED"]
    },
    {
        "name": "IfcCourse",
        "definition": "A course is a layer of material in a pavement or other layered construction. It is used to represent the structural layers of a road, railway, or other linear infrastructure.",
        "ifc_version": "IFC4X3",
        "item_type": "entity",
        "predefined_types": [
            "ARMOUR", "BALLASTBED", "CORE", "FILTER",
            "PAVEMENT", "PROTECTION", "USERDEFINED", "NOTDEFINED"
        ]
    },
    {
        "name": "IfcEarthworksCut",
        "definition": "An earthworks cut is a volume of material that is removed from the ground to create a depression or excavation for construction purposes.",
        "ifc_version": "IFC4X3",
        "item_type": "entity",
        "predefined_types": [
            "CUTANDCOVER", "DIAPHRAGMWALL", "EXCAVATION",
            "OVEREXCAVATION", "PAVEMENTMILLING", "TOPSOILREMOVAL",
            "TRENCH", "USERDEFINED", "NOTDEFINED"
        ]
    },
    {
        "name": "IfcEarthworksFill",
        "definition": "An earthworks fill is a volume of material that is placed to raise the ground level or to fill a depression for construction purposes.",
        "ifc_version": "IFC4X3",
        "item_type": "entity",
        "predefined_types": [
            "BACKFILL", "COUNTERWEIGHT", "EMBANKMENT",
            "SLOPEFILL", "SUBGRADE", "TRANSITIONSECTION",
            "USERDEFINED", "NOTDEFINED"
        ]
    },
    {
        "name": "IfcKerb",
        "definition": "A kerb is a component of a road or pavement that forms a boundary between different surfaces, typically between a roadway and a sidewalk.",
        "ifc_version": "IFC4X3",
        "item_type": "entity",
        "predefined_types": ["USERDEFINED", "NOTDEFINED"]
    },
    {
        "name": "IfcPavement",
        "definition": "A pavement is a structure consisting of one or more courses of material placed on a prepared surface to support and distribute traffic loads.",
        "ifc_version": "IFC4X3",
        "item_type": "entity",
        "predefined_types": [
            "FLEXIBLE", "RIGID", "USERDEFINED", "NOTDEFINED"
        ]
    },
    {
        "name": "IfcRail",
        "definition": "A rail is a steel bar that forms the running surface for railway vehicles. It is typically supported by sleepers and fastened to them.",
        "ifc_version": "IFC4X3",
        "item_type": "entity",
        "predefined_types": [
            "BLADE", "CHECKRAIL", "GUARDRAIL", "RACKRAIL",
            "RAIL", "STOCKRAIL", "USERDEFINED", "NOTDEFINED"
        ]
    },
    {
        "name": "IfcRailway",
        "definition": "A railway is a civil engineering works that provides a track for railway vehicles. IfcRailway defines the occurrence of a railway facility.",
        "ifc_version": "IFC4X3",
        "item_type": "entity",
        "predefined_types": ["USERDEFINED", "NOTDEFINED"]
    },
    {
        "name": "IfcRoad",
        "definition": "A road is a civil engineering works that provides a way for vehicles, pedestrians, and other traffic. IfcRoad defines the occurrence of a road facility.",
        "ifc_version": "IFC4X3",
        "item_type": "entity",
        "predefined_types": ["USERDEFINED", "NOTDEFINED"]
    },
    {
        "name": "IfcSign",
        "definition": "A sign is a device that displays information to road users, railway users, or other infrastructure users. It can be a traffic sign, information sign, or warning sign.",
        "ifc_version": "IFC4X3",
        "item_type": "entity",
        "predefined_types": [
            "MARKER", "PICTORAL", "USERDEFINED", "NOTDEFINED"
        ]
    }
]


def extend_knowledge_base():
    """扩展知识库，添加桥梁领域实体"""

    # 1. 加载现有数据库
    db_path = Path(__file__).parent / "c_knowledge_base_mapping" / "resources" / "entity_db.json"
    logger.info(f"Loading existing database from: {db_path}")

    with open(db_path, 'r', encoding='utf-8') as f:
        db_data = json.load(f)

    original_count = len(db_data['items'])
    logger.info(f"Original database has {original_count} entities")

    # 2. 加载向量模型
    # 系统实际使用 BAAI/bge-m3，直接用这个模型名称
    # SentenceTransformer会自动从HuggingFace缓存加载
    model_name = "BAAI/bge-m3"
    logger.info(f"Loading vector model: {model_name}")
    model = SentenceTransformer(model_name)

    # 3. 为新实体生成向量嵌入
    logger.info(f"Adding {len(BRIDGE_ENTITIES)} bridge entities...")

    for entity in BRIDGE_ENTITIES:
        # 检查是否已存在
        existing = [item for item in db_data['items'] if item['name'] == entity['name']]
        if existing:
            logger.warning(f"Entity {entity['name']} already exists, skipping")
            continue

        # 生成向量嵌入
        text_for_embedding = f"{entity['name']}: {entity['definition']}"
        vector = model.encode(text_for_embedding, normalize_embeddings=True).tolist()

        # 添加到数据库
        entity_with_vector = entity.copy()
        entity_with_vector['vector'] = vector
        db_data['items'].append(entity_with_vector)

        logger.info(f"Added: {entity['name']} (vector dim: {len(vector)})")

    # 4. 更新元数据
    new_count = len(db_data['items'])
    db_data['metadata']['item_counts']['entity'] = new_count
    db_data['metadata']['updated_at'] = "2026-04-20T23:45:00.000000"

    logger.info(f"Database updated: {original_count} -> {new_count} entities (+{new_count - original_count})")

    # 5. 保存更新后的数据库
    backup_path = db_path.with_suffix('.json.backup')
    logger.info(f"Creating backup at: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

    logger.info(f"Saving updated database to: {db_path}")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

    logger.info("Knowledge base extension completed successfully!")

    # 6. 打印添加的实体摘要
    print("\n" + "="*80)
    print("ADDED ENTITIES SUMMARY")
    print("="*80)
    for entity in BRIDGE_ENTITIES:
        print(f"\n{entity['name']} (IFC4X3)")
        print(f"  Definition: {entity['definition'][:100]}...")
        if entity['predefined_types']:
            print(f"  Predefined Types: {', '.join(entity['predefined_types'][:5])}...")


if __name__ == "__main__":
    extend_knowledge_base()
