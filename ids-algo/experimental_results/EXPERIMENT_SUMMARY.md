# 实验数据完整性总结报告

**生成时间**: 2026-04-20T21:09:45.402304

---

## 实验概览

本项目共进行了3类实验，覆盖系统的质量、性能和鲁棒性测试：

### 1. 批量性能与质量测试

**描述**: 13个测试样本的批量实验（simple/medium/complex）

**规模**: 39次运行

**成功率**: 100.0%

**关键发现**:
- 100% success rate across all complexity levels
- Average response time: 28.27s
- Stage C (KB Mapping) is the bottleneck: 37.7%

**数据文件**:
- `experimental_results\summary_20260420_201945.json`
- `experimental_results\summary_20260420_201945.csv`
- `runs/ (39 files)`

### 2. 大规模IDS鲁棒性测试

**描述**: 45个specification的大规模IDS处理测试

**输入规模**:
- ifc_file: 985KB
- ids_file: 57KB (45 specifications)
- text_length: 12438
- estimated_tokens: 3109

**性能指标**:
- total_time: 287.37s
- memory_peak: 2837.9MB
- memory_delta: +2479.4MB

**输出结果**:
- specifications_generated: 29
- coverage_rate: 64.4%

**关键发现**:
- Successfully processed 45 specifications in 287s
- Generated 29 specifications (64.4% coverage)
- Peak memory: 2837.9MB
- Stage C (KB Mapping) took 59.6% of total time

**数据文件**:
- `experimental_results\large_scale_test\report_20260420_205651.json`
- `experimental_results\large_scale_test\result_20260420_205651.json`
- `experimental_results\large_scale_test\ids_comparison_report.md`
- `experimental_results\large_scale_test\ids_input_text.txt`

### 3. IDS对比分析

**描述**: 原始IDS与生成IDS的对比分析

**对比结果**:
- original_specs: 45
- generated_specs: 29
- coverage_rate: 64.4%
- match_rate: 24/45 (53.3%)

**关键发现**:
- 24/45 specifications matched (53.3%)
- System intelligently merged similar specifications
- 21 specifications not matched (mostly detailed sub-components)

**数据文件**:
- `experimental_results\large_scale_test\ids_comparison_report.json`
- `experimental_results\large_scale_test\ids_comparison_report.md`

---

## 论文第五章可用数据

### 5.1 系统性能测试

- **数据来源**: 批量实验（13样本×3次）
- **可用指标**: 平均响应时间、各阶段耗时占比、成功率
- **图表建议**: 柱状图（各阶段耗时）、折线图（不同复杂度的响应时间）

### 5.2 大规模处理能力测试

- **数据来源**: 大规模IDS鲁棒性测试
- **可用指标**: 处理45个specification的总耗时、内存占用、覆盖率
- **图表建议**: 饼图（各阶段耗时占比）、对比表（原始vs生成）

### 5.3 准确率与质量评估

- **数据来源**: IDS对比分析
- **可用指标**: Specification匹配率53.3%、覆盖率64.4%
- **图表建议**: 对比表格（详见ids_comparison_report.md）

---

## 缺失的实验数据（可选补充）

以下实验数据可以进一步补充，但不是必需的：

1. **并发处理测试**: 测试系统同时处理多个请求的能力
2. **长时间稳定性测试**: 连续运行数小时的稳定性
3. **不同LLM模型对比**: 对比不同模型（Sonnet vs Opus）的性能
4. **错误恢复测试**: 测试系统在异常情况下的恢复能力
5. **用户满意度调查**: 实际用户使用反馈（如果有用户测试）

**建议**: 当前数据已足够支撑论文第五章的实验部分。上述可选实验可根据时间和需求选择性补充。

