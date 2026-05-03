# 第三章 系统需求分析与总体设计

## 3.1 需求分析

### 3.1.1 功能需求

海洋工程BIM模型的合规审查涉及结构强度、舾装设计、防腐防爆等多学科规范，条款数量庞大且更新频繁[8]。以海上风电导管架为例，一套完整的BIM模型通常包含数千个构件（如桩腿、节点板、支撑管、法兰等），IFC文件大小可达数十MB至上百MB。中国船级社（CCS）《海上固定平台入级规范》中，仅结构强度章节就涵盖数百条技术要求，涉及材料等级、焊缝质量、腐蚀裕度、疲劳寿命等属性的逐项核查。人工审查这样规模的模型需要数周时间，且审查人员在不同规范条款间切换时极易因疲劳产生疏漏。为缩短审查周期并降低人为失误，系统需要支持以下四项功能。

**IDS规则生成**。用户通过自然语言输入规范描述，系统自动生成符合IDS标准[37]的规则文件。流程包括：解析用户输入中的实体类型、属性名称与约束条件；将解析结果映射至IFC标准[49]定义的实体与属性集；生成符合XML Schema Definition（XSD）规范的IDS JSON结构。生成结果的准确性直接决定后续审查能否发现真实的违规项。与陆上建筑规范相比，海洋工程规范对IFC实体的属性要求更为严格——例如导管架桩腿不仅需要几何尺寸，还必须包含壁厚、材料等级、防腐涂层厚度等多维属性，IDS规则必须精确覆盖这些字段。

**IFC知识库检索**。系统提供IFC术语知识库的检索能力，支持按实体名称、属性集（Property Set）或属性定义进行模糊匹配与精确查询，并支持按IFC版本（IFC2x3、IFC4、IFC4.3）筛选结果[49]。该功能为IDS生成提供知识支撑，也便于用户验证映射结果的正确性。

**合规审查执行**。系统对IFC模型文件执行自动化合规审查。流程包括：接收用户上传的IFC文件、加载已生成的IDS规则、调用ifctester引擎执行检验、输出违规项清单。报告支持JSON、HTML与BCF（BIM Collaboration Format，BIM协作格式）三种格式[11]，形成"规则生成→审查执行→结果反馈"的闭环。

**用户管理与历史记录**。系统记录用户的IDS生成历史与审查历史，包含输入内容、生成结果、审查报告与时间戳，便于追溯与复用。该功能面向三类用户：BIM工程师在模型交付前将项目规范转化为IDS规则；审查人员加载IDS规则与IFC模型执行审查并生成报告；项目管理员维护规范库与审查标准配置。

系统功能模块之间的依赖关系如图3.1所示。

---

> **【图表需求 - 待创建】**
>
> **图3.1 系统功能模块关系图**
> - **位置**：此处（3.1.1节末）
> - **类型**：流程图/框图
> - **内容要点**：IDS生成、知识库检索、审查执行、用户管理四个模块的依赖与调用关系

---

### 3.1.2 非功能需求

除功能需求外，系统在实际部署中还需满足以下约束。

**性能要求**。IDS生成涉及大语言模型的多轮推理调用，单次请求的端到端响应时间受限于LLM推理延迟（远程LLM API的网络往返与推理通常在15-20秒）、本地知识库向量检索与验证（约3-5秒）以及输入解析与结果格式化开销，综合耗时约为30秒。IFC模型审查的耗时与文件大小和规则数量正相关，对一个约50MB的IFC文件执行200条IDS规则，ifctester引擎的解析与匹配过程约需10-15秒。上述响应时间未达到传统Web应用"秒级响应"的标准，但考虑到合规审查需要逐条遍历IFC实体属性并与规则进行匹配，这一量级的耗时在同类BIM自动化审查工具中处于可接受范围[55][57]。系统通过异步任务队列避免长时间请求阻塞，前端展示加载进度以改善用户等待体验。

**可靠性要求**。系统通过任务状态管理与重试机制保障基本的容错能力。每项任务在MongoDB中维护完整的状态生命周期，共包含8种状态：待处理（pending）、处理中（pending_conversion）、转换中（processing）、已完成（completed）、失败（failed），以及IFC审查专用的检查中（checking）、检查完成（checked）与检查失败（check_failed）。前端通过定时轮询感知状态变化，用户可在任务列表中查看每项任务的实时进展。当IDS生成或IFC审查任务失败时，用户可通过重试功能重新触发处理——系统将任务状态重置并重新调用Python后端，若重试过程中Python服务不可达，则将任务状态置为对应失败状态（IDS生成为failed，IFC审查为check_failed）并记录错误信息。知识库检索无结果时返回明确提示而非异常中断。

**安全性要求**。用户身份验证采用better-auth库实现基于会话Cookie（Session Cookie）的认证机制，支持OAuth第三方登录（Google、GitHub）与邮箱密码登录。认证防护分为两个层次：前端页面通过useSession钩子进行客户端守卫，未登录用户自动重定向至登录页；API路由通过getSession方法从请求Cookie中提取并校验会话，确保每个接口调用均经过身份验证。API接口通过Upstash Redis实现三级速率限制，采用滑动窗口算法按客户端IP限流：通用接口每10秒最多10次请求，认证相关接口每60秒最多5次请求（防止暴力破解），资源操作接口每60秒最多20次请求。文件上传接口校验文件扩展名（仅允许.ifc格式），前端通过accept属性与后端双重校验防范非法文件注入。此外，系统通过Content-Security-Policy、X-Frame-Options（DENY）、X-Content-Type-Options（nosniff）等HTTP安全响应头防范XSS与点击劫持攻击。

**可维护性要求**。前后端分离使前后端可独立迭代；组件化设计降低了功能扩展的耦合度；配置参数外置（环境变量+配置文件）便于环境迁移；代码结构遵循统一规范，降低后续维护成本。

## 3.2 系统架构设计

系统采用前端、后端、数据存储三层分离架构，如图3.2所示。这一架构选型基于以下考量：前端与后端的技术栈差异（TypeScript与Python）决定了二者难以在同一进程内运行，分离部署是自然选择；LLM调用与IFC文件解析均为计算密集型操作，独立的后端服务可以独立扩展资源，不受前端渲染负载影响；数据层的独立使得存储方案（MongoDB、GridFS）可以按需替换，不影响业务逻辑层。三层之间通过明确的接口契约（HTTP RESTful API）通信，各层内部的技术选型互不耦合。

前端基于Next.js 15框架构建，使用App Router模式管理页面路由与API端点，负责用户界面渲染、输入校验与结果展示。后端为独立的Python FastAPI服务，处理IDS生成管道与IFC合规审查等业务逻辑。浏览器不直接访问Python后端——Next.js的API Routes层承担了Backend-for-Frontend（BFF）职责，负责会话验证、速率限制与文件存储管理，所有请求均经BFF层转发至Python服务。

以IDS规则生成为例，一次完整的请求流转如下：用户在前端页面输入自然语言规范描述，浏览器向BFF层发送POST请求；BFF层完成会话验证与速率限制检查后，在MongoDB中创建一条状态为"待处理"的任务记录，并将请求转发至Python后端；Python后端通过FastAPI的BackgroundTasks机制异步启动五阶段生成管道，立即返回任务ID，避免长时间阻塞HTTP连接；管道执行过程中，任务状态经由"处理中"更新为"已完成"或"失败"，生成的IDS文件存储于GridFS；前端通过每5秒一次的状态轮询感知任务进展，任务完成后提供文件下载入口。

数据层采用MongoDB数据库存储用户数据、任务记录与审查报告等持久化信息；MongoDB GridFS（Grid File System，网格文件系统）用于处理大文件存储，IDS生成结果与IFC模型文件均通过GridFS分块存储；部分静态资源通过UploadThing服务托管。

---

> **【图表需求 - 待创建】**
>
> **图3.2 系统整体架构图**
> - **位置**：此处（3.2节架构描述后）
> - **类型**：三层架构图（层级图）
> - **内容要点**：前端交互层、后端服务层、数据存储层的结构与直接通信关系

---

### 3.2.1 前端交互层设计

前端包含以下页面：登录注册页（基于better-auth的会话认证）、IDS生成页（自然语言输入、IFC版本选择、规则预览）、知识库查询页（实体搜索与详情展示）、审查执行页（IFC文件上传、IDS文件选择、报告展示）、历史记录页（生成与审查历史的浏览与下载）。

前端采用TypeScript语言开发，利用React Hooks管理组件状态，通过原生fetch API发起HTTP请求。界面样式采用Tailwind CSS框架实现响应式布局。

Next.js的API Routes不仅服务于页面渲染，还承担BFF层职责：每个API路由在处理业务逻辑前，先执行会话验证（从请求Cookie中提取并校验session）与速率限制检查（基于客户端IP的滑动窗口限流），然后将文件写入GridFS或创建任务记录，最后才将请求转发至Python后端。这种设计将认证、限流等横切关注点集中在BFF层，Python后端无需重复实现，降低了后端服务的复杂度。

### 3.2.2 后端服务层设计

后端FastAPI服务包含以下接口模块。

**IDS生成接口**。接收自然语言输入，调用远程大语言模型与本地五阶段生成管道完成规则构建。五阶段管道涵盖结构化解析、方面分类、知识库映射、约束提取与IDS构建，详见第四章。

**知识库检索接口**。基于sentence-transformers加载BAAI/bge-m3嵌入模型生成1024维向量，通过faiss-cpu执行相似度检索。向量在首次计算后持久化缓存，避免重复推理。

**审查执行接口**。接收IFC文件与IDS文件，调用ifctester引擎执行检验并返回结构化报告。ifctester底层依赖ifcopenshell库解析IFC模型数据。

### 3.2.3 数据存储层设计

数据存储采用MongoDB数据库，其文档型存储模式适合存储结构化但不规则的BIM数据。Ellul等[54]针对BIM与3DGIS数据集的系统性能对比实验表明，在处理大规模空间数据时，MongoDB的灵活模式与查询性能优于传统关系型数据库PostgreSQL。该结论支撑了本研究选用MongoDB作为底层存储的方案。

主要数据集合包括：users（用户基本信息，含better-auth会话数据）、history_ids（IDS生成历史，含输入文本与生成结果JSON）、history_reviews（审查历史，含IFC文件ID、IDS文件ID与审查报告）。大文件（IFC模型、生成的IDS文件）通过MongoDB GridFS分块存储，突破单文档16MB大小限制[58]。部分静态资源文件使用UploadThing服务托管，与GridFS形成互补，减轻数据库的存储压力。

## 3.3 技术选型

上一节从系统层面阐述了三层架构的分层逻辑，本节聚焦于各层内部的具体技术选型，从技术特性与替代方案对比的角度论证选择依据。

### 3.3.1 前端技术选型

**Next.js框架**。Next.js是基于React的全栈框架，支持服务端渲染（SSR，Server-Side Rendering）与静态页面生成（SSG，Static Site Generation）。选用Next.js而非Vue/Nuxt或Angular的原因在于：其App Router模式支持服务端组件，减少了首屏JavaScript体积；同一技术栈内可同时实现页面渲染与API端点，降低维护成本；社区生态成熟，TypeScript支持完善。

**TypeScript语言**。TypeScript为JavaScript添加静态类型检查，能够在编译阶段发现类型错误。对于涉及复杂数据结构（如IDS JSON、IFC实体定义）的场景，类型约束可减少运行时异常。

**Tailwind CSS框架**。Tailwind采用原子化CSS类名，通过组合类名快速构建样式。相比Bootstrap等组件库，Tailwind避免了未使用样式的冗余加载，更适合自定义界面的精细化控制。

**原生fetch API**。前端HTTP请求采用浏览器原生fetch API，未引入Axios等第三方库。原因在于项目请求场景简单（主要为JSON数据的GET/POST），fetch API已能满足需求，引入外部库反而增加bundle体积。

### 3.3.2 后端技术选型

**FastAPI框架**。FastAPI是基于Starlette与Pydantic构建的Python异步Web框架。选用FastAPI而非Flask或Django的原因在于：其原生支持异步请求处理（async/await），适合LLM（Large Language Model，大语言模型）调用等I/O密集型操作；基于Pydantic的类型验证确保请求参数与响应数据的规范性；自动生成OpenAPI文档，便于接口调试。TechEmpower Web Framework Benchmarks的测试数据显示，FastAPI在JSON序列化场景下的吞吐量约为Flask的3-5倍，这一性能优势对于需要频繁调用LLM后端的系统尤为重要。

**LLM调用与远程服务选型**。本系统的LLM调用通过OpenAI Python SDK实现，未引入LangChain等中间框架。该决策基于以下考量：五阶段生成管道的逻辑较为固定，LangChain的链式抽象反而增加理解与调试成本；直接调用SDK使错误处理、日志追踪与版本控制更透明。实际的模型服务由OpenRouter平台提供，调用Claude-3.5-Sonnet模型执行语义理解与规则生成任务。OpenRouter提供兼容OpenAI格式的API接口，因此可直接复用OpenAI SDK作为客户端。

选择远程大语言模型而非本地部署方案，主要基于以下工程考量。其一，**温度参数的精确可控性**是本系统流水线设计的核心需求——各阶段需要不同的确定性水平（阶段一结构化解析设为0.1以兼顾灵活性，阶段二Facet分类设为0.05以保证一致性），远程API对温度参数的响应精确且可复现；本地部署的开源模型受量化精度、推理框架实现差异等因素影响，温度参数与输出随机性之间的对应关系不够稳定。其二，远程API支持JSON Schema格式约束，能够强制模型输出符合预定义结构，降低了后处理解析的失败率；本地模型的结构化输出能力依赖正则表达式后处理，成功率不稳定。其三，本地部署需要GPU资源管理、模型量化与推理框架维护等额外工程投入，与本研究聚焦的流水线架构设计目标无关。向量嵌入采用sentence-transformers库加载BAAI/bge-m3模型，生成1024维L2归一化向量。

**faiss-cpu向量检索库**。采用Facebook AI Similarity Search（FAISS）的IndexFlatIP索引执行精确内积检索[47]。对于归一化向量，内积等价于余弦相似度，保证了检索结果的准确性。当前知识库规模（2,291个实体）下，精确检索的计算开销处于可接受范围。

**ifcopenshell与ifctester**。ifcopenshell是开源IFC文件解析库，支持IFC2x3与IFC4版本的数据读取与修改，为知识库构建提供实体定义提取能力。ifctester是IDS合规审查工具，作为审查执行引擎加载IDS规则并对IFC模型执行检验。

### 3.3.3 数据存储技术选型

**MongoDB数据库**。MongoDB是基于BSON（Binary JSON）格式的文档型数据库，每条记录以键值对形式存储，支持嵌套文档与数组等复杂数据结构。与关系型数据库需要预定义表结构（schema）不同，MongoDB的集合（collection）中文档可以包含不同字段，这一特性适合存储结构不规则的BIM数据——例如IDS规则中的facet可能包含实体约束、属性约束或材料约束，各类约束的字段组合各不相同，若使用关系型数据库则需要多表关联或大量空列。MongoDB还提供聚合管道（Aggregation Pipeline）用于对文档进行多阶段的数据转换与统计查询，系统利用该能力实现任务状态的分组统计与历史记录的筛选排序。前文已述，Ellul等[54]针对BIM与3DGIS数据集的对比实验表明，MongoDB在处理大规模空间数据时的查询性能优于PostgreSQL，为本研究的选型提供了实证支撑。

**GridFS机制**。GridFS是MongoDB官方提供的大文件存储规范，将超过16MB的文件分割为固定大小的块（默认256KB/块），分别存储于chunks集合与files集合中。files集合记录文件的元数据（文件名、长度、上传时间、内容类型等），chunks集合存储文件的二进制数据块，二者通过文件ID关联[58]。这种分块存储机制带来两个优势：其一，支持流式上传与下载，无需将整个文件加载至内存，适合BIM模型等大文件场景；其二，支持对文件的部分读取，例如仅下载文件的前几块用于预览。本系统中，用户上传的IFC模型文件与系统生成的IDS XML文件均通过GridFS存储，前端下载时通过MongoDB的DownloadStream逐块读取并返回。

**UploadThing服务**。除MongoDB外，系统使用UploadThing服务托管部分静态资源文件（如用户头像、图片附件），与GridFS形成互补，减轻数据库的存储压力。UploadThing提供CDN加速与文件类型白名单等能力，适合体积较小但访问频率较高的静态资源。

## 3.4 本章小结

本章从需求分析、架构设计与技术选型三个层面展开论述。需求分析明确了IDS规则生成、IFC知识库检索、合规审查执行、用户管理四项功能需求，并结合LLM推理与IFC解析的实际耗时特征设定了性能指标；非功能需求覆盖了认证双层防护、三级速率限制、任务状态生命周期与失败重试等可靠性与安全性设计。架构设计提出了前端、后端、数据存储三层分离方案，通过Next.js API Routes承担BFF职责实现认证与限流的集中管理，并以IDS生成为例阐述了从请求接收到结果返回的完整数据流。技术选型部分对比了各层候选方案的特性差异，确定了Next.js、FastAPI、MongoDB等具体技术栈。本章明确的功能边界与架构约束为第四章IDS生成管道的详细设计界定了输入与输出条件。

---

## 第三章引用参考文献

| 编号 | 引用信息 |
|------|----------|
| [8] | Wu L, et al. Automated compliance checking in the architecture, engineering, and construction industry: A systematic review[J]. Automation in Construction, 2023. |
| [11] | Chen Z, et al. Large language model-based automated compliance checking for building designs[J]. 2024. |
| [37] | buildingSMART International. Information Delivery Specification (IDS) Standard[EB/OL]. https://www.buildingsmart.org/standards/bsi-standards/information-delivery-specification-ids/, 2023. |
| [47] | Johnson J, Douze M, Jégou H. Billion-scale similarity search with GPUs[J]. IEEE Transactions on Big Data, 2021, 7(3): 535-547. |
| [49] | buildingSMART International. IDS 1.0 Official Documentation[EB/OL]. https://buildingsmart.org/standards/bsi-standards/information-delivery-specification-ids/. |
| [54] | Ellul C, Loo R, Floros G. Exploring the potential of NoSQL databases for a BIM and 3D GIS enabled location framework for construction digital twins and the golden thread[J]. ISPRS Annals, 2024, X-4-W5: 137-144. https://isprs-annals.copernicus.org/articles/X-4-W5-2024/137/2024/ |
| [55] | Peng J, et al. Automated code compliance checking research based on BIM and knowledge graph[J]. Scientific Reports, 2023, 13: 5618. https://doi.org/10.1038/s41598-023-34342-1 |
| [57] | Automated compliance checking system for structural design codes in a BIM environment[J]. KSCE Journal of Civil Engineering, 2024. https://doi.org/10.1007/s12205-024-1121-5 |
| [58] | Lv Z, Li X, Lv H, Xiu W. BIM big data storage in WebVRGIS[J]. IEEE Transactions on Industrial Informatics, 2020, 16(4): 2566-2573. https://doi.org/10.1109/TII.2019.2916689 |
