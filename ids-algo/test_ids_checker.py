"""
使用现有的 checker_service 检查 IFC 文件是否符合 IDS 规范
"""
import sys
from pathlib import Path

# 添加 ifc_checker 模块路径
sys.path.insert(0, str(Path(__file__).parent.parent / "ifc_checker"))

from checker_service import check_ifc_against_ids


def main():
    """运行 IDS 检查"""
    ifc_path = r"E:\code for project\IDS_practise\backend\ids-agent\ids_converter\IFC\20250317023029_TRV-hdmi2-BRO-4x3.ifc"
    ids_path = r"E:\code for project\IDS_practise\backend\ids-agent\ids_converter\20250317023029_IFCBridge-IDS-xml.ids"
    output_dir = "test_output/ids_check_report"

    print("="*80)
    print("IFC 文件 IDS 规范检查")
    print("="*80)
    print(f"\nIFC 文件: {ifc_path}")
    print(f"IDS 文件: {ids_path}")
    print(f"输出目录: {output_dir}\n")

    # 执行检查
    result = check_ifc_against_ids(
        ids_file_path=ids_path,
        ifc_file_path=ifc_path,
        output_dir=output_dir
    )

    # 显示结果
    print("\n" + "="*80)
    print("检查结果")
    print("="*80)
    status = "[OK] 成功" if result['success'] else "[FAIL] 失败"
    print(f"状态: {status}")
    print(f"消息: {result['message']}")

    print(f"\n摘要:")
    print(f"  总规格数: {result['summary']['total_specs']}")
    print(f"  通过: {result['summary']['passed_specs']}")
    print(f"  失败: {result['summary']['failed_specs']}")
    print(f"  失败构件数: {result['summary']['total_failed_entities']}")

    if result.get('html_report_path'):
        print(f"\nHTML 报告: {result['html_report_path']}")
    if result.get('json_report_path'):
        print(f"JSON 报告: {result['json_report_path']}")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
