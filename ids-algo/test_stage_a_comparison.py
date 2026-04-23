"""
测试Stage A - 对比成功案例和v2输入

不修改源码，只测试Stage A的行为
参考: tests/a.py

目标：
1. 测试temp/input.json的成功案例
2. 测试我们的v2自然语言输入
3. 对比两者的输出差异
"""

import asyncio
import json
from pathlib import Path
from a_structured_parser import runStructuredParser, format_result_as_markdown


async def test_stage_a_with_text(text: str, label: str):
    """测试Stage A对单个文本的解析"""
    print(f"\n{'='*80}")
    print(f"Testing Stage A: {label}")
    print(f"{'='*80}")
    print(f"Input text ({len(text)} chars):")
    print(f"{text[:200]}..." if len(text) > 200 else text)
    print(f"\n{'-'*80}\n")

    # 调用Stage A
    result = await runStructuredParser(text)

    # 打印结果
    print(f"Result type: {type(result)}")
    print(f"Result attributes: {dir(result)}")

    # 尝试访问属性
    if hasattr(result, 'building_objects'):
        print(f"\nbuilding_objects: {len(result.building_objects)} items")
        for i, obj in enumerate(result.building_objects, 1):
            print(f"  {i}. {obj}")

    if hasattr(result, 'property_descriptions'):
        print(f"\nproperty_descriptions: {len(result.property_descriptions)} items")
        for i, prop in enumerate(result.property_descriptions, 1):
            print(f"  {i}. {prop}")

    if hasattr(result, 'material_requirements'):
        print(f"\nmaterial_requirements: {len(result.material_requirements)} items")
        for i, mat in enumerate(result.material_requirements, 1):
            print(f"  {i}. {mat}")

    # 转换为字典
    if hasattr(result, '__dict__'):
        result_dict = vars(result)
        print(f"\nResult as dict keys: {list(result_dict.keys())}")

        # 保存为JSON
        output_file = f"experimental_results/large_scale_test/stage_a_test_{label.replace(' ', '_')}.json"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        # 转换为可序列化格式
        def make_serializable(obj):
            if hasattr(obj, '__dict__'):
                return {k: make_serializable(v) for k, v in vars(obj).items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            else:
                return obj

        serializable_result = make_serializable(result)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_result, f, indent=2, ensure_ascii=False)

        print(f"\nSaved to: {output_file}")

    print(f"{'='*80}\n")

    return result


async def main():
    """主函数"""

    # 测试1: temp/input.json的成功案例
    print("\n" + "="*80)
    print("TEST 1: Successful case from temp/input.json")
    print("="*80)

    with open("temp/input.json", 'r', encoding='utf-8') as f:
        temp_inputs = json.load(f)

    # 测试第一个成功案例
    success_text = temp_inputs[0]['text']
    result1 = await test_stage_a_with_text(success_text, "success_case")

    # 测试2: 我们的v2自然语言输入
    print("\n" + "="*80)
    print("TEST 2: Our V2 natural language input")
    print("="*80)

    with open("experimental_results/large_scale_test/ids_input_natural_language_v2.json", 'r', encoding='utf-8') as f:
        v2_inputs = json.load(f)

    # 测试第一个v2输入
    v2_text = v2_inputs[0]['text']
    result2 = await test_stage_a_with_text(v2_text, "v2_case")

    # 对比分析
    print("\n" + "="*80)
    print("COMPARISON ANALYSIS")
    print("="*80)

    print(f"\nSuccess case:")
    print(f"  Text length: {len(success_text)} chars")
    if hasattr(result1, 'building_objects'):
        print(f"  Objects: {len(result1.building_objects)}")
        print(f"  Properties: {len(result1.property_descriptions)}")
        print(f"  Materials: {len(result1.material_requirements)}")

    print(f"\nV2 case:")
    print(f"  Text length: {len(v2_text)} chars")
    if hasattr(result2, 'building_objects'):
        print(f"  Objects: {len(result2.building_objects)}")
        print(f"  Properties: {len(result2.property_descriptions)}")
        print(f"  Materials: {len(result2.material_requirements)}")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(main())
