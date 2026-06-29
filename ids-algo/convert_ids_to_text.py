"""
将IDS文件转换为完整的结构化文本

使用IDSToTextGenerator保留所有信息：
- IFC版本
- Entity信息
- Requirements (partOf, attribute, property, material)
- 基数约束 (minOccurs/maxOccurs)
- Description

作者: IDS-Agent
日期: 2026-04-22
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ids_converter.ids_to_text import IDSToTextGenerator


def convert_ids_to_text(
    ids_file_path: str,
    output_file_path: str,
    language: str = "en"
):
    """
    将IDS文件转换为结构化文本

    Args:
        ids_file_path: 源IDS文件路径
        output_file_path: 输出文本文件路径
        language: 输出语言 ("en", "zh", "both")
    """
    print(f"Converting IDS file: {ids_file_path}")
    print(f"Output language: {language}")

    # 初始化生成器
    generator = IDSToTextGenerator()

    # 生成文本
    text = generator.generate_from_file(ids_file_path, language=language)

    # 保存到文件
    output_path = Path(output_file_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"[OK] Conversion complete!")
    print(f"[OK] Output saved to: {output_file_path}")
    print(f"[OK] File size: {len(text)} characters")

    # 统计specifications数量
    spec_count = text.count("Specification:")
    print(f"[OK] Total specifications: {spec_count}")


if __name__ == "__main__":
    # 源IDS文件
    ids_file = r"E:\code for project\IDS_practise\backend\ids-agent\ids_converter\20250317023029_IFCBridge-IDS-xml.ids"

    # 输出文件
    output_file = "ids-algo/experimental_results/large_scale_test/ids_input_text_full.txt"

    # 转换（使用英文，因为pipeline是英文）
    convert_ids_to_text(ids_file, output_file, language="en")
