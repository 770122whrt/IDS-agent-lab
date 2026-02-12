"""
LLM响应处理器

提供统一的LLM响应解析、清理和错误处理功能。
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional  # ✅ 删除未使用的 Callable

logger = logging.getLogger(__name__)


class LLMResponseHandler:
    """
    LLM响应处理器

    提供统一的JSON解析、错误处理和响应清理功能。
    """

    def __init__(self):
        # ✅ 移除无用的 _fix_common_json_errors
        self.cleaning_strategies = [
            self._clean_markdown_blocks,
            self._extract_json_from_text,
            self._extract_largest_json_object,
        ]

    def parse_json_response(
        self,
        response: str,
        fallback_structure: Optional[Dict[str, Any]] = None,
        context: str = "LLM response",
    ) -> Dict[str, Any]:
        """
        解析LLM返回的JSON响应

        Args:
            response: LLM原始响应
            fallback_structure: 解析失败时的备用结构
            context: 上下文信息，用于日志记录

        Returns:
            解析后的字典
        """
        if not response or not response.strip():
            logger.warning(f"Empty {context}")
            return fallback_structure or {}

        # 尝试直接解析
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            logger.warning(
                f"Initial JSON parsing failed for {context}, attempting to clean response"
            )

        # 尝试各种清理策略
        for strategy in self.cleaning_strategies:
            try:
                cleaned_response = strategy(response)
                if cleaned_response and cleaned_response.strip():
                    result = json.loads(cleaned_response)
                    logger.info(
                        f"Successfully parsed {context} using {strategy.__name__}"
                    )
                    return result
            except (json.JSONDecodeError, Exception) as e:
                logger.debug(
                    f"Strategy {strategy.__name__} failed for {context}: {str(e)}"
                )
                continue

        # 所有策略都失败，记录详细错误信息
        logger.error(f"All parsing strategies failed for {context}")
        logger.error(f"Response length: {len(response)}")
        logger.error(f"Response preview: {response[:200]}...")

        # 返回备用结构
        if fallback_structure:
            logger.info(f"Using fallback structure for {context}")
            return fallback_structure
        else:
            logger.warning(
                f"No fallback structure provided for {context}, returning empty dict"
            )
            return {}

    def _clean_markdown_blocks(self, response: str) -> str:
        """
        清理Markdown代码块

        Args:
            response: 原始响应

        Returns:
            清理后的JSON字符串
        """
        # 移除markdown代码块
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end != -1:
                response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end != -1:
                response = response[start:end].strip()

        # 移除常见前缀
        prefixes_to_remove = [
            "Here's the extracted information:",
            "Based on the text, here's the structured data:",
            "The structured extraction result is:",
            "Here is the JSON:",
            "I'll extract the structured components:",
            "Here's the structured analysis:",
            "```json",
            "```",
        ]

        cleaned = response.strip()
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()

        # 移除尾部标记
        suffixes_to_remove = ["```", "```json"]
        for suffix in suffixes_to_remove:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)].strip()

        return cleaned

    def _extract_json_from_text(self, response: str) -> str:
        """
        从混合文本中提取JSON

        Args:
            response: 原始响应

        Returns:
            提取的JSON字符串
        """
        # 寻找JSON对象模式
        json_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
        matches = re.findall(json_pattern, response, re.DOTALL)

        for match in matches:
            try:
                # 测试是否为有效JSON
                json.loads(match)
                return match
            except json.JSONDecodeError:
                continue

        # 如果没找到有效JSON，尝试寻找最大的大括号包围内容
        brace_pattern = r"\{.*\}"
        match = re.search(brace_pattern, response, re.DOTALL)
        if match:
            return match.group(0)

        return response

    def _extract_largest_json_object(self, response: str) -> str:
        """
        提取最大的JSON对象

        Args:
            response: 原始响应

        Returns:
            最大的JSON对象字符串
        """
        # 找到第一个和最后一个大括号
        first_brace = response.find("{")
        last_brace = response.rfind("}")

        if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
            return response[first_brace:last_brace + 1]

        # 如果没有找到大括号，尝试数组
        first_bracket = response.find("[")
        last_bracket = response.rfind("]")

        if first_bracket != -1 and last_bracket != -1 and first_bracket < last_bracket:
            return response[first_bracket:last_bracket + 1]

        return response


# 全局实例
llm_response_handler = LLMResponseHandler()


def parse_llm_json_response(
    response: str,
    fallback_structure: Optional[Dict[str, Any]] = None,
    context: str = "LLM response",
) -> Dict[str, Any]:
    """
    便捷函数：解析LLM的JSON响应

    Args:
        response: LLM原始响应
        fallback_structure: 解析失败时的备用结构
        context: 上下文信息

    Returns:
        解析后的字典
    """
    return llm_response_handler.parse_json_response(
        response, fallback_structure, context
    )
