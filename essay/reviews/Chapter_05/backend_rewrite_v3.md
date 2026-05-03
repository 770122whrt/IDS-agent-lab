# 5.2 后端服务实现（完整版重写）

后端采用双模块架构，包含Next.js API Routes与Python FastAPI两个子模块。双模块的分层逻辑与通信机制见3.2节，本节聚焦各模块的接口定义与数据模型。

## 5.2.1 API服务层

系统采用双层API架构，前端服务层由Next.js API Routes实现，后端计算层由Python FastAPI服务实现，两者通过HTTP协议通信。

Next.js API Routes是系统的前端服务层，负责用户认证、资源管理与任务调度。认证功能通过better-auth库实现，生成的会话数据存储于数据库sessions集合，后续请求通过会话机制验证用户身份。资源管理接口查询任务列表并处理文件上传，IFC文件存储于GridFS，接口验证资源所有权以防止越权访问。

任务调度接口接收用户的自然语言输入或IFC文件，将请求转发至Python FastAPI服务执行核心算法。文本输入通过/api/analyze-text接口调用Pipeline生成IDS文件，IFC文件通过/api/tasks/[id]/check接口执行合规性审查。任务完成后更新状态并存储结果，用户可通过文件下载接口获取生成的IDS文件。

Python FastAPI服务运行于独立进程，负责执行IDS生成与IFC审查的核心算法。文本分析接口（POST /analyze）调用五阶段Pipeline将自然语言转换为IDS规则数据，返回JSON格式的specifications数组。IFC检查接口（POST /check）调用ifctester库加载IFC模型与IDS规则，逐条验证后生成审查报告，报告包含每个Specification的通过状态与失败实体详情。

服务采用异步处理机制支持并发请求，健康检查接口（GET /health）用于监控服务可用性。两个模块通过HTTP协议通信，Next.js负责用户交互与会话管理，FastAPI负责计算密集型任务，实现了前后端职责分离。

## 5.2.2 数据存储与任务状态

数据存储采用MongoDB数据库，结合GridFS处理大文件存储。任务资源的数据模型包含用户标识（userId）、输入类型（input_type，区分文本与IFC文件）、任务状态（status）、文件引用（fileId、idsFileId、ifcFileId指向GridFS存储的文件）、审查报告数据（reportData）与错误信息（errorMessage）等字段。不同任务类型使用不同的文件存储字段组合。

任务状态采用有限状态机模型，共7种状态。正常流程为：pending（待处理）→ processing（Pipeline执行中）→ pending_conversion（等待IDS格式转换）→ completed（IDS生成完成）→ checking（IFC审查执行中）→ checked（审查完成）。异常分支包括：processing/pending_conversion阶段可能转入failed（IDS生成失败），checking阶段可能转入check_failed（审查失败）。状态更新由Pipeline各阶段与审查流程触发，前端通过轮询感知变化。

---

## 改进说明

### 合并5.2.1与5.2.2
- 新的5.2.1标题改为"API服务层"
- 增加总起段落描述双层API架构（Next.js + FastAPI）
- 保留原5.2.1和5.2.2的所有段落内容
- 原5.2.3改为5.2.2，内容不变

### 内容取舍
**保留**：
- MongoDB + GridFS存储架构
- 任务数据模型的核心字段（userId、input_type、status、文件引用、reportData、errorMessage）
- 7种任务状态的完整流转逻辑（正常流程 + 异常分支）
- 有限状态机模型

**删除**：
- 表格形式的字段定义（改为段落叙述）
- 过细的字段类型（"字符串"、"对象标识符"等）
- "数据库连接采用连接池管理，连接URI从环境变量读取"（过于技术化）
- "resultJson字段存储Pipeline中间结果，uploadTime字段记录任务创建时间"（次要字段）

### 段落组织
- **5.2.1第一段**：双层API架构总述
- **5.2.1第二段**：Next.js API Routes功能
- **5.2.1第三段**：Next.js任务调度接口
- **5.2.1第四段**：Python FastAPI服务功能
- **5.2.1第五段**：异步处理与职责分离
- **5.2.2第一段**：数据存储架构 → 任务数据模型核心字段
- **5.2.2第二段**：任务状态机模型 → 7种状态 → 正常流程 → 异常分支 → 状态更新机制

---

## 质量评分

| 维度 | 评估标准 | 得分 |
|------|----------|------|
| **直接性** | 直接陈述事实还是绕圈宣告？ | 9/10 |
| **节奏** | 句子长度是否变化？ | 8/10 |
| **信任度** | 是否尊重读者智慧？ | 9/10 |
| **真实性** | 听起来像真人说话吗？ | 8/10 |
| **精炼度** | 还有可删减的内容吗？ | 8/10 |
| **总分** |  | **42/50** |

**评价**：良好，保留了MongoDB和任务状态流转的核心内容，同时去除了AI痕迹和过细的技术实现细节。
