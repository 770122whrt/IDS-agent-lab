"""
Data structures for layered extraction pipeline

Defines clear interfaces between pipeline stages
分层提取管道的数据结构

定义管道阶段之间的清晰接口
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class BuildingObject:
    """Parsed building object
    解析后的建筑对象
    """
    raw_text: str  # 原始文本
    object_type: str  # 对象类型
    modifiers: List[str]  # 修饰词列表
    confidence: float  # 置信度


@dataclass
class PropertyDescription:
    """Parsed property description
    解析后的属性描述
    """
    raw_text: str  # 原始文本
    property_name: str  # 属性名称
    constraint_text: str  # 约束文本
    confidence: float  # 置信度


@dataclass
class MaterialRequirement:
    """Parsed material requirement
    解析后的材料要求
    """
    raw_text: str  # 原始文本
    material_name: str  # 材料名称
    specifications: str  # 规格说明
    confidence: float  # 置信度


@dataclass
class SpatialRelationship:
    """Parsed spatial relationship
    解析后的空间关系
    """
    raw_text: str  # 原始文本
    subject: str  # 主体
    relation: str  # 关系
    object: str  # 对象
    confidence: float  # 置信度


@dataclass
class StructuredParseResult:
    """Result from structured parsing stage
    结构化解析阶段的结果
    """

    building_objects: List[BuildingObject]  # 建筑对象列表
    property_descriptions: List[PropertyDescription]  # 属性描述列表
    material_requirements: List[MaterialRequirement]  # 材料要求列表
    spatial_relationships: List[SpatialRelationship]  # 空间关系列表
    unmatched_fragments: List[str]  # 未匹配的文本片段
    llm_analysis: Optional[str] = None  # LLM分析过程记录

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StructuredParseResult":
        """Create from dictionary
        从字典创建实例"""
        return cls(
            building_objects=[
                BuildingObject(**obj) for obj in data.get("building_objects", [])
            ],
            property_descriptions=[
                PropertyDescription(**prop)
                for prop in data.get("property_descriptions", [])
            ],
            material_requirements=[
                MaterialRequirement(**mat)
                for mat in data.get("material_requirements", [])
            ],
            spatial_relationships=[
                SpatialRelationship(**rel)
                for rel in data.get("spatial_relationships", [])
            ],
            unmatched_fragments=data.get("unmatched_fragments", []),
        )


