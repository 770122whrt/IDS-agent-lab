"""
向量缓存管理器

实现LRU缓存、持久化存储和缓存键管理，避免重复计算embedding向量。
"""

import hashlib
import logging
import pickle
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class VectorCacheManager:
    """
    向量缓存管理器

    功能：
    - LRU缓存机制
    - 内存缓存 + 磁盘持久化
    - 缓存键哈希管理
    - 线程安全操作
    - 缓存统计和监控
    """

    def __init__(
        self,
        max_memory_size: int = 10000,  # 内存中最大缓存条目数
        cache_dir: str = "./cache/vectors",  # 磁盘缓存目录
        enable_persistence: bool = True,  # 是否启用持久化
        model_name: str = "default",  # 模型名称，用于缓存隔离
    ):
        self.max_memory_size = max_memory_size
        self.cache_dir = Path(cache_dir)
        self.enable_persistence = enable_persistence
        self.model_name = model_name

        # 创建缓存目录
        if self.enable_persistence:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 内存缓存 (LRU)
        self._memory_cache: OrderedDict[str, np.ndarray] = OrderedDict()

        # 缓存统计
        self._stats = {
            "memory_hits": 0,
            "disk_hits": 0,
            "misses": 0,
            "total_requests": 0,
            "cache_size": 0,
        }

        # 线程锁
        self._lock = threading.RLock()

        logger.info(
            f"VectorCacheManager initialized: model={model_name}, "
            f"max_memory={max_memory_size}, persistence={enable_persistence}"
        )

    def _generate_cache_key(self, text: str, model_name: str) -> str:
        """生成缓存键"""
        # 使用文本内容 + 模型名称生成唯一哈希
        content = f"{text}|{model_name}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _get_disk_path(self, cache_key: str) -> Path:
        """获取磁盘缓存文件路径"""
        # 使用两级目录结构避免单个目录文件过多
        return self.cache_dir / cache_key[:2] / f"{cache_key}.pkl"

    def get_vector(self, text: str, model_name: str) -> Optional[np.ndarray]:
        """
        获取缓存的向量

        Args:
            text: 输入文本
            model_name: 模型名称

        Returns:
            缓存的向量，如果不存在则返回None
        """
        with self._lock:
            self._stats["total_requests"] += 1
            cache_key = self._generate_cache_key(text, model_name)

            # 1. 先检查内存缓存
            if cache_key in self._memory_cache:
                # LRU: 移动到末尾
                vector = self._memory_cache.pop(cache_key)
                self._memory_cache[cache_key] = vector
                self._stats["memory_hits"] += 1
                logger.debug(f"Memory cache hit for key: {cache_key[:8]}...")
                return vector.copy()

            # 2. 检查磁盘缓存
            if self.enable_persistence:
                disk_path = self._get_disk_path(cache_key)
                if disk_path.exists():
                    try:
                        with open(disk_path, "rb") as f:
                            vector = pickle.load(f)

                        # 加载到内存缓存
                        self._add_to_memory_cache(cache_key, vector)
                        self._stats["disk_hits"] += 1
                        logger.debug(f"Disk cache hit for key: {cache_key[:8]}...")
                        return vector.copy()
                    except Exception as e:
                        logger.warning(
                            f"Failed to load disk cache {cache_key[:8]}: {e}"
                        )
                        # 删除损坏的缓存文件
                        try:
                            disk_path.unlink()
                        except:
                            pass

            # 3. 缓存未命中
            self._stats["misses"] += 1
            logger.debug(f"Cache miss for key: {cache_key[:8]}...")
            return None

    def put_vector(self, text: str, model_name: str, vector: np.ndarray) -> None:
        """
        存储向量到缓存

        Args:
            text: 输入文本
            model_name: 模型名称
            vector: 计算得到的向量
        """
        with self._lock:
            cache_key = self._generate_cache_key(text, model_name)

            # 存储到内存缓存
            self._add_to_memory_cache(cache_key, vector.copy())

            # 异步存储到磁盘
            if self.enable_persistence:
                self._save_to_disk_async(cache_key, vector.copy())

            logger.debug(f"Cached vector for key: {cache_key[:8]}...")

    def get_batch_vectors(
        self, texts: List[str], model_name: str
    ) -> Tuple[List[Optional[np.ndarray]], List[str]]:
        """
        批量获取缓存向量

        Args:
            texts: 文本列表
            model_name: 模型名称

        Returns:
            (向量列表, 未命中的文本列表)
        """
        vectors = []
        missed_texts = []

        for text in texts:
            vector = self.get_vector(text, model_name)
            vectors.append(vector)
            if vector is None:
                missed_texts.append(text)

        return vectors, missed_texts

    def put_batch_vectors(
        self, texts: List[str], model_name: str, vectors: List[np.ndarray]
    ) -> None:
        """
        批量存储向量到缓存

        Args:
            texts: 文本列表
            model_name: 模型名称
            vectors: 向量列表
        """
        if len(texts) != len(vectors):
            raise ValueError("texts and vectors must have the same length")

        for text, vector in zip(texts, vectors):
            self.put_vector(text, model_name, vector)

    def _add_to_memory_cache(self, cache_key: str, vector: np.ndarray) -> None:
        """添加到内存缓存（LRU管理）"""
        # 如果已存在，先删除
        if cache_key in self._memory_cache:
            del self._memory_cache[cache_key]

        # 添加到末尾
        self._memory_cache[cache_key] = vector

        # LRU淘汰
        while len(self._memory_cache) > self.max_memory_size:
            oldest_key = next(iter(self._memory_cache))
            del self._memory_cache[oldest_key]
            logger.debug(f"Evicted from memory cache: {oldest_key[:8]}...")

        self._stats["cache_size"] = len(self._memory_cache)

    def _save_to_disk_async(self, cache_key: str, vector: np.ndarray) -> None:
        """异步保存到磁盘"""

        def save():
            try:
                disk_path = self._get_disk_path(cache_key)
                disk_path.parent.mkdir(parents=True, exist_ok=True)

                with open(disk_path, "wb") as f:
                    pickle.dump(vector, f)

                logger.debug(f"Saved to disk cache: {cache_key[:8]}...")
            except Exception as e:
                logger.warning(f"Failed to save disk cache {cache_key[:8]}: {e}")

        # 使用线程异步保存，不阻塞主流程
        threading.Thread(target=save, daemon=True).start()

    def clear_cache(self, model_name: Optional[str] = None) -> None:
        """
        清理缓存

        Args:
            model_name: 如果指定，只清理特定模型的缓存；否则清理所有
        """
        with self._lock:
            if model_name is None or model_name == self.model_name:
                # 清理内存缓存
                cleared_memory = len(self._memory_cache)
                self._memory_cache.clear()

                # 清理磁盘缓存
                cleared_disk = 0
                if self.enable_persistence and self.cache_dir.exists():
                    try:
                        import shutil

                        shutil.rmtree(self.cache_dir)
                        self.cache_dir.mkdir(parents=True, exist_ok=True)
                        # 估算清理的文件数（实际可能不准确）
                        cleared_disk = cleared_memory  # 简化估算
                    except Exception as e:
                        logger.warning(f"Failed to clear disk cache: {e}")

                # 重置统计
                self._stats = {
                    "memory_hits": 0,
                    "disk_hits": 0,
                    "misses": 0,
                    "total_requests": 0,
                    "cache_size": 0,
                }

                logger.info(
                    f"Cache cleared: {cleared_memory} memory entries, "
                    f"~{cleared_disk} disk entries"
                )

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            total_hits = self._stats["memory_hits"] + self._stats["disk_hits"]
            hit_rate = total_hits / max(self._stats["total_requests"], 1)

            return {
                **self._stats,
                "total_hits": total_hits,
                "hit_rate": hit_rate,
                "memory_hit_rate": self._stats["memory_hits"]
                / max(self._stats["total_requests"], 1),
                "disk_hit_rate": self._stats["disk_hits"]
                / max(self._stats["total_requests"], 1),
                "model_name": self.model_name,
                "max_memory_size": self.max_memory_size,
                "persistence_enabled": self.enable_persistence,
            }

    def get_cache_info(self) -> str:
        """获取缓存信息的可读字符串"""
        stats = self.get_stats()
        return (
            f"VectorCache[{stats['model_name']}]: "
            f"Size={stats['cache_size']}/{self.max_memory_size}, "
            f"Requests={stats['total_requests']}, "
            f"HitRate={stats['hit_rate']:.1%} "
            f"(Mem:{stats['memory_hit_rate']:.1%}, Disk:{stats['disk_hit_rate']:.1%})"
        )


# 全局缓存管理器实例
_cache_managers: Dict[str, VectorCacheManager] = {}
_cache_lock = threading.Lock()


def get_vector_cache_manager(
    model_name: str,
    max_memory_size: int = 10000,
    cache_dir: str = "./cache/vectors",
    enable_persistence: bool = True,
) -> VectorCacheManager:
    """
    获取向量缓存管理器实例（单例模式）

    Args:
        model_name: 模型名称
        max_memory_size: 最大内存缓存大小
        cache_dir: 缓存目录
        enable_persistence: 是否启用持久化

    Returns:
        VectorCacheManager实例
    """
    with _cache_lock:
        if model_name not in _cache_managers:
            _cache_managers[model_name] = VectorCacheManager(
                max_memory_size=max_memory_size,
                cache_dir=f"{cache_dir}/{model_name.replace('/', '_')}",
                enable_persistence=enable_persistence,
                model_name=model_name,
            )
        return _cache_managers[model_name]


def clear_all_caches() -> None:
    """清理所有缓存管理器"""
    with _cache_lock:
        for manager in _cache_managers.values():
            manager.clear_cache()
        _cache_managers.clear()
        logger.info("All vector caches cleared")


def get_all_cache_stats() -> Dict[str, Dict[str, Any]]:
    """获取所有缓存管理器的统计信息"""
    with _cache_lock:
        return {
            model_name: manager.get_stats()
            for model_name, manager in _cache_managers.items()
        }
