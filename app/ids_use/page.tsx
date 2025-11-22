"use client"; // 关键点 1：声明这是一个客户端组件 Next.js 13+ (App Router) 默认组件是服务端的

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useSession } from "@/app/lib/auth-client";

export default function IdsUse() {
  //通过你们的 auth-client 自动拿到了当前登录的用户 ID
  const { data: session } = useSession();
  const userId = session?.user?.id || session?.user?.email || ""; // 根据你的用户结构调整


  const [file, setFile] = useState<File | null>(null);
  const [resources, setResources] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // 关键点 2：使用 Ref 引用 DOM 元素 创建一个“空口袋”
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 上传资源
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();// 1. 阻止浏览器默认刷新页面的行为
    if (!userId || !file) return;// 2. 防御性编程：确保数据不为空
    
    setLoading(true);
    
    // 3.新创立 formdata类别 用来传输文件！！
    const formData = new FormData();
    formData.append("userId", userId);
    formData.append("file", file);


    // 4. 发送请求
    //前端把用户 ID + 上传文件通过 multipart/form-data 发送给 /api/resources 这个后端接口。
    await fetch("/api/resources", {
      method: "POST",
      body: formData,
    });
    // 5. 上传成功后的清理工作
    setFile(null);// 清除 React 状态
    if (fileInputRef.current) fileInputRef.current.value = "";// 清除视觉上的输入框
    await fetchResources();// 6. 立即刷新列表，让用户看到刚刚传的文件
    setLoading(false);
  };

  // 查询逻辑：fetchResources
  const fetchResources = async () => {
    // 为什么要用 URL 查询参数 (?userId=...)？
    // GET 请求没有 body。我们需要告诉后端“我是谁”，
    // 后端通过 request.nextUrl.searchParams.get('userId') 来获取这个值，
    // 从而只去 MongoDB 查属于该用户的数据，保证数据隔离。
    if (!userId) return;
    const res = await fetch(`/api/resources?userId=${userId}`);
    const data = await res.json();

    //data：这是你从后端 API 收到的整个包裹（JSON 对象）。
    //data.resources：这是包裹里真正重要的东西（你的文件列表数组）。
    setResources(data.resources || []);
  };

  return (
    <div className="max-w-xl mx-auto py-10">
      <h2 className="text-3xl md:text-4xl font-extrabold mb-6 flex items-center gap-2 text-blue-700 dark:text-blue-300">
        <span>📤</span> 资源上传与查询 <span>📋</span>
      </h2>
      <form className="space-y-4 mb-8" onSubmit={handleUpload}>
        {/* 用户ID自动获取，无需输入 */}
        <Input
          type="file"
          //进行绑定
          ref={fileInputRef}
          onChange={e => { setFile(e.target.files?.[0] ?? null); }}
        />
        <Button type="submit" disabled={loading || !userId || !file}>
          {loading ? "上传中..." : "上传资源"}
        </Button>
        <Button type="button" variant="outline" onClick={fetchResources} disabled={!userId}>
          查询我的资源
        </Button>
      </form>
      <div>
        <h3 className="text-lg font-semibold mb-2">我的资源列表</h3>
        {resources.length === 0 ? (
          <p className="text-gray-500">暂无资源</p>
        ) : (
          <ul className="space-y-2">
            {resources.map((r) => (
              <li key={r.id} className="border rounded p-2 flex flex-col">
                <span>文件名: {r.originalname}</span>
                <span>上传时间: {new Date(r.uploadTime).toLocaleString()}</span>
                <span>资源ID: {r.id}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}