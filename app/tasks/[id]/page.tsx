"use client";

import { useSession } from "@/app/lib/auth-client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useRouter, useParams } from "next/navigation";
import { useEffect, useState } from "react";

interface TaskDetail {
  _id: string;
  userId: string;
  originalname: string;
  input_type: "text" | "ifc_file";
  inputText?: string;
  status: "pending" | "processing" | "pending_conversion" | "completed" | "failed";
  uploadTime: string;
  resultJson?: object;
  errorMessage?: string;
}

export default function TaskDetailPage() {
  const { data: session, isPending: sessionLoading } = useSession();
  const router = useRouter();
  const params = useParams();
  const taskId = params.id as string;

  const [task, setTask] = useState<TaskDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionLoading && !session?.user) {
      router.push("/sign-in");
    }
  }, [sessionLoading, session?.user, router]);

  const fetchTaskDetail = async () => {
    try {
      const res = await fetch(`/api/tasks/${taskId}`);
      if (res.ok) {
        const data = await res.json();
        setTask(data.task);
      } else {
        console.error("Failed to fetch task detail");
      }
    } catch (error) {
      console.error("Error fetching task detail:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!taskId) return;

    fetchTaskDetail();

    // 轮询：每5秒刷新一次
    const intervalId = setInterval(() => {
      fetchTaskDetail();
    }, 5000);

    return () => clearInterval(intervalId);
  }, [taskId]);

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

  const downloadJson = () => {
    if (!task?.resultJson) return;

    const jsonStr = JSON.stringify(task.resultJson, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${task.originalname}_result.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (sessionLoading || !session?.user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-lg">加载中...</p>
      </div>
    );
  }

  if (loading) {
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
          <p className="text-lg text-gray-700">加载任务详情...</p>
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-10 text-center">
            <p className="text-gray-500 text-lg mb-4">任务不存在</p>
            <Button onClick={() => router.push("/tasks")}>返回任务列表</Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-800 dark:text-gray-100 mb-2">
              任务详情
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              {task.originalname}
            </p>
          </div>
          <Button variant="outline" onClick={() => router.push("/tasks")}>
            返回列表
          </Button>
        </div>

        {/* Task Info */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-500 mb-1">任务状态</p>
              <div>{getStatusBadge(task.status)}</div>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">输入类型</p>
              <p className="font-medium">
                {task.input_type === "text" ? "📝 文本输入" : "📁 IFC文件"}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">创建时间</p>
              <p className="font-medium">
                {new Date(task.uploadTime).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">任务ID</p>
              <p className="font-mono text-xs text-gray-600">{task._id}</p>
            </div>
          </div>

          {/* Error Message */}
          {task.status === "failed" && task.errorMessage && (
            <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 rounded border border-red-200 dark:border-red-800">
              <p className="text-sm font-semibold text-red-700 dark:text-red-300 mb-2">
                错误信息:
              </p>
              <p className="text-sm text-red-600 dark:text-red-400">
                {task.errorMessage}
              </p>
            </div>
          )}
        </div>

        {/* Input Text */}
        {task.input_type === "text" && task.inputText && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold mb-4 text-gray-800 dark:text-gray-100">
              输入文本
            </h2>
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600">
              <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                {task.inputText}
              </pre>
            </div>
          </div>
        )}

        {/* Result JSON */}
        {task.resultJson && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">
                生成的 JSON 结果
              </h2>
              <Button onClick={downloadJson}>下载 JSON</Button>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600 max-h-[600px] overflow-auto">
              <pre className="text-xs text-gray-700 dark:text-gray-300">
                {JSON.stringify(task.resultJson, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* Processing Indicator */}
        {task.status === "processing" && (
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg shadow p-6 text-center">
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
            <p className="text-blue-700 dark:text-blue-300 font-medium">
              正在处理中，请稍候...
            </p>
          </div>
        )}

        {/* Pending Conversion */}
        {task.status === "pending_conversion" && (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg shadow p-6 text-center mt-6">
            <p className="text-yellow-700 dark:text-yellow-300 font-medium mb-4">
              JSON 已生成，等待转换为 IDS 文件
            </p>
            <Button
              onClick={() => alert("阶段二功能即将开放")}
              variant="default"
            >
              转换为 IDS 文件
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
