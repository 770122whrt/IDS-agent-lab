"""
Data structures for layered extraction pipeline

Defines clear interfaces between pipeline stages
分层提取管道的数据结构

定义管道阶段之间的清晰接口
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class FacetCandidate:
    """Facet classification candidate
    分面分类候选
    """
    source_text: str  # 源文本
    facet_type: str  # 分面类型
    confidence: float  # 置信度
    reasoning: str  # 推理过程


@dataclass
class FacetClassification:
    """Result from facet classification stage
    分面分类阶段的结果
    """

    entity_candidates: List[FacetCandidate]  # 实体候选列表
    property_candidates: List[FacetCandidate]  # 属性候选列表
    attribute_candidates: List[FacetCandidate]  # 属性候选列表
    material_candidates: List[FacetCandidate]  # 材料候选列表
    classification_candidates: List[FacetCandidate]  # 分类候选列表
    partof_candidates: List[FacetCandidate]  # 部分关系候选列表
    llm_analysis: Optional[str] = None  # LLM分析过程记录

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FacetClassification":
        """Create from dictionary
        从字典创建实例"""
        return cls(
            entity_candidates=[
                FacetCandidate(**candidate)
                for candidate in data.get("entity_candidates", [])
            ],
            property_candidates=[
                FacetCandidate(**candidate)
                for candidate in data.get("property_candidates", [])
            ],
            attribute_candidates=[
                FacetCandidate(**candidate)
                for candidate in data.get("attribute_candidates", [])
            ],
            material_candidates=[
                FacetCandidate(**candidate)
                for candidate in data.get("material_candidates", [])
            ],
            classification_candidates=[
                FacetCandidate(**candidate)
                for candidate in data.get("classification_candidates", [])
            ],
            partof_candidates=[
                FacetCandidate(**candidate)
                for candidate in data.get("partof_candidates", [])
            ],
        )


