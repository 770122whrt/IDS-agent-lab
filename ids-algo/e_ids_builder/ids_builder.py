"""
LLM-Driven IDS Builder for converting classified facets into standard IDS format

Uses LLM's semantic understanding to intelligently group facets and assign them to 
appropriate IDS specification slots, then mechanically converts to standard format.
"""

import logging
import re
from typing import Dict, Any, List, Optional


from d_constrains.data_structures import MappedFacet
from d_constrains import (
    ValueRestriction,
    RestrictionType,
    ConstraintExtractor,   
)
from .data_structures import (
    SpecificationSlot, 
    ApplicabilitySlot, 
    RequirementsSlot,
)

from prompts import select_prompt

logger = logging.getLogger(__name__)

class IdsBuilder:
    """
    LLM-Driven IDS specifications builder.

    Uses LLM's semantic understanding to intelligently group and assign facets,
    then mechanically converts to standard IDS format.
    """

    def __init__(
        self,
        constraint_extractor: ConstraintExtractor,
        llm_client=None,
    ):
        self.constraint_extractor = constraint_extractor
        self.llm_client = llm_client

# -------------------------------------------------------------------------
    # 核心工具：确保符合 type IdsValue = string | ComplexRestriction
    # -------------------------------------------------------------------------
    def _build_ids_value(self, simple_value: Any, restriction: Optional[Dict]) -> Any:
        """
        解包函数：
        1. 如果有由 ConstraintExtractor 生成的复杂约束(restriction)，返回该字典。
        2. 否则直接返回 simple_value (字符串/数字/布尔)。
        3. 绝不返回 {"simpleValue": ..., "restriction": ...} 这种包裹对象。
        """
        # 检查 restriction 是否为有效的非空字典
        if restriction and isinstance(restriction, dict) and len(restriction) > 0:
            # 排除仅包含 base 的情况(视具体逻辑而定，通常有内容的字典即为约束)
            return restriction
        
        # 返回原始值，如果原始值也是 None，最终在 JSON 中表现为 null (或被后续清理)
        return simple_value
    

    async def build_ids_specifications(
        self,
        mapped_facets: List[MappedFacet],
        ifc_version: str = "IFC4",
        original_text: str = "",
        include_metadata: bool = True,
        #pipeline_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build IDS specifications using LLM-driven slot assignment approach.

        Args:
            mapped_facets: List of facets that have been mapped to IFC terminology
            ifc_version: IFC version to use
            original_text: Original user input text for context
            pipeline_context: Complete pipeline memory context for enhanced semantic understanding
        """
        try:
            logger.info(
                f"Building IDS specifications for {len(mapped_facets)} mapped facets"
            )

            # 1. Prepare context for LLM analysis
            context = self._prepare_llm_context(
                mapped_facets, original_text#, pipeline_context
            )

            # 2. Use LLM for self-validating slot assignment
            if self.llm_client and original_text:
                slots = await self._llm_slot_assignment(context)
            else:
                logger.warning("No LLM client available, using fallback logic")
                logger.exception(e)
                slots = self._fallback_slot_assignment(mapped_facets)

            # 3. Mechanical conversion to IDS format
            specifications = self._convert_slots_to_ids(
                slots, mapped_facets, ifc_version
            )

            result = {
                "specifications": specifications,
            }

            # 4. Generate metadata
            if include_metadata:
                metadata = {
                    "total_extracted": len(specifications),
                    "total_normalized": len(
                        [f for f in mapped_facets if f.confidence > 0.7]
                    ),
                    "ifc_version": ifc_version,
                    "slot_count": len(slots),
                }
                result["metadata"] = metadata
                result["error"] = None

            logger.info(
                f"Successfully built {len(specifications)} IDS specifications from {len(slots)} slots"
            )
            return result

        except Exception as e:
            logger.error(f"IDS specification building failed: {str(e)}")
            fallback_result = self._generate_basic_fallback(mapped_facets, ifc_version)
            # Simple fallback
            return fallback_result
        
    def _prepare_llm_context(
        self,
        mapped_facets: List[MappedFacet],
        original_text: str,
        #pipeline_context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """准备LLM所需的完整上下文"""
        return {
            "original_text": original_text,
            #"pipeline_context": pipeline_context or {},
            "mapped_facets": [
                {
                    "facet_id": f"facet_{i}",
                    "facet_type": facet.facet_type,
                    "original_text": facet.original_text,
                    "mapped_name": facet.mapped_name,
                    "confidence": facet.confidence,
                    "property_set": getattr(facet, "property_set", None),
                    "entity_name": getattr(facet, "entity_name", None),
                    "constraints": self._format_constraints_for_prompt(facet.constraints),
                    "additional_data": facet.additional_data or {},
                }
                for i, facet in enumerate(mapped_facets)
            ],
        }

    def _format_constraints_for_prompt(
        self, constraints: List[ValueRestriction]
    ) -> str:
        """将约束格式化为Prompt中的可读格式"""
        if not constraints: return ""
        constraint_descriptions = []
        for constraint in constraints:
            if constraint.restriction_type == RestrictionType.BOUNDS:
                bounds = constraint.restriction
                if bounds.min_value is not None and bounds.max_value is not None:
                    constraint_descriptions.append(
                        f"Range: {bounds.min_value}-{bounds.max_value} {bounds.unit or ''}"
                    )
                elif bounds.min_value is not None:
                    constraint_descriptions.append(
                        f"Minimum: {bounds.min_value} {bounds.unit or ''}"
                    )
                elif bounds.max_value is not None:
                    constraint_descriptions.append(
                        f"Maximum: {bounds.max_value} {bounds.unit or ''}"
                    )
            elif constraint.restriction_type == RestrictionType.ENUMERATION:
                enum = constraint.restriction
                constraint_descriptions.append(f"Options: {', '.join(enum.values)}")
            elif constraint.restriction_type == RestrictionType.PATTERN:
                pattern = constraint.restriction
                constraint_descriptions.append(f"Pattern: {pattern.pattern}")

        return "; ".join(constraint_descriptions)

    async def _llm_slot_assignment(
        self, context: Dict[str, Any]
    ) -> List[SpecificationSlot]:
        """使用LLM进行槽分配"""
        prompt = self._build_self_validating_prompt(context)

        messages = [{"role": "user", "content": prompt}]
        response = await self.llm_client.generate(messages)

        # 提取响应内容
        response_content = (
            response.get("content", "") if isinstance(response, dict) else str(response)
        )

        # 解析槽
        slots = self._parse_llm_slots(response_content)

        # 验证槽
        validated_slots = self._validate_slots(slots, context["mapped_facets"])

        return validated_slots

    def _build_self_validating_prompt(self, context: Dict[str, Any]) -> str:
        """构造详尽的 prompt 给 LLM，包含：说明、APPLICABILITY vs REQUIREMENTS 的区别、分配规则、输出模板与自检项。"""
        facets_description = self._format_facets_for_prompt(context["mapped_facets"])
        prompt_template = select_prompt("ids_builder")
        
        return prompt_template.format(
            original_text=context['original_text'],
            facets_description=facets_description
        )

    def _format_facets_for_prompt(self, mapped_facets: List[Dict[str, Any]]) -> str:
        """将Facets格式化为Prompt中的可读格式"""
        facet_descriptions = []

        for facet_data in mapped_facets:
            description = f"""
            Facet ID: {facet_data['facet_id']}
            Type: {facet_data['facet_type']}
            Original Text: "{facet_data['original_text']}"
            Mapped Term: {facet_data['mapped_name']}
            Confidence: {facet_data['confidence']:.3f}"""

            if facet_data.get("property_set"):
                description += f"\nProperty Set: {facet_data['property_set']}"

            if facet_data.get("entity_name"):
                description += f"\nAssociated Entity: {facet_data['entity_name']}"

            if facet_data.get("constraints"):
                description += f"\nConstraints: {facet_data['constraints']}"

            facet_descriptions.append(description)

        return "\n".join(facet_descriptions)

    def _parse_llm_slots(self, response_text: str) -> List[SpecificationSlot]:
        """容错的槽解析 - 尽力而为"""
        slots = []

        # 多种模式尝试
        patterns = [
            r"SPECIFICATION_START(.*?)SPECIFICATION_END",
            r"SPEC_START(.*?)SPEC_END",
            r"---START---(.*?)---END---",
        ]

        matches = []
        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if matches:
                break

        if not matches:
            logger.warning("No specification blocks found in LLM response")
            return []

        for match in matches:
            try:
                slot = self._parse_single_slot(match)
                if slot:
                    slots.append(slot)
            except Exception as e:
                logger.warning(f"Slot parsing failed: {e}, skipping")
                continue

        logger.info(f"Successfully parsed {len(slots)} specification slots")
        return slots

    def _parse_single_slot(self, slot_text: str) -> Optional[SpecificationSlot]:
        """解析单个槽 - 容错处理"""
        slot_data = {}

        # 灵活的键值对提取 行级别解析：跳过空行与注释（以 # 开头）
        for line in slot_text.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # 支持多种分隔符 :, =, ->
            separators = [":", "=", "->"]
            for sep in separators:
                if sep in line:
                    key, value = line.split(sep, 1)
                    key = key.strip().lower()
                    value = value.strip()

                    # --- 新增解析逻辑 START ---
                    if key == "target_ifc_version":
                        # 复用 parse_facet_list 的清理逻辑
                        slot_data["ifc_version"] = self._parse_facet_list(value) # 复用列表解析逻辑即可
                        # 注意：这里 _parse_facet_list 可能会过滤掉非 'facet_' 开头的，
                        # 建议写一个简单的 split 函数，或者修改 _parse_facet_list
                        # 更简单的写法：
                        cleaned = re.sub(r'[\[\]"\']', "", value)
                        if cleaned.lower() not in ["empty", "none"]:
                             slot_data["ifc_version"] = [v.strip() for v in re.split(r'[, ]+', cleaned) if v.strip()]
                    
                    # 键名包含 facet_ids，调用 _parse_facet_list
                    elif "facet_ids" in key:
                        value = self._parse_facet_list(value)
                    elif key == "applicability_entity_facet_id":
                        # 单个facet_id
                        value = value.strip()

                    slot_data[key] = value
                    break

        return self._create_slot_from_data(slot_data)

    def _parse_facet_list(self, value_str: str) -> List[str]:
        """灵活解析facet列表"""
        if not value_str or value_str.lower() in ["empty", "none", "[]", "[empty]"]:
            return []

        # 移除括号和引号
        cleaned = re.sub(r'[\[\]"\']', "", value_str)

        # 尝试多种分隔符
        for sep in [",", ";", " ", "|"]:
            if sep in cleaned:
                result = [f.strip() for f in cleaned.split(sep) if f.strip()]
                # 过滤掉非facet_id格式的内容
                return [f for f in result if f.startswith("facet_")]

        # 单个值
        cleaned = cleaned.strip()
        return [cleaned] if cleaned and cleaned.startswith("facet_") else []

    def _create_slot_from_data(
        self, slot_data: Dict[str, Any]
    ) -> Optional[SpecificationSlot]:
        """从解析的数据创建SpecificationSlot对象"""
        try:
            # 创建ApplicabilitySlot
            applicability = ApplicabilitySlot(
                entity_facet_id=slot_data.get("applicability_entity_facet_id", ""),
                predefined_type=slot_data.get("applicability_predefined_type", ""),
                property_facet_ids=slot_data.get(
                    "applicability_property_facet_ids", []
                ),
                material_facet_ids=slot_data.get(
                    "applicability_material_facet_ids", []
                ),
                classification_facet_ids=slot_data.get(
                    "applicability_classification_facet_ids", []
                ),
                attribute_facet_ids=slot_data.get(
                    "applicability_attribute_facet_ids", []
                ),
                partof_facet_ids=slot_data.get("applicability_partof_facet_ids", []),
            )

            # 创建RequirementsSlot
            requirements = RequirementsSlot(
                property_facet_ids=slot_data.get("requirements_property_facet_ids", []),
                material_facet_ids=slot_data.get("requirements_material_facet_ids", []),
                classification_facet_ids=slot_data.get(
                    "requirements_classification_facet_ids", []
                ),
                attribute_facet_ids=slot_data.get(
                    "requirements_attribute_facet_ids", []
                ),
                partof_facet_ids=slot_data.get("requirements_partof_facet_ids", []),
            )

            # 创建完整的SpecificationSlot
            slot = SpecificationSlot(
                name=slot_data.get("name", "Unnamed Specification"),
                description=slot_data.get("description", ""),
                applicability=applicability,
                requirements=requirements,
                reasoning=slot_data.get("reasoning", ""),
                # --- 注入新数据 ---
                ifc_version=slot_data.get("ifc_version", [])
            )

            return slot

        except Exception as e:
            logger.error(f"Failed to create slot from data: {e}")
            return None

    def _validate_slots(
        self, slots: List[SpecificationSlot], mapped_facets: List[Dict[str, Any]]
    ) -> List[SpecificationSlot]:
        """验证槽内容的合理性"""
        validated_slots = []
        used_facets = set()
        available_facet_ids = {f["facet_id"] for f in mapped_facets}
        available_entities = {
            f["facet_id"]: f["mapped_name"]
            for f in mapped_facets
            if f["facet_type"] == "entity"
        }

        for slot in slots:
            validation_errors = []

            # 验证entity facet
            if slot.applicability.entity_facet_id not in available_entities:
                validation_errors.append(
                    f"Invalid entity facet: {slot.applicability.entity_facet_id}"
                )

            # 收集所有使用的facet_ids
            all_facet_ids = []
            all_facet_ids.append(slot.applicability.entity_facet_id)
            all_facet_ids.extend(slot.applicability.property_facet_ids)
            all_facet_ids.extend(slot.applicability.material_facet_ids)
            all_facet_ids.extend(slot.applicability.classification_facet_ids)
            all_facet_ids.extend(slot.applicability.attribute_facet_ids)
            all_facet_ids.extend(slot.applicability.partof_facet_ids)
            all_facet_ids.extend(slot.requirements.property_facet_ids)
            all_facet_ids.extend(slot.requirements.material_facet_ids)
            all_facet_ids.extend(slot.requirements.classification_facet_ids)
            all_facet_ids.extend(slot.requirements.attribute_facet_ids)
            all_facet_ids.extend(slot.requirements.partof_facet_ids)

            # 验证facet_ids
            for facet_id in all_facet_ids:
                if facet_id in used_facets:
                    validation_errors.append(f"Facet {facet_id} already used")
                elif facet_id not in available_facet_ids:
                    validation_errors.append(f"Invalid facet_id: {facet_id}")
                else:
                    used_facets.add(facet_id)

            if validation_errors:
                logger.warning(
                    f"Slot validation errors for '{slot.name}': {validation_errors}"
                )
                # 可以选择跳过或尝试修复
                continue

            validated_slots.append(slot)

        logger.info(f"Validated {len(validated_slots)} out of {len(slots)} slots")
        return validated_slots

    def _convert_slots_to_ids(
        self,
        slots: List[SpecificationSlot],
        mapped_facets: List[MappedFacet],
        ifc_version: str,# 这里的 ifc_version 变成了 "fallback_version"
    ) -> List[Dict[str, Any]]:
        """将槽机械转换为标准IDS格式"""
        specifications = []
        facet_lookup = {f"facet_{i}": facet for i, facet in enumerate(mapped_facets)}

        for slot in slots:
            try:
                # 优先使用从文本中提取的版本，如果没有提取到，则使用默认传入的版本
                final_versions = slot.ifc_version if slot.ifc_version else [ifc_version]
                # 获取主要实体
                entity_facet = facet_lookup.get(slot.applicability.entity_facet_id)
                if not entity_facet:
                    logger.warning(
                        f"No entity facet found for {slot.applicability.entity_facet_id}"
                    )
                    continue

                spec = {
                    "name": slot.name,
                    "ifcVersion": final_versions,  # <--- 使用动态版本
                    "description": slot.description if slot.description else None,
                    "instructions": None,
                    "applicability": self._build_applicability_from_slot(
                        slot.applicability, facet_lookup
                    ),
                    "requirements": self._build_requirements_from_slot(
                        slot.requirements, facet_lookup
                    ),
                }

                specifications.append(spec)

            except Exception as e:
                logger.error(f"Failed to convert slot '{slot.name}': {e}")
                continue

        return specifications

    def _build_applicability_from_slot(
        self, app_slot: ApplicabilitySlot, facet_lookup: Dict[str, MappedFacet]
    ) -> Dict[str, Any]:
        """从槽构建Applicability部分"""
        # 获取主要实体
        entity_facet = facet_lookup.get(app_slot.entity_facet_id)
        if not entity_facet:
            raise ValueError(f"Entity facet not found: {app_slot.entity_facet_id}")

        applicability = {
            "minOccurs": "1",
            "maxOccurs": "unbounded",
            "entity": {
            ##------------新增解包逻辑------------##
            # 也可以不解包直接改架构
                "name": self._build_ids_value(entity_facet.mapped_name, None),
                "predefinedType": None,
            },
            "partOf": None,
            "classification": None,
            "attribute": None,
            "property": None,
            "material": None,
        }
        ##------------新增解包逻辑------------##
        # 添加predefinedType
        if app_slot.predefined_type:
            # 同样使用解包逻辑，防止未来扩展问题
            applicability["entity"]["predefinedType"] = self._build_ids_value(app_slot.predefined_type, None)

        # 处理各类applicability facets
        self._add_facets_to_section(
            applicability, "property", app_slot.property_facet_ids, facet_lookup
        )
        self._add_facets_to_section(
            applicability, "material", app_slot.material_facet_ids, facet_lookup
        )
        self._add_facets_to_section(
            applicability,
            "classification",
            app_slot.classification_facet_ids,
            facet_lookup,
        )
        self._add_facets_to_section(
            applicability, "attribute", app_slot.attribute_facet_ids, facet_lookup
        )
        self._add_facets_to_section(
            applicability, "partOf", app_slot.partof_facet_ids, facet_lookup
        )

        return applicability

    def _build_requirements_from_slot(
        self, req_slot: RequirementsSlot, facet_lookup: Dict[str, MappedFacet]
    ) -> Dict[str, Any]:
        """从槽构建Requirements部分"""
        requirements = {
            "description": None,
            "entity": None,
            "partOf": None,
            "classification": None,
            "attribute": None,
            "property": None,
            "material": None,
        }

        # 处理各类requirements facets
        self._add_facets_to_section(
            requirements, "property", req_slot.property_facet_ids, facet_lookup
        )
        self._add_facets_to_section(
            requirements, "material", req_slot.material_facet_ids, facet_lookup
        )
        self._add_facets_to_section(
            requirements,
            "classification",
            req_slot.classification_facet_ids,
            facet_lookup,
        )
        self._add_facets_to_section(
            requirements, "attribute", req_slot.attribute_facet_ids, facet_lookup
        )
        self._add_facets_to_section(
            requirements, "partOf", req_slot.partof_facet_ids, facet_lookup
        )

        return requirements

    def _add_facets_to_section(
        self,
        section: Dict[str, Any],
        section_name: str,
        facet_ids: List[str],
        facet_lookup: Dict[str, MappedFacet],
    ):
        """将facets添加到指定section"""
        if not facet_ids:return

        section_requirements = []
        for facet_id in facet_ids:
            facet = facet_lookup.get(facet_id)
            if not facet:
                logger.warning(f"Facet not found: {facet_id}")
                continue

            # 根据section类型调用对应的构建方法
            req = None
            if section_name == "property":
                req = self._build_property_requirement(facet)
            elif section_name == "material":
                req = self._build_material_requirement(facet)
            elif section_name == "classification":
                req = self._build_classification_requirement(facet)
            elif section_name == "attribute":
                req = self._build_attribute_requirement(facet)
            elif section_name == "partOf":
                req = self._build_partof_requirement(facet)
            else:
                logger.warning(f"Unknown section type: {section_name}")
                continue

            if req:
                section_requirements.append(req)

        if section_requirements:
            section[section_name] = section_requirements

    def _fallback_slot_assignment(
        self, mapped_facets: List[MappedFacet]
    ) -> List[SpecificationSlot]:
        """当LLM不可用时的后备槽分配"""
        logger.info("Using fallback slot assignment logic")

        # 简单的默认分组：每个entity一个槽
        entity_facets = [f for f in mapped_facets if f.facet_type == "entity"]

        if not entity_facets:
            # 如果没有entity，创建一个通用槽
            return [self._create_generic_slot(mapped_facets)]

        slots = []
        for i, entity_facet in enumerate(entity_facets):
            # 为每个entity创建一个槽
            applicability = ApplicabilitySlot(
                entity_facet_id=f"facet_{mapped_facets.index(entity_facet)}"
            )
            requirements = RequirementsSlot()

            # 将剩余facets放入requirements
            for j, facet in enumerate(mapped_facets):
                if facet.facet_type != "entity":
                    facet_id = f"facet_{j}"
                    if facet.facet_type == "property":
                        requirements.property_facet_ids.append(facet_id)
                    elif facet.facet_type == "material":
                        requirements.material_facet_ids.append(facet_id)
                    elif facet.facet_type == "classification":
                        requirements.classification_facet_ids.append(facet_id)
                    elif facet.facet_type == "attribute":
                        requirements.attribute_facet_ids.append(facet_id)
                    elif facet.facet_type == "partof":
                        requirements.partof_facet_ids.append(facet_id)

            slots.append(SpecificationSlot(
                name=f"{entity_facet.mapped_name} Requirements",
                description=f"Requirements for {entity_facet.mapped_name}",
                applicability=applicability,
                requirements=requirements,
                reasoning="Default fallback grouping",
            ))
           

        return slots

    def _create_generic_slot(
        self, mapped_facets: List[MappedFacet]
    ) -> SpecificationSlot:
        """创建通用槽（当没有entity时）"""
        requirements = RequirementsSlot()

        for i, facet in enumerate(mapped_facets):
            facet_id = f"facet_{i}"
            if facet.facet_type == "property":
                requirements.property_facet_ids.append(facet_id)
            elif facet.facet_type == "material":
                requirements.material_facet_ids.append(facet_id)
            elif facet.facet_type == "classification":
                requirements.classification_facet_ids.append(facet_id)
            elif facet.facet_type == "attribute":
                requirements.attribute_facet_ids.append(facet_id)
            elif facet.facet_type == "partof":
                requirements.partof_facet_ids.append(facet_id)

        return SpecificationSlot(
            name="General Requirements",
            description="General building requirements",
            applicability=ApplicabilitySlot(entity_facet_id=""),  # 空entity
            requirements=requirements,
            reasoning="Generic fallback for cases without explicit entities",
        )

    def _generate_basic_fallback(
        self, mapped_facets: List[MappedFacet], ifc_version: str
    ) -> Dict[str, Any]:
        """生成基础后备规范"""
        logger.warning("Generating basic fallback specification")

        # 创建一个简单的规范
        spec = {
            "name": "Basic Requirements",
            "ifcVersion": [ifc_version],
            "description": "Fallback specification",
            "instructions": None,
            "applicability": {
                "minOccurs": "1",
                "maxOccurs": "unbounded",
                "entity": {
                ##------------新增解包逻辑------------##
                    "name": self._build_ids_value("Building Element", None), 
                    "predefinedType": None,
                },
                "partOf": None,
                "classification": None,
                "attribute": None,
                "property": None,
                "material": None,
            },
            "requirements": {
                "description": "Basic requirements extracted from facets",
                "entity": None,
                "partOf": None,
                "classification": None,
                "attribute": None,
                "property": None,
                "material": None,
            },
        }

        return {
            "specification": [spec],
            "metadata": {
                "total_extracted": 1,
                "total_normalized": len(mapped_facets),
                "ifc_version": ifc_version,
                "is_fallback": True,
            },
            "error": "IDS generation failed, using basic fallback",
        }
    ##-------------------修复 利用解包进行结构化----------------------##
    def _build_property_requirement(
        self, facet: MappedFacet
    ) -> Optional[Dict[str, Any]]:
        """Build a property requirement from a mapped facet"""

        # -----------------------------------------------------------
        # 1. 确定 PropertySet 的值 (核心修复逻辑)
        # -----------------------------------------------------------
        pset_name = facet.property_set # 优先级 1: Facet 直接提取的

        # 优先级 2: 如果 Facet 没有，从知识库映射(ifc_item)中获取
        if not pset_name and facet.ifc_item:
            # 兼容 ifc_item 可能是字典(dict)也可能是对象(object)的情况
            if isinstance(facet.ifc_item, dict):
                pset_name = facet.ifc_item.get("property_set")
            else:
                pset_name = getattr(facet.ifc_item, "property_set", None)

        # 优先级 3: 如果还是没有，使用默认值
        if not pset_name:
            pset_name = "Pset_Common"

        # -----------------------------------------------------------
        # 2. 确定 DataType
        # -----------------------------------------------------------
        data_type = "IFCLABEL" # 默认
        if facet.ifc_item:
            if isinstance(facet.ifc_item, dict):
                data_type = facet.ifc_item.get("data_type", "IFCLABEL")
            else:
                data_type = getattr(facet.ifc_item, "data_type", "IFCLABEL")

        # -----------------------------------------------------------
        # 3. 计算 Value (使用解包逻辑)
        # -----------------------------------------------------------
        final_value = self._build_value_with_constraints(facet)
        # -----------------------------------------------------------
        # 4. 构建最终字典
        # -----------------------------------------------------------
        prop_req = {
            "propertySet": self._build_ids_value(pset_name, None), # 使用修正后的 pset_name
            "baseName": self._build_ids_value(facet.mapped_name, None),
            "value": final_value,
            "dataType": data_type,
            "uri": None,
            "cardinality": "required",
            "instructions": None,
        }
        return prop_req

    def _build_material_requirement(
        self, facet: MappedFacet
    ) -> Optional[Dict[str, Any]]:
        """Build a material requirement from a mapped facet"""
        mat_req = {
            #用解包代替原来的强格式化结构
            "value": self._build_ids_value(facet.mapped_name, None),
            "uri": None,
            "cardinality": "required",
            "instructions": None,
        }
        return mat_req

    def _build_attribute_requirement(
        self, facet: MappedFacet
    ) -> Optional[Dict[str, Any]]:
        """Build an attribute requirement from a mapped facet"""
        attr_req = {
            #用解包代替原来的强格式化结构
            "name": self._build_ids_value(facet.mapped_name, None),
            "value": self._build_value_with_constraints(facet),
            "cardinality": "required",
            "instructions": None,
        }
        return attr_req

    def _build_classification_requirement(
        self, facet: MappedFacet
    ) -> Optional[Dict[str, Any]]:
        """Build a classification requirement from a mapped facet"""
        # 从mapped_name中推断classification system
        system_name = "Unknown System"
        if "OmniClass" in facet.mapped_name:
            system_name = "OmniClass"
        elif "Uniclass" in facet.mapped_name:
            system_name = "Uniclass"
        elif "ETIM" in facet.mapped_name or (
            facet.additional_data and facet.additional_data.get("source") == "bsdd"
        ):
            system_name = "ETIM"
        elif "MasterFormat" in facet.mapped_name:
            system_name = "MasterFormat"

        class_req = {
            #用解包代替原来的强格式化结构
            "value": self._build_ids_value(facet.mapped_name, None),
            "system": self._build_ids_value(system_name, None),
            "uri": None,
            "cardinality": "required",
            "instructions": f"Classification: {facet.original_text}",
        }

        # Use bSDD classification if available
        if facet.bsdd_classification:
            class_req["system"]["simpleValue"] = "bSDD"
            class_req["value"]["simpleValue"] = facet.bsdd_classification.name
            class_req["uri"] = facet.bsdd_classification.uri

        return class_req

    def _build_partof_requirement(self, facet: MappedFacet) -> Optional[Dict[str, Any]]:
        """Build a partOf requirement from a mapped facet"""
        # 从resolver获取relation信息，默认为IFCRELCONTAINEDINSPATIALSTRUCTURE
        relation_type = "IFCRELCONTAINEDINSPATIALSTRUCTURE"
        if hasattr(facet, "additional_data") and facet.additional_data:
            relation_type = facet.additional_data.get("relation", relation_type)

        partof_req = {
            "entity": self._build_ids_value(facet.mapped_name, None),
            "relation": relation_type,
            "cardinality": "required",
            "instructions": f"PartOf relationship: {facet.original_text}",
        }
        return partof_req

    def _build_value_with_constraints(self, facet: MappedFacet) -> Dict[str, Any]:
        """Build a value object that includes constraints from ConstraintExtractor."""
        # Apply constraints if available
        if facet.constraints:
            # Use the highest confidence constraint
            best_constraint = max(facet.constraints, key=lambda c: c.confidence)
            restriction = self.constraint_extractor.format_restriction_for_ids(
                best_constraint
            )

            # --- [新增逻辑 START] 智能转换 Pattern 为 Enumeration ---
            # 如果是 Pattern 类型，且看起来像是一个简单的选项列表 (含 | 但没有括号等复杂符号)
            if restriction and "pattern" in restriction:
                pat = restriction["pattern"]
                # 检查是否包含 | 且不包含复杂正则符号 (如 [] {} () * + ?)
                # 这样可以安全地把 "A|B|C" 变成 ["A", "B", "C"]
                if "|" in pat and not re.search(r"[\[\]\{\}\(\)\*\+\?\\]", pat):
                    options = [opt.strip() for opt in pat.split("|") if opt.strip()]
                    
                    # 将 restriction 从 pattern 格式重写为 enumeration 格式
                    restriction = {
                        "base": "string",
                        "enumeration": options  # 这里是一个列表，会在 JSON 中展开
                    }
            # --- [新增逻辑 END] -------------------------------------
            if restriction and restriction != {"base": "string"}:
                # 对于有约束的情况，提取具体的数值或值
                simple_value = self._extract_constraint_value(best_constraint)
                return {"simpleValue": simple_value, "restriction": restriction}

        # 没有约束的情况，使用原文
        return {"simpleValue": facet.original_text, "restriction": None}

    def _extract_constraint_value(self, constraint: ValueRestriction) -> str:
        """从约束中提取具体的值"""
        if constraint.restriction_type == RestrictionType.BOUNDS:
            bounds = constraint.restriction
            if bounds.min_value is not None:
                unit = f" {bounds.unit}" if bounds.unit else ""
                if bounds.max_value is not None:
                    return f"{bounds.min_value}-{bounds.max_value}{unit}"
                else:
                    return f">= {bounds.min_value}{unit}"
            elif bounds.max_value is not None:
                unit = f" {bounds.unit}" if bounds.unit else ""
                return f"<= {bounds.max_value}{unit}"

        elif constraint.restriction_type == RestrictionType.ENUMERATION:
            enumeration = constraint.restriction
            return ", ".join(enumeration.values)

        elif constraint.restriction_type == RestrictionType.PATTERN:
            pattern = constraint.restriction
            return pattern.pattern

        elif constraint.restriction_type == RestrictionType.LENGTH:
            length = constraint.restriction
            if length.min_length is not None and length.max_length is not None:
                return f"{length.min_length}-{length.max_length} characters"
            elif length.min_length is not None:
                return f">= {length.min_length} characters"
            elif length.max_length is not None:
                return f"<= {length.max_length} characters"

        # 回退到原始文本
        return constraint.original_text

