from openrouter.settings import Settings
from b_facet_classifier import FacetClassification
from .data_structures import MappedFacet
from .database_manager import DatabaseManager
from .knowledge_mapping_strategy import KnowledgeBaseMappingOrchestrator, KnowledgeBaseMappingStrategy

import logging
import sys
# 配置全局日志
logging.basicConfig(
    level=logging.INFO,  # <--- 关键！把默认的 WARNING 改为 INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", # 让日志带上时间和模块名
    handlers=[
        logging.StreamHandler(sys.stdout) # 确保输出到控制台
    ]
)


async def runKnowledgeBaseMapping(classification_result: FacetClassification) -> list[MappedFacet]:
    try:
        settings = Settings()
        # Step 3: Mapping
        database_manager = DatabaseManager()
        await database_manager.initialize_databases()  # 初始化所有向量数据库

        kb_mapping_orchestrator = KnowledgeBaseMappingOrchestrator(
            database_manager=database_manager,
            settings=settings,
            strategy=KnowledgeBaseMappingStrategy()
        )

        # 获取映射结果列表
        mapped_facets: list[MappedFacet] = await kb_mapping_orchestrator.map_facets_clean(
            classification=classification_result,
            ifc_version="IFC4"
        )

        # 返回整个列表，如果为空也返回空列表
        return mapped_facets

    except Exception as e:
        logging.error(f"Error in knowledge base mapping: {e}")
        # 返回包含错误信息的 MappedFacet 放在列表中
        return [
            MappedFacet(
                facet_type="error",
                original_text="",
                mapped_name="",
                confidence=0.0,
                errors=[str(e)]
            )
        ]
