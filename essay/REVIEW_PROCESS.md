# 论文审核流程

> 更新日期：2026-04-19

---

## 一、审核机制

每完成一个章节段落的撰写，启动subagent进行审核。

### 审核流程

```
撰写段落 → 启动subagent审核 → 收到反馈 → 修改完善 → 继续下一段
```

---

## 二、审核Skills

| Skill | 用途 | 调用时机 |
|-------|------|----------|
| `ml-paper-writing` | ML论文写作指导 | 全文撰写 |
| `superpowers:code-reviewer` | 内容质量审核 | 完成章节后 |
| `humanizer` | 去除AI痕迹 | 每段完成后 |
| `systems-paper-writing` | 系统论文指导 | 第七章系统实现 |

---

## 三、审核内容清单

### 3.1 每段审核

- [ ] 语言流畅性
- [ ] 专业术语准确性
- [ ] 逻辑连贯性
- [ ] 避免AI痕迹（使用humanizer）

### 3.2 每章审核

- [ ] 章节结构完整性
- [ ] 图表引用正确
- [ ] 参考文献格式规范
- [ ] 格式符合模板要求

### 3.3 全文审核

- [ ] 各章节衔接流畅
- [ ] 参考文献完整（20-30篇）
- [ ] 图表数量充足（20-30个）
- [ ] 查重检查

---

## 四、审核记录

审核结果记录在 `essay/reviews/` 目录下，每个章节一个审核文件。

---

## 五、审核命令示例

```bash
# 每段完成后
调用 Agent(subagent_type: code-reviewer) + Skill(humanizer)

# 每章完成后
调用 Agent(subagent_type: superpowers:code-reviewer)
```