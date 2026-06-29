from datetime import datetime
from .data_structures import StructuredParseResult

def format_result_as_markdown(result: StructuredParseResult, text: str) -> str:
    """Convert StructuredParseResult to markdown format."""
    md_lines = []

    # Header
    md_lines.append("# Structured Parsing Result\n")
    md_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_lines.append(f"**Input Text:** {text}\n")
    md_lines.append("---\n")

    # Building Objects
    md_lines.append("## 🧱 Building Objects\n")
    if result.building_objects:
        for i, obj in enumerate(result.building_objects, 1):
            md_lines.append(f"### Object {i}\n")
            md_lines.append(f"- **Raw Text:** `{obj.raw_text}`\n")
            md_lines.append(f"- **Object Type:** `{obj.object_type}`\n")
            md_lines.append(f"- **Modifiers:** {', '.join(f'`{m}`' for m in obj.modifiers) if obj.modifiers else 'None'}\n")
            md_lines.append(f"- **Confidence:** {obj.confidence}\n")
            md_lines.append("")
    else:
        md_lines.append("*No building objects found.*\n")

    # Property Descriptions
    md_lines.append("## 📏 Property Descriptions\n")
    if result.property_descriptions:
        for i, prop in enumerate(result.property_descriptions, 1):
            md_lines.append(f"### Property {i}\n")
            md_lines.append(f"- **Raw Text:** `{prop.raw_text}`\n")
            md_lines.append(f"- **Property Name:** `{prop.property_name}`\n")
            md_lines.append(f"- **Constraint Text:** `{prop.constraint_text}`\n")
            md_lines.append(f"- **Confidence:** {prop.confidence}\n")
            md_lines.append("")
    else:
        md_lines.append("*No property descriptions found.*\n")

    # Material Requirements
    md_lines.append("## 🧪 Material Requirements\n")
    if result.material_requirements:
        for i, mat in enumerate(result.material_requirements, 1):
            md_lines.append(f"### Material {i}\n")
            md_lines.append(f"- **Raw Text:** `{mat.raw_text}`\n")
            md_lines.append(f"- **Material Name:** `{mat.material_name}`\n")
            md_lines.append(f"- **Specifications:** `{mat.specifications}`\n")
            md_lines.append(f"- **Confidence:** {mat.confidence}\n")
            md_lines.append("")
    else:
        md_lines.append("*No material requirements found.*\n")

    # Spatial Relationships
    md_lines.append("## 📐 Spatial Relationships\n")
    if result.spatial_relationships:
        for i, rel in enumerate(result.spatial_relationships, 1):
            md_lines.append(f"### Relationship {i}\n")
            md_lines.append(f"- **Raw Text:** `{rel.raw_text}`\n")
            md_lines.append(f"- **Subject:** `{rel.subject}`\n")
            md_lines.append(f"- **Relation:** `{rel.relation}`\n")
            md_lines.append(f"- **Object:** `{rel.object}`\n")
            md_lines.append(f"- **Confidence:** {rel.confidence}\n")
            md_lines.append("")
    else:
        md_lines.append("*No spatial relationships found.*\n")

    # Unmatched Fragments
    md_lines.append("## ❓ Unmatched Fragments\n")
    if result.unmatched_fragments:
        for i, fragment in enumerate(result.unmatched_fragments, 1):
            md_lines.append(f"{i}. `{fragment}`\n")
    else:
        md_lines.append("*No unmatched fragments.*\n")

    # LLM Analysis
    md_lines.append("## 🧠 LLM Analysis\n")
    if result.llm_analysis:
        md_lines.append("```\n")
        md_lines.append(result.llm_analysis)
        md_lines.append("\n```\n")
    else:
        md_lines.append("*No LLM analysis was generated.*\n")

    return "\n".join(md_lines)
