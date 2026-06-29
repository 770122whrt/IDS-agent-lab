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
        # IFC官方6种PartOf关系映射（支持中英文关键词）
        self.spatial_entities = {
            # IFCRELCONTAINEDINSPATIALSTRUCTURE - 空间包含关系
            "building": {
                "mapped_name": "IfcBuilding",
                "confidence": 1.0,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "建筑": {
                "mapped_name": "IfcBuilding",
                "confidence": 1.0,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "storey": {
                "mapped_name": "IfcBuildingStorey",
                "confidence": 1.0,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "楼层": {
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
            "场地": {
                "mapped_name": "IfcSite",
                "confidence": 1.0,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "project": {
                "mapped_name": "IfcProject",
                "confidence": 1.0,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "项目": {
                "mapped_name": "IfcProject",
                "confidence": 1.0,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "space": {
                "mapped_name": "IfcSpace",
                "confidence": 1.0,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "空间": {
                "mapped_name": "IfcSpace",
                "confidence": 1.0,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "room": {
                "mapped_name": "IfcSpace",
                "confidence": 0.9,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "房间": {
                "mapped_name": "IfcSpace",
                "confidence": 0.9,
                "relation": "IFCRELCONTAINEDINSPATIALSTRUCTURE",
            },
            "zone": {
                "mapped_name": "IfcZone",
                "confidence": 0.9,
                "relation": "IFCRELASSIGNSTOGROUP",
            },
            "区域": {
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
            "幕墙": {
                "mapped_name": "IfcCurtainWall",
                "confidence": 1.0,
                "relation": "IFCRELAGGREGATES",
            },
            "slab": {
                "mapped_name": "IfcSlab",
                "confidence": 1.0,
                "relation": "IFCRELAGGREGATES",
            },
            "楼板": {
                "mapped_name": "IfcSlab",
                "confidence": 1.0,
                "relation": "IFCRELAGGREGATES",
            },
            "assembly": {
                "mapped_name": "IfcElementAssembly",
                "confidence": 0.8,
                "relation": "IFCRELAGGREGATES",
            },
            "装配": {
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
            "系统": {
                "mapped_name": "IfcSystem",
                "confidence": 0.8,
                "relation": "IFCRELASSIGNSTOGROUP",
            },
            "circuit": {
                "mapped_name": "IfcDistributionCircuit",
                "confidence": 0.9,
                "relation": "IFCRELASSIGNSTOGROUP",
            },
            "回路": {
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
            "墙": {
                "mapped_name": "IfcWall",
                "confidence": 1.0,
                "relation": "IFCRELNESTS",
            },
            "host": {
                "mapped_name": "IfcElement",
                "confidence": 0.7,
                "relation": "IFCRELNESTS",
            },
            "宿主": {
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

            # 第一步：检查是否包含显式的IFC实体名称（如"IfcBridgePart"）
            import re
            # 修复：不使用\b边界，因为它在中文环境下不工作
            ifc_entity_pattern = r'(Ifc[A-Z][a-zA-Z0-9]*)'
            ifc_matches = re.findall(ifc_entity_pattern, query_text)

            if ifc_matches:
                # 找到显式IFC实体名称
                entity_name = ifc_matches[0]  # 取第一个匹配

                # 检查是否包含PredefinedType约束（如"类型为SUPERSTRUCTURE"）
                predefined_type = None
                predefined_pattern = r'类型为\s*([A-Z_]+)|PredefinedType\s*[=为]\s*([A-Z_]+)'
                predefined_matches = re.findall(predefined_pattern, query_text)
                if predefined_matches:
                    # predefined_matches是元组列表，取第一个非空组
                    predefined_type = next((m for group in predefined_matches for m in group if m), None)

                # 检查是否显式指定了关系类型（如"IFCRELAGGREGATES"）
                relation = None
                relation_pattern = r'(IFCREL[A-Z]+)'
                relation_matches = re.findall(relation_pattern, query_text)
                if relation_matches:
                    # 找到显式指定的关系类型，直接使用
                    relation = relation_matches[0]
                    logger.info(f"Found explicit relation type in text: {relation}")
                else:
                    # 如果没有显式指定，才根据实体类型推断关系类型
                    relation = self._infer_relation_type(entity_name)

                logger.info(
                    f"PartOf explicit entity match: '{query_text}' -> '{entity_name}' "
                    f"(relation={relation}, predefinedType={predefined_type})"
                )

                result = {
                    "mapped_name": entity_name,
                    "confidence": 1.0,
                    "relation": relation,
                    "ifc_item": {
                        "name": entity_name,
                        "type": "IFC_SPATIAL",
                        "relation_type": relation,
                    },
                    "source": "explicit_entity",
                }

                # 如果有PredefinedType约束，添加到结果中
                if predefined_type:
                    result["predefined_type"] = predefined_type

                return result

            # 第二步：直接匹配空间实体关键词
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
                    f"PartOf keyword match: '{query_text}' -> '{best_match['mapped_name']}' ({best_match['relation']})"
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

    def _infer_relation_type(self, entity_name: str) -> str:
        """根据实体类型推断关系类型"""
        entity_lower = entity_name.lower()

        # 空间结构实体 -> IFCRELCONTAINEDINSPATIALSTRUCTURE
        spatial_entities = [
            "ifcproject", "ifcsite", "ifcbuilding", "ifcbuildingstorey",
            "ifcspace", "ifcbridge", "ifcbridgepart", "ifcrailway", "ifcrailwaypart",
            "ifcroad", "ifcroadpart", "ifcfacility", "ifcfacilitypart"
        ]
        if entity_lower in spatial_entities:
            return "IFCRELCONTAINEDINSPATIALSTRUCTURE"

        # 聚合关系实体 -> IFCRELAGGREGATES
        aggregate_entities = [
            "ifcelementassembly", "ifccurtainwall", "ifcslab", "ifcbeam", "ifccolumn"
        ]
        if entity_lower in aggregate_entities:
            return "IFCRELAGGREGATES"

        # 系统分组 -> IFCRELASSIGNSTOGROUP
        group_entities = [
            "ifcsystem", "ifcdistributionsystem", "ifcdistributioncircuit", "ifczone"
        ]
        if entity_lower in group_entities:
            return "IFCRELASSIGNSTOGROUP"

        # 默认使用空间包含关系
        return "IFCRELCONTAINEDINSPATIALSTRUCTURE"
