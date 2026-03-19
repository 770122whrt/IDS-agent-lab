"""
Data structures for layered extraction pipeline

Defines clear interfaces between pipeline stages
分层提取管道的数据结构

定义管道阶段之间的清晰接口
"""
from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, List,Union,Optional

    
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
    bsdd_classification: Optional[Any] = None  # BsddClassification bSDD分类
    additional_data: Optional[Dict[str, Any]] = None  # For resolver-specific data (e.g., relation type)
    # 额外数据（用于解析器特定数据，如关系类型）

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []

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
            bsdd_classification=data.get("bsdd_classification"),
            additional_data=data.get("additional_data"),
        )

class RestrictionType(Enum):
    """Types of value restrictions supported by IDS
    IDS支持的值限制类型
    """

    BOUNDS = "bounds"  # 边界限制（数值范围）
    ENUMERATION = "enumeration"  # 枚举限制
    PATTERN = "pattern"  # 模式限制
    LENGTH = "length"  # 长度限制


@dataclass
class BoundsRestriction:
    """Numeric bounds restriction (e.g., >= 240mm, 10-20 meters)
    数值边界限制（例如：>= 240mm, 10-20米）
    """

    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_inclusive: bool = True
    max_inclusive: bool = True
    unit: Optional[str] = None


@dataclass
class EnumerationRestriction:
    """Enumeration restriction (e.g., "concrete", "steel", "wood")
    枚举限制（例如："concrete", "steel", "wood"）
    """

    values: List[str]


@dataclass
class PatternRestriction:
    """Pattern restriction using regex (e.g., format codes, naming conventions)
    使用正则表达式的模式限制
    """

    pattern: str
    description: Optional[str] = None


@dataclass
class LengthRestriction:
    """String length restriction
    字符串长度限制
    """

    min_length: Optional[int] = None
    max_length: Optional[int] = None


@dataclass
class ValueRestriction:
    """Container for any type of value restriction
    任意类型值限制的容器
    """

    restriction_type: RestrictionType
    restriction: Union[
        BoundsRestriction, EnumerationRestriction, PatternRestriction, LengthRestriction
    ]
    confidence: float = 1.0
    original_text: str = ""