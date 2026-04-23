"""
调试Entity Resolver的LLM选择

打印完整的prompt和LLM响应，看看为什么选择了错误的entity
"""

import asyncio
from c_knowledge_base_mapping.database_manager import DatabaseManager
from c_knowledge_base_mapping.resolvers.entity_resolver import EntityResolver


async def debug_entity_selection():
    """调试Entity选择过程"""

    print(f"\n{'='*80}")
    print(f"Debugging Entity Resolver LLM Selection")
    print(f"{'='*80}\n")

    # 初始化
    db_manager = DatabaseManager()
    await db_manager.initialize_databases()

    entity_resolver = EntityResolver(db_manager)

    # 测试查询
    query = "IfcProject entity"
    context = {"ifc_version": "IFC4"}

    print(f"Query: {query}")
    print(f"Context: {context}\n")

    # 获取向量搜索结果
    entity_db = db_manager.get_database("entity")
    candidates = entity_db.search(query, top_k=5, ifc_versions=["IFC4"])

    print(f"Vector Search Results (Top 5):\n")
    for i, (ifc_item, similarity) in enumerate(candidates, 1):
        print(f"  {i}. {ifc_item.name} (similarity: {similarity:.4f})")
        print(f"     Definition: {ifc_item.definition[:80]}...")
        print()

    # 构建LLM prompt（模拟entity_resolver的逻辑）
    candidate_info = []
    for ifc_item, similarity in candidates:
        candidate_info.append({
            "name": ifc_item.name,
            "definition": ifc_item.definition,
            "similarity": similarity
        })

    prompt = entity_resolver._build_selection_prompt(
        query, candidate_info, "IFC4", "", None
    )

    print(f"\n{'='*80}")
    print(f"LLM Prompt saved to: entity_llm_prompt.txt")
    print(f"{'='*80}\n")

    # 保存prompt到文件
    with open("entity_llm_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"Prompt length: {len(prompt)} characters\n")

    # 调用resolver
    result = await entity_resolver.resolve(query, context)

    if result:
        print(f"\n{'='*80}")
        print(f"Final Result:")
        print(f"{'='*80}\n")
        print(f"  Mapped Name: {result['mapped_name']}")
        print(f"  Confidence: {result['confidence']:.4f}")
        print(f"  Source: {result['source']}")
        print(f"\n{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(debug_entity_selection())
