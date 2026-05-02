"use client";

import { useSession } from "@/app/lib/auth-client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { useRouter } from "next/navigation";
import { useEffect, useState, useRef } from "react";
import { Loader2, RefreshCw, Plus } from "lucide-react";

interface ReportSummary {
  total_specs: number;
  passed_specs: number;
  failed_specs: number;
  total_failed_entities: number;
}

interface Task {
  _id: string;
  originalname: string;
  input_type: "text" | "ifc_file";
  inputText?: string;
  status: "pending" | "processing" | "pending_conversion" | "completed" | "checking" | "checked" | "check_failed" | "failed";
  uploadTime: string;
  idsFileId?: string;
  idsFileName?: string;
  ifcFileId?: string;
  ifcFileName?: string;
  reportSummary?: ReportSummary;
  errorMessage?: string;
  resultJson?: object; // 用于 XSD 验证失败时显示 JSON
}

export default function TasksPage() {
  const { data: session, isPending: sessionLoading } = useSession();
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloadingIds, setDownloadingIds] = useState<string | null>(null);
  const [downloadingJson, setDownloadingJson] = useState<string | null>(null);
  const [retrying, setRetrying] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [checking, setChecking] = useState<string | null>(null);
  const [ifcFiles, setIfcFiles] = useState<Record<string, File>>({});
  const [expandedJsonTasks, setExpandedJsonTasks] = useState<Set<string>>(new Set()); // 展开JSON的任务ID集合
  const ifcInputRefs = useRef<Record<string, HTMLInputElement | null>>({});

  useEffect(() => {
    if (!sessionLoading && !session?.user) {
      router.push("/sign-in");
    }
  }, [sessionLoading, session?.user, router]);

  const fetchTasks = async () => {
    if (!session?.user?.id) return;

    try {
      const res = await fetch("/api/resources", {  // 不再传递 userId
        credentials: "include", // 确保发送 cookie
      });
      const data = await res.json();
      setTasks(data.resources || []);
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!session?.user?.id) return;

    fetchTasks();

    // 轮询：每5秒刷新一次
    const intervalId = setInterval(() => {
      fetchTasks();
    }, 5000);

    return () => clearInterval(intervalId);
  }, [session?.user?.id]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge variant="success">已完成</Badge>;
      case "checking":
        return <Badge variant="processing">审查中</Badge>;
      case "checked":
        return <Badge variant="success">已审查</Badge>;
      case "check_failed":
        return <Badge variant="destructive">审查失败</Badge>;
      case "processing":
        return <Badge variant="processing">处理中</Badge>;
      case "pending_conversion":
        return <Badge variant="warning">转换中</Badge>;
      case "failed":
        return <Badge variant="destructive">失败</Badge>;
      default:
        return <Badge variant="secondary">待处理</Badge>;
    }
  };

  const getTypeLabel = (type: string) => {
    return type === "text" ? "文本输入" : "IFC文件";
  };

  // 检查是否是 XSD 验证失败
  const isXsdValidationError = (errorMsg: string): boolean => {
    return errorMsg.includes("XSD Validation") || errorMsg.includes("XSD验证");
  };

  // 切换 JSON 展开/折叠
  const toggleJsonExpand = (taskId: string) => {
    setExpandedJsonTasks((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(taskId)) {
        newSet.delete(taskId);
      } else {
        newSet.add(taskId);
      }
      return newSet;
    });
  };

  // 下载 JSON
  const downloadJson = async (task: Task) => {
    setDownloadingJson(task._id);
    try {
      const res = await fetch(`/api/tasks/${task._id}`);
      if (res.ok) {
        const data = await res.json();
        const resultJson = data.task?.resultJson;
        if (resultJson) {
          const jsonStr = JSON.stringify(resultJson, null, 2);
          const blob = new Blob([jsonStr], { type: "application/json" });
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `${task.originalname.replace(/\.[^/.]+$/, "")}_result.json`;
          a.click();
          URL.revokeObjectURL(url);
        } else {
          alert("JSON 结果不存在");
        }
      } else {
        alert("获取 JSON 失败");
      }
    } catch (error) {
      console.error("Download JSON error:", error);
      alert("下载失败");
    } finally {
      setDownloadingJson(null);
    }
  };

  // 下载 IDS 文件
  const downloadIdsFile = async (task: Task) => {
    setDownloadingIds(task._id);
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
      setDownloadingIds(null);
    }
  };

  // 重试任务
  const retryTask = async (task: Task) => {
    const isCheckFailed = task.status === "check_failed";
    const confirmMessage = isCheckFailed
      ? `确定要重置任务 "${task.originalname}" 吗？\n\n重置后任务将回到"已完成"状态，您可以重新上传 IFC 文件进行审查。`
      : `确定要重试任务 "${task.originalname}" 吗？`;

    if (!confirm(confirmMessage)) {
      return;
    }

    setRetrying(task._id);
    try {
      const response = await fetch(`/api/tasks/${task._id}/retry`, {
        method: "POST",
      });

      if (response.ok) {
        const result = await response.json();
        if (result.retryType === "check_retry") {
          alert("任务已重置为完成状态，请重新上传 IFC 文件进行审查。");
        } else {
          alert("任务已重新提交，请稍候...");
        }
        fetchTasks();
      } else {
        const error = await response.json();
        alert(`重试失败: ${error.error || "未知错误"}`);
      }
    } catch (error) {
      console.error("Retry error:", error);
      alert("重试失败，请检查网络连接");
    } finally {
      setRetrying(null);
    }
  };

  // 删除任务
  const deleteTask = async (task: Task) => {
    if (!confirm(`确定要删除任务 "${task.originalname}" 吗？此操作不可撤销！`)) {
      return;
    }

    setDeleting(task._id);
    try {
      const response = await fetch(`/api/tasks/${task._id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        alert("任务已删除");
        fetchTasks();
      } else {
        const error = await response.json();
        alert(`删除失败: ${error.error || "未知错误"}`);
      }
    } catch (error) {
      console.error("Delete error:", error);
      alert("删除失败，请检查网络连接");
    } finally {
      setDeleting(null);
    }
  };

  // 处理 IFC 文件选择
  const handleIfcFileChange = (taskId: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith('.ifc')) {
        alert("请选择 .ifc 格式的文件");
        return;
      }
      setIfcFiles(prev => ({ ...prev, [taskId]: file }));
    }
  };

  // IFC 审查 - 真实上传逻辑
  const handleIfcReview = async (task: Task) => {
    const file = ifcFiles[task._id];
    if (!file) {
      alert("请先选择 IFC 文件");
      return;
    }

    if (!confirm(`确定要上传 "${file.name}" 进行 IDS 合规性审查吗？\n审查可能需要几秒到几十秒的时间。`)) {
      return;
    }

    setChecking(task._id);
    try {
      // 构建 FormData
      const formData = new FormData();
      formData.append("ifc", file);

      const response = await fetch(`/api/tasks/${task._id}/check`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        alert(`审查失败: ${error.error || "未知错误"}`);
        return;
      }

      const result = await response.json();

      if (result.success) {
        const summary = result.summary;
        if (summary.failed_specs > 0) {
          alert(`审查完成！\n\n总规格: ${summary.total_specs}\n通过: ${summary.passed_specs}\n失败: ${summary.failed_specs}\n错误构件: ${summary.total_failed_entities}`);
        } else {
          alert(`审查通过！\n\n所有 ${summary.total_specs} 个规格均符合要求。`);
        }
        // 刷新任务列表
        fetchTasks();
        // 清除文件选择
        setIfcFiles(prev => {
          const newState = { ...prev };
          delete newState[task._id];
          return newState;
        });
      } else {
        alert(`审查失败: ${result.message || "未知错误"}`);
      }
    } catch (error) {
      console.error("IFC 审查错误:", error);
      alert("审查失败，请检查网络连接");
    } finally {
      setChecking(null);
    }
  };

  // 查看报告
  const viewReport = async (task: Task) => {
    // 获取任务详情并跳转到报告页
    router.push(`/tasks/${task._id}?tab=report`);
  };

  if (sessionLoading || !session?.user) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              任务列表
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              管理您的 IDS 生成和审查任务
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => router.push("/dashboard")}>
              <Plus className="w-4 h-4 mr-1" />
              新建任务
            </Button>
            <Button onClick={fetchTasks} disabled={loading} variant="outline">
              <RefreshCw className={`w-4 h-4 mr-1 ${loading ? "animate-spin" : ""}`} />
              刷新
            </Button>
          </div>
        </div>

        {/* Tasks List */}
        {loading ? (
          <div className="text-center py-10">
            <Loader2 className="w-6 h-6 animate-spin text-blue-600 mx-auto mb-2" />
            <p className="text-gray-500">加载任务列表中...</p>
          </div>
        ) : tasks.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-gray-500 text-lg mb-4">暂无任务</p>
              <Button onClick={() => router.push("/dashboard")}>
                创建第一个任务
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {tasks.map((task) => (
              <Card
                key={task._id}
                className="border-0 shadow-sm hover:shadow-md transition-shadow bg-white dark:bg-gray-900"
              >
                <CardContent className="p-5">
                {/* Task Header */}
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                        {task.originalname}
                      </h3>
                      {getStatusBadge(task.status)}
                    </div>
                    <div className="flex items-center gap-3 text-sm text-gray-500">
                      <span>{getTypeLabel(task.input_type)}</span>
                      <span>•</span>
                      <span>{new Date(task.uploadTime).toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                {/* Preview for text input */}
                {task.input_type === "text" && task.inputText && (
                  <div className="mb-3 p-3 bg-gray-50 dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600">
                    <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-2">
                      {task.inputText}
                    </p>
                  </div>
                )}

                {/* Report Summary for checked tasks */}
                {task.status === "checked" && task.reportSummary && (
                  <div className="mb-3 p-3 bg-green-50 dark:bg-green-900/20 rounded border border-green-200 dark:border-green-800">
                    <div className="flex items-center gap-4 text-sm">
                      <span className="font-medium text-green-700 dark:text-green-300">
                        审查结果:
                      </span>
                      <span className="text-gray-600 dark:text-gray-400">
                        总规格: {task.reportSummary.total_specs}
                      </span>
                      <span className="text-green-600 dark:text-green-400">
                        通过: {task.reportSummary.passed_specs}
                      </span>
                      {task.reportSummary.failed_specs > 0 && (
                        <span className="text-red-600 dark:text-red-400">
                          失败: {task.reportSummary.failed_specs} ({task.reportSummary.total_failed_entities} 个构件)
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Error message */}
                {(task.status === "failed" || task.status === "check_failed") && task.errorMessage && (
                  <div className="mb-3">
                    <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded border border-red-200 dark:border-red-800">
                      <p className="text-sm text-red-600 dark:text-red-400">
                        错误: {task.errorMessage.length > 200 ? task.errorMessage.slice(0, 200) + "..." : task.errorMessage}
                      </p>
                    </div>
                    {/* XSD 验证失败时显示 JSON 查看按钮 */}
                    {task.resultJson && isXsdValidationError(task.errorMessage) && (
                      <div className="mt-2">
                        <button
                          onClick={() => toggleJsonExpand(task._id)}
                          className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 flex items-center gap-1"
                        >
                          <svg
                            className={`w-4 h-4 transition-transform ${expandedJsonTasks.has(task._id) ? "rotate-90" : ""}`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                          {expandedJsonTasks.has(task._id) ? "隐藏 JSON 数据" : "查看生成的 JSON (用于调试)"}
                        </button>
                        {expandedJsonTasks.has(task._id) && (
                          <div className="mt-2 p-3 bg-gray-900 rounded border border-gray-700 overflow-auto max-h-64">
                            <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap">
                              {JSON.stringify(task.resultJson, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-2 items-center pt-2 border-t border-gray-100 dark:border-gray-700">
                  {/* Completed: Download JSON, Download IDS, Upload IFC, View Report */}
                  {task.status === "completed" && (task as any).idsFileId && (
                    <>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => downloadJson(task)}
                        disabled={downloadingJson === task._id}
                      >
                        {downloadingJson === task._id ? "下载中..." : "下载 JSON"}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => downloadIdsFile(task)}
                        disabled={downloadingIds === task._id}
                      >
                        {downloadingIds === task._id ? "下载中..." : "下载 .ids"}
                      </Button>
                      <div className="flex items-center gap-1">
                        <input
                          type="file"
                          ref={el => { ifcInputRefs.current[task._id] = el; }}
                          accept=".ifc"
                          onChange={(e) => handleIfcFileChange(task._id, e)}
                          className="hidden"
                        />
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => ifcInputRefs.current[task._id]?.click()}
                          disabled={checking === task._id}
                        >
                          {ifcFiles[task._id] ? `已选: ${ifcFiles[task._id].name.slice(0, 10)}...` : "选择 IFC"}
                        </Button>
                        {ifcFiles[task._id] && (
                          <Button
                            size="sm"
                            variant="default"
                            onClick={() => handleIfcReview(task)}
                            disabled={checking === task._id}
                          >
                            {checking === task._id ? (
                              <span className="flex items-center gap-1">
                                <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24">
                                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                                </svg>
                                审查中...
                              </span>
                            ) : "审查"}
                          </Button>
                        )}
                      </div>
                    </>
                  )}

                  {/* Checked: View Details, Download IDS, View Report */}
                  {task.status === "checked" && (
                    <>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => router.push(`/tasks/${task._id}`)}
                      >
                        查看任务详情
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => downloadIdsFile(task)}
                        disabled={downloadingIds === task._id}
                      >
                        {downloadingIds === task._id ? "下载中..." : "下载 .ids"}
                      </Button>
                      <Button
                        size="sm"
                        variant="default"
                        onClick={() => router.push(`/tasks/${task._id}/report`)}
                      >
                        查看审查报告
                      </Button>
                    </>
                  )}

                  {/* Checking status */}
                  {task.status === "checking" && (
                    <div className="flex items-center gap-2 text-blue-600">
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                      </svg>
                      <span className="text-sm">正在审查 IFC 模型...</span>
                    </div>
                  )}

                  {/* Processing/Pending: View Detail */}
                  {(task.status === "processing" || task.status === "pending" || task.status === "pending_conversion") && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => router.push(`/tasks/${task._id}`)}
                    >
                      查看详情
                    </Button>
                  )}

                  {/* Failed or Check Failed: Retry + Download JSON (if XSD error) */}
                  {(task.status === "failed" || task.status === "check_failed") && (
                    <>
                      <Button
                        size="sm"
                        variant="default"
                        onClick={() => retryTask(task)}
                        disabled={retrying === task._id}
                      >
                        {retrying === task._id ? "重试中..." : "重试"}
                      </Button>
                      {task.resultJson && task.errorMessage && isXsdValidationError(task.errorMessage) && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => downloadJson(task)}
                          disabled={downloadingJson === task._id}
                        >
                          {downloadingJson === task._id ? "下载中..." : "下载 JSON"}
                        </Button>
                      )}
                    </>
                  )}

                  {/* Delete Button - Always visible but on the right */}
                  <div className="flex-1"></div>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                    onClick={() => deleteTask(task)}
                    disabled={deleting === task._id || checking === task._id}
                  >
                    {deleting === task._id ? "删除中..." : "删除"}
                  </Button>
                </div>
              </CardContent>
            </Card>
            ))}
          </div>
        )}
    </div>
  );
}