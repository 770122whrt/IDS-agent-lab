"""
解析器工厂
创建和管理所有解析器实例
"""

import logging
from typing import Dict, Any

from .entity_resolver import EntityResolver
from .property_resolver import PropertyResolver
from .material_resolver import MaterialResolver
from .classification_resolver import ClassificationResolver
from .attribute_resolver import AttributeResolver
from .partof_resolver import PartOfResolver

logger = logging.getLogger(__name__)


class ResolverFactory:
    """解析器工厂"""

    @staticmethod
    def create_resolvers(
        database_manager
    ) -> Dict[str, Any]:
        """
        创建所有解析器

        Args:
            database_manager: 数据库管理器
            entity_property_manager: IFC API管理器

        Returns:
            解析器字典
        """
        resolvers = {
            "entity": EntityResolver(database_manager),
            "property": PropertyResolver(
                database_manager),
            "material": MaterialResolver(database_manager),
            "classification": ClassificationResolver(database_manager),
            "attribute": AttributeResolver(),
            "partof": PartOfResolver(),
        }

        logger.info(f"Created {len(resolvers)} resolvers")
        return resolvers
