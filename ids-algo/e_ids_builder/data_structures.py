"""
Data structures for layered extraction pipeline

Defines clear interfaces between pipeline stages
分层提取管道的数据结构

定义管道阶段之间的清晰接口
"""

from dataclasses import dataclass, field
from typing import List
    
@dataclass
class ApplicabilitySlot:
    """Applicability槽 - 定义检查范围"""

    entity_facet_id: str = ""  # 主要实体的facet_id
    predefined_type: str = ""  # 如果有具体类型

    # 其他过滤条件facets
    property_facet_ids: List[str] = field(default_factory=list)  # 描述性属性过滤
    material_facet_ids: List[str] = field(default_factory=list)  # 材料过滤
    classification_facet_ids: List[str] = field(default_factory=list)  # 分类过滤
    attribute_facet_ids: List[str] = field(default_factory=list)  # 属性过滤
    partof_facet_ids: List[str] = field(default_factory=list)  # 空间关系过滤


@dataclass
class RequirementsSlot:
    """Requirements槽 - 定义验证约束"""

    property_facet_ids: List[str] = field(default_factory=list)  # 属性约束
    material_facet_ids: List[str] = field(default_factory=list)  # 材料要求
    classification_facet_ids: List[str] = field(default_factory=list)  # 分类要求
    attribute_facet_ids: List[str] = field(default_factory=list)  # 属性要求
    partof_facet_ids: List[str] = field(default_factory=list)  # 空间关系要求


@dataclass
class SpecificationSlot:
    """完整的IDS规范槽"""

    name: str
    description: str = ""

    applicability: ApplicabilitySlot = field(default_factory=ApplicabilitySlot)
    requirements: RequirementsSlot = field(default_factory=RequirementsSlot)

    reasoning: str = ""  # 分组和分类的reasoning

    # --- 新增字段 START ---
    # 用于存储从原始文本中提取的元数据
    ifc_version: List[str] = field(default_factory=list)  # e.g. ["IFC4", "IFC2X3"]
    # --- 新增字段 END ---