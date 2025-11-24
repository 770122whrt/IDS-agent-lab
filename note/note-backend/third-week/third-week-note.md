# WEEK3

## 1. frontend code 

### 1.1 app/ids-use/page.tsx 

补充了看不懂的代码的注释 已经添加进文件。部分粘贴如下：

**关键点 1 (`useRef`)**：

- **为什么要这么写？** React 是数据驱动的，但在处理 `<input type="file" />` 时，我们需要直接操作这个 DOM 节点来**清空**它。当文件上传成功后，单纯把 `state` 设为 `null` 并不会清除输入框里显示的文件名，必须通过 `ref.current.value = ""` 来重置 UI。

使用 Ref 引用 DOM 元素  `const fileInputRef = useRef<HTMLInputElement>(null); `

useRef 它返回一个可变(mutable)的 ref 对象，这个对象的 `.current` 属性被初始化为你传入的值。 

返回的这个对象在组件的整个生命周期内都会保持存在（持久化）无论组件渲染多少次，`useRef` 返回的永远是**同一个内存地址**的那个对象，即值不会变。

**关键点2. 为什么要用 `FormData`:**   

* 因为文件是“二进制数据”，普通的 JSON ({ key: value }) 无法高效传输文件。    

* `FormData` 会自动将请求头的 Content-Type 设置为 "multipart/form-data", 这是浏览器上传文件的标准方式。   

  ```typescript
   const formData = new FormData();    
   formData.append("userId", userId);   
   formData.append("file", file);
  ```

## 1.2 暂时版本的 app/api/resources/route.ts

导入需要的模块 -----  设置存储目录  ------ 一个模拟的“数据库”

POST ---- 1. 解析表单   ----  2.检查参数是否缺失 -----3.把file转成 buffer 格式 ----  4.生成文件名 ---- 5.写入磁盘 ----6.返回成功信息

GET：获取某个用户的文件列表 ---- 1. 从 URL 里拿 userId ---- 2.没有 userId则报错 ---- 3.查找该用户上传的文件 --- 4.







## 2.Backend Addition

### 2.1 backend / resources.ts 

这个函数是用来存储resources类的！和储存User类的内容相似，















## 2.2 route.ts 重新改写

MongoDB 或 Node.js 都只接受：Buffer、Uint8Array、或其他底层二进制格式 

const arrayBuffer = await file.arrayBuffer(); //是 JavaScript 官方 Web 标准  File → ArrayBuffer

const buffer = Buffer.from(arrayBuffer);  //File → ArrayBuffer → Buffer 



**Post**  --- 1.连接数据库 --- 2.解析前端传来的 FormData并获取字段（根据前端 append 的 key） ---  3. 校验数据完整性 --- 4.文件处理：将 Web File 对象转换为 Node.js ---- 5.Buffer 创建数据库记录 --- 6.返回成功响应

**GET ** --- 1.获取 URL 中的查询参数 ?userId=... 2. 查询数据库 所有文件 + 按时间逆序排布 --- 3. 返回数据包裹



## 2.3 try GridFS

在 MongoDB 中，普通的文档（Document）有一个 **16MB 的硬性限制**。如果你试图往我们在上一步写的 `buffer` 字段里存一个 20MB 的高清视频，MongoDB 会直接报错拒绝保存。

为了解决这个问题，MongoDB 提供了一个官方规范：**GridFS**。

### 什么是 GridFS？（通俗解释）

想象你有一根超级长的法棍面包（大文件），冰箱（MongoDB 文档）太小放不进去。 **GridFS 的策略是：**

1. **切片**：把法棍切成一片片的小面包干（默认每片 255KB），这就叫 **Chunks**。
2. **索引**：找个笔记本，记录下“这个法棍切了多少片，按什么顺序拼回去”，这就叫 **Files (Metadata)**。
3. **存储**：把小面包干分别存进一个集合（`fs.chunks`），把笔记本记录存进另一个集合（`fs.files`）。

这样，无论文件多大（甚至是几 GB 的电影），都能存进去，取出来时自动拼好。



[使用GridFS存储大型文件 - Node.js驱动程序- MongoDB Docs](https://www.mongodb.com/zh-cn/docs/drivers/node/current/crud/gridfs/)

- `chunks` 集合存储二进制文件数据段。 数据

- `files` 集合存储文件元数据。 索引 

- `const db = client.db(dbName);
  const bucket = new mongodb.GridFSBucket(db);` 创建一个以FS为默认名字的bucket

  `const bucket = new mongodb.GridFSBucket(db, { bucketName: 'myCustomBucket' });`  自定义bucket

- 使用 `GridFSBucket` 中的 `openUploadStream()` 方法为指定文件名创建上传流。

  使用 `openUploadStream()` 方法可以指定配置信息，如文件数据块大小和其他作为元数据存储的字段/值对。

```typescript
fs.createReadStream('./myFile').//fs是name 
     pipe(bucket.openUploadStream('myFile', {
         chunkSizeBytes: 1048576,
         metadata: { field: 'myField', value: 'myValue' }
     }));
```

* 检索文件信息  查询GridFS 存储桶的 `files` 集合的文件元数据

  * 文件的 `_id`
  * 文件的名称
  * 文件的长度/大小
  * 上传日期和时间
  * 您可以在其中存储任何其他信息的 `metadata` 文档

  在 `GridFSBucket` 实例上调用 `find()` 方法，以便从 GridFS 存储桶中检索文件。该方法会返回一个 `FindCursor` 实例，您可以从该实列访问结果。

  ```typescript
  const cursor = bucket.find({});
  for await (const doc of cursor) {
     console.log(doc);
  }
  ```

* 删除文件`bucket.delete(ObjectId("60edece5e06275bf0463aaf3"));` + id 而不是name

* 删除GridFS存储桶 `bucket.drop();`

* 下载文件：您可以使用 `GridFSBucket` 中的 `openDownloadStreamByName()` 方法创建下载流，从 MongoDB 数据库下载文件。

  `bucket.openDownloadStreamByName('myFile').
       pipe(fs.createWriteStream('./outputFile'));`

  如果存在多个具有相同 `filename` 值的文档，`GridFS`将流式传输具有给定名称（由 `uploadDate` 字段决定）的最新文件。







需要重新改写 `route.ts `和 `resource.ts`

后者较为简单，将本来存储的buffer变成`fileID`即可

前者代码复杂但是基本注释中写的较为完整，这里补充一点：

* 为什么用 `const readStream = Readable.from(buffer);` 而不是`fs.createReadStream('./myFile')`

  * **数据源头** 前者是**内存 (RAM)**，而后者是**本地文件系统 (磁盘)** 前者不需要路径 后者需要清晰路径

    