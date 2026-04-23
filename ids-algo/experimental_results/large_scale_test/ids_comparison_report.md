# IDS对比分析报告

**生成时间**: 2026-04-20T21:07:06.215277

## 总体对比

| 指标 | 原始IDS | 生成IDS | 覆盖率 |
|------|---------|---------|--------|
| Specification数量 | 45 | 29 | 64.4% |
| Applicability Facets总数 | 46 | 34 | - |
| Requirements Facets总数 | 79 | 3 | - |
| 平均Applicability/Spec | 1.0 | 1.2 | - |
| 平均Requirements/Spec | 1.8 | 0.1 | - |

## Specification详细对比

| # | 原始名称 | 生成名称 | 状态 | Applicability (原/生成) | Requirements (原/生成) |
|---|----------|----------|------|------------------------|------------------------|
| 1 | Project | Project Units Definition | ✅ MATCHED | 1/1 | 0/1 |
| 2 | Site | Site Presence and Terrain Definition | ✅ MATCHED | 1/2 | 2/1 |
| 3 | Bridge | Bridge Structure Definition | ✅ MATCHED | 1/1 | 2/0 |
| 4 | Alignment | Alignment Curves | ✅ MATCHED | 1/1 | 2/0 |
| 5 | Substructure | Substructure Elements | ✅ MATCHED | 1/1 | 1/0 |
| 6 | Superstructure | Superstructure Elements | ✅ MATCHED | 1/1 | 2/0 |
| 7 | Girders | NOT FOUND | ❌ MISSING | 1/0 | 3/0 |
| 8 | Deck | Bridge Deck | ✅ MATCHED | 1/1 | 2/0 |
| 9 | Deck segments | NOT FOUND | ❌ MISSING | 1/0 | 2/0 |
| 10 | Abutments | Abutments | ✅ MATCHED | 2/1 | 0/1 |
| 11 | Piers | Piers | ✅ MATCHED | 1/1 | 2/0 |
| 12 | Piles | Piles | ✅ MATCHED | 1/2 | 3/0 |
| 13 | Surface Proposed | NOT FOUND | ❌ MISSING | 1/0 | 1/0 |
| 14 | Surface Existing | NOT FOUND | ❌ MISSING | 1/0 | 1/0 |
| 15 | Boring Points (IfcGeographicElement) | NOT FOUND | ❌ MISSING | 1/0 | 3/0 |
| 16 | Material | NOT FOUND | ❌ MISSING | 1/0 | 8/0 |
| 17 | Pier Stems | Pier Stems | ✅ MATCHED | 1/1 | 1/0 |
| 18 | Pier Segments | Pier Segments | ✅ MATCHED | 1/1 | 1/0 |
| 19 | Pier Caps | Pier Caps | ✅ MATCHED | 1/1 | 1/0 |
| 20 | Retaining Walls | Retaining Walls | ✅ MATCHED | 1/1 | 1/0 |
| 21 | Apron | Apron | ✅ MATCHED | 1/1 | 1/0 |
| 22 | Arch | Arch | ✅ MATCHED | 1/1 | 1/0 |
| 23 | Footing | Footings | ✅ MATCHED | 1/2 | 3/0 |
| 24 | Pile | Piles | ✅ MATCHED | 1/2 | 3/0 |
| 25 | Hat Stone | Hat Stone | ✅ MATCHED | 1/1 | 0/0 |
| 26 | Girder | Girder Definition | ✅ MATCHED | 1/3 | 3/0 |
| 27 | Boring Points 2 (IfcBorehole) | NOT FOUND | ❌ MISSING | 1/0 | 2/0 |
| 28 | Girder Type | NOT FOUND | ❌ MISSING | 1/0 | 1/0 |
| 29 | Girder Segment | NOT FOUND | ❌ MISSING | 1/0 | 3/0 |
| 30 | Plates | Plates | ✅ MATCHED | 1/1 | 0/0 |
| 31 | Cross Frame | Cross Frames | ✅ MATCHED | 1/1 | 1/0 |
| 32 | Diaphragm | Diaphragm | ✅ MATCHED | 1/1 | 3/0 |
| 33 | Truss | Truss | ✅ MATCHED | 1/1 | 1/0 |
| 34 | Deck Span | NOT FOUND | ❌ MISSING | 1/0 | 3/0 |
| 35 | Deck Segment | NOT FOUND | ❌ MISSING | 1/0 | 3/0 |
| 36 | Parapet | NOT FOUND | ❌ MISSING | 1/0 | 3/0 |
| 37 | Railing | NOT FOUND | ❌ MISSING | 1/0 | 3/0 |
| 38 | Approach slab | NOT FOUND | ❌ MISSING | 1/0 | 1/0 |
| 39 | Cornice | NOT FOUND | ❌ MISSING | 1/0 | 1/0 |
| 40 | Waterproofing | NOT FOUND | ❌ MISSING | 1/0 | 1/0 |
| 41 | Bearing | NOT FOUND | ❌ MISSING | 1/0 | 1/0 |
| 42 | Bearing type | NOT FOUND | ❌ MISSING | 1/0 | 1/0 |
| 43 | Joint | NOT FOUND | ❌ MISSING | 1/0 | 1/0 |
| 44 | Joint type | NOT FOUND | ❌ MISSING | 1/0 | 1/0 |
| 45 | Members | NOT FOUND | ❌ MISSING | 1/0 | 0/0 |

## 分析结论

- **匹配率**: 24/45 (53.3%)
- **生成效率**: 原始45个specification → 生成29个

### 未匹配的Specification (21个)

- Girders
- Deck segments
- Surface Proposed
- Surface Existing
- Boring Points (IfcGeographicElement)
- Material
- Boring Points 2 (IfcBorehole)
- Girder Type
- Girder Segment
- Deck Span
- Deck Segment
- Parapet
- Railing
- Approach slab
- Cornice
- Waterproofing
- Bearing
- Bearing type
- Joint
- Joint type
- Members
