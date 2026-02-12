"""
Property解析器
整合了IFC API请求功能，不再依赖外部Manager
"""

import logging
import requests
import asyncio
import numpy as np
from typing import Optional, Dict, Any, List, Tuple


from openrouter.settings import settings
from ..vector_database.core.model_manager import vector_model_manager

logger = logging.getLogger(__name__)

class PropertyResolver:
    """Property解析器 - 混合数据源 (API + 向量库)"""

    def __init__(self, database_manager):
        # 不再需要 entity_property_manager 参数
        self.database_manager = database_manager
        self.model = vector_model_manager.get_model()

    async def resolve_batch(
        self, queries: List[Tuple[str, Optional[Dict[str, Any]]]]
    ) -> List[Optional[Dict[str, Any]]]:
        """
        批次解析Properties
        
        Args:
            queries: 查询列表，每个元素为 (query_text, context) 元组
            
        Returns:
            解析结果列表，与输入queries顺序对应
        """
        if not queries:
            return []
            
        try:
            # 分离查询文本和上下文
            query_texts = [q[0] for q in queries]
            
            # 批量计算embedding
            query_embeddings = self._batch_encode(query_texts)
            
            # 并行处理每个查询
            tasks = []
            for i, (query_text, context) in enumerate(queries):
                task = self._resolve_single_with_embedding(
                    query_text, context, query_embeddings[i]
                )
                tasks.append(task)
                
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理异常情况
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Batch resolve error: {str(result)}")
                    processed_results.append(None)
                else:
                    processed_results.append(result)
                    
            return processed_results
            
        except Exception as e:
            logger.error(f"Batch property resolution failed: {str(e)}")
            return [None] * len(queries)

    async def resolve(
        self, query_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        解析Property

        Args:
            query_text: 查询文本
            context: 上下文（包含entity_name等）

        Returns:
            解析结果
        """
        results = await self.resolve_batch([(query_text, context)])
        return results[0] if results else None

    async def _resolve_single_with_embedding(
        self, 
        query_text: str, 
        context: Optional[Dict[str, Any]], 
        query_embedding: np.ndarray
    ) -> Optional[Dict[str, Any]]:
        """
        使用预计算的embedding解析单个Property
        
        Args:
            query_text: 查询文本
            context: 上下文
            query_embedding: 预计算的查询embedding
            
        Returns:
            解析结果
        """
        try:
            # 1. 优先使用IFC API（如果有Entity上下文）
            if context and "entity_name" in context:
                entity_name = context["entity_name"]
                ifc_version = context.get("ifc_version", "IFC4")

                # --- 变化点：直接调用内部方法获取属性集 ---
                property_sets = self._fetch_property_sets_from_api(
                    entity_name, [ifc_version]
                )

                if property_sets:
                    best_match = self._find_best_property_match_batch(
                        query_embedding, property_sets
                    )
                    if best_match:
                        return best_match

            # 2. 使用静态知识库 (Fallback)
            db = self.database_manager.get_database("property")
            if db:
                results = db.search(
                    query_text, top_k=5, ifc_versions=None, item_types=None
                )
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
            logger.error(f"Property resolution failed: {str(e)}")

        return None

    # -------------------------------------------------------------------------
    #  原本在 ifc_api_client.py 中的逻辑，现在并入此处 (Private Methods)
    # -------------------------------------------------------------------------

    def _fetch_property_sets_from_api(
        self, entity_name: str, ifc_versions: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """从外部API获取实体的属性集定义"""
        params = {
            "entityName": entity_name, 
            "schemaVersions": ifc_versions or ["IFC4"]
        }
        logger.info(f"获取实体 '{entity_name}' 的属性集和属性，版本: {ifc_versions or ['IFC4']}")
        # 使用配置中的URL
        url = settings.ifc_entity_pset_api_url
        
        try:
            # 设置较短的超时，避免阻塞主流程
            response = requests.post(url, json=params, timeout=5)
            response.raise_for_status()
            result = response.json()
            if result:
                logger.info(f"获取到实体 '{entity_name}' 的属性集和属性: {len(result)} 个版本")
            else:
                logger.debug(f"未找到实体 '{entity_name}' 的属性集和属性")
            return result or {}
        except requests.exceptions.ConnectionError:
            logger.warning(f"无法连接到API服务: {url} - 这是可选服务，将使用默认行为")
            return {}
        except requests.exceptions.Timeout:
            logger.warning(f"API请求超时: {url}")
            return {}
        except requests.exceptions.RequestException as e:
            logger.error(f"发送API请求时出错: {e}")
            return {}

    # -------------------------------------------------------------------------
    #  辅助方法
    # -------------------------------------------------------------------------

    def _batch_encode(self, texts: List[str]) -> List[np.ndarray]:
        """批量编码文本为embedding向量"""
        try:
            if not texts:
                return []
            
            # 使用模型进行编码
            embeddings = self.model.encode(texts)
            
            if isinstance(embeddings, np.ndarray) and len(embeddings.shape) == 2:
                return [embeddings[i] for i in range(embeddings.shape[0])]
            else:
                return [embeddings] if len(texts) == 1 else []
                
        except Exception as e:
            logger.warning(f"Batch encoding failed: {str(e)}")
            return [np.zeros(384) for _ in texts] # Fallback

    def _find_best_property_match_batch(
        self, 
        query_embedding: np.ndarray, 
        property_sets: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """批次查找最佳Property匹配"""
        try:
            property_candidates = []
            
            # 展平结构：提取所有可能的属性
            for version, psets_data in property_sets.items():
                if isinstance(psets_data, list):
                    for pset in psets_data:
                        if isinstance(pset, dict) and "properties" in pset:
                            for prop in pset["properties"]:
                                if isinstance(prop, dict):
                                    property_candidates.append({
                                        "prop": prop,
                                        "pset": pset,
                                        "name": prop.get("name", ""),
                                        "definition": prop.get("definition", "")
                                    })
            
            if not property_candidates:
                return None
                
            # 准备待编码文本
            all_texts = []
            for candidate in property_candidates:
                all_texts.extend([candidate["name"], candidate["definition"]])
                
            all_embeddings = self._batch_encode(all_texts)
            
            best_match = None
            best_score = 0.0
            
            for i, candidate in enumerate(property_candidates):
                name_emb = all_embeddings[i * 2] if i * 2 < len(all_embeddings) else None
                def_emb = all_embeddings[i * 2 + 1] if i * 2 + 1 < len(all_embeddings) else None
                
                name_score = self._calculate_cosine_similarity(query_embedding, name_emb)
                definition_score = self._calculate_cosine_similarity(query_embedding, def_emb)
                
                # 组合分数
                combined_score = definition_score * 0.7 + name_score * 0.3
                
                if combined_score > best_score and combined_score > 0.5:
                    best_score = combined_score
                    best_match = {
                        "mapped_name": candidate["prop"]["name"],
                        "confidence": combined_score,
                        "ifc_item": candidate["prop"],
                        "property_set": candidate["pset"].get("propertySetName", "Unknown"),
                        "source": "ifc_api",
                    }
            
            return best_match
            
        except Exception as e:
            logger.error(f"Batch property matching failed: {str(e)}")
            return None

    def _calculate_cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """计算余弦相似度 (原 _calculate_similarity_with_embeddings)"""
        if v1 is None or v2 is None:
            return 0.0
        try:
            dot = np.dot(v1, v2)
            norm = np.linalg.norm(v1) * np.linalg.norm(v2)
            if norm == 0: return 0.0
            return float(max(0, min(1, dot / norm)))
        except:
            return 0.0