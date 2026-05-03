"""
Material解析器
混合使用静态知识库
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class MaterialResolver:
    """Material解析器 - 混合数据源"""

    def __init__(self, database_manager):
        self.database_manager = database_manager


    async def resolve(
        self, query_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        解析Material

        Args:
            query_text: 查询文本
            context: 上下文

        Returns:
            解析结果
        """
        try:
            # 检查是否是通用材料要求（任意材料）
            generic_material_keywords = [
                "必须定义材料", "必须有材料", "需要材料", "材料定义",
                "must define material", "must have material", "material required",
                "定义材料", "材料信息"
            ]

            query_lower = query_text.lower().strip()
            for keyword in generic_material_keywords:
                if keyword in query_lower:
                    logger.info(f"Generic material requirement detected: '{query_text}'")
                    return {
                        "mapped_name": None,  # None表示任意材料
                        "confidence": 1.0,
                        "ifc_item": None,
                        "source": "generic_requirement",
                    }

            dictionary_uris = context.get("dictionary_uris") if context else None
            has_dictionary_uri = dictionary_uris and len(dictionary_uris) > 0

            # 2.  使用静态知识库
            db = self.database_manager.get_database("material")
            if db:
                ifc_version = context.get("ifc_version", "IFC4") if context else "IFC4"
                results = db.search(query_text, top_k=5, ifc_versions=[ifc_version])
                if results and len(results) > 0:
                    # results是tuple列表: (ifc_item, similarity)
                    ifc_item, similarity = results[0]
                    # similarity已经是点积相似度，不需要转换
                    if similarity > 0.5:
                        return {
                            "mapped_name": ifc_item.name,
                            "confidence": similarity,
                            "ifc_item": ifc_item,
                            "source": "static_kb",
                        }


        except Exception as e:
            logger.error(f"Material resolution failed: {str(e)}")

        return None
