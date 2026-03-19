"""
向量模型管理器

提供单例模式的向量模型管理，避免重复加载
"""

import logging
from typing import Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorModelManager:
    """向量模型管理器（单例模式）"""

    _instance = None
    _model = None
    _model_name = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_model(
        self, model_name: str = "BAAI/bge-m3"
    ) -> Optional[SentenceTransformer]:
        """获取向量模型实例

        Args:
            model_name: 模型名称

        Returns:
            SentenceTransformer实例或None
        """
        # 如果已经加载了相同的模型，直接返回
        if self._model is not None and self._model_name == model_name:
            return self._model

        # 如果模型名称不同，需要重新加载
        if self._model_name != model_name:
            logger.info(f"模型名称改变，从 {self._model_name} 切换到 {model_name}")
            self._model = None
            self._model_name = None

        # 加载新模型
        try:
            logger.info(f"加载向量模型: {model_name}")
            self._model = SentenceTransformer(model_name)
            self._model_name = model_name
            logger.info(f"向量模型加载成功: {model_name}")
            return self._model
        except Exception as e:
            logger.error(f"加载向量模型失败: {str(e)}")
            # 尝试回退到默认模型
            if model_name != "all-MiniLM-L6-v2":
                logger.warning("尝试加载默认模型: all-MiniLM-L6-v2")
                try:
                    self._model = SentenceTransformer("all-MiniLM-L6-v2")
                    self._model_name = "all-MiniLM-L6-v2"
                    logger.warning("已回退到默认模型")
                    return self._model
                except Exception as fallback_e:
                    logger.error(f"回退模型也失败: {str(fallback_e)}")
            return None

    def clear_cache(self):
        """清除缓存的模型"""
        logger.info("清除向量模型缓存")
        self._model = None
        self._model_name = None


# 全局单例实例
vector_model_manager = VectorModelManager()
