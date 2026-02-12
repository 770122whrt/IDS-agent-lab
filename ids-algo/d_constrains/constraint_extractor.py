"""
Constraint extraction for IDS value restrictions

Extracts and parses value constraints from natural language text into structured restriction formats
IDS值限制的约束提取

从自然语言文本中提取和解析值约束，转换为结构化限制格式
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union

from .data_structures import (
    RestrictionType,
    ValueRestriction,
    BoundsRestriction,
    EnumerationRestriction,
    PatternRestriction,
    LengthRestriction,
)

logger = logging.getLogger(__name__)



class ConstraintExtractor:
    """Extracts numeric bounds, enumerations, regex patterns, and length constraints."""

    def __init__(self):

        # 改进：pattern 匹配更宽松（支持空格、小写字母、管道符等）
        self.pattern_patterns = [
            r"matching\s+the\s+pattern\s+([^\n\r;,.]+)",
            r"(?:format|pattern):?\s+([^\n\r;,.]+)",
            r"must\s+match\s+([^\n\r;,.]+)",
            r"follows?\s+pattern\s+([^\n\r;,.]+)"
        ]

        # 数值边界正则（不变）
        self.numeric_patterns = [
            r"([><=]+)\s*(\d+(?:\.\d+)?)\s*(\w+)?",
            r"(?:between|from)\s+(\d+(?:\.\d+)?)\s+(?:and|to)\s+(\d+(?:\.\d+)?)\s*(\w+)?",
            r"(?:minimum|maximum|min|max|at least|no more than)\s+(\d+(?:\.\d+)?)\s*(\w+)?",
            r"(?:minimum|maximum|min|max|at least|no more than)\s+\w+\s+of\s+(\d+(?:\.\d+)?)\s*(\w+)?",
            r"(\d+(?:\.\d+)?)\s*(\w+)?\s+or\s+(?:more|less|greater|smaller)",
            r"(?:range:?\s*)?(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*(\w+)?",
        ]

        # 枚举匹配（不变）
        self.enumeration_patterns = [
            r'"([^"]+)"(?:\s*,\s*"([^"]+)")*(?:\s*,?\s*or\s+"([^"]+)")?',
            r"(\w+)(?:\s*,\s*(\w+))*(?:\s*,?\s*or\s+(\w+))",
            r"(?:one of|choose from|select from|must be):?\s*([^.;]+)",
            r"either\s+(\w+)\s+or\s+(\w+)",
        ]

        # 长度匹配（不变）
        self.length_patterns = [
            r"(?:max|maximum)\s+(\d+)\s+(?:characters?|chars?)",
            r"(?:min|minimum)\s+(\d+)\s+(?:characters?|chars?|letters?)",
            r"(?:at least|no more than)\s+(\d+)\s+(?:characters?|chars?)",
            r"between\s+(\d+)\s+and\s+(\d+)\s+(?:characters?|chars?)",
        ]

    # ---------------------------------------------------------
    # 主入口
    # ---------------------------------------------------------
    def extract_constraints(self, text: str) -> List[ValueRestriction]:

        constraints = []
        constraints.extend(self._extract_bounds_constraints(text))
        constraints.extend(self._extract_enumeration_constraints(text))
        constraints.extend(self._extract_pattern_constraints(text))
        constraints.extend(self._extract_length_constraints(text))

        # -------- A: 去除冗余 pattern ----------
        constraints = self._prune_pattern_duplicates(constraints)

        # -------- B: 去除重复 enumeration -----
        constraints = self._prune_enumeration_duplicates(constraints)

        constraints.sort(key=lambda x: x.confidence, reverse=True)
        return constraints

    # ---------------------------------------------------------
    # 去重：保留最长 pattern 匹配项
    # ---------------------------------------------------------
    def _prune_pattern_duplicates(self, constraints):
        patterns = [c for c in constraints if c.restriction_type == RestrictionType.PATTERN]
        others = [c for c in constraints if c.restriction_type != RestrictionType.PATTERN]

        if not patterns:
            return constraints

        # 只保留 original_text 最长的 pattern
        longest_len = max(len(c.original_text) for c in patterns)
        pruned = [c for c in patterns if len(c.original_text) == longest_len]

        return pruned + others

    # ---------------------------------------------------------
    # 去重：按枚举值内容去重
    # ---------------------------------------------------------
    def _prune_enumeration_duplicates(self, constraints):
        enums = [c for c in constraints if c.restriction_type == RestrictionType.ENUMERATION]
        others = [c for c in constraints if c.restriction_type != RestrictionType.ENUMERATION]

        seen = set()
        unique = []

        for c in enums:
            key = tuple(sorted(c.restriction.values))
            if key not in seen:
                seen.add(key)
                unique.append(c)

        return unique + others

    # ---------------------------------------------------------
    # 以下为原始提取代码（核心逻辑未改动）
    # ---------------------------------------------------------

    def _extract_bounds_constraints(self, text: str) -> List[ValueRestriction]:
        constraints = []
        text_lower = text.lower()

        for pattern in self.numeric_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                try:
                    bounds = self._parse_bounds_match(match, pattern)
                    if bounds:
                        constraints.append(ValueRestriction(
                            restriction_type=RestrictionType.BOUNDS,
                            restriction=bounds,
                            confidence=0.9,
                            original_text=match.group(0),
                        ))
                except Exception:
                    pass
        return constraints

    def _extract_enumeration_constraints(self, text: str) -> List[ValueRestriction]:
        constraints = []
        for pattern in self.enumeration_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    values = self._parse_enumeration_match(match)
                    if values:
                        constraints.append(ValueRestriction(
                            restriction_type=RestrictionType.ENUMERATION,
                            restriction=EnumerationRestriction(values=values),
                            confidence=0.8,
                            original_text=match.group(0),
                        ))
                except Exception:
                    pass
        return constraints

    def _extract_pattern_constraints(self, text: str) -> List[ValueRestriction]:
        constraints = []
        for pattern in self.pattern_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    p = match.group(1).strip()
                    if p:
                        constraints.append(ValueRestriction(
                            restriction_type=RestrictionType.PATTERN,
                            restriction=PatternRestriction(pattern=p, description=f"Must match pattern: {p}"),
                            confidence=0.85,
                            original_text=match.group(0),
                        ))
                except Exception:
                    pass
        return constraints

    def _extract_length_constraints(self, text: str) -> List[ValueRestriction]:
        constraints = []
        text_lower = text.lower()
        for pattern in self.length_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                try:
                    r = self._parse_length_match(match, pattern)
                    if r:
                        constraints.append(ValueRestriction(
                            restriction_type=RestrictionType.LENGTH,
                            restriction=r,
                            confidence=0.8,
                            original_text=match.group(0),
                        ))
                except Exception:
                    pass
        return constraints

    # ---------------------------------------------------------
    # 原始解析方法（略）
    # ---------------------------------------------------------

    def _parse_bounds_match(self, match, pattern: str) -> Optional[BoundsRestriction]:
        groups = match.groups()
        text = match.group(0)

        if ">=" in text or "<=" in text:
            op, val = match.group(1), float(match.group(2))
            unit = match.group(3)
            if ">=" in op:
                return BoundsRestriction(min_value=val, min_inclusive=True, unit=unit)
            if "<=" in op:
                return BoundsRestriction(max_value=val, max_inclusive=True, unit=unit)
            if ">" in op:
                return BoundsRestriction(min_value=val, min_inclusive=False, unit=unit)
            if "<" in op:
                return BoundsRestriction(max_value=val, max_inclusive=False, unit=unit)

        if "between" in text or "from" in text:
            return BoundsRestriction(
                min_value=float(match.group(1)),
                max_value=float(match.group(2)),
                unit=match.group(3),
            )

        if "minimum" in text or "min" in text or "at least" in text:
            return BoundsRestriction(
                min_value=float(match.group(1)),
                min_inclusive=True,
                unit=match.group(2),
            )

        if "maximum" in text or "max" in text or "no more than" in text:
            return BoundsRestriction(
                max_value=float(match.group(1)),
                max_inclusive=True,
                unit=match.group(2),
            )

        if "-" in text or "–" in text:
            return BoundsRestriction(
                min_value=float(match.group(1)),
                max_value=float(match.group(2)),
                unit=match.group(3),
            )

        return None

    def _parse_enumeration_match(self, match) -> List[str]:
        values = []
        for g in match.groups():
            if g:
                if "," in g:
                    values.extend([x.strip() for x in g.split(",")])
                else:
                    values.append(g.strip())
        # 去重保持顺序
        seen = set()
        final = []
        for v in values:
            if v not in seen:
                seen.add(v)
                final.append(v)
        return final

    def _parse_length_match(self, match, pattern: str) -> Optional[LengthRestriction]:
        text = match.group(0)
        if "between" in text:
            return LengthRestriction(int(match.group(1)), int(match.group(2)))
        if "max" in text or "no more than" in text:
            return LengthRestriction(max_length=int(match.group(1)))
        if "min" in text or "at least" in text:
            return LengthRestriction(min_length=int(match.group(1)))
        return None

    # ---------------------------------------------------------
    # IDS 格式化方法（不变）
    # ---------------------------------------------------------

    def format_restriction_for_ids(self, restriction: ValueRestriction) -> Dict[str, Any]:
        t = restriction.restriction_type

        if t == RestrictionType.BOUNDS:
            r = restriction.restriction
            data = {"base": "string"}
            if r.min_value is not None:
                key = "minInclusive" if r.min_inclusive else "minExclusive"
                data[key] = r.min_value
            if r.max_value is not None:
                key = "maxInclusive" if r.max_inclusive else "maxExclusive"
                data[key] = r.max_value
            return data

        if t == RestrictionType.ENUMERATION:
            return {"base": "string", "enumeration": restriction.restriction.values}

        if t == RestrictionType.PATTERN:
            return {"base": "string", "pattern": restriction.restriction.pattern}

        if t == RestrictionType.LENGTH:
            r = restriction.restriction
            data = {"base": "string"}
            if r.min_length is not None:
                data["minLength"] = r.min_length
            if r.max_length is not None:
                data["maxLength"] = r.max_length
            return data

        return {"base": "string"}
