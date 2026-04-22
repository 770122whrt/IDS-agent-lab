# IDS大型数据集测试优化 - 实施路线图

## Phase 1: 增强IDSToTextGenerator [2-3小时]

**目标**: 增强现有文本转换工具，保留完整的IDS信息

**计划**:
- [ ] 分析temp目录的输入输出格式（a1.json, input.json等）
- [ ] 阅读ids_converter/ids_to_text.py的IDSToTextGenerator实现
- [ ] 增强generate方法保留entity信息（applicability facets）
- [ ] 增强generate方法保留requirements信息（partOf/attribute/property/material facets）
- [ ] 增强generate方法保留基数约束（minOccurs/maxOccurs）
- [ ] 增强generate方法保留IFC版本信息

**成功标准**:
- IDSToTextGenerator能够将IDS完整转换为结构化文本
- 转换后的文本包含所有entity、requirements、基数约束信息
- 输出格式清晰，便于后续阶段解析

---

## Phase 2: 修复测试脚本 [1-2小时]

**目标**: 修复所有测试脚本使用增强版IDSToTextGenerator

**计划**:
- [ ] 修复test_large_scale_ids.py的文本转换逻辑
- [ ] 修复batch_experiment.py的文本转换逻辑
- [ ] 检查其他测试脚本（test_*.py）是否需要修复
- [ ] 统一所有测试脚本使用相同的文本转换方法
- [ ] 确保转换后的文本格式一致

**成功标准**:
- 所有测试脚本使用增强版IDSToTextGenerator
- 文本转换逻辑统一，避免不一致
- 代码清晰，易于维护

---

## Phase 3: 增强结果保存功能 [1-2小时]

**目标**: 保留所有阶段输出、中间结果、最终结果和性能指标

**计划**:
- [ ] 修改pipeline.py保存各阶段输出（a1/a2, b1/b2, c1/c2, d1/d2, e1/e2格式）
- [ ] 保存中间结果（parsed结构、classified facets、mapped facets）
- [ ] 保存最终结果（IDS JSON、验证结果）
- [ ] 记录性能指标（时间、内存、成功率、Requirements保留率）
- [ ] 参考temp目录的文件格式设计输出结构

**成功标准**:
- 每次运行保存完整的阶段输出
- 输出格式与temp目录一致
- 性能指标完整记录
- 便于后续分析和论文写作

---

## Phase 4: 快速验证 [30分钟]

**目标**: 使用3-5个样本快速验证修复效果

**计划**:
- [ ] 从45个specifications中选择3-5个代表性样本
- [ ] 运行修复后的测试脚本
- [ ] 检查阶段输出是否完整
- [ ] 验证Requirements保留率是否提升
- [ ] 验证匹配率是否提升
- [ ] 如有问题，快速调整并重新验证

**成功标准**:
- 3-5个样本全部成功处理
- Requirements保留率达到70%+
- 匹配率达到85%+
- 阶段输出完整保存

---

## Phase 5: Requirements保留率验证 [1小时]

**目标**: 详细验证Requirements保留率提升效果

**计划**:
- [ ] 分析修复前的Requirements丢失情况（79个中只保留3个）
- [ ] 运行修复后的测试，统计Requirements保留情况
- [ ] 对比修复前后的Requirements保留率
- [ ] 分析仍然丢失的Requirements原因（Stage D能力限制、Stage E分配错误）
- [ ] 生成Requirements保留率详细报告

**成功标准**:
- Requirements保留率从3.8%提升到70%+
- 详细记录每个specification的Requirements保留情况
- 识别剩余30%丢失的原因
- 生成可用于论文的对比数据

---

## Phase 6: 大规模测试 [2-3小时]

**目标**: 重新运行45个specifications的大规模测试

**计划**:
- [ ] 运行修复后的test_large_scale_ids.py
- [ ] 处理全部45个specifications
- [ ] 收集所有阶段输出和性能指标
- [ ] 统计匹配率、处理时间、内存占用
- [ ] 统计Requirements保留率
- [ ] 识别失败的specifications并分析原因

**成功标准**:
- 45个specifications全部处理完成
- 匹配率达到85%+（从53.3%提升）
- Requirements保留率达到70%+（从3.8%提升）
- 所有数据完整保存
- 处理时间记录完整

---

## Phase 7: 生成对比报告 [1-2小时]

**目标**: 生成修复前后的详细对比报告，提供论文所需数据

**计划**:
- [ ] 读取修复前的实验结果（experimental_results/large_scale_robustness/）
- [ ] 读取修复后的实验结果
- [ ] 对比匹配率（53.3% vs 85%+）
- [ ] 对比Requirements保留率（3.8% vs 70%+）
- [ ] 对比处理时间（是否有变化）
- [ ] 对比内存占用（是否有变化）
- [ ] 生成详细的对比表格和图表建议
- [ ] 生成论文所需的性能提升和准确性提升证明

**成功标准**:
- 详细的修复前后对比报告
- 包含匹配率、Requirements保留率、性能指标对比
- 提供论文所需的图表数据
- 证明大型数据集能够成功处理
- 证明现实需求能够成功转换

---

## Phase 8: 文档和总结 [30分钟]

**目标**: 更新文档，总结优化成果

**计划**:
- [ ] 更新README或相关文档，说明文本转换修复
- [ ] 记录IDSToTextGenerator的增强内容
- [ ] 记录测试脚本的修改内容
- [ ] 总结优化成果（匹配率提升、Requirements保留率提升）
- [ ] 提交所有修改到git（ESSAY分支）

**成功标准**:
- 文档清晰完整
- 代码修改已提交
- 优化成果已记录
- 论文数据已准备好

---

## 时间估算

- **Phase 1**: 2-3小时（增强IDSToTextGenerator）
- **Phase 2**: 1-2小时（修复测试脚本）
- **Phase 3**: 1-2小时（增强结果保存）
- **Phase 4**: 30分钟（快速验证）
- **Phase 5**: 1小时（Requirements验证）
- **Phase 6**: 2-3小时（大规模测试）
- **Phase 7**: 1-2小时（生成对比报告）
- **Phase 8**: 30分钟（文档总结）

**总计**: 9-14小时（可在今天完成，考虑并行执行和快速迭代）

---

## 风险和缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| IDSToTextGenerator增强复杂度超预期 | 延迟Phase 1 | 先实现最小可行版本，保留核心信息即可 |
| 快速验证失败 | 需要返工Phase 1-2 | Phase 4设置明确的成功标准，快速迭代 |
| 大规模测试运行时间过长 | 延迟Phase 6 | 考虑分批运行，先运行20个样本验证 |
| Requirements保留率未达70% | 影响论文数据 | 分析原因，如果是Stage D限制则记录并说明 |

---

*Last updated: 2026-04-23 after project setup*
