# 论文实验数据需求清单

> 更新日期：2026-04-20
> 状态：待收集

---

## 一、数据需求概览

论文第五章需要填充以下实验数据，用于验证系统性能与质量评估。

### 数据分类

| 类别 | 数据项数量 | 优先级 | 状态 |
|------|-----------|--------|------|
| **质量评估数据** | 3项 | 高 | 待收集 |
| **性能测试数据** | 3项 | 高 | 待收集 |
| **界面截图** | 2张 | 中 | 待采集 |
| **API接口表** | 1个 | 中 | 待创建 |
| **可视化图表** | 1张 | 中 | 待生成 |

---

## 二、质量评估数据（第5.6节）

### 2.1 Pipeline成功率统计

**位置**：第5.6.1节

**需要的数据**：
```
- Pipeline成功率：____% （目标：≥85%）
- 失败原因分布：
  - LLM调用失败：____%
  - 映射失败：____%
  - 验证失败：____%
  - 其他：____%
```

**数据收集方法**：
1. 准备测试样本：20-50个不同复杂度的自然语言规范描述
2. 通过系统提交所有测试样本
3. 记录每个任务的执行结果（成功/失败）
4. 对失败任务分类记录失败原因
5. 计算成功率 = 成功任务数 / 总任务数

**测试样本建议**：
- 简单规范（5-10个）：单一实体+单一属性约束，如"墙体厚度≥200mm"
- 中等规范（10-20个）：多个实体或多个属性约束，如"承重墙厚度≥200mm且防火等级为A级"
- 复杂规范（5-10个）：包含组合关系或复杂约束，如"位于地下室的承重墙厚度应在200-300mm之间"

---

### 2.2 IDS文件合规率评估

**位置**：第5.6.2节

**需要的数据**：
```
- IDS文件合规率：____% （目标：≥95%）
- 失败原因分布：
  - 字段缺失：____%
  - 格式错误：____%
  - 实体名称无效：____%
  - 其他：____%
```

**数据收集方法**：
1. 对所有成功生成的IDS文件执行XSD验证
2. 使用ifctester的`ids.open()`方法加载IDS文件
3. 记录验证结果（通过/失败）
4. 对失败文件分析错误日志，分类记录失败原因
5. 计算合规率 = 通过文件数 / 总文件数

**验证命令参考**：
```python
from ifctester import ids
try:
    my_ids = ids.open("path/to/file.ids")
    print("验证通过")
except Exception as e:
    print(f"验证失败：{e}")
```

---

### 2.3 映射准确率评估

**位置**：第5.6.3节

**需要的数据**：
```
- 映射准确率：____% （参考基准：78.75%）
```

**数据收集方法**：
1. 从测试样本中选取30-50个实体/属性名称
2. 人工标注正确的IFC标准映射目标（作为Ground Truth）
3. 运行系统获取映射结果
4. 对比系统映射结果与人工标注结果
5. 计算准确率 = 正确映射数 / 总映射数

**人工标注示例**：
| 自然语言 | 正确映射（Ground Truth） | 系统映射结果 | 是否正确 |
|----------|-------------------------|-------------|---------|
| 墙 | IfcWall | IfcWall | ✓ |
| 厚度 | Pset_WallCommon.Thickness | Pset_WallCommon.Thickness | ✓ |
| 防火等级 | Pset_WallCommon.FireRating | Pset_WallCommon.FireRating | ✓ |

**参考基准说明**：
- Guo等（2025）在BIM信息检索研究中报告的准确率为78.75%
- 本研究应达到或超过该基准

---

## 三、性能测试数据（第5.7节）

### 3.1 端到端响应时间测试

**位置**：第5.7.1节

**需要的数据**：
```
- 平均响应时间：____秒
- 最大响应时间：____秒
- 最小响应时间：____秒
- 标准差：____秒
```

**数据收集方法**：
1. 准备10-20个测试样本（不同复杂度）
2. 对每个样本重复测试3-5次
3. 记录每次测试的响应时间（从提交到完成）
4. 计算平均值、最大值、最小值、标准差

**测试脚本参考**：
```python
import time
import requests

def test_response_time(input_text):
    start_time = time.time()
    response = requests.post("http://localhost:3000/api/ids/generate", 
                            json={"inputText": input_text})
    end_time = time.time()
    return end_time - start_time

# 重复测试
times = []
for i in range(5):
    t = test_response_time("墙体厚度≥200mm")
    times.append(t)
    
print(f"平均：{sum(times)/len(times):.2f}秒")
print(f"最大：{max(times):.2f}秒")
print(f"最小：{min(times):.2f}秒")
```

---

### 3.2 各阶段耗时分析

**位置**：第5.7.2节

**需要的数据**：
```
| 阶段 | 平均耗时 | 占比 |
|------|----------|------|
| Stage A（结构化解析） | ____秒 | ____% |
| Stage B（方面分类） | ____秒 | ____% |
| Stage C（知识库映射） | ____秒 | ____% |
| Stage D（约束提取） | ____秒 | ____% |
| Stage E（IDS构建） | ____秒 | ____% |
```

**数据收集方法**：
1. 在Pipeline代码中添加时间戳记录（如果尚未添加）
2. 对10-20个测试样本运行Pipeline
3. 记录每个阶段的耗时
4. 计算各阶段平均耗时
5. 计算各阶段占比 = 阶段耗时 / 总耗时 × 100%

**代码插桩位置**：
- `ids-algo/a_parser/parser.py` - Stage A入口/出口
- `ids-algo/b_facet/facet_classifier.py` - Stage B入口/出口
- `ids-algo/c_mapper/mapper.py` - Stage C入口/出口
- `ids-algo/d_constrains/constraint_extractor.py` - Stage D入口/出口
- `ids-algo/e_builder/ids_builder.py` - Stage E入口/出口

**时间戳记录示例**：
```python
import time

def stage_a_parse(input_text):
    start_time = time.time()
    # ... 处理逻辑 ...
    end_time = time.time()
    duration = end_time - start_time
    print(f"Stage A耗时：{duration:.2f}秒")
    return result
```

---

### 3.3 并发处理能力测试

**位置**：第5.7.3节

**需要的数据**：
```
| 并发数 | 平均响应时间 | 成功率 |
|--------|--------------|--------|
| 1 | ____秒 | ____% |
| 5 | ____秒 | ____% |
| 10 | ____秒 | ____% |
| 20 | ____秒 | ____% |
```

**数据收集方法**：
1. 使用压力测试工具（推荐：Python的`concurrent.futures`或`locust`）
2. 准备相同的测试样本
3. 分别以1、5、10、20并发数发起请求
4. 记录每个并发级别下的平均响应时间与成功率
5. 观察系统在高并发下的表现（是否出现超时、错误）

**并发测试脚本参考**：
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time

def send_request(input_text):
    try:
        start = time.time()
        response = requests.post("http://localhost:3000/api/ids/generate",
                                json={"inputText": input_text},
                                timeout=60)
        duration = time.time() - start
        return {"success": response.status_code == 200, "time": duration}
    except Exception as e:
        return {"success": False, "time": None}

def test_concurrent(concurrency, num_requests=20):
    input_text = "墙体厚度≥200mm"
    results = []
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_request, input_text) 
                  for _ in range(num_requests)]
        for future in as_completed(futures):
            results.append(future.result())
    
    success_count = sum(1 for r in results if r["success"])
    success_rate = success_count / len(results) * 100
    avg_time = sum(r["time"] for r in results if r["time"]) / success_count
    
    print(f"并发数：{concurrency}")
    print(f"成功率：{success_rate:.1f}%")
    print(f"平均响应时间：{avg_time:.2f}秒")
    return {"concurrency": concurrency, "success_rate": success_rate, "avg_time": avg_time}

# 测试不同并发级别
for c in [1, 5, 10, 20]:
    test_concurrent(c)
```

---

## 四、界面截图（第5.1节）

### 4.1 图5.1 Dashboard界面截图

**位置**：第5.1.3节

**需要的内容**：
- IDS生成页面的完整界面
- 包含：输入框、生成按钮、状态显示、结果展示区域
- 建议状态：已输入文本，正在生成或已完成生成

**采集方法**：
1. 启动前端应用（`npm run dev`）
2. 登录系统
3. 进入Dashboard页面
4. 输入示例文本（如"承重墙厚度≥200mm"）
5. 截取完整页面（建议使用浏览器全屏截图功能）
6. 保存为PNG格式，分辨率≥1920×1080

**文件命名**：`figure_5_1_dashboard.png`

---

### 4.2 图5.2 审查报告页面截图

**位置**：第5.1.3节

**需要的内容**：
- IFC合规性审查报告页面
- 包含：规则列表、审查结果（通过/失败）、违规详情
- 建议状态：已完成审查，显示部分通过、部分失败的结果

**采集方法**：
1. 生成一个IDS文件
2. 上传一个IFC模型文件进行审查
3. 等待审查完成
4. 进入审查报告页面
5. 截取完整页面
6. 保存为PNG格式

**文件命名**：`figure_5_2_report.png`

---

## 五、API接口汇总表（第5.2节）

### 5.1 表5.1 核心API接口汇总表

**位置**：第5.2.3节

**需要的内容**：
- Next.js API Routes接口列表
- Python FastAPI接口列表
- 每个接口的：路径、方法、功能描述、请求参数、响应格式

**创建方法**：
1. 读取`app/api/`目录下的所有API路由文件
2. 读取`ids-algo/server.py`中的FastAPI路由定义
3. 整理成表格格式

**表格格式参考**：
| 接口路径 | 方法 | 模块 | 功能描述 | 主要参数 |
|---------|------|------|---------|---------|
| /api/auth/login | POST | Next.js | 用户登录 | email, password |
| /api/ids/generate | POST | Next.js | 创建IDS生成任务 | inputText, userId |
| /api/python/pipeline | POST | FastAPI | 执行Pipeline | json_data |
| /api/ifc/check | POST | FastAPI | IFC合规性审查 | ids_file, ifc_file |

**文件命名**：`table_5_1_api_interfaces.md`（Markdown格式，便于后续转换）

---

## 六、可视化图表（第5.7节）

### 6.1 图5.3 各阶段耗时柱状图

**位置**：第5.7.2节

**需要的内容**：
- 横轴：Stage A、Stage B、Stage C、Stage D、Stage E
- 纵轴：平均耗时（秒）
- 柱状图显示各阶段耗时对比

**生成方法**：
1. 收集3.2节的各阶段耗时数据
2. 使用Python的matplotlib或seaborn库生成柱状图
3. 保存为PNG格式，分辨率≥1200×800

**生成脚本参考**：
```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 中文字体
matplotlib.rcParams['axes.unicode_minus'] = False

stages = ['Stage A\n结构化解析', 'Stage B\n方面分类', 'Stage C\n知识库映射', 
          'Stage D\n约束提取', 'Stage E\nIDS构建']
times = [2.5, 1.8, 0.5, 1.2, 0.3]  # 示例数据，需替换为实际数据

plt.figure(figsize=(10, 6))
plt.bar(stages, times, color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6'])
plt.xlabel('Pipeline阶段', fontsize=12)
plt.ylabel('平均耗时（秒）', fontsize=12)
plt.title('IDS生成Pipeline各阶段耗时分布', fontsize=14)
plt.grid(axis='y', alpha=0.3)

# 在柱子上方显示数值
for i, v in enumerate(times):
    plt.text(i, v + 0.1, f'{v:.2f}s', ha='center', fontsize=10)

plt.tight_layout()
plt.savefig('figure_5_3_stage_timing.png', dpi=300, bbox_inches='tight')
plt.show()
```

**文件命名**：`figure_5_3_stage_timing.png`

---

## 七、数据存储结构建议

建议在`essay/experimental-data/`目录下创建以下子目录：

```
essay/experimental-data/
├── DATA_REQUIREMENTS.md          # 本文档
├── quality-assessment/            # 质量评估数据
│   ├── pipeline_success_rate.json
│   ├── ids_compliance_rate.json
│   └── mapping_accuracy.json
├── performance-testing/           # 性能测试数据
│   ├── response_time.json
│   ├── stage_timing.json
│   └── concurrency_test.json
├── screenshots/                   # 界面截图
│   ├── figure_5_1_dashboard.png
│   └── figure_5_2_report.png
├── tables/                        # 表格数据
│   └── table_5_1_api_interfaces.md
└── figures/                       # 生成的图表
    └── figure_5_3_stage_timing.png
```

---

## 八、数据收集优先级与时间估算

| 任务 | 优先级 | 预计耗时 | 依赖 |
|------|--------|---------|------|
| Pipeline成功率统计 | 高 | 2-3小时 | 准备测试样本 |
| IDS文件合规率评估 | 高 | 1-2小时 | Pipeline成功率数据 |
| 映射准确率评估 | 高 | 3-4小时 | 人工标注Ground Truth |
| 端到端响应时间测试 | 高 | 1-2小时 | 测试脚本 |
| 各阶段耗时分析 | 高 | 2-3小时 | 代码插桩 |
| 并发处理能力测试 | 中 | 2-3小时 | 压力测试脚本 |
| Dashboard截图 | 中 | 0.5小时 | 系统运行 |
| 审查报告截图 | 中 | 0.5小时 | 系统运行+IFC文件 |
| API接口表 | 中 | 1小时 | 代码梳理 |
| 耗时柱状图 | 低 | 0.5小时 | 各阶段耗时数据 |

**总计预估时间**：13-19小时

---

## 九、注意事项

1. **测试环境一致性**：所有性能测试应在相同的硬件环境下进行（记录CPU、内存、网络条件）
2. **数据真实性**：避免伪造数据，如果某些指标未达到预期，可在论文中如实说明并分析原因
3. **统计显著性**：每个测试至少重复3次，取平均值，并计算标准差
4. **异常值处理**：如果出现明显异常值（如网络波动导致的超长响应时间），可剔除后重新计算
5. **数据备份**：所有原始数据应保存JSON格式，便于后续分析和验证

---

## 十、数据填充后的后续工作

1. 将数据填充到`chapter_05_draft.md`对应位置
2. 生成图表并插入到Word文档中
3. 更新`thesis_draft_test.docx`
4. 对填充后的内容进行审核（humanizer + ml-paper-writing）
5. 提交最终版本

---

**文档维护者**：Claude (Kiro)  
**最后更新**：2026-04-20
