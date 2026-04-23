"""
测试Entity向量数据库搜索

查看为什么"IfcProject"会被映射到"IfcPersonAndOrganization"
"""

import asyncio
from c_knowledge_base_mapping.database_manager import DatabaseManager


async def test_entity_search():
    """测试Entity数据库搜索"""

    print(f"\n{'='*80}")
    print(f"Testing Entity Vector Database Search")
    print(f"{'='*80}\n")

    # 初始化数据库管理器
    db_manager = DatabaseManager()
    await db_manager.initialize_databases()

    # 获取entity数据库
    entity_db = db_manager.get_database("entity")

    if not entity_db:
        print("ERROR: Entity database not found!")
        return

    print(f"Entity database loaded successfully")
    print(f"Database type: {type(entity_db)}")

    # 测试查询
    test_queries = [
        "IfcProject entity",
        "IfcProject",
        "project entity",
        "provides default units for length",
        "length unit",
        "angle unit"
    ]

    for query in test_queries:
        print(f"\n{'-'*80}")
        print(f"Query: '{query}'")
        print(f"{'-'*80}")

        # 搜索Top 5候选
        results = entity_db.search(query, top_k=5, ifc_versions=None)

        if not results:
            print("  No results found!")
            continue

        print(f"  Found {len(results)} candidates:\n")

        for i, (ifc_item, similarity) in enumerate(results, 1):
            print(f"  {i}. {ifc_item.name}")
            print(f"     Similarity: {similarity:.4f}")
            print(f"     IFC Version: {ifc_item.ifc_version}")
            print(f"     Definition: {ifc_item.definition[:100]}...")
            if hasattr(ifc_item, 'predefined_types') and ifc_item.predefined_types:
                print(f"     Predefined Types: {ifc_item.predefined_types[:3]}")
            print()

    # 特别测试：直接搜索"IfcProject"
    print(f"\n{'='*80}")
    print(f"DETAILED TEST: Searching for 'IfcProject'")
    print(f"{'='*80}\n")

    results = entity_db.search("IfcProject", top_k=10, ifc_versions=None)

    if results:
        print(f"Found {len(results)} results:\n")
        for i, (ifc_item, similarity) in enumerate(results, 1):
            print(f"{i}. {ifc_item.name} (similarity: {similarity:.4f})")
            if ifc_item.name == "IfcProject":
                print(f"   [EXACT MATCH] FOUND at position {i}!")
                print(f"   Definition: {ifc_item.definition}")
                print(f"   IFC Version: {ifc_item.ifc_version}")
    else:
        print("❌ No results found for 'IfcProject'!")

    print(f"\n{'='*80}")
    print(f"Test completed")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(test_entity_search())
