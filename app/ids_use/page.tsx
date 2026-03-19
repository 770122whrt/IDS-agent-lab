"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge"; // 👈 新引入
import { useSession } from "@/app/lib/auth-client";
// import { UploadButton } from "@/components/uploading"; // 暂时注释掉，如果没用到的话

// 定义资源接口，方便 TypeScript 提示
interface Resource {
  _id: string;
  originalname: string;
  uploadTime: string;
  status?: 'pending' | 'processing' | 'completed' | 'failed'; // 👈 对应后端状态
}

export default function IdsUse() {
  const { data: session } = useSession();
  const userId = session?.user?.id || session?.user?.email || "";

  const [file, setFile] = useState<File | null>(null);
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(false);
  const [analyzingId, setAnalyzingId] = useState<string | null>(null); // 记录正在点击分析的ID

  const fileInputRef = useRef<HTMLInputElement>(null);

  // 1. 上传逻辑 (保持不变)
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId || !file) return;
    
    setLoading(true);
    const formData = new FormData();
    formData.append("userId", userId);
    formData.append("file", file);

    try {
      await fetch("/api/resources", {
        method: "POST",
        body: formData,
      });
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      await fetchResources(); 
    } catch (error) {
      console.error("Upload failed", error);
    } finally {
      setLoading(false);
    }
  };

  // 2. 查询逻辑
  const fetchResources = async () => {
    if (!userId) return;
    try {
      const res = await fetch(`/api/resources?userId=${userId}`);
      const data = await res.json();
      setResources(data.resources || []);
    } catch (error) {
      console.error("Fetch resources failed", error);
    }
  };

  // 👇 新增：自动轮询 (每5秒刷新一次列表，检查分析状态)
  useEffect(() => {
    if (!userId) return;
    
    // 初始加载
    fetchResources();

    // 设置定时器
    const intervalId = setInterval(() => {
      // 只有当列表中有处于 "processing" 状态的任务时，才需要频繁刷新
      // 这里为了简单，我们一直刷新，或者你可以加判断逻辑
      fetchResources();
    }, 5000);

    // 组件卸载时清理定时器
    return () => clearInterval(intervalId);
  }, [userId]);


  // 3. 下载原文件
  const handleDownload = (resourceId: string) => {
    window.open(`/api/resources/${resourceId}/download`, '_blank');
  };

  // 👇 新增：下载分析结果
  const handleDownloadResult = (resourceId: string) => {
    // 传递 type=result 参数告诉后端我们要下载结果文件
    window.open(`/api/resources/${resourceId}/download?type=result`, '_blank');
  };

  // 👇 新增：触发分析
  const handleAnalyze = async (resourceId: string) => {
    setAnalyzingId(resourceId); // 设置按钮 loading 状态
    try {
      const res = await fetch("/api/resources/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resourceId }),
      });

      if (res.ok) {
        // 成功触发后，立即刷新一次列表，状态应该变为 processing
        await fetchResources();
      } else {
        alert("分析请求失败，请检查后端服务");
      }
    } catch (error) {
      console.error("Analyze request failed", error);
    } finally {
      setAnalyzingId(null);
    }
  };

  // 辅助函数：根据状态返回 Badge 的样式 variant
  const getStatusBadge = (status?: string) => {
    switch (status) {
      case 'completed': return <Badge variant="success">已完成</Badge>;
      case 'processing': return <Badge variant="processing">处理中...</Badge>;
      case 'failed': return <Badge variant="destructive">失败</Badge>;
      default: return <Badge variant="secondary">待处理</Badge>;
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-10 px-4">
      <h2 className="text-3xl md:text-4xl font-extrabold mb-6 flex items-center gap-2 text-blue-700 dark:text-blue-300">
        <span>📤</span> 资源上传与分析 <span>📋</span>
      </h2>

      {/* 上传区域 */}
      <form className="space-y-4 mb-8 bg-white p-6 rounded-lg shadow-sm border" onSubmit={handleUpload}>
        <div className="flex gap-4 items-center">
          <Input
            type="file"
            ref={fileInputRef}
            onChange={e => { setFile(e.target.files?.[0] ?? null); }}
            className="flex-1"
          />
          <Button type="submit" disabled={loading || !userId || !file}>
            {loading ? "上传中..." : "上传资源"}
          </Button>
        </div>
        <div className="flex justify-end">
           <Button type="button" variant="outline" onClick={fetchResources} disabled={!userId}>
            手动刷新列表
          </Button>
        </div>
      </form>

      {/* 列表区域 */}
      <div>
        <h3 className="text-xl font-semibold mb-4">我的资源列表</h3>
        {resources.length === 0 ? (
          <p className="text-gray-500 text-center py-10">暂无资源，请先上传文件</p>
        ) : (
          <ul className="space-y-4">
            {resources.map((r) => (
              <li key={r._id} className="bg-white border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <div className="font-bold text-lg text-gray-800">{r.originalname}</div>
                    <div className="text-sm text-gray-500">
                      上传时间: {new Date(r.uploadTime).toLocaleString()}
                    </div>
                  </div>
                  {/* 状态标签 */}
                  <div>
                    {getStatusBadge(r.status)}
                  </div>
                </div>

                <div className="flex gap-2 mt-4 justify-end border-t pt-3">
                  {/* 1. 分析按钮：只有 pending 或 failed 状态才显示 */}
                  {(r.status === 'pending' || r.status === 'failed' || !r.status) && (
                    <Button 
                      size="sm" 
                      onClick={() => handleAnalyze(r._id)}
                      disabled={analyzingId === r._id}
                    >
                      {analyzingId === r._id ? "请求中..." : "⚡ 开始分析"}
                    </Button>
                  )}

                  {/* 2. 原文件下载 */}
                  <Button size="sm" variant="outline" onClick={() => handleDownload(r._id)}>
                    📄 原文件
                  </Button>

                  {/* 3. 结果下载：只有 completed 状态才显示 */}
                  {r.status === 'completed' && (
                    <Button size="sm" className="bg-green-600 hover:bg-green-700 text-white" onClick={() => handleDownloadResult(r._id)}>
                      ⬇️ 下载 JSON 结果
                    </Button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}