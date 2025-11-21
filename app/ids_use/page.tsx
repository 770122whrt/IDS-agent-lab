"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useSession } from "@/app/lib/auth-client";

export default function IdsUse() {
  const { data: session } = useSession();
  const userId = session?.user?.id || session?.user?.email || ""; // 根据你的用户结构调整
  const [file, setFile] = useState<File | null>(null);
  const [resources, setResources] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 上传资源
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId || !file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("userId", userId);
    formData.append("file", file);
    await fetch("/api/resources", {
      method: "POST",
      body: formData,
    });
    setFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
    await fetchResources();
    setLoading(false);
  };

  // 获取资源列表
  const fetchResources = async () => {
    if (!userId) return;
    const res = await fetch(`/api/resources?userId=${userId}`);
    const data = await res.json();
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