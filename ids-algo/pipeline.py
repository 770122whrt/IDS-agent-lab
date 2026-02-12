import sys
import os
import json

# 引入各个模块
# 确保你在 ids-algo 目录下运行，或者设置了 PYTHONPATH
from a_structured_parser import entry as step_a
from b_facet_classifier import entry as step_b
from c_knowledge_base_mapping import entry as step_c
from d_constrains import entry as step_d
from e_ids_builder import entry as step_e

def run_ids_pipeline(text_content: str):
    """
    执行完整的 IDS 生成流水线
    Input: 原始文本字符串
    Output: 最终的 JSON 结果
    """
    print("--- 1. Starting Structured Parsing ---")
    data_a = step_a.run(text_content) # 假设 entry.run 接受文本返回中间结构

    print("--- 2. Starting Facet Classification ---")
    data_b = step_b.run(data_a)

    print("--- 3. Starting Knowledge Base Mapping ---")
    data_c = step_c.run(data_b)

    print("--- 4. Starting Constraint Extraction ---")
    data_d = step_d.run(data_c)

    print("--- 5. Starting IDS Builder ---")
    final_json = step_e.run(data_d)
    
    return final_json