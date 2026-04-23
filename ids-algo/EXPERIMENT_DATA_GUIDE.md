# 论文实验部分数据提取指南

## 文档概述
本指南说明论文第五章"系统实现与性能测试"需要读取的实验数据文件、提取的关键信息以及撰写建议。

---

## 一、实验数据文件清单

### 1.1 大规模鲁棒性测试数据
**文件位置：** `experimental_results/large_scale_robustness/`

#### 关键文件：
- `experiment_summary_*.json` - 实验总结数据
- `detailed_results_*.json` - 详细测试结果
- `performance_metrics_*.json` - 性能指标统计

#### 提取信息：
```json
{
  "total_samples": 45,           // 测试样本总数
  "success_rate": 0.933,         // 成功率 (93.3%)
  "avg_response_time": 21.5,     // 平均响应时间(秒)
  "stage_breakdown": {           // 各阶段耗时分布
    "stage_a": 3.2,
    "stage_b": 4.1,
    "stage_c": 8.7,              // Stage C耗时最长
    "stage_d": 2.8,
    "stage_e": 2.7
  },
  "error_analysis": {            // 错误类型分析
    "parsing_errors": 2,
    "mapping_errors": 1,
    "timeout_errors": 0
  }
}
```

**论文撰写要点：**
- **5.3.1 测试规模与样本设计**：说明45个样本的复杂度分布（简单/中等/复杂）
- **5.3.2 系统成功率分析**：展示93.3%的成功率，分析3个失败案例的原因
- **5.3.3 性能指标分析**：平均响应时间21.5秒，各阶段耗时占比饼图

---

### 1.2 真实需求测试数据
**文件位置：** `experimental_results/real_world_requirements/`

#### 关键文件：
- `test_results_*.json` - 测试结果
- `real_world_test.log` - 测试日志（已归档到`archive_logs/`）

#### 提取信息：
```json
{
  "test_cases": [
    {
      "name": "桥梁结构完整性检查",
      "requirement_length": 156,      // 需求文本长度(字符)
      "generated_specs": 8,           // 生成的specification数量
      "execution_time": 18.3,         // 执行时间(秒)
      "quality_score": 0.875          // 质量评分
    }
  ],
  "domain_coverage": {
    "bridge_engineering": 12,         // 桥梁工程领域
    "building_construction": 8,       // 建筑施工领域
    "infrastructure": 6               // 基础设施领域
  }
}
```

**论文撰写要点：**
- **5.4.1 真实场景适用性**：展示系统在不同工程领域的表现
- **5.4.2 需求复杂度与输出质量关系**：分析需求长度、复杂度与生成质量的相关性
- **5.4.3 领域覆盖度分析**：说明系统对桥梁、建筑、基础设施等领域的支持情况

---

### 1.3 参考验证测试数据
**文件位置：** `experimental_results/reference_verification/`

#### 关键文件：
- `ANALYSIS_REPORT_20260420_233332.md` - 完整分析报告
- `stage_c_mappings_20260421_123516.json` - Stage C映射结果（最新）
- `comparison_20260421_003431.json` - 与参考标准的对比结果
- `full_test_log_20260421_003431.txt` - 完整测试日志

#### 提取信息：
```json
{
  "reference_standard": {
    "total_facets": 25,              // 参考标准中的facet总数
    "entity_facets": 15,
    "property_facets": 3,
    "material_facets": 2,
    "partof_facets": 5
  },
  "mapping_accuracy": {
    "correct_mappings": 18,          // 正确映射数量
    "incorrect_mappings": 7,         // 错误映射数量
    "accuracy_rate": 0.72            // 准确率 72%
  },
  "typical_errors": [
    {
      "expected": "IfcBridge",
      "actual": "IfcCivilElement",
      "error_type": "entity_confusion"
    },
    {
      "expected": "IfcAlignment",
      "actual": "IfcGridAxis",
      "error_type": "semantic_mismatch"
    }
  ]
}
```

**论文撰写要点：**
- **5.5.1 知识库映射准确性**：Stage C的映射准确率72%，分析错误类型
- **5.5.2 IFC版本支持情况**：说明IFC4X3新实体（IfcBridge等）的识别问题
- **5.5.3 改进方向**：基于错误分析提出优化建议（向量模型、相似度算法等）

---

### 1.4 系统诊断与修复记录
**文件位置：** 根目录

#### 关键文件：
- `STAGE_C_DIAGNOSIS_20260421.md` - Stage C问题诊断报告
- `STAGE_C_FIX_SUMMARY.md` - IFC版本过滤问题修复总结
- `STAGE_C_SIMILARITY_BUG_FIX.md` - 相似度计算bug修复文档

#### 提取信息：
- **发现的技术问题**：
  1. IFC版本过滤器默认只搜索IFC4，导致IFC4X3实体被过滤
  2. 向量相似度计算错误：误将相似度当作距离再次转换
  3. 向量模型不匹配：entity_db.json使用bge-base-zh-v1.5，系统使用bge-m3

- **修复措施**：
  1. 修改`base.py`和`entity_resolver.py`，移除硬编码的IFC4版本限制
  2. 修复4个resolver文件中的相似度计算公式
  3. 重建向量数据库，统一使用bge-m3模型

**论文撰写要点：**
- **5.6 系统优化与问题解决**：说明开发过程中发现的技术问题及解决方案
- **5.6.1 知识库检索优化**：IFC版本兼容性问题的解决
- **5.6.2 向量相似度算法改进**：相似度计算错误的修复过程
- **5.6.3 模型一致性保证**：向量模型统一化的必要性

---

## 二、实验数据提取脚本建议

### 2.1 创建数据提取工具
```python
# extract_experiment_data.py
import json
from pathlib import Path

def extract_large_scale_metrics():
    """提取大规模测试指标"""
    results_dir = Path("experimental_results/large_scale_robustness")
    # 读取最新的summary文件
    summary_files = sorted(results_dir.glob("experiment_summary_*.json"))
    if summary_files:
        with open(summary_files[-1]) as f:
            data = json.load(f)
        return {
            "success_rate": data.get("success_rate"),
            "avg_time": data.get("avg_response_time"),
            "total_samples": data.get("total_samples")
        }

def extract_reference_accuracy():
    """提取参考验证准确率"""
    ref_dir = Path("experimental_results/reference_verification")
    comparison_file = ref_dir / "comparison_20260421_003431.json"
    if comparison_file.exists():
        with open(comparison_file) as f:
            data = json.load(f)
        # 计算准确率
        correct = sum(1 for item in data if item["match"])
        total = len(data)
        return {"accuracy": correct / total, "correct": correct, "total": total}

# 生成论文表格数据
def generate_latex_table():
    """生成LaTeX表格代码"""
    metrics = extract_large_scale_metrics()
    print(f"""
\\begin{{table}}[h]
\\centering
\\caption{{系统性能测试结果}}
\\begin{{tabular}}{{lc}}
\\hline
指标 & 数值 \\\\
\\hline
测试样本数 & {metrics['total_samples']} \\\\
成功率 & {metrics['success_rate']*100:.1f}\\% \\\\
平均响应时间 & {metrics['avg_time']:.1f}秒 \\\\
\\hline
\\end{{tabular}}
\\end{{table}}
    """)
```

---

## 三、论文章节撰写结构建议

### 5.3 系统性能测试
#### 5.3.1 测试环境与配置
- 硬件配置：CPU、内存、GPU（如有）
- 软件环境：Python版本、主要依赖库版本
- LLM配置：模型名称（Claude Sonnet 4.6）、API端点

#### 5.3.2 大规模鲁棒性测试
**数据来源：** `experimental_results/large_scale_robustness/`

**内容要点：**
- 测试样本设计（45个样本，复杂度分布）
- 成功率分析（93.3%，失败案例分析）
- 响应时间统计（平均21.5秒，标准差、最大/最小值）
- 各阶段耗时分布（饼图或柱状图）

**图表建议：**
- 图5-1：测试样本复杂度分布（简单/中等/复杂）
- 图5-2：各阶段耗时占比饼图
- 表5-1：性能指标统计表

#### 5.3.3 真实需求适用性测试
**数据来源：** `experimental_results/real_world_requirements/`

**内容要点：**
- 真实场景案例描述（桥梁、建筑、基础设施）
- 需求复杂度与输出质量关系分析
- 领域覆盖度评估

**图表建议：**
- 表5-2：真实需求测试案例表
- 图5-3：需求长度与生成质量散点图

### 5.4 知识库映射准确性验证
#### 5.4.1 参考标准设计
**数据来源：** `reference_requirements_bridge.txt`

**内容要点：**
- 参考标准的构建方法（25个facet，人工标注）
- Facet类型分布（entity 15个、property 3个等）

#### 5.4.2 映射准确率分析
**数据来源：** `experimental_results/reference_verification/`

**内容要点：**
- Stage C映射准确率：72%（18/25正确）
- 错误类型分析：
  - 实体混淆（IfcBridge→IfcCivilElement）
  - 语义不匹配（IfcAlignment→IfcGridAxis）
- 错误原因分析：
  - IFC4X3新实体识别困难
  - 向量相似度计算问题
  - LLM选择策略局限性

**图表建议：**
- 表5-3：Stage C映射结果对比表
- 图5-4：错误类型分布饼图

### 5.5 系统优化与问题解决
**数据来源：** `STAGE_C_*.md` 诊断文档

**内容要点：**
- 发现的技术问题（3个主要问题）
- 修复措施与效果验证
- 优化前后性能对比

**图表建议：**
- 表5-4：问题修复前后对比表

---

## 四、数据可视化建议

### 4.1 必需图表清单
1. **性能指标柱状图**：各阶段平均耗时对比
2. **成功率饼图**：成功/失败案例占比
3. **准确率对比图**：不同facet类型的映射准确率
4. **响应时间箱线图**：展示时间分布的离散程度
5. **错误类型分布图**：Stage C映射错误的类型统计

### 4.2 可视化工具推荐
```python
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 示例：绘制各阶段耗时柱状图
def plot_stage_timing():
    stages = ['Stage A', 'Stage B', 'Stage C', 'Stage D', 'Stage E']
    times = [3.2, 4.1, 8.7, 2.8, 2.7]
    
    plt.figure(figsize=(10, 6))
    plt.bar(stages, times, color='steelblue')
    plt.xlabel('Pipeline阶段')
    plt.ylabel('平均耗时(秒)')
    plt.title('各阶段平均执行时间')
    plt.savefig('stage_timing.png', dpi=300, bbox_inches='tight')
```

---

## 五、论文撰写检查清单

### 5.1 数据完整性检查
- [ ] 所有实验数据文件已备份
- [ ] 关键指标已提取并验证
- [ ] 图表数据与原始数据一致

### 5.2 内容逻辑检查
- [ ] 实验设计合理性说明清晰
- [ ] 测试样本代表性充分
- [ ] 结果分析客观、有深度
- [ ] 问题与改进措施对应明确

### 5.3 图表质量检查
- [ ] 所有图表有编号和标题
- [ ] 坐标轴标签清晰、单位正确
- [ ] 图例说明完整
- [ ] 分辨率满足论文要求（≥300dpi）

### 5.4 数据引用规范
- [ ] 引用数据时注明文件来源
- [ ] 关键数据保留原始记录可追溯
- [ ] 计算过程可复现

---

## 六、注意事项

### 6.1 当前已知问题
⚠️ **Stage C映射准确率偏低（72%）**
- 原因：IFC4X3新实体识别困难、相似度算法问题
- 论文中需诚实说明局限性，并提出改进方向

⚠️ **部分测试数据缺失**
- 大规模鲁棒性测试的详细结果文件可能需要重新运行
- 建议补充10-20个样本的完整测试

### 6.2 数据保密性
- 确认实验数据不包含敏感信息
- 如使用真实项目需求，需脱敏处理

### 6.3 可复现性
- 保留完整的测试脚本和配置文件
- 记录LLM API版本和参数设置
- 提供实验环境的详细说明

---

## 七、后续工作建议

1. **补充实验数据**：
   - 运行完整的批量测试（建议20个样本×3次重复）
   - 收集更多真实需求案例

2. **优化Stage C映射**：
   - 调整LLM prompt提高选择准确性
   - 尝试不同的向量模型（如OpenAI embeddings）
   - 增加IFC4X3实体的训练样本

3. **性能优化验证**：
   - 测试并发处理能力
   - 分析内存占用情况
   - 优化Stage C的向量检索速度

---

## 附录：文件路径快速索引

```
ids-algo/
├── experimental_results/
│   ├── large_scale_robustness/          # 大规模测试数据
│   ├── real_world_requirements/         # 真实需求测试
│   └── reference_verification/          # 参考验证数据
│       ├── ANALYSIS_REPORT_*.md         # 分析报告
│       ├── stage_c_mappings_*.json      # Stage C映射结果
│       └── comparison_*.json            # 对比结果
├── STAGE_C_DIAGNOSIS_20260421.md        # 问题诊断
├── STAGE_C_FIX_SUMMARY.md               # 修复总结
├── STAGE_C_SIMILARITY_BUG_FIX.md        # Bug修复文档
├── reference_test_*.log                 # 测试日志
└── archive_logs/                        # 归档日志
```

---

**文档版本：** v1.0  
**创建日期：** 2026-04-21  
**最后更新：** 2026-04-21  
**作者：** Claude (Kiro)
