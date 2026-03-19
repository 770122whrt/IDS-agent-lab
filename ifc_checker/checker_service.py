"""
IFC Checker Service

提供 IFC 模型与 IDS 规范的合规性审查服务。

主要功能：
1. run_ids_checker() - 独立运行，从固定目录读取文件
2. check_ifc_against_ids() - API 可调用，接收文件路径参数

依赖：
- ifcopenshell: IFC 文件解析
- ifctester: IDS 验证和报告生成
"""

import os
import sys
import json
import tempfile
import ifcopenshell
from ifctester import ids, reporter
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


def check_ifc_against_ids(
    ids_file_path: str,
    ifc_file_path: str,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    对 IFC 模型执行 IDS 规范检查

    Args:
        ids_file_path: IDS 规范文件的绝对路径
        ifc_file_path: IFC 模型文件的绝对路径
        output_dir: 可选的输出目录，用于保存报告文件（如果为 None，使用临时目录）

    Returns:
        包含检查结果的字典：
        {
            "success": True/False,
            "message": "状态消息",
            "report_data": {...},  # JSON 格式的报告数据（已清洗）
            "html_report_path": "...",  # HTML 报告路径（如果指定 output_dir）
            "json_report_path": "...",  # JSON 报告路径（如果指定 output_dir）
            "summary": {
                "total_specs": 10,
                "passed_specs": 8,
                "failed_specs": 2,
                "total_failed_entities": 15
            }
        }
    """
    result = {
        "success": False,
        "message": "",
        "report_data": None,
        "html_report_path": None,
        "json_report_path": None,
        "summary": {
            "total_specs": 0,
            "passed_specs": 0,
            "failed_specs": 0,
            "total_failed_entities": 0
        }
    }

    # 验证文件存在
    if not os.path.exists(ids_file_path):
        result["message"] = f"IDS 文件不存在: {ids_file_path}"
        return result

    if not os.path.exists(ifc_file_path):
        result["message"] = f"IFC 文件不存在: {ifc_file_path}"
        return result

    # 决定是否使用临时目录
    use_temp_dir = output_dir is None
    if use_temp_dir:
        output_dir = tempfile.mkdtemp(prefix="ifc_check_")
        print(f"[Checker] Using temp directory: {output_dir}")
    else:
        os.makedirs(output_dir, exist_ok=True)

    try:
        # 1. 加载 IFC 模型
        print(f"[Checker] Loading IFC file: {ifc_file_path}")
        model = ifcopenshell.open(ifc_file_path)

        # 2. 加载 IDS 规范
        print(f"[Checker] Loading IDS file: {ids_file_path}")
        my_ids = ids.open(ids_file_path)

        # 验证 IDS 是否有效
        if not my_ids or not my_ids.specifications:
            result["message"] = "IDS 文件无效或不包含任何规格说明"
            return result

        print(f"[Checker] Found {len(my_ids.specifications)} specifications")

        # 3. 执行校验
        print(f"[Checker] Running validation...")
        my_ids.validate(model)

        # 4. 生成报告文件（让 ifctester 自己处理序列化）
        # JSON 报告
        json_file = os.path.join(output_dir, "report.json")
        print(f"[Checker] Generating JSON report: {json_file}")
        json_reporter = reporter.Json(my_ids)
        json_reporter.report()
        json_reporter.to_file(json_file)

        # HTML 报告
        html_file = os.path.join(output_dir, "report.html")
        print(f"[Checker] Generating HTML report: {html_file}")
        try:
            html_reporter = reporter.Html(my_ids)
            html_reporter.report()
            html_reporter.to_file(html_file)
            if not use_temp_dir:
                result["html_report_path"] = html_file
        except Exception as e:
            print(f"[Warning] HTML report generation failed: {e}")

        # BCF 报告（可选）
        bcf_file = os.path.join(output_dir, "report.bcf")
        try:
            bcf_reporter = reporter.Bcf(my_ids)
            bcf_reporter.report()
            bcf_reporter.to_file(bcf_file)
        except Exception as e:
            print(f"[Warning] BCF report generation failed: {e}")

        # 5. 读取 JSON 报告内容（已经是纯 JSON 格式，完全可序列化）
        print(f"[Checker] Reading JSON report...")
        with open(json_file, 'r', encoding='utf-8') as f:
            report_data = json.load(f)

        # 验证 JSON 数据
        print(f"[Checker] JSON report loaded, validating...")
        json.dumps(report_data)  # 确保可以序列化
        print(f"[Checker] JSON validation passed")

        result["report_data"] = report_data

        # 如果指定了输出目录，保留 JSON 文件路径
        if not use_temp_dir:
            result["json_report_path"] = json_file

        # 6. 计算摘要统计
        total_specs = len(my_ids.specifications)
        passed_specs = 0
        failed_specs = 0
        total_failed_entities = 0

        for spec in my_ids.specifications:
            if spec.failed_entities:
                failed_specs += 1
                total_failed_entities += len(spec.failed_entities)
            else:
                passed_specs += 1

        result["summary"] = {
            "total_specs": total_specs,
            "passed_specs": passed_specs,
            "failed_specs": failed_specs,
            "total_failed_entities": total_failed_entities
        }

        result["success"] = True
        result["message"] = "检查完成"

        if failed_specs > 0:
            result["message"] = f"发现 {failed_specs} 个不合规规格，共 {total_failed_entities} 个构件错误"
        else:
            result["message"] = "所有构件均符合 IDS 要求"

        print(f"[Checker] Validation complete: {result['message']}")

    except Exception as e:
        result["message"] = f"检查过程中发生错误: {str(e)}"
        import traceback
        traceback.print_exc()

    finally:
        # 7. 清理临时目录（如果使用了临时目录）
        if use_temp_dir:
            try:
                import shutil
                shutil.rmtree(output_dir)
                print(f"[Checker] Cleaned up temp directory: {output_dir}")
            except Exception as e:
                print(f"[Warning] Failed to clean up temp directory: {e}")

    return result


def find_file_by_extension(directory, extension):
    """在指定目录查找第一个匹配后缀的文件"""
    if not os.path.exists(directory):
        return None
    for file in os.listdir(directory):
        if file.lower().endswith(extension.lower()):
            return os.path.join(directory, file)
    return None


def run_ids_checker():
    """
    独立运行模式 - 从固定目录读取文件进行测试

    输入目录：
    - input/ids_parser/: 存放 .ids 文件
    - input/ifc_parser/: 存放 .ifc 文件

    输出目录：
    - output/checker/IFCtest/: 生成报告文件
    """
    # 获取当前脚本所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 定义输入目录
    input_ids_dir = os.path.join(base_dir, 'input', 'ids_parser')
    input_ifc_dir = os.path.join(base_dir, 'input', 'ifc_parser')

    # 定义输出目录
    output_dir = os.path.join(base_dir, 'output', 'checker', 'IFCtest')

    # 创建输出文件夹
    if not os.path.exists(output_dir):
        print(f"[Init] 创建输出目录: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

    # 自动发现输入文件
    ids_path = find_file_by_extension(input_ids_dir, '.ids')
    ifc_path = find_file_by_extension(input_ifc_dir, '.ifc')

    if not ids_path:
        print(f"[Error] 在 {input_ids_dir} 中未找到 .ids 文件。")
        return
    if not ifc_path:
        print(f"[Error] 在 {input_ifc_dir} 中未找到 .ifc 文件。")
        return

    print(f"[Input] IDS 文件: {ids_path}")
    print(f"[Input] IFC 文件: {ifc_path}")

    # 执行检查
    print("-" * 50)
    print("开始执行 IDS 合规性检查...")

    result = check_ifc_against_ids(ids_path, ifc_path, output_dir)

    print("-" * 50)
    if result["success"]:
        print(f"✅ {result['message']}")
        print(f"摘要: 总规格 {result['summary']['total_specs']} | "
              f"通过 {result['summary']['passed_specs']} | "
              f"失败 {result['summary']['failed_specs']}")
        if result["html_report_path"]:
            print(f"HTML 报告: {result['html_report_path']}")
        if result["json_report_path"]:
            print(f"JSON 报告: {result['json_report_path']}")
    else:
        print(f"❌ {result['message']}")


if __name__ == "__main__":
    run_ids_checker()