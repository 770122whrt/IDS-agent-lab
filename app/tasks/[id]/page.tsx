"use client";

import { useSession } from "@/app/lib/auth-client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useRouter, useParams } from "next/navigation";
import { useEffect, useState, useRef } from "react";
import { Loader2, ArrowLeft, Download, Upload, CheckCircle } from "lucide-react";

interface TaskDetail {
  _id: string;
  userId: string;
  originalname: string;
  input_type: "text" | "ifc_file";
  inputText?: string;
  status: "pending" | "processing" | "pending_conversion" | "completed" | "failed";
  uploadTime: string;
  resultJson?: object;
  idsFilePath?: string;
  errorMessage?: string;
}

export default function TaskDetailPage() {
  const { data: session, isPending: sessionLoading } = useSession();
  const router = useRouter();
  const params = useParams();
  const taskId = params.id as string;

  const [task, setTask] = useState<TaskDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloadingIds, setDownloadingIds] = useState(false);
  const [ifcFile, setIfcFile] = useState<File | null>(null);
  const [uploadingIfc, setUploadingIfc] = useState(false);
  const ifcInputRef = useRef<HTMLInputElement>(null);

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

  // 下载 IDS 文件
  const downloadIdsFile = async () => {
    if (!task?._id) return;

    setDownloadingIds(true);
    try {
      const response = await fetch(`/api/tasks/${task._id}/download`);

      if (!response.ok) {
        const errorData = await response.json();
        alert(`下载失败: ${errorData.error || "未知错误"}`);
        return;
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      // 从 Content-Disposition 获取文件名，或使用默认名称
      const contentDisposition = response.headers.get("Content-Disposition");
      let filename = `${task.originalname.replace(/\.[^/.]+$/, "")}.ids`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename\*=UTF-8''(.+)/);
        if (filenameMatch) {
          filename = decodeURIComponent(filenameMatch[1]);
        }
      }

      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("下载 IDS 文件失败:", error);
      alert("下载失败，请重试");
    } finally {
      setDownloadingIds(false);
    }
  };

  // 处理 IFC 文件选择
  const handleIfcFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // 验证文件类型
      if (!file.name.toLowerCase().endsWith('.ifc')) {
        alert("请选择 .ifc 格式的文件");
        return;
      }
      setIfcFile(file);
      console.log("选择的 IFC 文件:", {
        name: file.name,
        size: file.size,
        type: file.type,
        lastModified: new Date(file.lastModified).toISOString()
      });
    }
  };

  // 上传 IFC 并审查（当前为 Mock 功能）
  const handleIfcUploadAndReview = async () => {
    if (!ifcFile) {
      alert("请先选择 IFC 文件");
      return;
    }

    setUploadingIfc(true);
    try {
      // 阶段三：当前仅为 Mock 功能，打印文件信息
      console.log("=====================================");
      console.log("🚀 IFC 上传审查功能（Mock）");
      console.log("=====================================");
      console.log("任务 ID:", task?._id);
      console.log("IDS 文件路径:", task?.idsFilePath);
      console.log("IFC 文件信息:");
      console.log("  - 文件名:", ifcFile.name);
      console.log("  - 文件大小:", (ifcFile.size / 1024).toFixed(2), "KB");
      console.log("  - 文件类型:", ifcFile.type);
      console.log("=====================================");
      console.log("⏳ 阶段四将实现真正的 IFC 审查逻辑...");
      console.log("=====================================");

      // 模拟 API 调用延迟
      await new Promise(resolve => setTimeout(resolve, 1000));

      alert(`IFC 文件 "${ifcFile.name}" 已选择。\n\n此功能将在阶段四实现完整的审查逻辑。\n当前仅为 Mock 功能，请在控制台查看详细信息。`);

    } catch (error) {
      console.error("IFC 上传审查失败:", error);
      alert("操作失败，请重试");
    } finally {
      setUploadingIfc(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!task) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500 text-lg mb-4">任务不存在</p>
            <Button onClick={() => router.push("/tasks")}>返回任务列表</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              任务详情
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              {task.originalname}
            </p>
          </div>
          <Button variant="outline" onClick={() => router.push("/tasks")}>
            <ArrowLeft className="w-4 h-4 mr-1" />
            返回列表
          </Button>
        </div>

        {/* Task Info */}
        <Card className="border-0 shadow-sm bg-white dark:bg-gray-900">
          <CardContent className="p-6">
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
        </CardContent>
      </Card>

        {/* Input Text */}
        {task.input_type === "text" && task.inputText && (
          <Card className="border-0 shadow-sm bg-white dark:bg-gray-900">
            <CardHeader>
              <CardTitle>输入文本</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                  {task.inputText}
                </pre>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Result JSON */}
        {task.resultJson && (
          <Card className="border-0 shadow-sm bg-white dark:bg-gray-900">
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>生成的 JSON 结果</CardTitle>
                <Button onClick={downloadJson} variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-1" />
                  下载 JSON
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 max-h-[400px] overflow-auto">
                <pre className="text-xs text-gray-700 dark:text-gray-300">
                  {JSON.stringify(task.resultJson, null, 2)}
                </pre>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Completed Task Actions - IDS Download & IFC Review */}
        {task.status === "completed" && task.idsFilePath && (
          <Card className="border-0 shadow-sm bg-green-50 dark:bg-green-900/20">
            <CardContent className="p-6">
              <h2 className="text-xl font-bold text-green-800 dark:text-green-300 mb-4">
                IDS 文件已生成
              </h2>
              <div className="flex flex-col sm:flex-row gap-3">
                <Button
                  onClick={downloadIdsFile}
                  disabled={downloadingIds}
                  className="flex items-center gap-2"
                >
                  {downloadingIds ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Download className="w-4 h-4" />
                  )}
                  {downloadingIds ? "下载中..." : "下载 .ids 文件"}
                </Button>

                <div className="flex items-center gap-2">
                  <input
                    type="file"
                    ref={ifcInputRef}
                    accept=".ifc"
                    onChange={handleIfcFileChange}
                    className="hidden"
                  />
                  <Button
                    variant="outline"
                    onClick={() => ifcInputRef.current?.click()}
                    className="flex items-center gap-2"
                  >
                    <Upload className="w-4 h-4" />
                    {ifcFile ? ifcFile.name : "选择 IFC 模型"}
                  </Button>
                  {ifcFile && (
                    <Button
                      onClick={handleIfcUploadAndReview}
                      disabled={uploadingIfc}
                      className="flex items-center gap-2"
                    >
                      {uploadingIfc ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <CheckCircle className="w-4 h-4" />
                      )}
                      {uploadingIfc ? "审查中..." : "开始审查"}
                    </Button>
                  )}
                </div>
              </div>

              {ifcFile && (
                <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-700">
                  <p className="text-sm text-blue-700 dark:text-blue-300">
                    已选择: <strong>{ifcFile.name}</strong> ({(ifcFile.size / 1024).toFixed(2)} KB)
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Processing Indicator */}
        {task.status === "processing" && (
          <Card className="border-0 shadow-sm bg-blue-50 dark:bg-blue-900/20">
            <CardContent className="p-6 text-center">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-3" />
              <p className="text-blue-700 dark:text-blue-300 font-medium">
                正在处理中，请稍候...
              </p>
            </CardContent>
          </Card>
        )}

        {/* Pending Conversion */}
        {task.status === "pending_conversion" && (
          <Card className="border-0 shadow-sm bg-yellow-50 dark:bg-yellow-900/20">
            <CardContent className="p-6 text-center">
              <p className="text-yellow-700 dark:text-yellow-300 font-medium">
                任务正在转换中，请稍候...
              </p>
            </CardContent>
          </Card>
        )}
    </div>
  );
}
