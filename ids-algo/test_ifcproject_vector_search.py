"""
测试为什么向量搜索找不到IfcProject
"""

import asyncio
from c_knowledge_base_mapping.database_manager import DatabaseManager


async def test_ifcproject_search():
    """测试IfcProject搜索"""

    print(f"\n{'='*80}")
    print(f"Testing IfcProject Vector Search")
    print(f"{'='*80}\n")

    # 初始化数据库
    db_manager = DatabaseManager()
    await db_manager.initialize_databases()

    entity_db = db_manager.get_database("entity")

    # 测试不同的查询
    test_cases = [
        ("IfcProject", None),  # 不限制IFC版本
        ("IfcProject entity", None),
        ("IfcProject", ["IFC4"]),  # 限制IFC4
        ("project", None),
        ("building project context", None),
    ]

    for query, ifc_versions in test_cases:
        print(f"\n{'='*80}")
        print(f"Query: '{query}'")
        print(f"IFC Versions Filter: {ifc_versions}")
        print(f"{'='*80}\n")

        results = entity_db.search(query, top_k=10, ifc_versions=ifc_versions)

        if not results:
            print("  No results found!")
            continue

        print(f"  Found {len(results)} results:\n")

        for i, (ifc_item, similarity) in enumerate(results, 1):
            marker = ""
            if "Project" in ifc_item.name:
                marker = " <-- PROJECT ENTITY"

            print(f"  {i}. {ifc_item.name} (similarity: {similarity:.4f}){marker}")
            print(f"     IFC Version: {ifc_item.ifc_version}")
            print(f"     Definition: {ifc_item.definition[:80]}...")
            print()

    print(f"\n{'='*80}")
    print(f"Test completed")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(test_ifcproject_search())
