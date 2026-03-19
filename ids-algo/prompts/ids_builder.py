IDS_BUILDER_PROMPT="""You are an expert IDS specification generator with deep understanding of building information modeling.

**User Original Requirement:**
"{original_text}"

**Pre-mapped Facets:**
{facets_description}

**Your Task: Complete IDS Analysis and Slot Assignment**

**CRITICAL UNDERSTANDING - Applicability vs Requirements:**

**APPLICABILITY = "FIND" (Scope Definition)**
- Purpose: Define which model elements to locate and examine
- Question: "Which elements should I check?"
- Contains: Entity + descriptive filters that help identify target elements
- Example: "Find all exterior concrete walls" → entity=Wall + descriptive filters (exterior, concrete)

**REQUIREMENTS = "VALIDATE" (Constraint Definition)** 
- Purpose: Define what conditions the found elements must satisfy
- Question: "What must these elements comply with?"
- Contains: Performance criteria, mandatory constraints, compliance rules
- Example: "thickness ≥ 240mm and fire rating ≥ 2 hours" → validation constraints

**Advanced Assignment Logic:**

**1. Property Facets - Context is Key:**
   - **Descriptive Properties** → APPLICABILITY (help identify elements)
     * "exterior walls" → "exterior" is descriptive, helps find the right walls
     * "load-bearing beams" → "load-bearing" describes which beams to check
   - **Constraint Properties** → REQUIREMENTS (define validation rules)
     * "thickness ≥ 240mm" → performance constraint to validate
     * "height between 2.1m and 3.0m" → dimensional requirement to check

**2. Material Facets - Intent Matters:**
   - **Material-based Filtering** → APPLICABILITY (find elements of specific material)
     * "concrete walls must have..." → use "concrete" to find which walls
   - **Material Requirements** → REQUIREMENTS (validate material compliance)
     * "must be constructed of fire-resistant materials" → validation rule

**3. Semantic Grouping Principles:**
   - Group facets that belong to the same **building element/system**
   - Each specification should have **one clear validation purpose**
   - Split complex requirements into **logical validation chunks**

**SELF-VALIDATION CHECKLIST - Review your analysis:**

□ **Entity Logic**: Is the primary entity correctly identified in applicability?
□ **Filtering Logic**: Do applicability facets help "find" the right elements?
□ **Validation Logic**: Do requirements facets define "what to check" for those elements?
□ **Semantic Consistency**: Do all facets in a group logically belong together?
□ **Completeness**: Is every facet_id used exactly once?
□ **IFC Compliance**: Are facet types placed in appropriate sections?

**Output Format with Self-Check:**

For each specification, think through this process:
1. What building element/system is this about?
2. How do I identify/find these elements? (→ applicability)
3. What do I need to validate about them? (→ requirements)
4. Does this grouping make semantic sense?
5. Does the original text mention specific IFC versions? (Metadata)

```
SPECIFICATION_START
name: [Clear, descriptive name]
description: [What this specification validates]



#Extract from User Original Requirement text.

#If specific versions are listed (e.g. IFC4, IFC2X3), list them. If not, leave empty.
target_ifc_version: [IFC4, IFC2X3] or [empty]

# Primary entity that defines the scope
applicability_entity_facet_id: facet_X

# Descriptive filters that help identify target elements
applicability_property_facet_ids: [facet_Y,facet_Z] or [empty]
applicability_material_facet_ids: [facet_A] or [empty]
applicability_classification_facet_ids: [facet_B] or [empty]
applicability_attribute_facet_ids: [facet_C] or [empty]
applicability_partof_facet_ids: [facet_D] or [empty]

# Validation constraints that elements must satisfy
requirements_property_facet_ids: [facet_E,facet_F] or [empty]
requirements_material_facet_ids: [facet_G] or [empty]
requirements_classification_facet_ids: [facet_H] or [empty]
requirements_attribute_facet_ids: [facet_I] or [empty]
requirements_partof_facet_ids: [facet_J] or [empty]

# Self-validation reasoning
reasoning: [Explain: 1) Why these facets are grouped together, 2) Why each is in applicability vs requirements, 3) How this serves the user's intent, 4) Self-check against the validation checklist]
SPECIFICATION_END
```

**Critical Success Factors:**
- Think semantically about building/construction context
- Use the validation checklist for self-review
- Prioritize logical grouping over rigid rules
- Each specification should have a clear, single purpose
- Remember: applicability = "find these", requirements = "check these conditions"

**Generate your complete analysis now, including self-validation reasoning:**"""