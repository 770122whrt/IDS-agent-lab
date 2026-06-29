"""
知识库映射策略
重新设计的分阶段知识库映射逻辑
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from b_facet_classifier import  FacetClassification,FacetCandidate
from .data_structures import MappedFacet,KnowledgeBaseMappingStrategy

from .resolvers.resolver_factory import ResolverFactory
logger = logging.getLogger(__name__)



class KnowledgeBaseMappingOrchestrator:
    """知识库映射编排器 - 管理分阶段映射逻辑"""

    def __init__(
        self,
        database_manager,
        settings,
        strategy: KnowledgeBaseMappingStrategy = None,
    ):
        self.database_manager = database_manager
        self.settings = settings
        self.strategy = strategy or KnowledgeBaseMappingStrategy()


        self.resolvers = ResolverFactory.create_resolvers(
            database_manager=database_manager,
        )

        # 映射结果缓存，用于后续阶段的上下文
        self.mapped_entities: Dict[str, MappedFacet] = {}
        self.mapped_properties: List[MappedFacet] = []
        self.mapped_materials: List[MappedFacet] = []

        logger.info("KnowledgeBaseMappingOrchestrator initialized with clean resolvers")

    async def _map_facets_with_resolver(
        self,
        facet_type: str,
        candidates: List[FacetCandidate],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[MappedFacet]:
        """使用解析器映射facets"""
        mapped_facets = []

        if facet_type not in self.resolvers:
            logger.warning(f"No resolver found for facet type: {facet_type}")
            return mapped_facets

        resolver = self.resolvers[facet_type]

        for candidate in candidates:
            try:
                result = await resolver.resolve(candidate.source_text, context)

                if result:
                    # 提取resolver的额外数据
                    additional_data = {}
                    for key, value in result.items():
                        if key not in [
                            "mapped_name",
                            "confidence",
                            "ifc_item",
                            "property_set",
                            "source",
                        ]:
                            additional_data[key] = value

                    mapped_facet = MappedFacet(
                        facet_type=facet_type,
                        original_text=candidate.source_text,
                        mapped_name=result["mapped_name"],
                        confidence=result["confidence"],
                        ifc_item=result["ifc_item"],
                        property_set=result.get("property_set"),
                        entity_name=context.get("entity_name") if context else None,
                        constraints=[],
                        additional_data=additional_data if additional_data else None,
                    )
                    mapped_facets.append(mapped_facet)

                    logger.info(
                        f"Mapped {facet_type}: '{candidate.source_text}' -> '{result['mapped_name']}' (confidence: {result['confidence']:.3f}, source: {result['source']})"
                    )
                else:
                    logger.warning(
                        f"Failed to map {facet_type}: '{candidate.source_text}'"
                    )

            except Exception as e:
                logger.error(
                    f"{facet_type} mapping failed for '{candidate.source_text}': {str(e)}"
                )

        return mapped_facets

    async def map_facets_clean(
        self,
        classification: FacetClassification,
        ifc_version: str = "IFC4",
        dictionary_uris: Optional[List[str]] = None,
        pipeline_memory=None,
    ) -> List[MappedFacet]:
        """
        使用干净解析器进行facet映射

        Args:
            classification: 分类结果
            ifc_version: IFC版本
            dictionary_uris: bSDD Dictionary URI列表
            pipeline_memory: Pipeline记忆系统，包含完整的处理上下文

        Returns:
            映射后的facets列表
        """
        logger.info("Starting clean facet mapping")
        all_mapped_facets = []

        # 1. Entity映射 (优先级最高，为其他映射提供上下文)
        if classification.entity_candidates:
            # 为Entity映射传递完整上下文，包括pipeline memory
            entity_context = {
                "ifc_version": ifc_version,
                "dictionary_uris": dictionary_uris,
                "pipeline_memory": pipeline_memory,
            }
            entity_facets = await self._map_facets_with_resolver(
                "entity", classification.entity_candidates, entity_context
            )
            all_mapped_facets.extend(entity_facets)
            self.mapped_entities = {facet.mapped_name: facet for facet in entity_facets}

        # 2. Property映射 (使用Entity上下文)
        if classification.property_candidates:
            # 构建Entity上下文
            entity_context = {}
            if self.mapped_entities:
                entity_context = {
                    "entity_name": list(self.mapped_entities.keys())[0],
                    "ifc_version": ifc_version,
                    "dictionary_uris": dictionary_uris,
                }
            property_facets = await self._map_facets_with_resolver(
                "property", classification.property_candidates, entity_context
            )
            all_mapped_facets.extend(property_facets)
            self.mapped_properties = property_facets

        # 3. Material映射 (相对独立)
        if classification.material_candidates:
            material_context = {
                "ifc_version": ifc_version,
                "dictionary_uris": dictionary_uris,
            }
            material_facets = await self._map_facets_with_resolver(
                "material", classification.material_candidates, material_context
            )
            all_mapped_facets.extend(material_facets)
            self.mapped_materials = material_facets

        # 4. Classification映射
        if classification.classification_candidates:
            classification_context = {
                "ifc_version": ifc_version,
                "dictionary_uris": dictionary_uris,
            }
            classification_facets = await self._map_facets_with_resolver(
                "classification",
                classification.classification_candidates,
                classification_context,
            )
            all_mapped_facets.extend(classification_facets)

        # 5. Attribute映射
        if classification.attribute_candidates:
            attribute_context = {
                "ifc_version": ifc_version,
                "dictionary_uris": dictionary_uris,
            }
            attribute_facets = await self._map_facets_with_resolver(
                "attribute", classification.attribute_candidates, attribute_context
            )
            all_mapped_facets.extend(attribute_facets)

        # 6. PartOf映射
        if classification.partof_candidates:
            partof_context = {
                "ifc_version": ifc_version,
                "dictionary_uris": dictionary_uris,
            }
            partof_facets = await self._map_facets_with_resolver(
                "partof", classification.partof_candidates, partof_context
            )
            all_mapped_facets.extend(partof_facets)

        logger.info(f"Clean mapping completed: {len(all_mapped_facets)} facets mapped")
        return all_mapped_facets
