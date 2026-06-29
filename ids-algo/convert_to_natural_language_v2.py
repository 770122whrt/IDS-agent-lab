"""
将结构化IDS文本转换为简洁的自然语言描述（改进版）

使用改进的prompt生成Stage A期望的简洁自然语言格式。

参考成功案例：
- "All walls should have the property FireRating in the set Pset_WallCommon with a value being one of REI30, REI60, REI90."
- 简洁、直接、口语化

输入: ids_input_text_full.txt (结构化文本)
输出: ids_input_natural_language_v2.json (简洁自然语言JSON)

作者: IDS-Agent
日期: 2026-04-23
"""

import json
import re
from pathlib import Path
from typing import List, Dict
import anthropic
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('.env-pipeline')


def parse_specifications(text: str) -> List[Dict]:
    """
    解析结构化文本，提取每个specification

    Args:
        text: 完整的结构化文本

    Returns:
        specifications列表，每个包含id和structured_text
    """
    specs = []

    # 按【Specification N】分割
    pattern = r'【Specification (\d+)】([^【]*?)(?=【Specification \d+】|$)'
    matches = re.findall(pattern, text, re.DOTALL)

    for spec_id, spec_text in matches:
        specs.append({
            "id": spec_id,
            "structured_text": f"【Specification {spec_id}】{spec_text.strip()}"
        })

    return specs


def convert_to_natural_language_v2(structured_text: str, client: anthropic.Anthropic) -> str:
    """
    使用Claude将结构化文本转换为简洁的自然语言（改进版）

    Args:
        structured_text: 结构化的specification文本
        client: Anthropic客户端

    Returns:
        简洁的自然语言描述
    """
    prompt = f"""Convert this IDS specification into a CONCISE, SIMPLE natural language sentence or short paragraph.

IMPORTANT STYLE REQUIREMENTS:
1. Write in a simple, direct style like: "All walls should have the property FireRating in the set Pset_WallCommon with a value being one of REI30, REI60, REI90."
2. NO markdown formatting (no **, no headers, no bullet points)
3. NO section titles like "Requirements:" or "Specification:"
4. Keep it SHORT and CONVERSATIONAL
5. Use simple sentence structures

CONTENT REQUIREMENTS:
- Start with the entity type (e.g., "All IfcProject entities", "All walls", "All IfcBridge structures")
- State requirements directly (e.g., "should have", "must contain", "must be part of")
- Include property names, property sets, and value constraints
- Mention IFC version if specified
- Include cardinality if important (e.g., "exactly one", "one or more")

GOOD EXAMPLES:
✓ "All walls should have the property FireRating in the set Pset_WallCommon with a value being one of REI30, REI60, REI90."
✓ "All IfcBuildingStorey entities must have a Name attribute matching the pattern '00 ground floor|01 first floor|02 second floor'. IFC versions: IFC4X3_ADD2, IFC4, IFC2X3."
✓ "The model must contain exactly one IfcProject entity that provides default units for length (meters), angle (degrees), mass (kilograms), and temperature (Celsius)."

BAD EXAMPLES (too verbose/formatted):
✗ "**IFC4X3_ADD2 Project Specification**\n\nThis specification applies to all IfcProject entities..."
✗ "Requirements:\n- The model MUST contain...\n- The IfcProject MUST provide..."

Structured specification:
{structured_text}

Convert to simple natural language (2-4 sentences max):"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,  # Reduced to encourage brevity
        temperature=0.3,  # Lower temperature for more consistent output
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text.strip()


def main():
    """主函数"""
    # 配置路径
    input_file = "experimental_results/large_scale_test/ids_input_text_full.txt"
    output_file = "experimental_results/large_scale_test/ids_input_natural_language_v2.json"

    print(f"Reading structured text from: {input_file}")

    # 读取结构化文本
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # 解析specifications
    specs = parse_specifications(text)
    print(f"Found {len(specs)} specifications\n")

    # 初始化Anthropic客户端
    api_key = os.getenv("ANTHROPIC_AUTH_TOKEN") or os.getenv("LLM_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL") or os.getenv("LLM_BASE_URL")

    if not api_key:
        raise ValueError("ANTHROPIC_AUTH_TOKEN or LLM_API_KEY environment variable not set")

    client = anthropic.Anthropic(
        api_key=api_key,
        base_url=base_url
    )

    # 转换每个specification
    results = []
    for i, spec in enumerate(specs, 1):
        print(f"[{i}/{len(specs)}] Converting specification {spec['id']}...", end=" ")

        try:
            natural_text = convert_to_natural_language_v2(spec['structured_text'], client)

            # 验证输出不包含markdown格式
            if '**' in natural_text or natural_text.startswith('#'):
                print(f"[WARNING] Output contains markdown, retrying...")
                # 可以选择重试或清理
                natural_text = natural_text.replace('**', '').replace('#', '')

            results.append({
                "id": spec['id'],
                "text": natural_text,
                "language": "en"
            })

            # 显示预览
            preview = natural_text[:80] + "..." if len(natural_text) > 80 else natural_text
            print(f"[OK] {preview}")

        except Exception as e:
            print(f"[ERROR] {e}")
            # 失败时使用原始文本
            results.append({
                "id": spec['id'],
                "text": spec['structured_text'],
                "language": "en"
            })

    # 保存结果
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"[OK] Conversion complete!")
    print(f"[OK] Output saved to: {output_file}")
    print(f"[OK] Total specifications: {len(results)}")

    # 统计信息
    avg_length = sum(len(r['text']) for r in results) / len(results)
    print(f"[INFO] Average text length: {avg_length:.0f} characters")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
