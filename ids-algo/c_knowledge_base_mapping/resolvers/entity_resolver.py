"""
Entity解析器
使用静态知识库解析IFC实体，LLM选择最佳匹配
"""

import logging
from typing import Optional, Dict, Any, List, Tuple

from openrouter.client import OpenRouterClient
from openrouter.llm_response_handler import parse_llm_json_response
from prompts.prompt_selector import select_prompt

logger = logging.getLogger(__name__)


class EntityResolver:
    """Entity解析器 - 使用静态entities.db + LLM选择"""

    def __init__(self, database_manager):
        self.database_manager = database_manager
        self.llm_client = OpenRouterClient()

    async def resolve(
        self, query_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        解析Entity

        Args:
            query_text: 查询文本
            context: 上下文，包含pipeline_memory等

        Returns:
            解析结果
        """
        try:
            db = self.database_manager.get_database("entity")
            if db:
                ifc_version = context.get("ifc_version") if context else None

                # 从context中获取pipeline memory
                pipeline_memory = context.get("pipeline_memory")
                original_text = ""
                if pipeline_memory:
                    original_text = pipeline_memory.user_input

                # 向量搜索TopK - 默认搜索所有IFC版本
                ifc_versions_filter = [ifc_version] if ifc_version else None
                results = db.search(query_text, top_k=5, ifc_versions=ifc_versions_filter)
                if not results:
                    return None

                # LLM选择最佳匹配
                best_match = await self._llm_select_best_match(
                    query_text, results, ifc_version, original_text, pipeline_memory
                )

                if best_match:
                    ifc_item, similarity = best_match
                    return {
                        "mapped_name": ifc_item.name,
                        "confidence": similarity,
                        "ifc_item": ifc_item,
                        "source": "static_kb_llm_selected",
                    }

        except Exception as e:
            logger.error(f"Entity resolution failed: {str(e)}")

        return None

    async def _llm_select_best_match(
        self,
        query_text: str,
        candidates: List[Tuple[Any, float]],
        ifc_version: str,
        original_text: str = "",
        pipeline_memory=None,
    ) -> Optional[Tuple[Any, float]]:
        """
        LLM选择最佳匹配

        Args:
            query_text: 原始查询文本
            candidates: 候选实体列表 [(ifc_item, distance), ...]
            ifc_version: IFC版本
            original_text: 完整的用户输入原文
            pipeline_memory: Pipeline记忆系统，包含完整的处理上下文

        Returns:
            最佳匹配的实体和相似度
        """
        try:
            # 构建候选实体信息
            candidate_info = []
            for ifc_item, similarity in candidates:
                # Note: search() returns similarity (dot product), not distance
                candidate_info.append(
                    {
                        "name": ifc_item.name,
                        "definition": getattr(ifc_item, "definition", ""),
                        "similarity": similarity,
                    }
                )

            # 构建LLM提示
            prompt = self._build_selection_prompt(
                query_text, candidate_info, ifc_version, original_text, pipeline_memory
            )

            # 调用LLM
            response = await self.llm_client.generate(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=3000,
            )

            # 解析LLM响应
            if response:
                content = None
                if hasattr(response, "content"):
                    content = response.content
                elif hasattr(response, "choices") and response.choices:
                    content = response.choices[0].message.content
                elif isinstance(response, dict):
                    content = response.get("content") or response.get("choices", [{}])[
                        0
                    ].get("message", {}).get("content")

                if content:
                    # 使用统一的LLM响应处理器
                    fallback_structure = {"selected_entity": None, "reasoning": ""}
                    result = parse_llm_json_response(
                        content, fallback_structure, "entity selection"
                    )

                    selected_name = result.get("selected_entity")
                    if selected_name:
                        # 找到对应的候选实体
                        for ifc_item, similarity in candidates:
                            if ifc_item.name == selected_name:
                                logger.info(
                                    f"LLM selected entity: {query_text} -> {selected_name}"
                                )
                                return (ifc_item, similarity)

        except Exception as e:
            logger.error(f"LLM entity selection failed: {str(e)}")

        return None

    def _build_selection_prompt(
        self,
        query_text: str,
        candidates: List[Dict[str, Any]],
        ifc_version: str,
        original_text: str = "",
        pipeline_memory=None,
    ) -> str:
        """构建LLM选择提示"""

        candidates_text = "\n".join(
            [
                f"{i+1}. {c['name']} (similarity: {c['similarity']:.3f})\n   Definition: {c['definition']}"
                for i, c in enumerate(candidates)
            ]
        )

        # 构建完整的上下文信息
        context_sections = []

        # 1. 原始用户输入
        if original_text:
            context_sections.append(f'**COMPLETE USER INPUT**: "{original_text}"')
            context_sections.append(f'**CURRENT ENTITY QUERY**: "{query_text}"')

        # 2. Pipeline处理上下文
        if pipeline_memory:
            # 获取前面的处理步骤信息
            previous_steps = []
            for step in pipeline_memory.steps[-3:]:  # 最近3个步骤
                if step.output_data:
                    step_summary = f"Step {step.step_number}: {step.step_name}"
                    if hasattr(step.output_data, "components"):
                        step_summary += (
                            f" - Found {len(step.output_data.components)} components"
                        )
                    elif hasattr(step.output_data, "facets"):
                        step_summary += (
                            f" - Classified {len(step.output_data.facets)} facets"
                        )
                    previous_steps.append(step_summary)

            if previous_steps:
                context_sections.append("**PIPELINE CONTEXT**:")
                context_sections.extend(previous_steps)

        context_text = "\n".join(context_sections) if context_sections else ""
              
        prompt_template = select_prompt("entity_resolver")
        
        prompt = prompt_template.format(
            context_text=context_text,
            ifc_version=ifc_version,
            candidates_text=candidates_text,
            query_text=query_text
        )

        return prompt
