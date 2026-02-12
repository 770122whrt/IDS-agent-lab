"""
PartOf解析器
基于IFC官方标准的6种空间关系
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class PartOfResolver:
    """PartOf解析器 - 基于IFC官方6种关系类型"""

    def __init__(self):
        # IFC官方6种PartOf关系映射
        self.spatial_entities = {
            # IFCRELCONTAINEDINSPATIALSTRUCTURE - 空间包含关系
            "building": {
                "mapped_name": "IfcBuilding",
                "confidence": 1.0,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "storey": {
                "mapped_name": "IfcBuildingStorey",
                "confidence": 1.0,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "floor": {
                "mapped_name": "IfcBuildingStorey",
                "confidence": 0.9,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "site": {
                "mapped_name": "IfcSite",
                "confidence": 1.0,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "space": {
                "mapped_name": "IfcSpace",
                "confidence": 1.0,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "room": {
                "mapped_name": "IfcSpace",
                "confidence": 0.9,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "zone": {
                "mapped_name": "IfcZone",
                "confidence": 0.9,
                "relation": "IFCRELASSIGNSTOGROUP",
            },
            # IFCRELAGGREGATES - 聚合关系
            "curtain wall": {
                "mapped_name": "IfcCurtainWall",
                "confidence": 1.0,
                "relation": "IFCRELAGGREGATES",
            },
            "slab": {
                "mapped_name": "IfcSlab",
                "confidence": 1.0,
                "relation": "IFCRELAGGREGATES",
            },
            "assembly": {
                "mapped_name": "IfcElementAssembly",
                "confidence": 0.8,
                "relation": "IFCRELAGGREGATES",
            },
            # IFCRELASSIGNSTOGROUP - 系统分组关系
            "distribution system": {
                "mapped_name": "IfcDistributionSystem",
                "confidence": 1.0,
                "relation": "IFCRELASSIGNSTOGROUP",
            },
            "system": {
                "mapped_name": "IfcSystem",
                "confidence": 0.8,
                "relation": "IFCRELASSIGNSTOGROUP",
            },
            "circuit": {
                "mapped_name": "IfcDistributionCircuit",
                "confidence": 0.9,
                "relation": "IFCRELASSIGNSTOGROUP",
            },
            # IFCRELNESTS - 嵌套关系
            "wall": {
                "mapped_name": "IfcWall",
                "confidence": 1.0,
                "relation": "IFCRELNESTS",
            },
            "host": {
                "mapped_name": "IfcElement",
                "confidence": 0.7,
                "relation": "IFCRELNESTS",
            },
        }

    async def resolve(
        self, query_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        解析PartOf关系

        基于IFC官方6种关系类型:
        - IFCRELCONTAINEDINSPATIALSTRUCTURE (空间包含)
        - IFCRELAGGREGATES (聚合关系)
        - IFCRELASSIGNSTOGROUP (系统分组)
        - IFCRELNESTS (嵌套关系)
        - IFCRELVOIDSELEMENT (空隙关系)
        - IFCRELFILLSELEMENT (填充关系)

        Args:
            query_text: 查询文本
            context: 上下文

        Returns:
            解析结果，包含entity和relation信息
        """
        try:
            query_lower = query_text.lower().strip()

            # 直接匹配空间实体
            best_match = None
            best_score = 0.0

            for key, relation_info in self.spatial_entities.items():
                if key in query_lower:
                    # 计算匹配度（考虑关键词长度）
                    match_score = (
                        len(key) / len(query_lower) * relation_info["confidence"]
                    )
                    if match_score > best_score:
                        best_score = match_score
                        best_match = relation_info

            if best_match:
                logger.info(
                    f"PartOf match: '{query_text}' -> '{best_match['mapped_name']}' ({best_match['relation']})"
                )
                return {
                    "mapped_name": best_match["mapped_name"],
                    "confidence": best_match["confidence"],
                    "relation": best_match["relation"],
                    "ifc_item": {
                        "name": best_match["mapped_name"],
                        "type": "IFC_SPATIAL",
                        "relation_type": best_match["relation"],
                    },
                    "source": "rule_engine",
                }

        except Exception as e:
            logger.error(f"PartOf resolution failed: {str(e)}")

        return None
