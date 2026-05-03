"""
IFC向量知识库基类实现

该模块实现了基于FAISS的IFC实体、属性集和属性的向量数据库基类，
用于语义检索和规范化。
"""

import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Set
from datetime import datetime

import faiss

from .models import (
    IFCItem,
    IFCVersion,
    IFCItemType,
)

from .vector_cache_manager import get_vector_cache_manager
from .model_manager import vector_model_manager

# 导入全局配置
from openrouter.settings import settings

VECTOR_DIM = settings.vector_dim

logger = logging.getLogger(__name__)


class IFCVectorKnowledgeBaseMetadata:
    """IFC向量知识库元数据"""

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        version: str = "1.0.0",
        ifc_versions: Optional[List[IFCVersion]] = None,
        item_types: Optional[List[IFCItemType]] = None,
        vector_dim: int = VECTOR_DIM,  # 使用全局配置
        model_name: str = "BAAI/bge-m3",  # Default embedding model
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.name = name
        self.description = description
        self.version = version
        self.ifc_versions = ifc_versions or []
        self.item_types = item_types or []
        self.vector_dim = vector_dim
        self.model_name = model_name
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at

        # 统计信息
        self.item_counts: Dict[str, int] = {}

    def update_stats(self, items: List[IFCItem]) -> None:
        """更新统计信息"""
        # 统计IFC版本和项目类型
        versions: Set[IFCVersion] = set()
        types: Set[IFCItemType] = set()

        # 统计各类型的数量
        type_counts: Dict[str, int] = {}

        for item in items:
            versions.add(item.ifc_version)
            types.add(item.item_type)

            # 统计类型数量
            item_type = item.item_type
            type_counts[item_type] = type_counts.get(item_type, 0) + 1

        self.ifc_versions = list(versions)
        self.item_types = list(types)
        self.item_counts = type_counts

        # 更新时间
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "ifc_versions": self.ifc_versions,
            "item_types": self.item_types,
            "vector_dim": self.vector_dim,
            "model_name": self.model_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "item_counts": self.item_counts,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IFCVectorKnowledgeBaseMetadata":
        """从字典创建对象"""
        return cls(
            name=data.get("name", "IFC Vector Knowledge Base"),
            description=data.get("description"),
            version=data.get("version", "1.0.0"),
            ifc_versions=data.get("ifc_versions", []),
            item_types=data.get("item_types", []),
            vector_dim=data.get("vector_dim", VECTOR_DIM),
            model_name=data.get("model_name", "BAAI/bge-m3"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


class IFCVectorKnowledgeBase:
    """IFC向量知识库基类"""

    def __init__(
        self,
        vector_dim: int = VECTOR_DIM,
        model_name: str = "BAAI/bge-m3",
        top_k: int = 5,
        name: str = "IFC Vector Knowledge Base",
        description: Optional[str] = None,
    ):
        self.vector_dim = vector_dim
        self.model_name = model_name
        self.top_k = top_k

        # 初始化元数据
        self.metadata = IFCVectorKnowledgeBaseMetadata(
            name=name,
            description=description,
            vector_dim=vector_dim,
            model_name=model_name,
        )

        # 使用全局模型管理器

        self.model = vector_model_manager.get_model(model_name)
        if self.model is None:
            raise RuntimeError(
                f"Cannot initialize knowledge base without embedding model: {model_name}"
            )
        self.model_name = model_name

        # 初始化向量缓存管理器
        self.cache_manager = get_vector_cache_manager(
            model_name=model_name,
            max_memory_size=getattr(settings, "vector_cache_size", 10000),
            enable_persistence=getattr(settings, "vector_cache_persistence", True),
        )

        # 初始化FAISS索引
        self.index = faiss.IndexFlatIP(vector_dim)  # 使用内积作为相似度度量

        # 存储实体映射关系
        self.items: List[IFCItem] = []

    def _encode_text(self, text: str) -> np.ndarray:
        """将文本编码为向量（带缓存）"""
        if self.model is None:
            logger.error("Embedding model not available for text encoding")
            raise RuntimeError("Embedding model not initialized")

        # 检查缓存
        cached_vector = self.cache_manager.get_vector(text, self.model_name)
        if cached_vector is not None:
            return cached_vector

        # 计算向量
        vector = self.model.encode(text, normalize_embeddings=True)

        # 存储到缓存
        self.cache_manager.put_vector(text, self.model_name, vector)

        return vector

    def _filter_items_by_metadata(
        self,
        items: List[IFCItem],
        ifc_versions: Optional[List[str]] = None,
        item_types: Optional[List[str]] = None,
    ) -> List[IFCItem]:
        """根据元数据过滤项目"""
        # 如果没有过滤条件，返回所有项目
        if not ifc_versions and not item_types:
            return items

        filtered_items = []
        for item in items:
            # 过滤IFC版本
            if ifc_versions and item.ifc_version not in ifc_versions:
                continue

            # 过滤项目类型
            if item_types and item.item_type not in item_types:
                continue

            filtered_items.append(item)

        return filtered_items

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        ifc_versions: Optional[List[str]] = None,
        item_types: Optional[List[str]] = None,
    ) -> List[Tuple[IFCItem, float]]:
        """搜索与查询最相似的IFC项目

        Args:
            query: 查询文本
            top_k: 返回的结果数量
            ifc_versions: 过滤的IFC版本列表
            item_types: 过滤的项目类型列表

        Returns:
            List[Tuple[IFCItem, float]]: 匹配项目和相似度得分列表
        """
        if not self.items:
            logger.warning("知识库为空，无法执行搜索")
            return []

        k = top_k or self.top_k

        # 第一层：精确匹配（在版本过滤之前，大小写不敏感）
        query_lower = query.lower().strip()

        # 先在所有项目中查找精确匹配
        for item in self.items:
            if item.name.lower() == query_lower:
                # 如果指定了版本过滤，检查是否匹配
                if ifc_versions:
                    # 如果精确匹配的项目版本不在过滤列表中，记录警告但仍返回
                    if item.ifc_version not in ifc_versions:
                        logger.warning(f"精确匹配命中 {item.name}，但版本 {item.ifc_version} 不在请求的版本列表 {ifc_versions} 中，仍然返回此匹配")
                else:
                    logger.info(f"精确匹配命中: {item.name} (query: {query})")
                return [(item, 1.0)]

        # 第二层：向量搜索（处理模糊查询）
        logger.info(f"精确匹配未命中，使用向量搜索: {query}")

        # 根据元数据过滤项目
        filtered_items = self._filter_items_by_metadata(
            self.items, ifc_versions, item_types
        )
        if not filtered_items:
            logger.warning("过滤后没有符合条件的项目")
            return []

        # 对查询进行编码
        query_vector = self._encode_text(query)

        # 直接在filtered_items中计算相似度
        results = []
        for item in filtered_items:
            # 获取item在原始列表中的索引
            item_idx = self.items.index(item)

            # 获取item的向量（从FAISS索引中）
            item_vector = self.index.reconstruct(item_idx)

            # 计算相似度（使用内积）
            similarity = float(np.dot(query_vector, item_vector))

            results.append((item, similarity))

        # 按相似度排序并返回top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    def add_item(self, item: IFCItem) -> None:
        """添加项目到知识库"""
        # 编码项目文本
        text_to_encode = f"{item.name}: {item.definition}"
        vector = self._encode_text(text_to_encode)
        vector = np.array([vector], dtype=np.float32)

        # 添加到FAISS索引
        self.index.add(vector)

        # 存储项目
        self.items.append(item)

        # 更新元数据
        self.metadata.update_stats(self.items)

    def save(self, file_path: str) -> None:
        """保存知识库到文件"""
        raise NotImplementedError("子类必须实现save方法")

    def load(self, file_path: str) -> None:
        """从文件加载知识库"""
        raise NotImplementedError("子类必须实现load方法")