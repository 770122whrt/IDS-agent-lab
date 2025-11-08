## 1.basic knowledge of MongoDB

### 1.1 the basic structure interpretation

**Cluster**(集群 最大概念 相当于是磁盘) -- **database**(数据库 相当于一个文件夹) -- **collection**(相当于是 一个excel文件) -- **document**(文档 MongoDB的最小单元 相当于excel中的最小数据 但是更多样化)

For example， the following Image indicate that I create a cluster called cluster0. Meanwhile there is a dataset which has been created called sample_mflix. Then we noticed that in this sample_mflix we got varies collection like comments and so on, followed with number of documents.

![](E:\code for project\IDS_practise\week1\my-first-app\note\structure.png)

**cluster** is where MongoDB based on and execute. Choose a selective server(Microsoft Azure) and region(Hong Kong) and other .

**collection** is a series of Document that stored in Database, one database could have many collections to store it. Different to SQL, it didn't predefined some fields, so it's flexible for users.

### 1.2 the route.js

A **route** file allows you to create custom request handlers for a given route. The following [HTTP methods](https://developer.mozilla.org/docs/Web/HTTP/Methods) are supported: **.`GET`,`POST`,`PUT`,`PATCH`,`DELETE`,`HEAD`,`OPTIONS`**.

If `OPTIONS` is not defined, Next.js will automatically implement `OPTIONS` and set the appropriate Response `Allow` header depending on the other methods defined in the Route Handler.

- request ：The object is a [NextRequest](https://nextjs.org/docs/app/api-reference/functions/next-request) object, which is an extension of the Web `request`API.
- context ：focus on **`params`**: a promise that resolves to an object containing the [dynamic route parameters](https://nextjs.org/docs/app/api-reference/file-conventions/dynamic-routes) for the current route.

 pay attention to the example structure!

![](.\image-context-structure.png)

- RouteContext: You can type the Route Handler context using to get strongly typed from a route literal. It is a globally available helper.After type generation, the helper is globally available. It doesn't need to be imported.
- other examples in website [文件系统约定：route.js |Next.js](https://nextjs.org/docs/app/api-reference/file-conventions/route)

There are a few cases where you have to **write database queries**:

- When creating your **API endpoints**, you need to write logic to interact with your database.
- If you are using React Server Components (fetching data on the server), you can skip the API layer, and query your database directly without risking exposing your database secrets to the client.

Mind of that **client - API - database**

### 1.3 promise

Server Components(服务器组件) support JavaScript Promises, providing a solution for asynchronous tasks like data fetching natively and support await. no longer need useState and useEffect to manage async function.

- pending 正在进行 triggered by `initialization`

- fullfilled 已成功 triggered by `resolve()`

- reject 已失败 调用了 `reject()`

- **Promise< number >** a genetic define. It means that if it resolved it will return number

- `Promise.all`（Parallel execute multi-request） `Promise.race`（the fastest finshed one）

- ```typescript
  async function run() {
    try {
      const result = await p; // result 推断为 number
      console.log("成功：", result);
    } catch (err) {
      console.error("失败：", err);
    }
  }
  run();`Promise.all`（并行多个请求）
  ```

### 1.5 func of  API create, read, update, delete. (collection - users)

* Firstly, find the data in cluster. It's cluster0 - sample_mflix - users, and we get its schema and fix ours in document User.ts.

![image-20251107205200115](.\image-users-data.png)

* Then Fix the link to atlas, and record it in our **.env.local** , and fix the mongodb.ts.

* we try to create the function **`. GET`  `POST`** in route.ts. Use the function imported from mogoose, they `User.create` `User.find({})`  And we use rest-client to test the 

  ```http
  ### Create User Alice
  POST http://localhost:3000/api/users
  Content-Type: application/json
  
  {
    "name": "Alice",
    "email": "alice@example.com",
    "password": "secret123"
  }
  
  
  ```

  

*  the function of the function of POST back is as follows, we could also see the new `Alice` append.

  <img src="E:\code for project\IDS_practise\week1\my-first-app\note\GET-back.png" alt="image-20251107222925164" style="zoom: 33%;" />

* the function of POST back is as follows, the status 201 means created successfully

  <img src="E:\code for project\IDS_practise\week1\my-first-app\note\post-back.png" alt="image-20251107222534558" style="zoom:50%;" />

* the other two functions need [id] which means the main-field(not repeatible).`User.findByIdAndDelete(id)`

  `User.findByIdAndUpdate(id, body, {new: true, }); `// return updated user ,default back old version

**the Dynamic segments** Used in the function of PUT and Delete because they all need the [id] to  locate the user. 

<img src="E:\code for project\IDS_practise\week1\my-first-app\note\image-dynamic-route.png" alt="image-20251107203007167" style="zoom:67%;" />

 PUT /api/users/690dff1bd2afd0c9d2de0451 200 in 2.5s (compile: 2.4s, render: 128ms)  and the response as follow

<img src="C:\Users\rt do believe\AppData\Roaming\Typora\typora-user-images\image-20251107225924943.png" alt="image-20251107225924943" style="zoom: 67%;" />

DELETE /api/users/690dff1bd2afd0c9d2de0451 200 in 144ms (compile: 19ms, render: 125ms) After delete, there's no record for specifically Alice, we can get the information from GET again.

<img src="C:\Users\rt do believe\AppData\Roaming\Typora\typora-user-images\image-20251107230034606.png" alt="image-20251107230034606" style="zoom:67%;" />

But I found that the id is difficult to find anyway. So it's neccesery to write a **search function**. It's in app/api/users/search/route.ts.

 

```
const { searchParams } = new URL(req.url);
const name = searchParams.get("name");
const users = await User.find({ name: { $regex: name, $options: "i" } });
```

the final result is as follows, it pack the results of the names which contains the search pattern.

![image-20251107232155215](E:\code for project\IDS_practise\week1\my-first-app\note\search-name.png)

## 2. create authentication with user, research lib (mongo, ORM?)

[Object-Relational Mappers](https://en.wikipedia.org/wiki/Object–relational_mapping) (or ORMs) can improve the developer experience customizing database interactions in the following ways:

- Abstracting away the need for query language.
- Managing serialization/deserialization of data into objects.
- Enforcing schema requirements.

Because MongoDB is a non-relational database management system, ORMs are sometimes referred to as ODMs (Object Document Mappers), but the terms can be used interchangeably in the MongoDB domain.

### Mongoose

Mongoose is a third-party Node.js-based ODM library for MongoDB. It enforces a specific schema at the application layer and offers a variety of hooks, model validation, and other features.

See the [Mongoose documentation](https://mongoosejs.com/) or [MongoDB & Mongoose: Compatibility and Comparison](https://www.mongodb.com/developer/languages/javascript/mongoose-versus-nodejs-driver/) for more information.

### Prisma

Prisma is a third-party ODM for Node.js and Typescript that fundamentally differs from traditional ORMs. It uses declarative Prisma schemas as the single source of truth for both your database schema and models. The Prisma client reads and writes data in a type-safe manner, and returns plain JavaScript objects.

See [Prisma & MongoDB](https://www.prisma.io/mongodb) for more information.



Mainly use **Mongoose** for we has created the enviroment. AND followings are some websites for reference and some libs.

* [教程：开始使用Mongoose - Node.js驱动程序- MongoDB Docs](https://www.mongodb.com/zh-cn/docs/drivers/node/current/integrations/mongoose-get-started/)

* [Mongoose v8.19.1: Getting Started](https://mongoosejs.com/docs/index.html)

* [Node.js + MongoDB: User Authentication & Authorization with JWT - BezKoder](https://www.bezkoder.com/node-js-mongodb-auth-jwt/)

- AWS authentication - [@aws-sdk/credential-providers ](https://github.com/aws/aws-sdk-js-v3/tree/main/packages/credential-providers)  but it seems to reload the whole project.

- [Web 身份验证 API - Web API |MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API)

- Passport lib [Username & Password Tutorial: Verify Password](http://www.passportjs.org/tutorials/password/verify/)

- json-web-token [auth0/node-jsonwebtoken: JsonWebToken implementation for node.js http://self-issued.info/docs/draft-ietf-oauth-json-web-token.html](https://github.com/auth0/node-jsonwebtoken) 

- Oauth2:  [oauth - npm](https://www.npmjs.com/package/oauth)   [理解OAuth 2.0 - 阮一峰的网络日志](https://www.ruanyifeng.com/blog/2014/05/oauth_2_0.html)  Open Authorization from an app to another seem not suitable 

  <img src="E:\code for project\IDS_practise\week1\my-first-app\note\OAuth-structure.jpg" alt="77961513e833d47af40d933997ba4c70" style="zoom: 25%;" />

- Now I Refer to that article for the file with registration and login functionality added.

  <img src="E:\code for project\IDS_practise\week1\my-first-app\note\jwt-token-based-authentication.png" style="zoom: 67%;" />

  The Client typically attaches JWT in **Authorization** header with Bearer prefix:

  ```
  Authorization: Bearer [header].[payload].[signature]
  ```

  | Methods | Urls             | Actions    |
  | :------ | :--------------- | :--------- |
  | POST    | /api/auth/signup | 注册新帐户 |
  | POST    | /api/auth/signin | 登录帐户   |



## 3. some usage of command and notes

**pnpm run lint**: use eslint to research the whole project and fix some problems

**pnpm exec prettier . --write** use prettier to regular code. But now it has been set to run prettier before every commit.

**pnpm run dev** : run the whole backend project. And use http://localhost:3000 to open in explorer.

The function _Get_ in path **app/api/users/route.ts** will be automatically recognized. When the frontend use _fetch("/api/users");_ it will get it. It use **File-based routing** (文件系统自动路由) to create an address.

- Make sure to reveal your database secrets before copying it into your file.`.env`
- The URL = 'mongodb+srv://user:password@cluster0.maypzsy.mongodb.net/mydatabase?appName==admin'

