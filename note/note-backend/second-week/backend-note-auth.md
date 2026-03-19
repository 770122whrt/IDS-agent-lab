# HOW TO USE GIT

## 本地仓库

1.`git commit` 提交 直接往下走一个叶节点

2.`git branch` 创建一个分支节点！！多创建分支总是不会错的

3.`git checkout  **`  : ** 代表着分支的名字 这个命令用来切换到另一个分支

4.`git checkout - b **`: 创建切换到某一个分支上面

5.`git merge`: 合并多个分支

6.`git rebase **`Rebase 实际上就是取出一系列的提交记录，“复制”它们，然后在另外一个地方线性跟在后面

7.`HEAD` 总是指向当前分支上最近一次提交记录 head是一个指向！！！ 指向目前所在处 checkout ** 可改变。

8.` ^`操作 向上进行一个level的回溯  `main^^`向上两次  `git checkout main^`

9.使用相对引用最多的就是移动分支。可以直接使用 `-f` 选项让分支指向另一个提交。例如:

```bash
git branch -f main HEAD~3
```

上面的命令会将 main 分支强制指向 HEAD 的第 3 级 parent 提交。  `-f` 则容许我们将分支强制移动到那个位置。

10.撤销变更: `git reset`  相当于回退记录  `git reset HEAD~1` 向上移动一格

`git revert `撤销更改并**分享**给别人，我们需要使用 `git revert`

11.`git cherry-pick <提交号>...` 提交号就是分支的名字 知道哈希值时非常简单

12.交互式 rebase 指的是使用带参数 `--interactive` 的 rebase 命令, 简写为 `-i`  重新复制了一份。

* 调整提交记录的顺序
* 删除你不想要的提交 pick改变
* 合并提交。 `git rebase -i C1`

看一个在开发中经常会遇到的情况：我正在解决某个特别棘手的 Bug，为了便于调试而在代码中添加了一些调试命令并向控制台打印了一些信息。这些调试和打印语句都在它们各自的提交记录里。最后我终于找到了造成这个 Bug 的根本原因，解决掉以后觉得沾沾自喜！

最后就差把 `bugFix` 分支里的工作合并回 `main` 分支了。你可以选择通过 fast-forward 快速合并到 `main` 分支上，但这样的话 `main` 分支就会包含我这些调试语句了。

- 用这两个命令`git rebase -i` `git cherry-pick` 进行对于最后一个提交记录的提交即可。

13.这种情况也是很常见的：你之前在 `newImage` 分支上进行了一次提交，然后又基于它创建了 `caption` 分支，然后又提交了一次。此时你想对某个以前的提交记录进行一些小小的调整。比如设计师想修改一下 `newImage` 中图片的分辨率，尽管那个提交记录并不是最新的了。

我们可以通过下面的方法来克服困难：

- 先用 `git rebase -i` 将提交重新排序，然后把我们想要修改的提交记录挪到最前
- 然后用 **`git commit --amend` **来进行一些小修改
- 接着再用 `git rebase -i` 来将他们调回原来的顺序
- 最后我们把 main 移到修改的最前端（用你自己喜欢的方法），就大功告成啦！





## 远程仓库：

1.git clone  从技术上来讲，`git clone` 命令在真实的环境下的作用是在**本地**创建一个远程仓库的拷贝

​	本地仓库多了一个名为 `o/main` `<remote name>/<branch name>`的分支, 这种类型的分支就叫**远程**分支。由于远程分支的特性导致其拥有一些特殊属性。远程分支反映了远程仓库(在你上次和它通信时)的**状态**。这会有助于你理解本地的工作与公共工作的差别 —— 这是你与别人分享工作成果前至关重要的一步.

​	远程分支有一个特别的属性，在你切换到远程分支时，自动进入分离 HEAD 状态。Git 这么做是出于不能直接在这些分支上进行操作的原因, 你必须在别的地方完成你的工作, （更新了远程分支之后）再用远程分享你的工作成果。

2.`git fetch`:从远程仓库获取数据 fetch 会获得所有关于仓库的内容,  实际上将本地仓库中的远程分支更新成了远程仓库相应分支最新的状态。`git fetch` 通常通过互联网（使用 `http://` 或 `git://` 协议) 与远程仓库通信。

**单纯的下载操作**

* 从远程仓库下载本地仓库中缺失的提交记录
* 更新远程分支指针(如 `o/main`)

3.`git pull` `git pull` 就是 `git fetch` 和 `git merge` 的缩写！抓取新的 并合并

4.`git fakeTeamwork`  执行一次提交 默认操作就是在远程仓库的 main 分支上做一次提交。

5.`git push` 负责将**你的**变更上传到指定的远程仓库，并在远程仓库上合并你的新提交记录。一旦 `git push` 完成, 你的朋友们就可以从这个远程仓库下载你分享的成果了！ **`push.default`** 检查 

这个操作会导致所有步骤被同步！！

6.For example!

假设你周一克隆了一个仓库，然后开始研发某个新功能。到周五时，你新功能开发测试完毕，可以发布了。但是 —— 天啊！你的同事这周写了一堆代码，还改了许多你的功能中使用的 API，这些变动会导致你新开发的功能变得不可用。但是他们已经将那些提交推送到远程仓库了，因此你的工作就变成了基于项目**旧版**的代码，与远程仓库最新的代码不匹配了。

这种情况下, `git push` 就不知道该如何操作了。如果你执行 `git push`，Git 应该让远程仓库回到星期一那天的状态吗？还是直接在新代码的基础上添加你的代码，亦或由于你的提交已经过时而直接忽略你的提交？

因为这情况（历史偏离）有许多的不确定性，Git 是不会允许你 `push` 变更的。实际上它会强制你先合并远程最新的代码，然后才能分享你的工作。



方法1：我们用 `git fetch` 更新了本地仓库中的远程分支，然后`merge`**合并**了新变更到我们的本地分支（为了包含远程仓库的变更），最后我们用 `git push` 把工作推送到远程仓库

方法2：我们用 `git fetch` 更新了本地仓库中的远程分支，然后用 rebase 将我们的工作移动到最新的提交记录下，最后再用 `git push` 推送到远程仓库。

`git pull --rebase `用 rebase 代替 merge

7.远程服务器拒绝!(Remote Rejected)

main被锁定 - Pull Request流程进行修改 ---(commit)到本地main, 然后试图推送(push)修改 会被拒绝

新建分支 - 推送(push)这个分支并申请pull request

新建一个分支feature, 推送到远程服务器. 然后reset你的main分支和远程服务器保持一致, 否则下次你pull并且他人的提交和你冲突的时候就会有问题.





# 2.BETTER AUTH

## 2.1 Config 

1.[Installation | Better Auth](https://www.better-auth.com/docs/installation)

2.Create Database Tables this part use commands as follows 没法成功跑起来？？

* `npx @better-auth/cli generate ` 
  * **`npx`**：这是一个 Node.js 的包运行工具，可以直接运行本地或远程的 npm 包，而不需要全局安装。`npx` 会从 npm 仓库或本地项目的 `node_modules` 中查找并执行指定的命令。
  * Better Auth includes a CLI tool to help manage the schema required by the library.**Generate**: This command generates an ORM schema or SQL migration file. 可能需要定义schema架构但是文档没有详细说明如何构建
  * ERROR [Better Auth]: mongodb-adapter is not supported. If it is a custom adapter, please request the maintainer to implement createSchema
* **`Migrate`**: This command creates the required tables directly in the database. (Available only for the built-in Kysely adapter) kysely是什么不知道——感觉不能用没跑

3.完善了app/lib/auth.ts文件，可包含`socialProviders` +  `emailAndPassword`

4.**`Mount Handler`** To handle API requests, you need to set up a route handler on your server.This route should handle requests for the path (unless you've configured a different base path).`/api/auth/*`

在 tsconfig中`"paths": { "@/*": ["./src/*"]` 定义了@代表根目录下src文件的意思—— 可以找有生改一下！

## 2.2 Basic Use

1. **`Email and password`** : `emailAndPassword:{enabled: true} `

2. better-auth -> auth.ts 主要是后端使用 因此存储在lib中 和 auth-client一起

3. 要对服务器上的用户进行身份验证，可以使用`auth.api.signInEmail`

   登录客户端方法：`authClient.signIn.email` 

   注册用户，您需要使用用户的信息调用客户端方法：`signUp.email`

## 2.3 Nextjs-integration

1. **Create API route**: We need to mount the handler to an API route. Create a route file inside directory. And add the following code:`/api/auth/[...all]`









# 3.Knowledge from the youtube video

1.zod 数据验证工具？`pnpm add zod` `pnpm add prisma -D` `pnpm add @Prisma/client` `pnpm dlx prisma init --datasource-provider mongodb` 得到 schema prisma----创建prisma.ts 创建实例 + 将schema组push到数据库中（？利用mongoose做这一步）

![image-20251112173305373](.\prisma.ts.png)

![image-20251112174246638](E:\code for project\IDS_practise\backend\ids-agent\note\note-backend\second-week\schema-examples.png)

## 4. Restore large files：MongoDB+GridFS

1.GridFS 用于存储和恢复那些超过16M（BSON文件限制）的文件(如：图片、音频、视频等)。GridFS 也是文件存储的一种方式，但是它是存储在MonoDB的集合中。

2.GridFS 可以更好的存储大于16M的文件。GridFS 会将大文件对象分割成多个小的chunk(文件片段),一般为256k/个,每个chunk将作为MongoDB的一个文档(document)被存储在chunks集合中。

3.GridFS 用两个集合来存储一个文件：fs.files与fs.chunks。每个文件的实际内容被存在chunks(二进制数据)中,和文件有关的meta数据(filename,content_type,还有用户自定义的属性)将会被存在files集合中。





mongodb-GridFS一些官方定义

[MongoDB-CN-Manual/cun-chu/gridfs.md at master · mongodb-china/MongoDB-CN-Manual](https://github.com/mongodb-china/MongoDB-CN-Manual/blob/master/cun-chu/gridfs.md)

[GridFS - 数据库手册 - MongoDB Docs](https://www.mongodb.com/zh-cn/docs/manual/core/gridfs/)

[使用GridFS存储大型文件 - Node.js驱动程序- MongoDB Docs](https://www.mongodb.com/zh-cn/docs/drivers/node/current/crud/gridfs/)

可能不太靠谱的mongoose-GridFS

[Mongoose 插件 storage-gridfs 的使用教程-JavaScript中文网-JavaScript教程资源分享门户](https://www.javascriptcn.com/post/65fbfba5d10417a222787aab)

[MongoDB 如何为GridFS集合创建mongoose模型|极客教程](https://geek-docs.com/mongodb/mongodb-questions/295_mongodb_how_to_create_mongoose_model_for_gridfs_collection.html)



