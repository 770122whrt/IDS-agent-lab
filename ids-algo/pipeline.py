import asyncio
import logging
import time
from typing import Tuple, Dict, Any

# 引入各个模块的核心入口
# Step A
from a_structured_parser import runStructuredParser
# Step B
from b_facet_classifier import runFacetClassifier
# Step C
from c_knowledge_base_mapping import runKnowledgeBaseMapping
from c_knowledge_base_mapping.data_structures import MappedFacet
# Step D
from d_constrains import runConstraintExtraction
# Step E
from e_ids_builder.entry import runIDSBuilder

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ids_pipeline")

async def run_ids_pipeline(text_content: str, return_timing: bool = False, return_stage_outputs: bool = False) -> Tuple[Dict[str, Any], Dict[str, float], Dict[str, Any]]:
    """
    执行完整的 IDS 生成流水线 (Memory-Only Version)
    逻辑完全对应 tests/a.py -> tests/e.py

    Args:
        text_content: 输入的自然语言需求文本
        return_timing: 是否返回计时数据（默认False保持向后兼容）
        return_stage_outputs: 是否返回各阶段的详细输出（默认False）

    Returns:
        如果 return_timing=True 且 return_stage_outputs=True: (result, timing_data, stage_outputs)
        如果 return_timing=True: (result, timing_data, {})
        如果 return_timing=False: result (向后兼容)
    """
    timing = {}
    stage_outputs = {}
    start_total = time.perf_counter()

    try:
        # --- Step A: 结构化解析 (Structured Parser) ---
        logger.info("[Step A] Running Structured Parser...")
        start_a = time.perf_counter()
        res_a = await runStructuredParser(text_content)
        timing["stage_a"] = time.perf_counter() - start_a

        if return_stage_outputs:
            stage_outputs["stage_a"] = {
                "objects": [{"raw_text": obj.raw_text, "object_type": obj.object_type, "modifiers": obj.modifiers, "confidence": obj.confidence} for obj in getattr(res_a, 'building_objects', [])] if hasattr(res_a, 'building_objects') else [],
                "properties": [{"raw_text": prop.raw_text, "property_name": prop.property_name, "constraint_text": prop.constraint_text, "confidence": prop.confidence} for prop in getattr(res_a, 'property_descriptions', [])] if hasattr(res_a, 'property_descriptions') else [],
                "materials": [{"raw_text": mat.raw_text, "material_name": mat.material_name, "specifications": mat.specifications, "confidence": mat.confidence} for mat in getattr(res_a, 'material_requirements', [])] if hasattr(res_a, 'material_requirements') else []
            }

        # --- Step B: 方面分类 (Facet Classifier) ---
        logger.info("[Step B] Running Facet Classifier...")
        start_b = time.perf_counter()
        # 注意: runFacetClassifier 接受的是 Step A 的结果对象
        res_b = await runFacetClassifier(res_a)
        timing["stage_b"] = time.perf_counter() - start_b

        if return_stage_outputs:
            # FacetClassification has 6 separate candidate lists, not a single 'facets' field
            all_facets = []
            if hasattr(res_b, 'entity_candidates'):
                all_facets.extend([{"text": f.source_text, "type": f.facet_type, "confidence": f.confidence} for f in res_b.entity_candidates])
            if hasattr(res_b, 'property_candidates'):
                all_facets.extend([{"text": f.source_text, "type": f.facet_type, "confidence": f.confidence} for f in res_b.property_candidates])
            if hasattr(res_b, 'attribute_candidates'):
                all_facets.extend([{"text": f.source_text, "type": f.facet_type, "confidence": f.confidence} for f in res_b.attribute_candidates])
            if hasattr(res_b, 'material_candidates'):
                all_facets.extend([{"text": f.source_text, "type": f.facet_type, "confidence": f.confidence} for f in res_b.material_candidates])
            if hasattr(res_b, 'classification_candidates'):
                all_facets.extend([{"text": f.source_text, "type": f.facet_type, "confidence": f.confidence} for f in res_b.classification_candidates])
            if hasattr(res_b, 'partof_candidates'):
                all_facets.extend([{"text": f.source_text, "type": f.facet_type, "confidence": f.confidence} for f in res_b.partof_candidates])

            stage_outputs["stage_b"] = {
                "facets": all_facets,
                "entity_count": len(res_b.entity_candidates) if hasattr(res_b, 'entity_candidates') else 0,
                "property_count": len(res_b.property_candidates) if hasattr(res_b, 'property_candidates') else 0,
                "material_count": len(res_b.material_candidates) if hasattr(res_b, 'material_candidates') else 0
            }

        # --- Step C: 知识库映射 (KB Mapping) ---
        logger.info("[Step C] Running Knowledge Base Mapping...")
        start_c = time.perf_counter()
        # 返回的是 List[MappedFacet] 对象
        facets: list[MappedFacet] = await runKnowledgeBaseMapping(res_b)
        timing["stage_c"] = time.perf_counter() - start_c
        logger.info(f"   Generated {len(facets)} facets.")

        # Always capture Stage C mapping results (for accuracy evaluation)
        stage_c_mappings = []
        for facet in facets:
            mapping = {
                "facet_type": getattr(facet, 'facet_type', ''),
                "original_text": getattr(facet, 'original_text', ''),
                "mapped_name": getattr(facet, 'mapped_name', ''),
                "confidence": getattr(facet, 'confidence', 0.0),
                "property_set": getattr(facet, 'property_set', None),
                "entity_name": getattr(facet, 'entity_name', None),
                "constraints": getattr(facet, 'constraints', []),
                "additional_data": getattr(facet, 'additional_data', None)
            }

            # Serialize ifc_item if present
            if hasattr(facet, 'ifc_item') and facet.ifc_item:
                ifc_item = facet.ifc_item
                if hasattr(ifc_item, 'to_dict'):
                    mapping["ifc_item"] = ifc_item.to_dict()
                else:
                    # Fallback: manually extract fields
                    mapping["ifc_item"] = {
                        "name": getattr(ifc_item, 'name', ''),
                        "definition": getattr(ifc_item, 'definition', ''),
                        "ifc_version": getattr(ifc_item, 'ifc_version', ''),
                        "item_type": getattr(ifc_item, 'item_type', '')
                    }
            else:
                mapping["ifc_item"] = None

            stage_c_mappings.append(mapping)

        stage_outputs["stage_c_mappings"] = stage_c_mappings

        # --- Step D: 约束提取 (Constraint Extraction) ---
        logger.info("[Step D] Running Constraint Extraction...")
        start_d = time.perf_counter()
        all_constraints = []

        # tests/d.py 中的逻辑是遍历 facet 列表进行提取
        for facet in facets:
            # 注意: runConstraintExtraction 似乎接受列表作为输入
            constraints = runConstraintExtraction([facet])

            # 处理返回可能是单个对象或列表的情况
            if isinstance(constraints, list):
                all_constraints.extend(constraints)
            else:
                all_constraints.append(constraints)

        timing["stage_d"] = time.perf_counter() - start_d
        logger.info(f"   Extracted {len(all_constraints)} constraints.")

        if return_stage_outputs:
            stage_outputs["stage_d"] = {
                "constraints": [{"text": getattr(c, 'original_text', ''), "type": getattr(c, 'constraint_type', '')} for c in all_constraints]
            }

        # --- Step E (Part 1): 数据缝合 (Merge Logic) ---
        # 这是 tests/e.py 中的关键逻辑：通过文本匹配把 Constraint 塞回 Facet
        logger.info("[Step E-1] Merging Constraints into Facets...")
        start_e1 = time.perf_counter()
        merged_count = 0

        for facet in facets:
            # 确保 constraints 列表初始化
            if not hasattr(facet, 'constraints') or facet.constraints is None:
                facet.constraints = []

            facet_text = (facet.original_text or "").strip().lower()

            for constr in all_constraints:
                constr_text = (constr.original_text or "").strip().lower()

                # tests/e.py 中的核心匹配逻辑
                if constr_text and facet_text and (constr_text in facet_text or facet_text in constr_text):
                    facet.constraints.append(constr)
                    merged_count += 1

        timing["stage_e_merge"] = time.perf_counter() - start_e1
        logger.info(f"   Merged {merged_count} constraints.")

        # --- Step E (Part 2): 构建 IDS (IDS Builder) ---
        logger.info("[Step E-2] Building Final IDS JSON...")
        start_e2 = time.perf_counter()

        # 调用 e_ids_builder
        final_json = await runIDSBuilder(
            facets,
            text=text_content,
            include_metadata=False
        )

        timing["stage_e_build"] = time.perf_counter() - start_e2
        timing["total"] = time.perf_counter() - start_total

        logger.info("[OK] Pipeline completed successfully.")

        if return_timing:
            return final_json, timing, stage_outputs
        else:
            return final_json

    except Exception as e:
        timing["total"] = time.perf_counter() - start_total
        timing["error"] = str(e)
        logger.error(f"[ERROR] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

        if return_timing:
            return None, timing, stage_outputs
        else:
            raise e