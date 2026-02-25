import os
import sys
import json
import ifcopenshell
from ifctester import ids, reporter

def find_file_by_extension(directory, extension):
    """在指定目录查找第一个匹配后缀的文件"""
    if not os.path.exists(directory):
        return None
    for file in os.listdir(directory):
        if file.lower().endswith(extension.lower()):
            return os.path.join(directory, file)
    return None

def run_ids_checker():
    # =========================================================================
    # 1. 路径配置 (Path Configuration)
    # =========================================================================
    # 获取当前脚本所在的最外层目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义输入目录
    input_ids_dir = os.path.join(base_dir, 'input', 'ids_parser')
    input_ifc_dir = os.path.join(base_dir, 'input', 'ifc_parser')
    
    # 定义输出目录 (output/checker/IFCtest)
    output_base = os.path.join(base_dir, 'output', 'checker')
    output_dir = os.path.join(output_base, 'IFCtest')
    
    # 创建输出文件夹 (如果不存在)
    if not os.path.exists(output_dir):
        print(f"[Init] 创建输出目录: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

    # =========================================================================
    # 2. 自动发现输入文件 (File Discovery)
    # =========================================================================
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

    # =========================================================================
    # 3. 核心校验逻辑 (Core Logic based on model_checker_service.py)
    # =========================================================================
    print("-" * 50)
    print("开始加载与校验...")

    try:
        # 3.1 加载 IFC 模型
        # 对应 model_checker_service.py: model = ifcopenshell.open(ifc_file_path)
        model = ifcopenshell.open(ifc_path)
        print(f"[Load] IFC 模型加载成功 ({ifc_path})")

        # 3.2 加载 IDS 规范
        # 对应 model_checker_service.py: ids_obj = ids.open(ids_file_path)
        my_ids = ids.open(ids_path)
        print(f"[Load] IDS 规范加载成功 ({ids_path})")

        # 验证 IDS 是否有效
        if not my_ids or not my_ids.specifications:
            print("[Error] IDS 文件无效或不包含任何规格说明。")
            return

        # 3.3 执行校验
        # 对应 model_checker_service.py: ids_obj.validate(model)
        # 这一步 ifctester 会遍历所有规格，检查适用性并验证需求
        my_ids.validate(model)
        print("[Validate] 校验完成。")

    except Exception as e:
        print(f"[Fatal Error] 校验过程中发生错误: {e}")
        return

    # =========================================================================
    # 4. 生成报告 (Reporting)
    # =========================================================================
    print("-" * 50)
    print(f"正在生成报告至: {output_dir}")

    # 4.1 HTML 报告 (可视化)
    # 对应 model_checker_service.py: html_reporter = reporter.Html(ids_obj)
    html_file = os.path.join(output_dir, "report.html")
    try:
        html_reporter = reporter.Html(my_ids)
        html_reporter.report()
        html_reporter.to_file(html_file)
        print(f"[Report] HTML 报告已生成: {html_file}")
    except Exception as e:
        print(f"[Warning] HTML 报告生成失败: {e}")

    # 4.2 JSON 报告 (数据化)
    json_file = os.path.join(output_dir, "report.json")
    try:
        json_reporter = reporter.Json(my_ids)
        report_data = json_reporter.report()

        # 自定义转换函数：处理 ifcopenshell 的实体对象
        def ifc_json_serializer(obj):
            # 如果是 ifcopenshell 的实体实例
            if hasattr(obj, "get_info"):
                try:
                    # 尝试返回该实体的字符串表示（如 #123=IfcWall...）
                    return str(obj)
                except:
                    return f"ID: {getattr(obj, 'id', 'Unknown')}"
            # 其他无法识别的对象转为字符串
            return str(obj)

        with open(json_file, 'w', encoding='utf-8') as f:
            # 使用 default 参数调用自定义序列化函数
            json.dump(
                report_data, 
                f, 
                indent=4, 
                ensure_ascii=False, 
                default=ifc_json_serializer
            )
            
        print(f"[Report] JSON 报告已成功美化并保存: {json_file}")
    except Exception as e:
        print(f"[Warning] JSON 报告生成失败: {e}")

    # 4.3 BCF 报告 (协作格式 - 可选)
    bcf_file = os.path.join(output_dir, "report.bcf")
    try:
        bcf_reporter = reporter.Bcf(my_ids)
        bcf_reporter.report()
        bcf_reporter.to_file(bcf_file)
        print(f"[Report] BCF 报告已生成: {bcf_file}")
    except Exception as e:
        print(f"[Warning] BCF 报告生成失败: {e}")

    # =========================================================================
    # 5. 最终状态摘要
    # =========================================================================
    # 检查是否有失败的实体
    failed_specs = [spec for spec in my_ids.specifications if spec.failed_entities]
    
    print("-" * 50)
    if failed_specs:
        print(f"❌ 校验失败 (FAILED)")
        print(f"发现 {len(failed_specs)} 个不合规的规格说明:")
        for spec in failed_specs:
            print(f"   - {spec.name}: {len(spec.failed_entities)} 个构件错误")
    else:
        print(f"✅ 校验通过 (PASSED)")
        print("所有构件均符合 IDS 要求。")

if __name__ == "__main__":
    run_ids_checker()