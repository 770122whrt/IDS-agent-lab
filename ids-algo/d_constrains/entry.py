from .constraint_extractor import ConstraintExtractor
from .data_structures import MappedFacet
from .constraint_extractor import ValueRestriction
import logging


def runConstraintExtraction(mapped_facets: list[MappedFacet]) -> list[ValueRestriction]:
    try:
        constraint_extractor = ConstraintExtractor()
        all_constraints: list[ValueRestriction] = []

        for facet in mapped_facets:
            text = facet.original_text or ""
            if not text.strip():
                continue  # 跳过空文本

            print(f"\nExtracting constraints from: \"{text}\"")

            constraints = constraint_extractor.extract_constraints(text)

            if constraints:
                print(f"Found {len(constraints)} constraint(s).")
                for c in constraints:
                    if c.restriction_type.name == "BOUNDS":
                        r = c.restriction
                        print(f" {c.original_text} → min={r.min_value}, max={r.max_value}, unit={r.unit}")
                    elif c.restriction_type.name == "ENUMERATION":
                        print(f" {c.original_text} → {c.restriction.values}")
                    elif c.restriction_type.name == "PATTERN":
                        print(f" {c.original_text} → pattern={c.restriction.pattern}")
                    elif c.restriction_type.name == "LENGTH":
                        r = c.restriction
                        print(f" {c.original_text} → minLen={r.min_length}, maxLen={r.max_length}")
                all_constraints.extend(constraints)
            else:
                print("No constraints extracted from this text.")

        return all_constraints

    except Exception as e:
        logging.error(f"Error in constraint extraction: {e}")
        return []
