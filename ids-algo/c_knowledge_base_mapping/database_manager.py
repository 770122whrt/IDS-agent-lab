"""
全局数据库管理器

该模块负责管理应用中的所有向量数据库实例，在应用启动时预加载，
避免第一个用户请求时的加载延迟。
"""

import os
import logging
import threading
from typing import Dict, Any
from pathlib import Path

from .vector_database.unified_db import (
    IFCItemType,
    create_ifc_unified_db,
    create_ifc_db_by_type,
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

class DatabaseManager:
    """全局数据库管理器，负责预加载和管理所有向量数据库"""

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化数据库管理器"""
        if not DatabaseManager._initialized:
            with DatabaseManager._lock:
                if not DatabaseManager._initialized:
                    self._databases: Dict[str, Any] = {}
                    self._kb_manager = None  # 延迟初始化
                    DatabaseManager._initialized = True
                    logger.info("数据库管理器初始化完成")

    async def initialize_databases(self) -> None:
        """异步初始化所有数据库（在应用启动时调用）"""
        try:
            logger.info("开始预加载向量数据库...")

            # 使用标准化的数据库路径，不依赖环境变量
            resources_dir = BASE_DIR / "resources"
            entity_db_path = resources_dir / "entity_db.json"

            # 如果标准文件不存在，尝试查找可用的entity数据库文件
            if not entity_db_path.exists():
                # 查找任何entity相关的数据库文件
                for candidate in resources_dir.glob("*entity*.json"):
                    if candidate.is_file():
                        entity_db_path = candidate
                        logger.info(f"使用找到的entity数据库文件: {entity_db_path}")
                        break
                else:
                    logger.warning("未找到entity数据库文件，将创建空数据库")

            # 1. 加载主要的统一数据库
            await self._load_main_database(entity_db_path)

            # 2. 加载其他类型的数据库（如果存在）
            await self._load_additional_databases()

            logger.info("所有数据库预加载完成")

        except Exception as e:
            logger.error(f"数据库预加载失败: {str(e)}")
            # 即使失败也要确保基本功能可用
            await self._ensure_fallback_databases()

    async def _load_main_database(self, db_path: str) -> None:
        """加载主要的统一数据库"""
        try:
            if os.path.exists(db_path):
                logger.info(f"加载主要数据库: {db_path}")
                db = create_ifc_unified_db(db_path=db_path)
                self._databases["main"] = db
                self._databases["entity"] = db  # 兼容旧代码
                logger.info(f"主要数据库加载成功，包含 {len(db.items)} 个项目")
            else:
                logger.warning(f"主要数据库文件不存在: {db_path}")
                # 创建空数据库
                db = create_ifc_unified_db()
                self._databases["main"] = db
                self._databases["entity"] = db
        except Exception as e:
            logger.error(f"加载主要数据库失败: {str(e)}")
            # 创建空数据库作为回退
            db = create_ifc_unified_db()
            self._databases["main"] = db
            self._databases["entity"] = db

    async def _load_additional_databases(self) -> None:
        """加载其他类型的数据库"""
        base_dir = BASE_DIR / "resources"

        # 定义需要加载的数据库类型
        db_types = [
            IFCItemType.PROPERTY,
            IFCItemType.MATERIAL,
            IFCItemType.ATTRIBUTE,
            IFCItemType.PART_OF,
            IFCItemType.CLASSIFICATION,
        ]

        for item_type in db_types:
            try:
                db_file = base_dir / f"{item_type.value}_db.json"
                if db_file.exists():
                    logger.info(f"加载 {item_type.value} 数据库: {db_file}")
                    db = create_ifc_db_by_type(item_type, db_path=str(db_file))
                    self._databases[item_type.value] = db
                    logger.info(f"{item_type.value} 数据库加载成功，包含 {len(db.items)} 个项目")
                else:
                    logger.debug(f"{item_type.value} 数据库文件不存在: {db_file}")
                    # 创建空数据库
                    db = create_ifc_db_by_type(item_type)
                    self._databases[item_type.value] = db
            except Exception as e:
                logger.error(f"加载 {item_type.value} 数据库失败: {str(e)}")
                # 创建空数据库作为回退
                db = create_ifc_db_by_type(item_type)
                self._databases[item_type.value] = db

    async def _ensure_fallback_databases(self) -> None:
        """确保基本数据库可用（回退机制）"""
        logger.info("确保回退数据库可用...")

        # 确保主数据库存在
        if "main" not in self._databases:
            self._databases["main"] = create_ifc_unified_db()
            self._databases["entity"] = self._databases["main"]

        logger.info("回退数据库设置完成")

    def get_database(self, db_type: str = "main") -> Any:
        """获取指定类型的数据库

        Args:
            db_type: 数据库类型，如 'main', 'entity', 'attribute' 等

        Returns:
            相应的数据库实例
        """
        if db_type in self._databases:
            return self._databases[db_type]

        # 如果请求的数据库不存在，返回主数据库
        logger.warning(f"请求的数据库类型不存在: {db_type}，返回主数据库")
        return self._databases.get("main")


# 全局数据库管理器实例
db_manager = DatabaseManager()
