"use client";

import { useSession } from "@/app/lib/auth-client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface Task {
  _id: string;
  originalname: string;
  input_type: "text" | "ifc_file";
  inputText?: string;
  status: "pending" | "processing" | "pending_conversion" | "completed" | "failed";
  uploadTime: string;
  errorMessage?: string;
}

export default function TasksPage() {
  const { data: session, isPending: sessionLoading } = useSession();
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  const userId = session?.user?.id || session?.user?.email || "";

  useEffect(() => {
    if (!sessionLoading && !session?.user) {
      router.push("/sign-in");
    }
  }, [sessionLoading, session?.user, router]);

  const fetchTasks = async () => {
    if (!userId) return;

    try {
      const res = await fetch(`/api/resources?userId=${userId}`);
      const data = await res.json();
      setTasks(data.resources || []);
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!userId) return;

    fetchTasks();

    // 轮询：每5秒刷新一次
    const intervalId = setInterval(() => {
      fetchTasks();
    }, 5000);

    return () => clearInterval(intervalId);
  }, [userId]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge variant="success">已完成</Badge>;
      case "processing":
        return <Badge variant="processing">处理中</Badge>;
      case "pending_conversion":
        return <Badge variant="warning">待转换</Badge>;
      case "failed":
        return <Badge variant="destructive">失败</Badge>;
      default:
        return <Badge variant="secondary">待处理</Badge>;
    }
  };

  const getTypeLabel = (type: string) => {
    return type === "text" ? "📝 文本输入" : "📁 IFC文件";
  };

  if (sessionLoading || !session?.user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <svg
            className="animate-spin h-8 w-8 text-blue-600 mb-4 mx-auto"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
            ></path>
          </svg>
          <p className="text-lg text-gray-700">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-800 dark:text-gray-100">
              我的任务列表
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              查看所有文本和文件分析任务
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => router.push("/dashboard")}>
              返回主页
            </Button>
            <Button onClick={fetchTasks} disabled={loading}>
              {loading ? "刷新中..." : "手动刷新"}
            </Button>
          </div>
        </div>

        {/* Tasks List */}
        {loading ? (
          <div className="text-center py-10">
            <p className="text-gray-500">加载任务列表中...</p>
          </div>
        ) : tasks.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-10 text-center">
            <p className="text-gray-500 text-lg mb-4">暂无任务</p>
            <Button onClick={() => router.push("/dashboard")}>
              创建第一个任务
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {tasks.map((task) => (
              <div
                key={task._id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow p-6 cursor-pointer"
                onClick={() => router.push(`/tasks/${task._id}`)}
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100">
                        {task.originalname}
                      </h3>
                      {getStatusBadge(task.status)}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                      <span>{getTypeLabel(task.input_type)}</span>
                      <span>•</span>
                      <span>
                        创建时间: {new Date(task.uploadTime).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Preview for text input */}
                {task.input_type === "text" && task.inputText && (
                  <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600">
                    <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">
                      {task.inputText}
                    </p>
                  </div>
                )}

                {/* Error message */}
                {task.status === "failed" && task.errorMessage && (
                  <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 rounded border border-red-200 dark:border-red-800">
                    <p className="text-sm text-red-700 dark:text-red-300">
                      错误: {task.errorMessage}
                    </p>
                  </div>
                )}

                <div className="mt-4 flex justify-end gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`/tasks/${task._id}`);
                    }}
                  >
                    查看详情
                  </Button>
                  {task.status === "pending_conversion" && (
                    <Button
                      size="sm"
                      variant="default"
                      onClick={(e) => {
                        e.stopPropagation();
                        alert("阶段二功能即将开放");
                      }}
                    >
                      转换为IDS
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
