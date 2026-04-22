# IDS大型数据集测试优化项目

## What This Is

针对IDS生成系统的大型数据集测试失败问题进行修复和优化。当前系统在处理45个真实specifications时，匹配率仅53.3%，Requirements保留率仅3.8%，主要原因是测试脚本使用简化的文本转换导致85%的关键信息丢失。本项目通过增强IDSToTextGenerator并修复所有测试脚本，使系统能够成功处理大型数据集和现实需求，为毕业论文提供可靠的实验数据。

## Core Value

证明IDS生成系统能够成功处理大型真实数据集，匹配率达到85%+，Requirements保留率达到70%+，生成可用于论文的性能和准确性提升数据。

## Requirements

### Validated

- ✓ 五阶段IDS生成管道 (A→B→C→D→E) — existing
- ✓ IDSToTextGenerator完整文本转换工具 — existing in ids_converter/ids_to_text.py
- ✓ 大规模测试框架 (45 specifications) — existing
- ✓ 实验结果分析工具 — existing

### Active

- [ ] 增强IDSToTextGenerator保留完整信息（entity、requirements、基数约束、IFC版本）
- [ ] 修复test_large_scale_ids.py使用增强版转换工具
- [ ] 修复batch_experiment.py使用增强版转换工具
- [ ] 修复所有相关测试脚本使用统一的文本转换
- [ ] 保留所有阶段输出（a1/a2, b1/b2, c1/c2, d1/d2, e1/e2格式，参考temp目录）
- [ ] 保留中间结果（parsed/classified/mapped）
- [ ] 保留最终结果（IDS JSON和验证结果）
- [ ] 记录性能指标（时间、内存、成功率、Requirements保留率）
- [ ] 快速验证（3-5个样本）+ Requirements保留率验证
- [ ] 重新运行45个specifications大规模测试
- [ ] 生成修复前后对比报告（匹配率、处理时间、Requirements保留率）
- [ ] 生成论文所需数据（性能提升、准确性提升证明）

### Out of Scope

- Stage C性能优化（批量LLM、向量索引） — 后续优化项目
- IFC4X3实体扩充 — 后续优化项目
- 自动化测试框架 — 后续工程化项目
- 前端界面改进 — 不在本次范围

## Context

**当前问题分析：**
- **文本转换信息丢失85%**：test_large_scale_ids.py只提取name和description，丢失了entity信息、所有requirements（partOf/attribute/property/material）、基数约束（minOccurs/maxOccurs）
- **Requirements保留率3.8%**：79个requirements中只保留3个，21个specifications完全丢失
- **匹配率53.3%**：45个specifications中24个成功匹配
- **已有完整工具**：ids_converter/ids_to_text.py的IDSToTextGenerator类可以完整转换IDS到文本

**实验数据参考：**
- temp目录包含各阶段输入输出示例（a1.json/a2.json, b1.json/b2.json等）
- 需要保留完整的阶段输出以便论文分析

**论文需求：**
- 证明大型数据集能够成功通过
- 证明现实需求能够成功转换
- 提供修复前后的性能和准确性对比数据

## Constraints

- **时间**: 今天完成 — 快速修复，立即见效
- **技术栈**: Python 3.12.4, 现有IDS生成管道，IDSToTextGenerator
- **数据格式**: 参考temp目录的输入输出格式（a1/a2, b1/b2等）
- **测试数据**: 45个真实specifications（ids-algo/experimental_results/large_scale_robustness/）
- **成功标准**: 匹配率85%+，Requirements保留率70%+

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 增强IDSToTextGenerator而非重写 | 现有工具已有完整框架，只需增强以保留更多信息 | — Pending |
| 修复所有测试脚本统一使用增强版 | 确保所有测试使用一致的文本转换，避免不一致 | — Pending |
| 保留所有阶段输出和中间结果 | 论文需要详细的数据分析和对比 | — Pending |
| 先快速验证再大规模测试 | 3-5个样本快速验证修复效果，避免浪费时间 | — Pending |
| 生成修复前后对比报告 | 论文需要证明优化效果的数据支撑 | — Pending |

---
*Last updated: 2026-04-23 after initial project setup*
