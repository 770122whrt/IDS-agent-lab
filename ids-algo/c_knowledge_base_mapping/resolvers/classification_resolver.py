"""
Classification解析器
使用静态数据库
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ClassificationResolver:
    """Classification解析器 - 混合数据源"""

    def __init__(self, database_manager):
        self.database_manager = database_manager

    async def resolve(
        self, query_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        解析Classification

        目前策略:
        - Dictionary URI → 优先静态知识库

        Args:
            query_text: 查询文本
            context: 上下文 (可包含 dictionary_uris)

        Returns:
            解析结果
        """
        try:
            # 检查是否有Dictionary URI
            dictionary_uris = context.get("dictionary_uris") if context else None
            has_dictionary_uri = dictionary_uris and len(dictionary_uris) > 0


            # 使用静态知识库
            db = self.database_manager.get_database("classification")
            if db:
                ifc_version = context.get("ifc_version", "IFC4") if context else "IFC4"
                results = db.search(query_text, top_k=5, ifc_versions=[ifc_version])
                if results and len(results) > 0:
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
            logger.error(f"Classification resolution failed: {str(e)}")

        return None
