"""
Data structures for layered extraction pipeline

Defines clear interfaces between pipeline stages
分层提取管道的数据结构

定义管道阶段之间的清晰接口
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
    
@dataclass
class MappedFacet:
    """A facet that has been mapped to IFC terminology
    已映射到IFC术语的分面
    """

    facet_type: str  # entity, property, attribute, material, classification, partof
    # 分面类型：实体、属性、特性、材料、分类、部分关系
    original_text: str  # 原始文本
    mapped_name: str  # 映射后的名称
    confidence: float  # 置信度
    ifc_item: Optional[Any] = None  # IFCEntity, IFCProperty, etc. IFC项目
    property_set: Optional[str] = None  # For property facets 属性集（用于属性分面）
    entity_name: Optional[str] = None  # For property facets - associated entity 实体名称（用于属性分面-关联实体）
    constraints: List[Any] = None  # List[ValueRestriction] 约束列表
    #bsdd_classification: Optional[Any] = None  # BsddClassification bSDD分类
    additional_data: Optional[Dict[str, Any]] = None  # For resolver-specific data (e.g., relation type)
    # 额外数据（用于解析器特定数据，如关系类型）

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MappedFacet":
        """Create from dictionary
        从字典创建实例"""
        return cls(
            facet_type=data["facet_type"],
            original_text=data["original_text"],
            mapped_name=data["mapped_name"],
            confidence=float(data["confidence"]),
            ifc_item=data.get("ifc_item"),
            property_set=data.get("property_set"),
            entity_name=data.get("entity_name"),
            constraints=data.get("constraints", []),
            additional_data=data.get("additional_data"),
        )

@dataclass
class KnowledgeBaseMappingStrategy:
    """知识库映射策略配置"""

    # Entity映射策略
    entity_kb_type: str = "main"  # 使用主数据库
    entity_filter_abstract: bool = True  # 过滤抽象实体
    entity_search_threshold: float = 0.1  # 搜索阈值

    # Property映射策略
    property_kb_type: str = "property"
    property_require_entity_context: bool = True  # 需要Entity上下文
    property_search_threshold: float = 0.1

    # Material映射策略
    material_kb_type: str = "material"
    material_search_threshold: float = 0.1

    # Attribute映射策略
    attribute_kb_type: str = "attribute"
    attribute_search_threshold: float = 0.1

    # Classification映射策略
    classification_kb_type: str = "classification"
    classification_search_threshold: float = 0.1

    # PartOf映射策略
    partof_kb_type: str = "partof"
    partof_search_threshold: float = 0.1

