"""
IFC向量知识库模块

该模块提供IFC向量知识库相关的功能，支持实体、属性集、属性、
部分关系和分类等多种类型项目的向量存储和检索。
"""

# 导出模型
from .core.models import (
    IFCVersion,
    IFCItemType,
    IFCItem,
    IFCEntity,
    IFCPropertySet,
    IFCProperty,
    IFCAttribute,
    IFCPartOf,
    IFCClassification,
    IFCMaterial,
)

# 导出基类
from .core.base import (
    IFCVectorKnowledgeBase,
    IFCVectorKnowledgeBaseMetadata,
)

# 导出专用数据库类
from .unified_db import IFCUnifiedVectorDB
from .core.model_manager import VectorModelManager,vector_model_manager



# 向后兼容导出，使原有代码不受影响
IFCEntityVectorDB = IFCUnifiedVectorDB

__all__ = [
    # 模型
    "IFCVersion",
    "IFCItemType",
    "IFCItem",
    "IFCEntity",
    "IFCPropertySet",
    "IFCProperty",
    "IFCAttribute",
    "IFCPartOf",
    "IFCClassification",
    "IFCMaterial",
    # 基类
    "IFCVectorKnowledgeBase",
    "IFCVectorKnowledgeBaseMetadata",
    # 工厂函数
    "create_ifc_unified_db",
    "create_ifc_db_by_type",

    "VectorModelManager",
    "vector_model_manager",
]
