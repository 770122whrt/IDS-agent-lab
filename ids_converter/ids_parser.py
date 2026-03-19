"""
IDS XML Parser

将 IDS XML 文件解析为结构化 Python 字典。

核心功能:
1. 解析 IDS XML 文件内容
2. 处理 6 种 facet 类型 (entity, property, attribute, classification, material, partOf)
3. 处理各种约束条件 (enumeration, pattern, range 等)

作者: IDS-Agent
版本: 1.0.0
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from lxml import etree


# =============================================================================
# 命名空间定义
# =============================================================================

NAMESPACES = {
    'ids': 'http://standards.buildingsmart.org/IDS',
    'xs': 'http://www.w3.org/2001/XMLSchema',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}


# =============================================================================
# 自定义异常
# =============================================================================

class IDSParseError(Exception):
    """IDS 解析错误"""
    pass


# =============================================================================
# 核心解析类
# =============================================================================

class IDSParser:
    """
    将 IDS XML 解析为结构化 Python 字典

    支持解析:
    - info 元信息
    - specifications 规范列表
    - 6 种 facet 类型: entity, property, attribute, classification, material, partOf
    - 各种约束条件: enumeration, pattern, minInclusive, maxInclusive 等
    """

    def __init__(self):
        """初始化解析器"""
        pass

    def parse(self, xml_content: str) -> Dict[str, Any]:
        """
        解析 IDS XML 字符串

        Args:
            xml_content: IDS XML 内容字符串

        Returns:
            结构化的 IDS 数据字典

        Raises:
            IDSParseError: 解析失败
        """
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
            return self._parse_root(root)
        except etree.XMLSyntaxError as e:
            raise IDSParseError(f"Invalid XML syntax: {e}") from e
        except Exception as e:
            raise IDSParseError(f"Failed to parse IDS XML: {e}") from e

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析 IDS XML 文件

        Args:
            file_path: IDS XML 文件路径

        Returns:
            结构化的 IDS 数据字典

        Raises:
            IDSParseError: 解析失败
            FileNotFoundError: 文件不存在
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"IDS file not found: {file_path}")

        try:
            with open(path, 'rb') as f:
                tree = etree.parse(f)
                root = tree.getroot()
                return self._parse_root(root)
        except etree.XMLSyntaxError as e:
            raise IDSParseError(f"Invalid XML syntax in file: {e}") from e
        except Exception as e:
            raise IDSParseError(f"Failed to parse IDS file: {e}") from e

    def _parse_root(self, root: etree._Element) -> Dict[str, Any]:
        """
        解析根节点

        Args:
            root: XML 根节点

        Returns:
            结构化的 IDS 数据
        """
        result = {
            "info": {},
            "specifications": []
        }

        # 解析 info
        info_elem = root.find('ids:info', NAMESPACES)
        if info_elem is not None:
            result["info"] = self._parse_info(info_elem)

        # 解析 specifications
        specs_elem = root.find('ids:specifications', NAMESPACES)
        if specs_elem is not None:
            for spec_elem in specs_elem.findall('ids:specification', NAMESPACES):
                result["specifications"].append(self._parse_specification(spec_elem))

        return result

    def _parse_info(self, info_elem: etree._Element) -> Dict[str, str]:
        """
        解析 info 节点

        Args:
            info_elem: info 元素

        Returns:
            info 数据字典
        """
        info = {}

        # title - 必填
        title_elem = info_elem.find('ids:title', NAMESPACES)
        if title_elem is not None:
            info["title"] = title_elem.text or ""

        # copyright - 可选
        copyright_elem = info_elem.find('ids:copyright', NAMESPACES)
        if copyright_elem is not None:
            info["copyright"] = copyright_elem.text or ""

        # version - 可选
        version_elem = info_elem.find('ids:version', NAMESPACES)
        if version_elem is not None:
            info["version"] = version_elem.text or ""

        # date - 可选
        date_elem = info_elem.find('ids:date', NAMESPACES)
        if date_elem is not None:
            info["date"] = date_elem.text or ""

        # author - 可选
        author_elem = info_elem.find('ids:author', NAMESPACES)
        if author_elem is not None:
            info["author"] = author_elem.text or ""

        # description - 可选
        description_elem = info_elem.find('ids:description', NAMESPACES)
        if description_elem is not None:
            info["description"] = description_elem.text or ""

        return info

    def _parse_specification(self, spec_elem: etree._Element) -> Dict[str, Any]:
        """
        解析 specification 节点

        Args:
            spec_elem: specification 元素

        Returns:
            specification 数据字典
        """
        spec = {}

        # 属性
        spec["name"] = spec_elem.get("name", "")
        spec["ifcVersion"] = spec_elem.get("ifcVersion", "")

        # 可选属性
        if spec_elem.get("description"):
            spec["description"] = spec_elem.get("description")
        if spec_elem.get("instructions"):
            spec["instructions"] = spec_elem.get("instructions")
        if spec_elem.get("identifier"):
            spec["identifier"] = spec_elem.get("identifier")

        # applicability - 必填
        app_elem = spec_elem.find('ids:applicability', NAMESPACES)
        if app_elem is not None:
            spec["applicability"] = self._parse_applicability(app_elem)

        # requirements - 可选
        req_elem = spec_elem.find('ids:requirements', NAMESPACES)
        if req_elem is not None:
            spec["requirements"] = self._parse_requirements(req_elem)

        return spec

    def _parse_applicability(self, app_elem: etree._Element) -> Dict[str, Any]:
        """
        解析 applicability 节点

        Args:
            app_elem: applicability 元素

        Returns:
            applicability 数据字典
        """
        app = {}

        # 属性
        if app_elem.get("minOccurs"):
            app["minOccurs"] = app_elem.get("minOccurs")
        if app_elem.get("maxOccurs"):
            app["maxOccurs"] = app_elem.get("maxOccurs")

        # 解析各种 facet
        facets = []

        # entity
        for entity_elem in app_elem.findall('ids:entity', NAMESPACES):
            facets.append(("entity", self._parse_entity(entity_elem)))

        # partOf
        for partof_elem in app_elem.findall('ids:partOf', NAMESPACES):
            facets.append(("partOf", self._parse_partof(partof_elem)))

        # classification
        for class_elem in app_elem.findall('ids:classification', NAMESPACES):
            facets.append(("classification", self._parse_classification(class_elem)))

        # attribute
        for attr_elem in app_elem.findall('ids:attribute', NAMESPACES):
            facets.append(("attribute", self._parse_attribute(attr_elem)))

        # property
        for prop_elem in app_elem.findall('ids:property', NAMESPACES):
            facets.append(("property", self._parse_property(prop_elem)))

        # material
        for mat_elem in app_elem.findall('ids:material', NAMESPACES):
            facets.append(("material", self._parse_material(mat_elem)))

        app["facets"] = facets
        return app

    def _parse_requirements(self, req_elem: etree._Element) -> Dict[str, Any]:
        """
        解析 requirements 节点

        Args:
            req_elem: requirements 元素

        Returns:
            requirements 数据字典
        """
        req = {}

        # 属性
        if req_elem.get("description"):
            req["description"] = req_elem.get("description")

        # 解析各种 facet
        facets = []

        # entity
        for entity_elem in req_elem.findall('ids:entity', NAMESPACES):
            facets.append(("entity", self._parse_entity(entity_elem, is_requirement=True)))

        # partOf
        for partof_elem in req_elem.findall('ids:partOf', NAMESPACES):
            facets.append(("partOf", self._parse_partof(partof_elem, is_requirement=True)))

        # classification
        for class_elem in req_elem.findall('ids:classification', NAMESPACES):
            facets.append(("classification", self._parse_classification(class_elem, is_requirement=True)))

        # attribute
        for attr_elem in req_elem.findall('ids:attribute', NAMESPACES):
            facets.append(("attribute", self._parse_attribute(attr_elem, is_requirement=True)))

        # property
        for prop_elem in req_elem.findall('ids:property', NAMESPACES):
            facets.append(("property", self._parse_property(prop_elem, is_requirement=True)))

        # material
        for mat_elem in req_elem.findall('ids:material', NAMESPACES):
            facets.append(("material", self._parse_material(mat_elem, is_requirement=True)))

        req["facets"] = facets
        return req

    def _parse_entity(
        self,
        entity_elem: etree._Element,
        is_requirement: bool = False
    ) -> Dict[str, Any]:
        """
        解析 entity 节点

        Args:
            entity_elem: entity 元素
            is_requirement: 是否在 requirements 中

        Returns:
            entity 数据字典
        """
        entity = {}

        # requirement 特有属性
        if is_requirement and entity_elem.get("instructions"):
            entity["instructions"] = entity_elem.get("instructions")

        # name
        name_elem = entity_elem.find('ids:name', NAMESPACES)
        if name_elem is not None:
            entity["name"] = self._parse_ids_value(name_elem)

        # predefinedType
        predefined_elem = entity_elem.find('ids:predefinedType', NAMESPACES)
        if predefined_elem is not None:
            entity["predefinedType"] = self._parse_ids_value(predefined_elem)

        return entity

    def _parse_property(
        self,
        prop_elem: etree._Element,
        is_requirement: bool = False
    ) -> Dict[str, Any]:
        """
        解析 property 节点

        Args:
            prop_elem: property 元素
            is_requirement: 是否在 requirements 中

        Returns:
            property 数据字典
        """
        prop = {}

        # dataType 属性
        if prop_elem.get("dataType"):
            prop["dataType"] = prop_elem.get("dataType")

        # requirement 特有属性
        if is_requirement:
            if prop_elem.get("uri"):
                prop["uri"] = prop_elem.get("uri")
            if prop_elem.get("cardinality"):
                prop["cardinality"] = prop_elem.get("cardinality")
            if prop_elem.get("instructions"):
                prop["instructions"] = prop_elem.get("instructions")

        # propertySet
        pset_elem = prop_elem.find('ids:propertySet', NAMESPACES)
        if pset_elem is not None:
            prop["propertySet"] = self._parse_ids_value(pset_elem)

        # baseName
        base_name_elem = prop_elem.find('ids:baseName', NAMESPACES)
        if base_name_elem is not None:
            prop["baseName"] = self._parse_ids_value(base_name_elem)

        # value
        value_elem = prop_elem.find('ids:value', NAMESPACES)
        if value_elem is not None:
            prop["value"] = self._parse_ids_value(value_elem)

        return prop

    def _parse_attribute(
        self,
        attr_elem: etree._Element,
        is_requirement: bool = False
    ) -> Dict[str, Any]:
        """
        解析 attribute 节点

        Args:
            attr_elem: attribute 元素
            is_requirement: 是否在 requirements 中

        Returns:
            attribute 数据字典
        """
        attr = {}

        # requirement 特有属性
        if is_requirement:
            if attr_elem.get("cardinality"):
                attr["cardinality"] = attr_elem.get("cardinality")
            if attr_elem.get("instructions"):
                attr["instructions"] = attr_elem.get("instructions")

        # name
        name_elem = attr_elem.find('ids:name', NAMESPACES)
        if name_elem is not None:
            attr["name"] = self._parse_ids_value(name_elem)

        # value
        value_elem = attr_elem.find('ids:value', NAMESPACES)
        if value_elem is not None:
            attr["value"] = self._parse_ids_value(value_elem)

        return attr

    def _parse_classification(
        self,
        class_elem: etree._Element,
        is_requirement: bool = False
    ) -> Dict[str, Any]:
        """
        解析 classification 节点

        Args:
            class_elem: classification 元素
            is_requirement: 是否在 requirements 中

        Returns:
            classification 数据字典
        """
        classification = {}

        # requirement 特有属性
        if is_requirement:
            if class_elem.get("uri"):
                classification["uri"] = class_elem.get("uri")
            if class_elem.get("cardinality"):
                classification["cardinality"] = class_elem.get("cardinality")
            if class_elem.get("instructions"):
                classification["instructions"] = class_elem.get("instructions")

        # system
        system_elem = class_elem.find('ids:system', NAMESPACES)
        if system_elem is not None:
            classification["system"] = self._parse_ids_value(system_elem)

        # value
        value_elem = class_elem.find('ids:value', NAMESPACES)
        if value_elem is not None:
            classification["value"] = self._parse_ids_value(value_elem)

        return classification

    def _parse_material(
        self,
        mat_elem: etree._Element,
        is_requirement: bool = False
    ) -> Dict[str, Any]:
        """
        解析 material 节点

        Args:
            mat_elem: material 元素
            is_requirement: 是否在 requirements 中

        Returns:
            material 数据字典
        """
        material = {}

        # requirement 特有属性
        if is_requirement:
            if mat_elem.get("uri"):
                material["uri"] = mat_elem.get("uri")
            if mat_elem.get("cardinality"):
                material["cardinality"] = mat_elem.get("cardinality")
            if mat_elem.get("instructions"):
                material["instructions"] = mat_elem.get("instructions")

        # value
        value_elem = mat_elem.find('ids:value', NAMESPACES)
        if value_elem is not None:
            material["value"] = self._parse_ids_value(value_elem)

        return material

    def _parse_partof(
        self,
        partof_elem: etree._Element,
        is_requirement: bool = False
    ) -> Dict[str, Any]:
        """
        解析 partOf 节点

        Args:
            partof_elem: partOf 元素
            is_requirement: 是否在 requirements 中

        Returns:
            partOf 数据字典
        """
        partof = {}

        # relation 属性
        if partof_elem.get("relation"):
            partof["relation"] = partof_elem.get("relation")

        # requirement 特有属性
        if is_requirement:
            if partof_elem.get("cardinality"):
                partof["cardinality"] = partof_elem.get("cardinality")
            if partof_elem.get("instructions"):
                partof["instructions"] = partof_elem.get("instructions")

        # entity (嵌套)
        entity_elem = partof_elem.find('ids:entity', NAMESPACES)
        if entity_elem is not None:
            partof["entity"] = self._parse_entity(entity_elem)

        return partof

    def _parse_ids_value(self, parent_elem: etree._Element) -> Dict[str, Any]:
        """
        解析 idsValue 类型节点

        idsValue 是一个选择类型:
        - simpleValue: 简单字符串
        - xs:restriction: 复杂约束

        Args:
            parent_elem: 父元素

        Returns:
            idsValue 数据字典
        """
        result = {}

        # simpleValue
        simple_elem = parent_elem.find('ids:simpleValue', NAMESPACES)
        if simple_elem is not None:
            result["simpleValue"] = simple_elem.text or ""
            return result

        # xs:restriction
        restriction_elem = parent_elem.find('xs:restriction', NAMESPACES)
        if restriction_elem is not None:
            result["restriction"] = self._parse_restriction(restriction_elem)
            return result

        return result

    def _parse_restriction(self, restriction_elem: etree._Element) -> Dict[str, Any]:
        """
        解析 xs:restriction 节点

        Args:
            restriction_elem: restriction 元素

        Returns:
            restriction 数据字典
        """
        restriction = {}

        # base 属性
        if restriction_elem.get("base"):
            restriction["base"] = restriction_elem.get("base")

        # enumeration
        enum_values = []
        for enum_elem in restriction_elem.findall('xs:enumeration', NAMESPACES):
            if enum_elem.get("value"):
                enum_values.append(enum_elem.get("value"))
        if enum_values:
            restriction["enumeration"] = enum_values

        # pattern
        pattern_elem = restriction_elem.find('xs:pattern', NAMESPACES)
        if pattern_elem is not None and pattern_elem.get("value"):
            restriction["pattern"] = pattern_elem.get("value")

        # minInclusive
        min_inc_elem = restriction_elem.find('xs:minInclusive', NAMESPACES)
        if min_inc_elem is not None and min_inc_elem.get("value"):
            restriction["minInclusive"] = min_inc_elem.get("value")

        # maxInclusive
        max_inc_elem = restriction_elem.find('xs:maxInclusive', NAMESPACES)
        if max_inc_elem is not None and max_inc_elem.get("value"):
            restriction["maxInclusive"] = max_inc_elem.get("value")

        # minExclusive
        min_exc_elem = restriction_elem.find('xs:minExclusive', NAMESPACES)
        if min_exc_elem is not None and min_exc_elem.get("value"):
            restriction["minExclusive"] = min_exc_elem.get("value")

        # maxExclusive
        max_exc_elem = restriction_elem.find('xs:maxExclusive', NAMESPACES)
        if max_exc_elem is not None and max_exc_elem.get("value"):
            restriction["maxExclusive"] = max_exc_elem.get("value")

        # minLength
        min_len_elem = restriction_elem.find('xs:minLength', NAMESPACES)
        if min_len_elem is not None and min_len_elem.get("value"):
            restriction["minLength"] = min_len_elem.get("value")

        # maxLength
        max_len_elem = restriction_elem.find('xs:maxLength', NAMESPACES)
        if max_len_elem is not None and max_len_elem.get("value"):
            restriction["maxLength"] = max_len_elem.get("value")

        # length
        length_elem = restriction_elem.find('xs:length', NAMESPACES)
        if length_elem is not None and length_elem.get("value"):
            restriction["length"] = length_elem.get("value")

        # totalDigits
        total_digits_elem = restriction_elem.find('xs:totalDigits', NAMESPACES)
        if total_digits_elem is not None and total_digits_elem.get("value"):
            restriction["totalDigits"] = total_digits_elem.get("value")

        # fractionDigits
        fraction_digits_elem = restriction_elem.find('xs:fractionDigits', NAMESPACES)
        if fraction_digits_elem is not None and fraction_digits_elem.get("value"):
            restriction["fractionDigits"] = fraction_digits_elem.get("value")

        return restriction


# =============================================================================
# 便捷函数
# =============================================================================

def parse_ids_file(file_path: str) -> Dict[str, Any]:
    """
    解析 IDS 文件

    Args:
        file_path: IDS 文件路径

    Returns:
        结构化的 IDS 数据字典
    """
    parser = IDSParser()
    return parser.parse_file(file_path)


def parse_ids_content(xml_content: str) -> Dict[str, Any]:
    """
    解析 IDS XML 内容

    Args:
        xml_content: IDS XML 内容字符串

    Returns:
        结构化的 IDS 数据字典
    """
    parser = IDSParser()
    return parser.parse(xml_content)


# =============================================================================
# 测试入口
# =============================================================================

if __name__ == "__main__":
    import sys

    # 测试文件路径
    current_dir = Path(__file__).parent
    ids_file = current_dir / "case1.ids"

    print("=" * 60)
    print("IDS XML Parser Test")
    print("=" * 60)
    print()

    if not ids_file.exists():
        print(f"Error: IDS file not found: {ids_file}")
        sys.exit(1)

    try:
        parser = IDSParser()
        result = parser.parse_file(str(ids_file))

        print("Parsed successfully!")
        print()
        print("Info:")
        for key, value in result.get("info", {}).items():
            print(f"  {key}: {value}")

        print()
        print(f"Specifications: {len(result.get('specifications', []))}")

        for i, spec in enumerate(result.get("specifications", []), 1):
            print(f"\n  Specification {i}:")
            print(f"    Name: {spec.get('name')}")
            print(f"    IFC Version: {spec.get('ifcVersion')}")

            # Applicability
            app = spec.get("applicability", {})
            print(f"    Applicability facets: {len(app.get('facets', []))}")
            for facet_type, facet_data in app.get("facets", []):
                print(f"      - {facet_type}: {facet_data}")

            # Requirements
            req = spec.get("requirements", {})
            print(f"    Requirements facets: {len(req.get('facets', []))}")
            for facet_type, facet_data in req.get("facets", []):
                print(f"      - {facet_type}: {facet_data}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)