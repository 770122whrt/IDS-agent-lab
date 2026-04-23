"""
IDS对比分析工具
对比原始IDS和生成的IDS，生成详细的对比报告
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import xml.etree.ElementTree as ET
from datetime import datetime


def parse_original_ids(ids_path: str) -> Dict[str, Any]:
    """解析原始IDS XML文件"""
    tree = ET.parse(ids_path)
    root = tree.getroot()

    # 移除命名空间前缀
    ns = {'ids': 'http://standards.buildingsmart.org/IDS'}

    specs = []
    for spec in root.findall('.//ids:specification', ns):
        name = spec.get('name', 'Unnamed')

        # 统计applicability
        applicability = spec.find('ids:applicability', ns)
        app_count = len(list(applicability)) if applicability is not None else 0

        # 统计requirements
        requirements = spec.find('ids:requirements', ns)
        req_count = len(list(requirements)) if requirements is not None else 0

        specs.append({
            'name': name,
            'applicability_count': app_count,
            'requirements_count': req_count
        })

    return {
        'total_specifications': len(specs),
        'specifications': specs
    }


def parse_generated_ids(json_path: str) -> Dict[str, Any]:
    """解析生成的IDS JSON文件"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    specs = []
    for spec in data.get('specifications', []):
        # 统计applicability facets
        app = spec.get('applicability', {})
        app_count = sum(1 for k, v in app.items() if v is not None and k != 'minOccurs' and k != 'maxOccurs')

        # 统计requirements facets
        req = spec.get('requirements', {})
        req_count = sum(1 for k, v in req.items() if v is not None and k != 'description')

        specs.append({
            'name': spec.get('name', 'Unnamed'),
            'description': spec.get('description', ''),
            'applicability_count': app_count,
            'requirements_count': req_count
        })

    return {
        'total_specifications': len(specs),
        'specifications': specs
    }


def generate_comparison_report(original: Dict, generated: Dict, output_dir: Path):
    """生成对比报告"""

    report = {
        'comparison_date': datetime.now().isoformat(),
        'summary': {
            'original_specs': original['total_specifications'],
            'generated_specs': generated['total_specifications'],
            'coverage_rate': f"{(generated['total_specifications'] / original['total_specifications'] * 100):.1f}%"
        },
        'statistics': {
            'original': {
                'total_applicability_facets': sum(s['applicability_count'] for s in original['specifications']),
                'total_requirements_facets': sum(s['requirements_count'] for s in original['specifications']),
                'avg_applicability_per_spec': sum(s['applicability_count'] for s in original['specifications']) / len(original['specifications']),
                'avg_requirements_per_spec': sum(s['requirements_count'] for s in original['specifications']) / len(original['specifications'])
            },
            'generated': {
                'total_applicability_facets': sum(s['applicability_count'] for s in generated['specifications']),
                'total_requirements_facets': sum(s['requirements_count'] for s in generated['specifications']),
                'avg_applicability_per_spec': sum(s['applicability_count'] for s in generated['specifications']) / len(generated['specifications']),
                'avg_requirements_per_spec': sum(s['requirements_count'] for s in generated['specifications']) / len(generated['specifications'])
            }
        },
        'specification_comparison': []
    }

    # 对比每个specification
    for orig_spec in original['specifications']:
        # 尝试在生成的IDS中找到匹配的specification
        matched = None
        for gen_spec in generated['specifications']:
            if orig_spec['name'].lower() in gen_spec['name'].lower() or \
               gen_spec['name'].lower() in orig_spec['name'].lower():
                matched = gen_spec
                break

        comparison = {
            'original_name': orig_spec['name'],
            'generated_name': matched['name'] if matched else 'NOT FOUND',
            'status': 'MATCHED' if matched else 'MISSING',
            'original_applicability': orig_spec['applicability_count'],
            'generated_applicability': matched['applicability_count'] if matched else 0,
            'original_requirements': orig_spec['requirements_count'],
            'generated_requirements': matched['requirements_count'] if matched else 0
        }

        report['specification_comparison'].append(comparison)

    # 保存JSON报告
    json_output = output_dir / 'ids_comparison_report.json'
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # 生成Markdown表格报告
    md_output = output_dir / 'ids_comparison_report.md'
    with open(md_output, 'w', encoding='utf-8') as f:
        f.write("# IDS对比分析报告\n\n")
        f.write(f"**生成时间**: {report['comparison_date']}\n\n")

        f.write("## 总体对比\n\n")
        f.write("| 指标 | 原始IDS | 生成IDS | 覆盖率 |\n")
        f.write("|------|---------|---------|--------|\n")
        f.write(f"| Specification数量 | {report['summary']['original_specs']} | {report['summary']['generated_specs']} | {report['summary']['coverage_rate']} |\n")
        f.write(f"| Applicability Facets总数 | {report['statistics']['original']['total_applicability_facets']} | {report['statistics']['generated']['total_applicability_facets']} | - |\n")
        f.write(f"| Requirements Facets总数 | {report['statistics']['original']['total_requirements_facets']} | {report['statistics']['generated']['total_requirements_facets']} | - |\n")
        f.write(f"| 平均Applicability/Spec | {report['statistics']['original']['avg_applicability_per_spec']:.1f} | {report['statistics']['generated']['avg_applicability_per_spec']:.1f} | - |\n")
        f.write(f"| 平均Requirements/Spec | {report['statistics']['original']['avg_requirements_per_spec']:.1f} | {report['statistics']['generated']['avg_requirements_per_spec']:.1f} | - |\n\n")

        f.write("## Specification详细对比\n\n")
        f.write("| # | 原始名称 | 生成名称 | 状态 | Applicability (原/生成) | Requirements (原/生成) |\n")
        f.write("|---|----------|----------|------|------------------------|------------------------|\n")

        for i, comp in enumerate(report['specification_comparison'], 1):
            status_emoji = "✅" if comp['status'] == 'MATCHED' else "❌"
            f.write(f"| {i} | {comp['original_name']} | {comp['generated_name']} | {status_emoji} {comp['status']} | {comp['original_applicability']}/{comp['generated_applicability']} | {comp['original_requirements']}/{comp['generated_requirements']} |\n")

        f.write("\n## 分析结论\n\n")
        matched_count = sum(1 for c in report['specification_comparison'] if c['status'] == 'MATCHED')
        f.write(f"- **匹配率**: {matched_count}/{len(report['specification_comparison'])} ({matched_count/len(report['specification_comparison'])*100:.1f}%)\n")
        f.write(f"- **生成效率**: 原始{report['summary']['original_specs']}个specification → 生成{report['summary']['generated_specs']}个\n")

        missing = [c for c in report['specification_comparison'] if c['status'] == 'MISSING']
        if missing:
            f.write(f"\n### 未匹配的Specification ({len(missing)}个)\n\n")
            for m in missing:
                f.write(f"- {m['original_name']}\n")

    print(f"[OK] Comparison report generated:")
    print(f"   - JSON: {json_output}")
    print(f"   - Markdown: {md_output}")

    return report


def main():
    # 文件路径
    original_ids_path = Path("../ids_converter/20250317023029_IFCBridge-IDS-xml.ids")
    generated_ids_path = Path("experimental_results/large_scale_test/result_20260420_205651.json")
    output_dir = Path("experimental_results/large_scale_test")

    print("=" * 60)
    print("IDS Comparison Analysis Tool")
    print("=" * 60)

    # 解析原始IDS
    print(f"\n[PARSE] Original IDS: {original_ids_path}")
    original = parse_original_ids(str(original_ids_path))
    print(f"   Found {original['total_specifications']} specifications")

    # 解析生成的IDS
    print(f"\n[PARSE] Generated IDS: {generated_ids_path}")
    generated = parse_generated_ids(str(generated_ids_path))
    print(f"   Found {generated['total_specifications']} specifications")

    # 生成对比报告
    print(f"\n[REPORT] Generating comparison report...")
    report = generate_comparison_report(original, generated, output_dir)

    print("\n" + "=" * 60)
    print("Comparison completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
