import asyncio
import logging

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

async def run_ids_pipeline(text_content: str):
    """
    执行完整的 IDS 生成流水线 (Memory-Only Version)
    逻辑完全对应 tests/a.py -> tests/e.py
    """
    try:
        # --- Step A: 结构化解析 (Structured Parser) ---
        logger.info("▶️ [Step A] Running Structured Parser...")
        res_a = await runStructuredParser(text_content)
        
        # --- Step B: 方面分类 (Facet Classifier) ---
        logger.info("▶️ [Step B] Running Facet Classifier...")
        # 注意: runFacetClassifier 接受的是 Step A 的结果对象
        res_b = await runFacetClassifier(res_a)

        # --- Step C: 知识库映射 (KB Mapping) ---
        logger.info("▶️ [Step C] Running Knowledge Base Mapping...")
        # 返回的是 List[MappedFacet] 对象
        facets: list[MappedFacet] = await runKnowledgeBaseMapping(res_b)
        logger.info(f"   Generated {len(facets)} facets.")

        # --- Step D: 约束提取 (Constraint Extraction) ---
        logger.info("▶️ [Step D] Running Constraint Extraction...")
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
        
        logger.info(f"   Extracted {len(all_constraints)} constraints.")

        # --- Step E (Part 1): 数据缝合 (Merge Logic) ---
        # 这是 tests/e.py 中的关键逻辑：通过文本匹配把 Constraint 塞回 Facet
        logger.info("▶️ [Step E-1] Merging Constraints into Facets...")
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
        
        logger.info(f"   Merged {merged_count} constraints.")

        # --- Step E (Part 2): 构建 IDS (IDS Builder) ---
        logger.info("▶️ [Step E-2] Building Final IDS JSON...")
        
        # 调用 e_ids_builder
        final_json = await runIDSBuilder(
            facets, 
            text=text_content,
            include_metadata=False
        )

        logger.info("✅ Pipeline completed successfully.")
        return final_json

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        raise e