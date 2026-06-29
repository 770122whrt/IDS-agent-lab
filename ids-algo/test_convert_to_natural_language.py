"""
测试LLM自然语言转换 - 仅转换前3个specifications

用于验证转换逻辑是否正确
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


def parse_specifications(text: str, limit: int = None) -> List[Dict]:
    """
    解析结构化文本，提取每个specification

    Args:
        text: 完整的结构化文本
        limit: 限制提取的数量

    Returns:
        specifications列表，每个包含id和structured_text
    """
    specs = []

    # 按【Specification N】分割
    pattern = r'【Specification (\d+)】([^【]*?)(?=【Specification \d+】|$)'
    matches = re.findall(pattern, text, re.DOTALL)

    for spec_id, spec_text in matches[:limit]:
        specs.append({
            "id": spec_id,
            "structured_text": f"【Specification {spec_id}】{spec_text.strip()}"
        })

    return specs


def convert_to_natural_language(structured_text: str, client: anthropic.Anthropic) -> str:
    """
    使用Claude将结构化文本转换为自然语言

    Args:
        structured_text: 结构化的specification文本
        client: Anthropic客户端

    Returns:
        自然语言描述
    """
    prompt = f"""Convert the following structured IDS specification into natural language description.

The output should be a clear, concise natural language description that:
1. States the IFC version if present
2. Describes what entities the specification applies to
3. Lists all requirements in natural language (e.g., "MUST HAVE property X", "MUST BE part of Y")
4. Includes cardinality constraints where relevant
5. Uses clear imperative language like "All X should...", "The model MUST contain..."

Structured specification:
{structured_text}

Natural language description:"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text.strip()


def main():
    """主函数"""
    # 配置路径
    input_file = "experimental_results/large_scale_test/ids_input_text_full.txt"
    output_file = "experimental_results/large_scale_test/ids_input_natural_language_test.json"

    print(f"Reading structured text from: {input_file}")

    # 读取结构化文本
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # 解析specifications (仅前3个)
    specs = parse_specifications(text, limit=3)
    print(f"Testing with {len(specs)} specifications")

    # 初始化Anthropic客户端
    api_key = os.getenv("ANTHROPIC_AUTH_TOKEN") or os.getenv("LLM_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL") or os.getenv("LLM_BASE_URL")

    if not api_key:
        raise ValueError("ANTHROPIC_AUTH_TOKEN or LLM_API_KEY environment variable not set")

    print(f"Using API base URL: {base_url}")

    client = anthropic.Anthropic(
        api_key=api_key,
        base_url=base_url
    )

    # 转换每个specification
    results = []
    for i, spec in enumerate(specs, 1):
        print(f"\nConverting specification {spec['id']}/{len(specs)}...")
        print(f"Input preview: {spec['structured_text'][:200]}...")

        try:
            natural_text = convert_to_natural_language(spec['structured_text'], client)
            results.append({
                "id": spec['id'],
                "text": natural_text,
                "language": "en"
            })
            print(f"[OK] Success")
            print(f"Output preview: {natural_text[:200]}...")
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

    print(f"\n[OK] Test conversion complete!")
    print(f"[OK] Output saved to: {output_file}")
    print(f"[OK] Total specifications: {len(results)}")


if __name__ == "__main__":
    main()
