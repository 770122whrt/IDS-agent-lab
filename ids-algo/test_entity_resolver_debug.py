"""
测试Entity Resolver的完整流程

模拟entity_resolver.resolve()的调用，查看：
1. 向量搜索返回的候选列表
2. 传递给LLM的prompt
3. LLM的选择结果
"""

import asyncio
import json
from c_knowledge_base_mapping.database_manager import DatabaseManager
from c_knowledge_base_mapping.resolvers.entity_resolver import EntityResolver


async def test_entity_resolver():
    """测试Entity Resolver"""

    print(f"\n{'='*80}")
    print(f"Testing Entity Resolver - Full Flow")
    print(f"{'='*80}\n")

    # 初始化数据库管理器
    db_manager = DatabaseManager()
    await db_manager.initialize_databases()

    # 创建Entity Resolver
    entity_resolver = EntityResolver(db_manager)

    # 测试查询（来自我们的debug文件）
    test_cases = [
        {
            "query": "IfcProject entity that establishes the context for the bridge project",
            "context": {
                "ifc_version": "IFC4",
                "pipeline_memory": None
            }
        },
        {
            "query": "provides default units for length (meters)",
            "context": {
                "ifc_version": "IFC4",
                "pipeline_memory": None
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test Case {i}")
        print(f"{'='*80}")
        print(f"Query: {test_case['query']}")
        print(f"IFC Version: {test_case['context']['ifc_version']}")
        print(f"{'-'*80}\n")

        # 先查看向量搜索结果
        entity_db = db_manager.get_database("entity")
        search_results = entity_db.search(
            test_case['query'],
            top_k=5,
            ifc_versions=[test_case['context']['ifc_version']]
        )

        print(f"Vector Search Results (Top 5):\n")
        for j, (ifc_item, similarity) in enumerate(search_results, 1):
            print(f"  {j}. {ifc_item.name} (similarity: {similarity:.4f})")
            print(f"     Definition: {ifc_item.definition[:100]}...")
            print()

        # 调用resolver
        print(f"\n{'-'*80}")
        print(f"Calling Entity Resolver...")
        print(f"{'-'*80}\n")

        result = await entity_resolver.resolve(
            test_case['query'],
            test_case['context']
        )

        if result:
            print(f"[RESULT]")
            print(f"  Mapped Name: {result['mapped_name']}")
            print(f"  Confidence: {result['confidence']:.4f}")
            print(f"  Source: {result['source']}")
            print(f"  IFC Item: {result['ifc_item'].name}")
            print(f"  Definition: {result['ifc_item'].definition[:150]}...")
        else:
            print(f"[ERROR] No result returned!")

        print(f"\n{'='*80}\n")

    print(f"\nTest completed\n")


if __name__ == "__main__":
    asyncio.run(test_entity_resolver())
