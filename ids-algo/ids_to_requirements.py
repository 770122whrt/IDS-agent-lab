"""
将IDS XML转换为自然语言需求描述
专门为pipeline设计的转换器
"""
import sys
from pathlib import Path

# 添加ids_converter到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from ids_converter.ids_parser import IDSParser


def convert_ids_to_requirements(ids_file_path: str) -> str:
    """
    将IDS文件转换为自然语言需求描述

    Args:
        ids_file_path: IDS文件路径

    Returns:
        自然语言需求描述文本
    """
    parser = IDSParser()
    ids_data = parser.parse_file(ids_file_path)

    requirements = []

    for spec in ids_data.get('specifications', []):
        spec_name = spec.get('name', 'Unnamed')
        description = spec.get('description', '')

        # 提取applicability信息
        applicability = spec.get('applicability', {})
        entity_name = ""
        predefined_type = ""

        # 获取entity facet
        entity_facet = applicability.get('entity', {})
        if entity_facet:
            name_value = entity_facet.get('name', {})
            if isinstance(name_value, dict):
                entity_name = name_value.get('simpleValue', '')

            predefined_value = entity_facet.get('predefinedType', {})
            if isinstance(predefined_value, dict):
                predefined_type = predefined_value.get('simpleValue', '')

        # 构建基础需求描述
        if entity_name:
            if predefined_type:
                base_req = f"All {entity_name} elements with predefined type {predefined_type}"
            else:
                base_req = f"All {entity_name} elements"
        else:
            base_req = f"Elements for {spec_name}"

        # 添加描述（如果有）
        if description:
            # 清理描述，移除换行和多余空格
            clean_desc = ' '.join(description.split())
            if len(clean_desc) > 200:
                clean_desc = clean_desc[:200] + "..."
            base_req += f". {clean_desc}"

        # 提取requirements信息
        requirements_data = spec.get('requirements', {})
        req_parts = []

        # partOf requirements
        partof_list = requirements_data.get('partOf', [])
        if not isinstance(partof_list, list):
            partof_list = [partof_list] if partof_list else []

        for partof in partof_list:
            if isinstance(partof, dict):
                relation = partof.get('relation', '')
                entity = partof.get('entity', {})
                if isinstance(entity, dict):
                    entity_name_val = entity.get('name', {})
                    if isinstance(entity_name_val, dict):
                        parent_entity = entity_name_val.get('simpleValue', '')
                    elif isinstance(entity_name_val, str):
                        parent_entity = entity_name_val
                    else:
                        parent_entity = str(entity_name_val)

                    if parent_entity:
                        req_parts.append(f"must be part of {parent_entity}")

        # attribute requirements
        attribute_list = requirements_data.get('attribute', [])
        if not isinstance(attribute_list, list):
            attribute_list = [attribute_list] if attribute_list else []

        for attr in attribute_list:
            if isinstance(attr, dict):
                attr_name_val = attr.get('name', {})
                if isinstance(attr_name_val, dict):
                    attr_name = attr_name_val.get('simpleValue', '')
                elif isinstance(attr_name_val, str):
                    attr_name = attr_name_val
                else:
                    attr_name = str(attr_name_val)

                cardinality = attr.get('cardinality', 'optional')
                if attr_name:
                    if cardinality == 'required':
                        req_parts.append(f"must have {attr_name} attribute")
                    else:
                        req_parts.append(f"should have {attr_name} attribute")

        # property requirements
        property_list = requirements_data.get('property', [])
        if not isinstance(property_list, list):
            property_list = [property_list] if property_list else []

        for prop in property_list:
            if isinstance(prop, dict):
                pset_val = prop.get('propertySet', {})
                if isinstance(pset_val, dict):
                    pset = pset_val.get('simpleValue', '')
                else:
                    pset = str(pset_val)

                name_val = prop.get('baseName', {})
                if isinstance(name_val, dict):
                    prop_name = name_val.get('simpleValue', '')
                else:
                    prop_name = str(name_val)

                cardinality = prop.get('cardinality', 'optional')
                if pset and prop_name:
                    if cardinality == 'required':
                        req_parts.append(f"must have property {pset}.{prop_name}")
                    else:
                        req_parts.append(f"should have property {pset}.{prop_name}")

        # material requirements
        material_list = requirements_data.get('material', [])
        if not isinstance(material_list, list):
            material_list = [material_list] if material_list else []

        for mat in material_list:
            if isinstance(mat, dict):
                mat_val = mat.get('value', {})
                if isinstance(mat_val, dict):
                    mat_name = mat_val.get('simpleValue', '')
                else:
                    mat_name = str(mat_val)

                cardinality = mat.get('cardinality', 'optional')
                if mat_name:
                    if cardinality == 'required':
                        req_parts.append(f"must be made of {mat_name}")
                    else:
                        req_parts.append(f"should be made of {mat_name}")

        # 组合完整需求
        if req_parts:
            full_req = base_req + " " + ", ".join(req_parts) + "."
        else:
            full_req = base_req + "."

        requirements.append(full_req)

    return "\n\n".join(requirements)


if __name__ == "__main__":
    # 测试
    ids_path = Path(__file__).parent.parent / "ids_converter" / "20250317023029_IFCBridge-IDS-xml.ids"
    result = convert_ids_to_requirements(str(ids_path))
    print(result)
    print(f"\n\nTotal length: {len(result)} characters")
