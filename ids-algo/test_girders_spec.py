"""
测试Girders规范的完整pipeline
"""
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Stage imports
from a_spec_parser.spec_parser import parseSpecification
from b_facet_classifier.facet_classifier import classifyFacets
from c_knowledge_base_mapping.pipeline import runKnowledgeBaseMapping
from d_constraint_extractor.constraint_extractor import runConstraintExtraction
from e_ids_builder.ids_builder import IDSBuilder

async def test_girders_pipeline():
    """测试Girders规范的完整pipeline"""

    # 测试输入
    test_input = """所有IfcElementAssembly实体，且PredefinedType为GIRDER的构件，必须包含在IfcBridgePart（类型为SUPERSTRUCTURE）的上层结构中，必须有Name属性，必须定义材料。"""

    print("=" * 80)
    print("测试输入:")
    print(test_input)
    print("=" * 80)

    # 创建输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"experimental_results/large_scale_test/girders_test_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Stage A: Parse
        print("\n[Stage A] Parsing specification...")
        parse_result = await parseSpecification(test_input)

        with open(output_dir / "a_parsed.json", "w", encoding="utf-8") as f:
            json.dump({
                "applicability": parse_result.applicability,
                "requirements": parse_result.requirements
            }, f, indent=2, ensure_ascii=False)

        print(f"  Applicability: {parse_result.applicability}")
        print(f"  Requirements: {len(parse_result.requirements)} items")

        # Stage B: Classify
        print("\n[Stage B] Classifying facets...")
        classified = await classifyFacets(parse_result)

        with open(output_dir / "b_classified.json", "w", encoding="utf-8") as f:
            json.dump({
                "applicability": classified.applicability,
                "requirements": classified.requirements
            }, f, indent=2, ensure_ascii=False)

        print(f"  Applicability facets: {len(classified.applicability)}")
        print(f"  Requirement facets: {len(classified.requirements)}")

        # Stage C: Map to knowledge base
        print("\n[Stage C] Mapping to knowledge base...")
        mapped = await runKnowledgeBaseMapping(classified)

        with open(output_dir / "c_mapped.json", "w", encoding="utf-8") as f:
            json.dump({
                "applicability": [
                    {
                        "facet_type": f.facet_type,
                        "original_text": f.original_text,
                        "mapped_value": f.mapped_value,
                        "confidence": f.confidence,
                        "metadata": f.metadata
                    }
                    for f in mapped.applicability
                ],
                "requirements": [
                    {
                        "facet_type": f.facet_type,
                        "original_text": f.original_text,
                        "mapped_value": f.mapped_value,
                        "confidence": f.confidence,
                        "metadata": f.metadata
                    }
                    for f in mapped.requirements
                ]
            }, f, indent=2, ensure_ascii=False)

        print(f"  Applicability mapped: {len(mapped.applicability)}")
        for facet in mapped.applicability:
            print(f"    - {facet.facet_type}: {facet.original_text} → {facet.mapped_value} (confidence: {facet.confidence:.4f})")

        print(f"  Requirements mapped: {len(mapped.requirements)}")
        for facet in mapped.requirements:
            print(f"    - {facet.facet_type}: {facet.original_text} → {facet.mapped_value} (confidence: {facet.confidence:.4f})")

        # Stage D: Extract constraints
        print("\n[Stage D] Extracting constraints...")
        constraints = runConstraintExtraction(mapped)

        with open(output_dir / "d_constraints.json", "w", encoding="utf-8") as f:
            json.dump(constraints, f, indent=2, ensure_ascii=False)

        print(f"  Extracted {len(constraints)} constraints")
        for constraint in constraints:
            print(f"    - {constraint}")

        # 合并约束到mapped facets
        print("\n[Stage D+] Merging constraints into facets...")
        for constraint in constraints:
            target_facet = None
            for facet in mapped.applicability + mapped.requirements:
                if constraint.get("target_facet_id") == id(facet):
                    target_facet = facet
                    break

            if target_facet:
                if not hasattr(target_facet, "constraints"):
                    target_facet.constraints = []
                target_facet.constraints.append(constraint)
                print(f"    Merged constraint to {target_facet.facet_type}: {constraint}")

        # Stage E: Build IDS
        print("\n[Stage E] Building IDS...")
        builder = IDSBuilder()
        ids_xml = builder.build_ids(
            specifications=[{
                "applicability": mapped.applicability,
                "requirements": mapped.requirements
            }],
            metadata={
                "title": "Girders Test IDS",
                "description": "Generated from test specification"
            }
        )

        output_ids_path = output_dir / "e_output.ids"
        with open(output_ids_path, "w", encoding="utf-8") as f:
            f.write(ids_xml)

        print(f"  IDS file generated: {output_ids_path}")

        # 验证生成的IDS
        print("\n[Verification] Checking generated IDS...")
        with open(output_ids_path, "r", encoding="utf-8") as f:
            ids_content = f.read()

        # 检查关键内容
        checks = {
            "IfcElementAssembly": "IfcElementAssembly" in ids_content,
            "GIRDER": "GIRDER" in ids_content,
            "IfcBridgePart": "IfcBridgePart" in ids_content,
            "SUPERSTRUCTURE": "SUPERSTRUCTURE" in ids_content,
            "Name attribute": '<ids:attribute' in ids_content and 'Name' in ids_content,
            "Material": '<ids:material' in ids_content or 'material' in ids_content.lower()
        }

        print("  Verification results:")
        for check_name, result in checks.items():
            status = "✓" if result else "✗"
            print(f"    {status} {check_name}")

        # 显示IDS片段
        print("\n[IDS Preview] First 2000 characters:")
        print(ids_content[:2000])

        print("\n" + "=" * 80)
        print(f"✓ Test completed. Output directory: {output_dir}")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n✗ Error during pipeline execution:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_girders_pipeline())
    exit(0 if success else 1)
