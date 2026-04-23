"""测试向量搜索IfcProject的结果"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from c_knowledge_base_mapping.vector_database.core.base import VectorDatabase

def test_search():
    # 初始化向量数据库
    db = VectorDatabase()

    # 测试不同的查询
    queries = [
        "IfcProject",
        "IfcProject entity",
        "project entity",
        "IFC project",
        "building project"
    ]

    for query in queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"{'='*80}")

        results = db.search(
            query=query,
            item_type="entity",
            ifc_version="IFC4",
            top_k=10
        )

        print(f"\nTop 10 results:")
        for i, result in enumerate(results, 1):
            name = result['name']
            similarity = result['similarity']
            definition = result.get('definition', '')[:100]
            print(f"  {i}. {name} (similarity: {similarity:.4f})")
            if 'Project' in name:
                print(f"     ✓ FOUND PROJECT-RELATED ENTITY")
                print(f"     Definition: {definition}...")

if __name__ == "__main__":
    test_search()
