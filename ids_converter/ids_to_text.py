"""
IDS to Natural Language Generator

将解析后的 IDS 数据生成中英文双语自然语言描述。

核心功能:
1. 使用模板生成自然语言描述
2. 支持中文、英文、双语输出
3. 处理所有 facet 类型和约束条件

作者: IDS-Agent
版本: 1.0.0
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import yaml

from .ids_parser import IDSParser, parse_ids_file, parse_ids_content


# =============================================================================
# 模板加载器
# =============================================================================

class TemplateLoader:
    """加载和管理语言模板"""

    def __init__(self, template_dir: Optional[str] = None):
        """
        初始化模板加载器

        Args:
            template_dir: 模板目录路径，默认为当前目录下的 templates
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"
        self.template_dir = Path(template_dir)
        self._cache: Dict[str, Dict] = {}

    def load(self, language: str) -> Dict:
        """
        加载指定语言的模板

        Args:
            language: 语言代码 ("zh" 或 "en")

        Returns:
            模板字典
        """
        if language in self._cache:
            return self._cache[language]

        template_file = self.template_dir / f"{language}.yaml"
        if not template_file.exists():
            raise FileNotFoundError(f"Template file not found: {template_file}")

        with open(template_file, 'r', encoding='utf-8') as f:
            template = yaml.safe_load(f)

        self._cache[language] = template
        return template


# =============================================================================
# 文本生成器
# =============================================================================

class IDSToTextGenerator:
    """
    将解析后的 IDS 数据生成自然语言描述

    支持三种输出模式:
    - "zh": 仅中文
    - "en": 仅英文
    - "both": 双语输出
    """

    def __init__(self, template_dir: Optional[str] = None):
        """
        初始化生成器

        Args:
            template_dir: 模板目录路径
        """
        self.template_loader = TemplateLoader(template_dir)
        self.parser = IDSParser()

    def generate(
        self,
        ids_data: Dict[str, Any],
        language: str = "both"
    ) -> str:
        """
        生成自然语言描述

        Args:
            ids_data: 解析后的 IDS 数据
            language: 输出语言 ("zh", "en", 或 "both")

        Returns:
            自然语言描述文本
        """
        if language == "both":
            zh_text = self.generate_zh(ids_data)
            en_text = self.generate_en(ids_data)
            return f"{zh_text}\n\n{'=' * 60}\n\n=== English Version ===\n\n{en_text}"
        elif language == "zh":
            return self.generate_zh(ids_data)
        elif language == "en":
            return self.generate_en(ids_data)
        else:
            raise ValueError(f"Unsupported language: {language}")

    def generate_zh(self, ids_data: Dict[str, Any]) -> str:
        """生成中文描述"""
        template = self.template_loader.load("zh")
        return self._generate_text(ids_data, template, "zh")

    def generate_en(self, ids_data: Dict[str, Any]) -> str:
        """生成英文描述"""
        template = self.template_loader.load("en")
        return self._generate_text(ids_data, template, "en")

    def _generate_text(
        self,
        ids_data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> str:
        """
        生成文本的核心方法

        Args:
            ids_data: IDS 数据
            template: 语言模板
            language: 语言代码

        Returns:
            生成的文本
        """
        lines = []

        # 标题
        if language == "zh":
            lines.append("=== IDS 审查规范说明 ===")
        else:
            lines.append("=== IDS Specification Description ===")
        lines.append("")

        # 基本信息
        info_text = self._generate_info(ids_data.get("info", {}), template)
        lines.extend(info_text)
        lines.append("")

        # 规范列表
        specifications = ids_data.get("specifications", [])
        for i, spec in enumerate(specifications, 1):
            spec_text = self._generate_specification(spec, template, language, i)
            lines.extend(spec_text)
            if i < len(specifications):
                lines.append("")

        return "\n".join(lines)

    def _generate_info(
        self,
        info: Dict[str, str],
        template: Dict
    ) -> List[str]:
        """生成基本信息部分"""
        lines = []
        info_template = template.get("info", {})
        fields_template = info_template.get("fields", {})

        lines.append(info_template.get("header", "【基本信息】"))

        # 按照固定顺序输出字段
        field_order = ["title", "copyright", "version", "date", "author", "description"]

        for field in field_order:
            if field in info and info[field]:
                field_name = fields_template.get(field, field)
                lines.append(f"{field_name}: {info[field]}")

        return lines

    def _generate_specification(
        self,
        spec: Dict[str, Any],
        template: Dict,
        language: str,
        index: int
    ) -> List[str]:
        """生成规范部分"""
        lines = []
        spec_template = template.get("specification", {})

        # 规范标题
        header = spec_template.get("header", "【规范 {index}】{name}")
        lines.append(header.format(index=index, name=spec.get("name", "")))

        # IFC 版本
        if spec.get("ifcVersion"):
            lines.append(f"{spec_template.get('ifc_version', 'IFC Version')}: {spec['ifcVersion']}")

        # 描述
        if spec.get("description"):
            lines.append(f"{spec_template.get('description', 'Description')}: {spec['description']}")

        # 说明
        if spec.get("instructions"):
            lines.append(f"{spec_template.get('instructions', 'Instructions')}: {spec['instructions']}")

        # 标识符
        if spec.get("identifier"):
            lines.append(f"{spec_template.get('identifier', 'Identifier')}: {spec['identifier']}")

        lines.append("")

        # 适用范围
        if "applicability" in spec:
            app_text = self._generate_applicability(
                spec["applicability"],
                template,
                language
            )
            lines.extend(app_text)
            lines.append("")

        # 要求
        if "requirements" in spec:
            req_text = self._generate_requirements(
                spec["requirements"],
                template,
                language
            )
            lines.extend(req_text)

        return lines

    def _generate_applicability(
        self,
        applicability: Dict[str, Any],
        template: Dict,
        language: str
    ) -> List[str]:
        """生成适用范围部分"""
        lines = []
        app_template = template.get("applicability", {})

        lines.append(app_template.get("header", "Applicability") + ":")

        # 基数约束
        if applicability.get("minOccurs") or applicability.get("maxOccurs"):
            min_occurs = applicability.get("minOccurs", "1")
            max_occurs = applicability.get("maxOccurs", "unbounded")
            if language == "zh":
                lines.append(f"  基数: {min_occurs}..{max_occurs}")
            else:
                lines.append(f"  Cardinality: {min_occurs}..{max_occurs}")

        # Facets
        facets = applicability.get("facets", [])
        for facet_type, facet_data in facets:
            facet_text = self._generate_facet(facet_type, facet_data, template, language)
            lines.append(f"  • {facet_text}")

        return lines

    def _generate_requirements(
        self,
        requirements: Dict[str, Any],
        template: Dict,
        language: str
    ) -> List[str]:
        """生成要求部分"""
        lines = []
        req_template = template.get("requirements", {})

        lines.append(req_template.get("header", "Requirements") + ":")

        # 描述
        if requirements.get("description"):
            lines.append(f"  {req_template.get('description', 'Description')}: {requirements['description']}")

        # Facets
        facets = requirements.get("facets", [])
        for i, (facet_type, facet_data) in enumerate(facets, 1):
            facet_text = self._generate_facet_requirement(
                facet_type,
                facet_data,
                template,
                language,
                i
            )
            lines.extend(facet_text)

        return lines

    def _generate_facet(
        self,
        facet_type: str,
        facet_data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> str:
        """
        生成适用范围中的 facet 描述

        Args:
            facet_type: facet 类型
            facet_data: facet 数据
            template: 语言模板
            language: 语言代码

        Returns:
            facet 描述文本
        """
        facet_templates = template.get("facet_types", {})

        if facet_type == "entity":
            return self._generate_entity_facet(facet_data, template, language)
        elif facet_type == "property":
            return self._generate_property_facet(facet_data, template, language)
        elif facet_type == "attribute":
            return self._generate_attribute_facet(facet_data, template, language)
        elif facet_type == "classification":
            return self._generate_classification_facet(facet_data, template, language)
        elif facet_type == "material":
            return self._generate_material_facet(facet_data, template, language)
        elif facet_type == "partOf":
            return self._generate_partof_facet(facet_data, template, language)
        else:
            return f"Unknown facet: {facet_type}"

    def _generate_facet_requirement(
        self,
        facet_type: str,
        facet_data: Dict[str, Any],
        template: Dict,
        language: str,
        index: int
    ) -> List[str]:
        """
        生成要求中的 facet 描述

        Args:
            facet_type: facet 类型
            facet_data: facet 数据
            template: 语言模板
            language: 语言代码
            index: 序号

        Returns:
            facet 描述文本列表
        """
        lines = []

        # 获取 facet 标题
        facet_template = template.get(facet_type, {})
        title = facet_template.get("title", f"{facet_type.capitalize()} Requirement")

        lines.append(f"  {index}. {title}")

        # 根据类型生成详细描述
        if facet_type == "entity":
            details = self._generate_entity_details(facet_data, template, language)
        elif facet_type == "property":
            details = self._generate_property_details(facet_data, template, language)
        elif facet_type == "attribute":
            details = self._generate_attribute_details(facet_data, template, language)
        elif facet_type == "classification":
            details = self._generate_classification_details(facet_data, template, language)
        elif facet_type == "material":
            details = self._generate_material_details(facet_data, template, language)
        elif facet_type == "partOf":
            details = self._generate_partof_details(facet_data, template, language)
        else:
            details = []

        lines.extend(details)
        return lines

    def _generate_entity_facet(
        self,
        data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> str:
        """生成 entity facet 简短描述"""
        entity_template = template.get("entity", {})

        if language == "zh":
            name = data.get("name", {}).get("simpleValue", "")
            if name:
                return f"适用于 {name} 类型的所有构件"
            return "实体类型未指定"
        else:
            name = data.get("name", {}).get("simpleValue", "")
            if name:
                return f"Applies to all {name} type entities"
            return "Entity type not specified"

    def _generate_entity_details(
        self,
        data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> List[str]:
        """生成 entity facet 详细描述"""
        lines = []
        entity_template = template.get("entity", {})

        # 实体类型
        name = data.get("name", {})
        if name:
            name_value = self._get_value_string(name, template, language)
            lines.append(f"     - {entity_template.get('name', 'Entity Type')}: {name_value}")

        # 预定义类型
        predefined_type = data.get("predefinedType", {})
        if predefined_type:
            type_value = self._get_value_string(predefined_type, template, language)
            lines.append(f"     - {entity_template.get('predefined_type', 'Predefined Type')}: {type_value}")

        # 说明
        if data.get("instructions"):
            lines.append(f"     - {template.get('specification', {}).get('instructions', 'Instructions')}: {data['instructions']}")

        return lines

    def _generate_property_facet(
        self,
        data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> str:
        """生成 property facet 简短描述"""
        pset = data.get("propertySet", {}).get("simpleValue", "")
        name = data.get("baseName", {}).get("simpleValue", "")

        if language == "zh":
            if pset and name:
                return f"属性 {pset}.{name}"
            return "属性未指定"
        else:
            if pset and name:
                return f"Property {pset}.{name}"
            return "Property not specified"

    def _generate_property_details(
        self,
        data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> List[str]:
        """生成 property facet 详细描述"""
        lines = []
        prop_template = template.get("property", {})

        # 属性集
        pset = data.get("propertySet", {})
        if pset:
            pset_value = self._get_value_string(pset, template, language)
            lines.append(f"     - {prop_template.get('property_set', 'Property Set')}: {pset_value}")

        # 属性名
        base_name = data.get("baseName", {})
        if base_name:
            name_value = self._get_value_string(base_name, template, language)
            lines.append(f"     - {prop_template.get('property_name', 'Property Name')}: {name_value}")

        # 数据类型
        if data.get("dataType"):
            lines.append(f"     - {prop_template.get('data_type', 'Data Type')}: {data['dataType']}")

        # 属性值
        value = data.get("value", {})
        if value:
            value_str = self._get_value_string(value, template, language)
            lines.append(f"     - {prop_template.get('value', 'Value')}: {value_str}")

        # URI
        if data.get("uri"):
            lines.append(f"     - {prop_template.get('uri', 'URI')}: {data['uri']}")

        # 基数约束
        if data.get("cardinality"):
            cardinality = self._translate_cardinality(data["cardinality"], template)
            lines.append(f"     - {prop_template.get('cardinality', 'Cardinality')}: {cardinality}")

        # 说明
        if data.get("instructions"):
            lines.append(f"     - {template.get('specification', {}).get('instructions', 'Instructions')}: {data['instructions']}")

        return lines

    def _generate_attribute_facet(
        self,
        data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> str:
        """生成 attribute facet 简短描述"""
        name = data.get("name", {}).get("simpleValue", "")

        if language == "zh":
            if name:
                return f"属性 {name}"
            return "属性未指定"
        else:
            if name:
                return f"Attribute {name}"
            return "Attribute not specified"

    def _generate_attribute_details(
        self,
        data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> List[str]:
        """生成 attribute facet 详细描述"""
        lines = []
        attr_template = template.get("attribute", {})

        # 属性名
        name = data.get("name", {})
        if name:
            name_value = self._get_value_string(name, template, language)
            lines.append(f"     - {attr_template.get('name', 'Attribute Name')}: {name_value}")

        # 属性值
        value = data.get("value", {})
        if value:
            value_str = self._get_value_string(value, template, language)
            lines.append(f"     - {attr_template.get('value', 'Value')}: {value_str}")

        # 基数约束
        if data.get("cardinality"):
            cardinality = self._translate_cardinality(data["cardinality"], template)
            lines.append(f"     - {attr_template.get('cardinality', 'Cardinality')}: {cardinality}")

        # 说明
        if data.get("instructions"):
            lines.append(f"     - {template.get('specification', {}).get('instructions', 'Instructions')}: {data['instructions']}")

        return lines

    def _generate_classification_facet(
        self,
        data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> str:
        """生成 classification facet 简短描述"""
        system = data.get("system", {}).get("simpleValue", "")
        value = data.get("value", {}).get("simpleValue", "")

        if language == "zh":
            if system and value:
                return f"分类 {system}: {value}"
            elif value:
                return f"分类 {value}"
            return "分类未指定"
        else:
            if system and value:
                return f"Classification {system}: {value}"
            elif value:
                return f"Classification {value}"
            return "Classification not specified"

    def _generate_classification_details(
        self,
        data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> List[str]:
        """生成 classification facet 详细描述"""
        lines = []
        class_template = template.get("classification", {})

        # 分类系统
        system = data.get("system", {})
        if system:
            system_value = self._get_value_string(system, template, language)
            lines.append(f"     - {class_template.get('system', 'Classification System')}: {system_value}")

        # 分类值
        value = data.get("value", {})
        if value:
            value_str = self._get_value_string(value, template, language)
            lines.append(f"     - {class_template.get('value', 'Classification Value')}: {value_str}")

        # URI
        if data.get("uri"):
            lines.append(f"     - {class_template.get('uri', 'URI')}: {data['uri']}")

        # 基数约束
        if data.get("cardinality"):
            cardinality = self._translate_cardinality(data["cardinality"], template)
            lines.append(f"     - {class_template.get('cardinality', 'Cardinality')}: {cardinality}")

        # 说明
        if data.get("instructions"):
            lines.append(f"     - {template.get('specification', {}).get('instructions', 'Instructions')}: {data['instructions']}")

        return lines

    def _generate_material_facet(
        self,
        data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> str:
        """生成 material facet 简短描述"""
        value = data.get("value", {}).get("simpleValue", "")

        if language == "zh":
            if value:
                return f"材料 {value}"
            return "材料未指定"
        else:
            if value:
                return f"Material {value}"
            return "Material not specified"

    def _generate_material_details(
        self,
        data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> List[str]:
        """生成 material facet 详细描述"""
        lines = []
        mat_template = template.get("material", {})

        # 材料名称
        value = data.get("value", {})
        if value:
            value_str = self._get_value_string(value, template, language)
            lines.append(f"     - {mat_template.get('value', 'Material Name')}: {value_str}")

        # URI
        if data.get("uri"):
            lines.append(f"     - {mat_template.get('uri', 'URI')}: {data['uri']}")

        # 基数约束
        if data.get("cardinality"):
            cardinality = self._translate_cardinality(data["cardinality"], template)
            lines.append(f"     - {mat_template.get('cardinality', 'Cardinality')}: {cardinality}")

        # 说明
        if data.get("instructions"):
            lines.append(f"     - {template.get('specification', {}).get('instructions', 'Instructions')}: {data['instructions']}")

        return lines

    def _generate_partof_facet(
        self,
        data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> str:
        """生成 partOf facet 简短描述"""
        entity = data.get("entity", {}).get("name", {}).get("simpleValue", "")
        relation = data.get("relation", "")

        if language == "zh":
            if entity:
                relation_str = f" ({relation})" if relation else ""
                return f"属于 {entity}{relation_str}"
            return "组成关系未指定"
        else:
            if entity:
                relation_str = f" ({relation})" if relation else ""
                return f"Part of {entity}{relation_str}"
            return "Part of relationship not specified"

    def _generate_partof_details(
        self,
        data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> List[str]:
        """生成 partOf facet 详细描述"""
        lines = []
        partof_template = template.get("partOf", {})

        # 关系类型
        if data.get("relation"):
            lines.append(f"     - {partof_template.get('relation', 'Relation Type')}: {data['relation']}")

        # 关联实体
        entity = data.get("entity", {})
        if entity:
            entity_name = entity.get("name", {})
            if entity_name:
                name_value = self._get_value_string(entity_name, template, language)
                lines.append(f"     - {partof_template.get('entity', 'Related Entity')}: {name_value}")

            predefined_type = entity.get("predefinedType", {})
            if predefined_type:
                type_value = self._get_value_string(predefined_type, template, language)
                entity_template = template.get("entity", {})
                lines.append(f"     - {entity_template.get('predefined_type', 'Predefined Type')}: {type_value}")

        # 基数约束
        if data.get("cardinality"):
            cardinality = self._translate_cardinality(data["cardinality"], template)
            lines.append(f"     - {partof_template.get('cardinality', 'Cardinality')}: {cardinality}")

        # 说明
        if data.get("instructions"):
            lines.append(f"     - {template.get('specification', {}).get('instructions', 'Instructions')}: {data['instructions']}")

        return lines

    def _get_value_string(
        self,
        value_data: Dict[str, Any],
        template: Dict,
        language: str
    ) -> str:
        """
        获取值的字符串表示

        Args:
            value_data: 值数据 (simpleValue 或 restriction)
            template: 语言模板
            language: 语言代码

        Returns:
            值的字符串表示
        """
        # simpleValue
        if "simpleValue" in value_data:
            return value_data["simpleValue"]

        # restriction
        if "restriction" in value_data:
            return self._generate_restriction_string(value_data["restriction"], template, language)

        return ""

    def _generate_restriction_string(
        self,
        restriction: Dict[str, Any],
        template: Dict,
        language: str
    ) -> str:
        """
        生成约束条件的字符串描述

        Args:
            restriction: 约束数据
            template: 语言模板
            language: 语言代码

        Returns:
            约束描述字符串
        """
        constraint_templates = template.get("constraint_templates", {})
        parts = []

        # enumeration
        if "enumeration" in restriction:
            values = restriction["enumeration"]
            template_str = constraint_templates.get("enumeration", "Must be one of: {values}")
            separator = template.get("general", {}).get("separator", ", ")
            parts.append(template_str.format(values=separator.join(values)))

        # pattern
        if "pattern" in restriction:
            template_str = constraint_templates.get("pattern", "Must match pattern: {value}")
            parts.append(template_str.format(value=restriction["pattern"]))

        # range (minInclusive + maxInclusive)
        if "minInclusive" in restriction and "maxInclusive" in restriction:
            template_str = constraint_templates.get("range", "Must be between {min} and {max}")
            parts.append(template_str.format(
                min=restriction["minInclusive"],
                max=restriction["maxInclusive"]
            ))
        else:
            # minInclusive
            if "minInclusive" in restriction:
                template_str = constraint_templates.get("min_inclusive", "Must be >= {value}")
                parts.append(template_str.format(value=restriction["minInclusive"]))

            # maxInclusive
            if "maxInclusive" in restriction:
                template_str = constraint_templates.get("max_inclusive", "Must be <= {value}")
                parts.append(template_str.format(value=restriction["maxInclusive"]))

        # minExclusive
        if "minExclusive" in restriction:
            template_str = constraint_templates.get("min_exclusive", "Must be > {value}")
            parts.append(template_str.format(value=restriction["minExclusive"]))

        # maxExclusive
        if "maxExclusive" in restriction:
            template_str = constraint_templates.get("max_exclusive", "Must be < {value}")
            parts.append(template_str.format(value=restriction["maxExclusive"]))

        # minLength
        if "minLength" in restriction:
            template_str = constraint_templates.get("min_length", "Length >= {value}")
            parts.append(template_str.format(value=restriction["minLength"]))

        # maxLength
        if "maxLength" in restriction:
            template_str = constraint_templates.get("max_length", "Length <= {value}")
            parts.append(template_str.format(value=restriction["maxLength"]))

        # length
        if "length" in restriction:
            template_str = constraint_templates.get("length", "Length = {value}")
            parts.append(template_str.format(value=restriction["length"]))

        # totalDigits
        if "totalDigits" in restriction:
            template_str = constraint_templates.get("total_digits", "Total digits = {value}")
            parts.append(template_str.format(value=restriction["totalDigits"]))

        # fractionDigits
        if "fractionDigits" in restriction:
            template_str = constraint_templates.get("fraction_digits", "Fraction digits = {value}")
            parts.append(template_str.format(value=restriction["fractionDigits"]))

        if not parts:
            return ""

        and_str = template.get("general", {}).get("and", "and")
        return f" {and_str} ".join(parts)

    def _translate_cardinality(
        self,
        cardinality: str,
        template: Dict
    ) -> str:
        """
        翻译基数约束

        Args:
            cardinality: 基数值 (required, prohibited, optional)
            template: 语言模板

        Returns:
            翻译后的基数描述
        """
        prop_template = template.get("property", {})
        cardinality_values = prop_template.get("cardinality_values", {})

        return cardinality_values.get(cardinality, cardinality)

    def generate_from_file(
        self,
        file_path: str,
        language: str = "both"
    ) -> str:
        """
        从 IDS 文件生成自然语言描述

        Args:
            file_path: IDS 文件路径
            language: 输出语言

        Returns:
            自然语言描述
        """
        ids_data = self.parser.parse_file(file_path)
        return self.generate(ids_data, language)

    def generate_from_content(
        self,
        xml_content: str,
        language: str = "both"
    ) -> str:
        """
        从 IDS XML 内容生成自然语言描述

        Args:
            xml_content: IDS XML 内容
            language: 输出语言

        Returns:
            自然语言描述
        """
        ids_data = self.parser.parse(xml_content)
        return self.generate(ids_data, language)


# =============================================================================
# CLI 入口
# =============================================================================

def main():
    """命令行入口"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="IDS to Natural Language Generator"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input IDS file path"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--lang", "-l",
        choices=["zh", "en", "both"],
        default="both",
        help="Output language (default: both)"
    )

    args = parser.parse_args()

    try:
        generator = IDSToTextGenerator()
        result = generator.generate_from_file(args.input, args.lang)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"Output written to: {args.output}")
        else:
            print(result)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()