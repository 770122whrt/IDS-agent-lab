# THESIS-5P 章节审核计划模板

> 使用说明：复制此模板到 `essay/reviews/Chapter_XX/`，将 `XX` 替换为章节编号，按P1-P5逐步执行。

---

## Context

- **论文章节**：第XX章 《章节标题》
- **论文题目**：基于自然语言的IDS规则文件生成系统
- **学校/学院**：浙江大学海洋学院
- **审核日期**：YYYY-MM-DD

### 待审核文件
- [ ] `essay/chapters/chapter_XX_draft.md`（Markdown正文）
- [ ] `essay/output/chapter_XX_draft.docx`（Word正文，如有）

### 参考资料（必读）
- [ ] `reference-for-essay/开题报告和文献综述.md`
- [ ] `reference-for-essay/论文模板.md`
- [ ] `essay/template_structure.md`
- [ ] `essay/FORMAT_REQUIREMENTS.md`

---

## P1 - Review：严格审读

### AI痕迹检查

#### 1.1 高频词统计
使用 Grep 统计以下词汇出现次数：

```bash
grep -oE '显著|核心|关键|有效|突破|进一步|逐渐|凸显' chapter_XX_draft.md | sort | uniq -c
```

| 词汇 | 出现次数 | 密度评估 | 处理建议 |
|------|----------|----------|----------|
| 显著 | | | |
| 核心 | | | |
| 关键 | | | |
| 有效 | | | |
| 突破 | | | |
| 进一步 | | | |
| 逐渐 | | | |
| 凸显 | | | |

#### 1.2 句式模式检查

| # | 检查项 | 位置 | 具体问题 | 严重程度 |
|---|--------|------|----------|----------|
| 1 | 三段式并列 | | | |
| 2 | 被动语态 | | | |
| 3 | 模糊归因 | | | |
| 4 | 套话连接词 | | | |
| 5 | 结论性过强 | | | |
| 6 | 空洞积极表述 | | | |

### 学术规范检查

#### 2.1 引用密度

| 节号 | 引用数量 | 评估 | 问题说明 |
|------|----------|------|----------|
| | | | |

#### 2.2 术语一致性

| 术语 | 首次出现位置 | 是否给全称 | 后续使用是否一致 | 问题说明 |
|------|--------------|------------|------------------|----------|
| | | | | |

#### 2.3 逻辑映射
- [ ] 存在问题（如1.2.4）与主要工作（如1.3.1）一一对应
- [ ] 相邻章节无内容重复
- [ ] 领域特殊性充分论述

### P1 产出
- [ ] `CHAPTER_XX_REVIEW_REPORT.md` 已写入 `essay/reviews/Chapter_XX/`

---

## P2 - Plan：修改方案

### 问题汇总与优先级

| 序号 | 问题描述 | 位置 | 严重程度 | 修改策略 | 预计耗时 |
|------|----------|------|----------|----------|----------|
| 1 | | | 🔴高 | | |
| 2 | | | 🟡中 | | |
| 3 | | | 🟢低 | | |

### 修改阶段规划

| 阶段 | 任务 | 产出文件 | 预计耗时 |
|------|------|----------|----------|
| 3-1 | 去AI化 | `CHAPTER_XX_HUMANIZED.md` | |
| 3-2 | 内容增强 | `CHAPTER_XX_ENHANCED.md` | |
| 3-3 | 术语统一 | `CHAPTER_XX_POLISHED.md` | |
| 3-4 | 润色优化 | `CHAPTER_XX_FINAL.md` | |
| 4 | 量化验证 | `CHAPTER_XX_VALIDATION_REPORT.md` | |
| 5 | 总结交付 | `CHAPTER_XX_REVISION_SUMMARY.md` | |

### P2 产出
- [ ] `CHAPTER_XX_REVISION_PLAN.md` 已写入
- [ ] `CHAPTER_XX_TODOLIST.md` 已写入

---

## P3 - Execute：分步修改

### 阶段3-1：去AI化

**调用 humanizer skill**：
```
/humanizer [文件路径]
```

**手动修正清单**：
- [ ] 替换高频AI词（见P1统计）
- [ ] 打破三段式结构
- [ ] 长句拆短
- [ ] 减少被动语态

**产出**：`CHAPTER_XX_HUMANIZED.md`

### 阶段3-2：内容增强

**补充内容清单**：
- [ ] 薄弱章节补充引用（列出拟补充文献）
- [ ] 强化领域特殊性（添加规范数据/工程案例）
- [ ] 明确问题-方案映射（如需要）

**拟补充引用**：
| 编号 | 作者 | 年份 | 支撑内容 | 插入位置 |
|------|------|------|----------|----------|
| | | | | |

**产出**：`CHAPTER_XX_ENHANCED.md`

### 阶段3-3：术语统一

**检查清单**：
- [ ] 缩写首次全称（列出需补充的术语）
- [ ] 同义词统一
- [ ] 删除重复定义

**产出**：`CHAPTER_XX_POLISHED.md`

### 阶段3-4：润色优化

**检查清单**：
- [ ] 段落长度3-5句
- [ ] 过渡自然
- [ ] 引用格式统一
- [ ] 数字表达一致

**产出**：`CHAPTER_XX_FINAL.md`

---

## P4 - Validate：量化验证

### 验证检查表

| 验证项 | 目标值 | 实际值 | 状态 |
|--------|--------|--------|------|
| AI高频词密度 | ≤0.05% | | |
| 引用数量 | ≥XX篇 | | |
| 术语规范性 | 100% | | |
| 问题-方案映射 | 清晰 | | |
| 领域特殊性 | 充分体现 | | |

### 统计数据

- 总字数：
- 总段落数：
- 总句子数：
- 平均句长：
- 引用总数：

### P4 产出
- [ ] `CHAPTER_XX_VALIDATION_REPORT.md` 已写入

---

## P5 - Deliver：交付

### 文件清单确认

- [ ] `CHAPTER_XX_REVIEW_REPORT.md`
- [ ] `CHAPTER_XX_REVISION_PLAN.md`
- [ ] `CHAPTER_XX_TODOLIST.md`
- [ ] `CHAPTER_XX_HUMANIZED.md`
- [ ] `CHAPTER_XX_ENHANCED.md`
- [ ] `CHAPTER_XX_POLISHED.md`
- [ ] `CHAPTER_XX_FINAL.md` ⭐
- [ ] `CHAPTER_XX_VALIDATION_REPORT.md`
- [ ] `CHAPTER_XX_REVISION_SUMMARY.md`

### 修改总结要点

1. **AI痕迹控制**：修改前密度___ → 修改后密度___
2. **内容完整性**：新增引用___篇，新增内容___字
3. **术语规范性**：修正术语___处
4. **逻辑连贯性**：优化逻辑连接___处
5. **可读性**：优化句式___处

### 后续建议

- [ ] Word文档生成（见下方工具说明）
- [ ] 格式调整（字体、行距、页边距）
- [ ] 图表补充
- [ ] 参考文献列表同步（确认新增引用已加入总参考文献）

---

## 附录：修订对比Word文档生成工具

### 工具位置
`essay/reviews/generate_revision_docx.py`

### 功能
将原始markdown与修订后的markdown对比，自动生成带红色标记的Word文档（红色=新增/修改，黑色=原文保留）。

### 依赖安装
```bash
pip install python-docx
```

### 使用方法（命令行）

```bash
python essay/reviews/generate_revision_docx.py \
  --original essay/chapters/chapter_XX_draft.md \
  --final essay/reviews/Chapter_XX/CHAPTER_XX_FINAL.md \
  --output essay/output/chapter_XX_revised_red.docx \
  --title "第X章 章节标题（修订稿）" \
  --red-sections "X.X.X,X.X.X" \
  --legend "红色=新增/修改；黑色=原文保留。主要修改：..."
```

### 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--original` | 是 | 原始markdown文件路径（如 `chapter_02_draft.md`） |
| `--final` | 是 | 修订后markdown文件路径（如 `CHAPTER_02_FINAL.md`） |
| `--output` | 是 | 输出Word文档路径 |
| `--title` | 是 | 文档标题 |
| `--red-sections` | 否 | 需要整节标红的章节编号，逗号分隔（如 `2.2.2,2.2.3`）。适用于整节重写的情况。 |
| `--legend` | 否 | 修改说明文字，显示在文档开头 |

### 使用建议

1. **red_sections的使用**：仅当某节被"整节重写"时才填入（如2.2.2从OpenRouter改为分词+知识图谱）。对于"扩写"而非"重写"的章节，不填此参数，脚本会自动逐段比对标红新增段落。

2. **字体说明**：生成的文档使用仿宋（中文）/Times New Roman（英文），符合浙江大学论文格式要求。

3. **验证生成结果**：建议在Microsoft Word中打开检查，确认红色标记覆盖了所有修改位置。

### 示例（第二章）

```bash
python essay/reviews/generate_revision_docx.py \
  --original essay/chapters/chapter_02_draft.md \
  --final essay/reviews/Chapter_02/CHAPTER_02_FINAL.md \
  --output essay/output/chapter_02_revised_red.docx \
  --title "第二章 相关技术与理论基础（修订稿）" \
  --red-sections "2.2.2,2.2.3,2.3.1,2.3.2,2.3.3,2.4.1,2.4.2,2.4.3" \
  --legend "红色=新增/修改；黑色=原文保留。主要修改：(1)2.2.2改为分词+知识图谱；(2)2.2.3扩写LLM规范语义；(3)2.3.1扩写向量嵌入原理；(4)2.3.2/2.3.3结合项目实际；(5)2.4.1强化BIM领域；(6)2.4.2改为buildingSMART介绍。"
```

---

## 执行记录

| 阶段 | 执行时间 | 执行人 | 状态 |
|------|----------|--------|------|
| P1 Review | | | |
| P2 Plan | | | |
| P3-1 De-AI | | | |
| P3-2 Enhance | | | |
| P3-3 Terminology | | | |
| P3-4 Polish | | | |
| P4 Validate | | | |
| P5 Deliver | | | |
