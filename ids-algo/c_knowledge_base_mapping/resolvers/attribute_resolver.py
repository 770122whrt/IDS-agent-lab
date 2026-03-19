"""
Attribute解析器
基于规则引擎的IFC标准属性
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AttributeResolver:
    """Attribute解析器 - 规则引擎"""

    def __init__(self):
        # IFC标准属性规则
        self.ifc_attributes = {
            "name": {"mapped_name": "Name", "confidence": 1.0},
            "description": {"mapped_name": "Description", "confidence": 1.0},
            "globalid": {"mapped_name": "GlobalId", "confidence": 1.0},
            "objecttype": {"mapped_name": "ObjectType", "confidence": 1.0},
            "tag": {"mapped_name": "Tag", "confidence": 1.0},
            "predefinedtype": {"mapped_name": "PredefinedType", "confidence": 1.0},
        }

    async def resolve(
        self, query_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        解析Attribute

        Args:
            query_text: 查询文本
            context: 上下文

        Returns:
            解析结果
        """
        try:
            query_lower = query_text.lower().strip()

            # 直接匹配
            if query_lower in self.ifc_attributes:
                attr = self.ifc_attributes[query_lower]
                return {
                    "mapped_name": attr["mapped_name"],
                    "confidence": attr["confidence"],
                    "ifc_item": {"name": attr["mapped_name"], "type": "IFC_ATTRIBUTE"},
                    "source": "rule_engine",
                }

            # 模糊匹配
            for key, attr in self.ifc_attributes.items():
                if query_lower in key or key in query_lower:
                    return {
                        "mapped_name": attr["mapped_name"],
                        "confidence": 0.8,
                        "ifc_item": {
                            "name": attr["mapped_name"],
                            "type": "IFC_ATTRIBUTE",
                        },
                        "source": "rule_engine",
                    }

        except Exception as e:
            logger.error(f"Attribute resolution failed: {str(e)}")

        return None
