"""
IFC统一数据库实现与工厂
(整合了原 factory, unified_db, attribute_db, classification_db, part_of_db)
"""

import os
import json
import logging
from typing import List, Optional, Union

from .core.base import IFCVectorKnowledgeBase
from .core.models import (
    IFCItem, IFCItemType, IFCEntity, IFCPropertySet, 
    IFCProperty, IFCAttribute, IFCPartOf, IFCClassification, IFCMaterial
)
from openrouter.settings import settings

# Use entity embedding model as default
VECTOR_MODEL_NAME = settings.entity_embedding_model
VECTOR_DIM = settings.vector_dim

logger = logging.getLogger(__name__)


class IFCUnifiedVectorDB(IFCVectorKnowledgeBase):
    """
    IFC统一向量数据库
    既可以作为全量库(Unified)，也可以作为特定类型库(如AttributeDB)使用
    """

    def __init__(
        self,
        name: str = "IFC Unified Knowledge Base",
        description: str = "IFC向量知识库",
        allowed_item_types: Optional[List[IFCItemType]] = None,  # 允许限制该数据库只接受特定类型 (例如只存 Attribute)
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            **kwargs
        )
        self.allowed_item_types = allowed_item_types

    def add_item(self, item: IFCItem) -> None:
        """重写add_item,增加类型检查"""
        if self.allowed_item_types:
            if item.item_type not in self.allowed_item_types:
                logger.warning(
                    f"Item type mismatch: {item.item_type} not in allowed types {self.allowed_item_types}. "
                    f"Skipping {item.name}"
                )
                return
        
        # 调用基类真正的入库逻辑
        super().add_item(item)

    def save(self, file_path: str) -> None:
        """保存到JSON文件"""
        data = {
            "metadata": self.metadata.to_dict(),
            "items": [item.to_dict() for item in self.items],
        }
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved DB to {file_path} ({len(self.items)} items)")

    def load(self, file_path: str) -> None:
        logger.info(f"Loading DB from {file_path}...")
        """从JSON文件加载"""
        if not os.path.exists(file_path):
            logger.warning(f"DB file not found: {file_path}")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 1. 加载元数据 (可选)
            # if "metadata" in data: ...

            # 2. 加载项目
            # 建立类型映射表，方便快速实例化
            type_map = {
                IFCItemType.ENTITY.value: IFCEntity,
                IFCItemType.PROPERTY_SET.value: IFCPropertySet,
                IFCItemType.PROPERTY.value: IFCProperty,
                IFCItemType.ATTRIBUTE.value: IFCAttribute,
                IFCItemType.PART_OF.value: IFCPartOf,
                IFCItemType.CLASSIFICATION.value: IFCClassification,
                IFCItemType.MATERIAL.value: IFCMaterial,
            }

            count = 0
            for item_data in data.get("items", []):
                t_str = item_data.get("item_type")
                cls = type_map.get(t_str, IFCItem) # 默认回退到基类
                try:
                    item_obj = cls.from_dict(item_data)
                    self.add_item(item_obj)
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to load item: {e}")

            logger.info(f"Loaded {count} items from {file_path}")

        except Exception as e:
            logger.error(f"Failed to load DB: {e}")


# -----------------------------------------------------------------------------
# 3. 工厂函数 (The Factory) - 替代 factory.py
# -----------------------------------------------------------------------------

def create_ifc_unified_db(db_path: Optional[str] = None) -> IFCUnifiedVectorDB:
    """创建主数据库（包含所有类型）"""
    db = IFCUnifiedVectorDB(
        name="IFC Unified DB",
        description="Contains all IFC entities, properties, etc.",
        allowed_item_types=None # 不限制类型
    )
    if db_path and os.path.exists(db_path):
        db.load(db_path)
    return db

def create_ifc_db_by_type(
    item_type: Union[IFCItemType, str], 
    db_path: Optional[str] = None
) -> IFCUnifiedVectorDB:
    """根据类型创建特定的子数据库 (替代 attribute_db.py 等)"""
    
    # 统一转为枚举
    if isinstance(item_type, str):
        try:
            item_type = IFCItemType(item_type)
        except ValueError:
            pass # 可能是 "property" 这种简写，视情况处理

    # 定义配置
    # 这里我们复用同一个类，只是限制它能存什么
    db = IFCUnifiedVectorDB(
        name=f"IFC {item_type} DB",
        allowed_item_types=[item_type] if isinstance(item_type, IFCItemType) else None
    )

    if db_path and os.path.exists(db_path):
        db.load(db_path)
    
    return db