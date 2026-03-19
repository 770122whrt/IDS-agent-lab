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
            dictionary_uris = context.get("dictionary_uris") if context else None
            has_dictionary_uri = dictionary_uris and len(dictionary_uris) > 0

            # 2.  使用静态知识库
            db = self.database_manager.get_database("material")
            if db:
                ifc_version = context.get("ifc_version", "IFC4") if context else "IFC4"
                results = db.search(query_text, top_k=5, ifc_versions=[ifc_version])
                if results and len(results) > 0:
                    # results是tuple列表: (ifc_item, distance)
                    ifc_item, distance = results[0]
                    # 将距离转换为相似度
                    similarity = 1.0 / (1.0 + distance)
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
