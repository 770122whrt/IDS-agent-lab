"use client";

import { useEffect, useRef, useState } from "react";
import { Loader2, Plus, RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import { useSession } from "@/app/lib/auth-client";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useLanguage } from "@/i18n/context/language-context";
import { cn } from "@/lib/utils";

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
  resultJson?: object;
}

export default function TasksPage() {
  const { data: session, isPending: sessionLoading } = useSession();
  const { t, locale } = useLanguage();
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloadingIds, setDownloadingIds] = useState<string | null>(null);
  const [downloadingJson, setDownloadingJson] = useState<string | null>(null);
  const [retrying, setRetrying] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [checking, setChecking] = useState<string | null>(null);
  const [ifcFiles, setIfcFiles] = useState<Record<string, File>>({});
  const [expandedJsonTasks, setExpandedJsonTasks] = useState<Set<string>>(new Set());
  const ifcInputRefs = useRef<Record<string, HTMLInputElement | null>>({});

  useEffect(() => {
    if (!sessionLoading && !session?.user) {
      router.push(`/${locale}/sign-in`);
    }
  }, [sessionLoading, session?.user, router, locale]);

  const fetchTasks = async () => {
    if (!session?.user?.id) return;

    try {
      const res = await fetch("/api/resources", { credentials: "include" });
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
    const intervalId = setInterval(() => {
      fetchTasks();
    }, 5000);

    return () => clearInterval(intervalId);
  }, [session?.user?.id]);

  const getStatusBadge = (status: Task["status"]) => {
    switch (status) {
      case "completed":
      case "checked":
        return <Badge variant="success">{t(`status.${status}`)}</Badge>;
      case "checking":
      case "processing":
        return <Badge variant="processing">{t(`status.${status}`)}</Badge>;
      case "pending_conversion":
        return <Badge variant="warning">{t("status.pending_conversion")}</Badge>;
      case "failed":
      case "check_failed":
        return <Badge variant="destructive">{t(`status.${status}`)}</Badge>;
      default:
        return <Badge variant="secondary">{t("status.pending")}</Badge>;
    }
  };

  const getTypeLabel = (type: string) => {
    return type === "text" ? t("tasks.type.text") : t("tasks.type.ifcFile");
  };

  const isXsdValidationError = (errorMsg: string): boolean => {
    return errorMsg.includes("XSD Validation") || errorMsg.includes("XSD验证");
  };

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
          const anchor = document.createElement("a");
          anchor.href = url;
          anchor.download = `${task.originalname.replace(/\.[^/.]+$/, "")}_result.json`;
          anchor.click();
          URL.revokeObjectURL(url);
        } else {
          alert(t("tasks.alert.jsonMissing"));
        }
      } else {
        alert(t("tasks.alert.jsonFetchFailed"));
      }
    } catch (error) {
      console.error("Download JSON error:", error);
      alert(t("tasks.alert.downloadFailed"));
    } finally {
      setDownloadingJson(null);
    }
  };

  const downloadIdsFile = async (task: Task) => {
    setDownloadingIds(task._id);
    try {
      const response = await fetch(`/api/tasks/${task._id}/download`);

      if (!response.ok) {
        const errorData = await response.json();
        alert(
          t("tasks.alert.checkFailed", {
            message: errorData.error || t("tasks.alert.unknownError"),
          }),
        );
        return;
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;

      const contentDisposition = response.headers.get("Content-Disposition");
      let filename = `${task.originalname.replace(/\.[^/.]+$/, "")}.ids`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename\*=UTF-8''(.+)/);
        if (filenameMatch) {
          filename = decodeURIComponent(filenameMatch[1]);
        }
      }

      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Download IDS file failed:", error);
      alert(t("tasks.alert.downloadFailed"));
    } finally {
      setDownloadingIds(null);
    }
  };

  const retryTask = async (task: Task) => {
    const isCheckFailed = task.status === "check_failed";
    const confirmMessage = isCheckFailed
      ? t("tasks.confirm.resetCheck", { name: task.originalname })
      : t("tasks.confirm.retry", { name: task.originalname });

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
        alert(result.retryType === "check_retry" ? t("tasks.alert.checkReset") : t("tasks.alert.retrySubmitted"));
        fetchTasks();
      } else {
        const error = await response.json();
        alert(
          t("tasks.alert.checkFailed", {
            message: error.error || t("tasks.alert.unknownError"),
          }),
        );
      }
    } catch (error) {
      console.error("Retry error:", error);
      alert(t("tasks.alert.networkFailed"));
    } finally {
      setRetrying(null);
    }
  };

  const deleteTask = async (task: Task) => {
    if (!confirm(t("tasks.confirm.delete", { name: task.originalname }))) {
      return;
    }

    setDeleting(task._id);
    try {
      const response = await fetch(`/api/tasks/${task._id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        alert(t("tasks.alert.deleteSuccess"));
        fetchTasks();
      } else {
        const error = await response.json();
        alert(
          t("tasks.alert.checkFailed", {
            message: error.error || t("tasks.alert.unknownError"),
          }),
        );
      }
    } catch (error) {
      console.error("Delete error:", error);
      alert(t("tasks.alert.networkFailed"));
    } finally {
      setDeleting(null);
    }
  };

  const handleIfcFileChange = (taskId: string, event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith(".ifc")) {
        alert(t("tasks.alert.invalidIfc"));
        return;
      }
      setIfcFiles((prev) => ({ ...prev, [taskId]: file }));
    }
  };

  const handleIfcReview = async (task: Task) => {
    const file = ifcFiles[task._id];
    if (!file) {
      alert(t("tasks.alert.selectIfc"));
      return;
    }

    setChecking(task._id);
    try {
      const formData = new FormData();
      formData.append("ifc", file);

      const response = await fetch(`/api/tasks/${task._id}/check`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        alert(
          t("tasks.alert.checkFailed", {
            message: error.error || t("tasks.alert.unknownError"),
          }),
        );
        return;
      }

      const result = await response.json();

      if (result.success) {
        const summary = result.summary;
        if (summary.failed_specs > 0) {
          alert(
            t("tasks.alert.checkCompleted", {
              total: summary.total_specs,
              passed: summary.passed_specs,
              failed: summary.failed_specs,
              entities: summary.total_failed_entities,
            }),
          );
        } else {
          alert(t("tasks.alert.checkPassed", { total: summary.total_specs }));
        }
        fetchTasks();
        setIfcFiles((prev) => {
          const newState = { ...prev };
          delete newState[task._id];
          return newState;
        });
      } else {
        alert(
          t("tasks.alert.checkFailed", {
            message: result.message || t("tasks.alert.unknownError"),
          }),
        );
      }
    } catch (error) {
      console.error("IFC check error:", error);
      alert(t("tasks.alert.networkFailed"));
    } finally {
      setChecking(null);
    }
  };

  if (sessionLoading || !session?.user) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t("tasks.title")}</h1>
          <p className="mt-1 text-gray-500 dark:text-gray-400">{t("tasks.description")}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => router.push(`/${locale}/dashboard`)}>
            <Plus className="mr-1 h-4 w-4" />
            {t("tasks.newTask")}
          </Button>
          <Button onClick={fetchTasks} disabled={loading} variant="outline">
            <RefreshCw className={`mr-1 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            {t("tasks.refresh")}
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="py-10 text-center">
          <Loader2 className="mx-auto mb-2 h-6 w-6 animate-spin text-blue-600" />
          <p className="text-gray-500">{t("tasks.loading")}</p>
        </div>
      ) : tasks.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="mb-4 text-lg text-gray-500">{t("tasks.empty.title")}</p>
            <Button onClick={() => router.push(`/${locale}/dashboard`)}>
              {t("tasks.empty.createFirst")}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {tasks.map((task) => (
            <Card key={task._id} className="border-0 bg-white shadow-sm transition-shadow hover:shadow-md dark:bg-gray-900">
              <CardContent className="p-5">
                <div className="mb-3 flex items-start justify-between">
                  <div className="flex-1">
                    <div className="mb-1 flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                        {task.originalname}
                      </h3>
                      {getStatusBadge(task.status)}
                    </div>
                    <div className="flex items-center gap-3 text-sm text-gray-500">
                      <span>{getTypeLabel(task.input_type)}</span>
                      <span>-</span>
                      <span>{new Date(task.uploadTime).toLocaleString(locale === "zh" ? "zh-CN" : "en-US")}</span>
                    </div>
                  </div>
                </div>

                {task.input_type === "text" && task.inputText && (
                  <div className="mb-3 rounded border border-gray-200 bg-gray-50 p-3 dark:border-gray-600 dark:bg-gray-700">
                    <p className="line-clamp-2 text-sm text-gray-600 dark:text-gray-300">{task.inputText}</p>
                  </div>
                )}

                {task.status === "checked" && task.reportSummary && (
                  <div className="mb-3 rounded border border-green-200 bg-green-50 p-3 dark:border-green-800 dark:bg-green-900/20">
                    <div className="flex items-center gap-4 text-sm">
                      <span className="font-medium text-green-700 dark:text-green-300">
                        {t("tasks.reportSummary.title")}:
                      </span>
                      <span className="text-gray-600 dark:text-gray-400">
                        {t("tasks.reportSummary.totalSpecs")} {task.reportSummary.total_specs}
                      </span>
                      <span className="text-green-600 dark:text-green-400">
                        {t("tasks.reportSummary.passed")}: {task.reportSummary.passed_specs}
                      </span>
                      {task.reportSummary.failed_specs > 0 && (
                        <span className="text-red-600 dark:text-red-400">
                          {t("tasks.reportSummary.failed")}: {task.reportSummary.failed_specs} (
                          {t("tasks.reportSummary.failedEntities", {
                            count: task.reportSummary.total_failed_entities,
                          })}
                          )
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {(task.status === "failed" || task.status === "check_failed") && task.errorMessage && (
                  <div className="mb-3">
                    <div className="rounded border border-red-200 bg-red-50 p-3 dark:border-red-800 dark:bg-red-900/20">
                      <p className="text-sm text-red-600 dark:text-red-400">
                        {t("tasks.errorPrefix")}: {task.errorMessage.length > 200 ? `${task.errorMessage.slice(0, 200)}...` : task.errorMessage}
                      </p>
                    </div>
                    {task.resultJson && isXsdValidationError(task.errorMessage) && (
                      <div className="mt-2">
                        <button
                          type="button"
                          onClick={() => toggleJsonExpand(task._id)}
                          className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                        >
                          <svg
                            className={`h-4 w-4 transition-transform ${expandedJsonTasks.has(task._id) ? "rotate-90" : ""}`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                          {expandedJsonTasks.has(task._id) ? t("tasks.xsd.hideJson") : t("tasks.xsd.showJson")}
                        </button>
                        {expandedJsonTasks.has(task._id) && (
                          <div className="mt-2 max-h-64 overflow-auto rounded border border-gray-700 bg-gray-900 p-3">
                            <pre className="whitespace-pre-wrap font-mono text-xs text-green-400">
                              {JSON.stringify(task.resultJson, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                <div className="flex flex-wrap items-center gap-2 border-t border-gray-100 pt-2 dark:border-gray-700">
                  {task.status === "completed" && task.idsFileId && (
                    <>
                      <Button size="sm" variant="outline" onClick={() => downloadJson(task)} disabled={downloadingJson === task._id}>
                        {downloadingJson === task._id ? t("tasks.actions.downloading") : t("tasks.actions.downloadJson")}
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => downloadIdsFile(task)} disabled={downloadingIds === task._id}>
                        {downloadingIds === task._id ? t("tasks.actions.downloading") : t("tasks.actions.downloadIds")}
                      </Button>
                      <div className="flex items-center gap-1">
                        <input
                          type="file"
                          ref={(element) => {
                            ifcInputRefs.current[task._id] = element;
                          }}
                          accept=".ifc"
                          onChange={(event) => handleIfcFileChange(task._id, event)}
                          className="hidden"
                        />
                        <Button size="sm" variant="outline" onClick={() => ifcInputRefs.current[task._id]?.click()} disabled={checking === task._id}>
                          {ifcFiles[task._id]
                            ? t("tasks.actions.selectedIfc", { name: `${ifcFiles[task._id].name.slice(0, 10)}...` })
                            : t("tasks.actions.selectIfc")}
                        </Button>
                        {ifcFiles[task._id] && (
                          <Button size="sm" variant="default" onClick={() => handleIfcReview(task)} disabled={checking === task._id}>
                            {checking === task._id ? (
                              <span className="flex items-center gap-1">
                                <Loader2 className="h-3 w-3 animate-spin" />
                                {t("tasks.actions.reviewing")}
                              </span>
                            ) : (
                              t("tasks.actions.review")
                            )}
                          </Button>
                        )}
                      </div>
                    </>
                  )}

                  {task.status === "checked" && (
                    <>
                      <Button size="sm" variant="outline" onClick={() => router.push(`/${locale}/tasks/${task._id}`)}>
                        {t("tasks.actions.viewTask")}
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => downloadIdsFile(task)} disabled={downloadingIds === task._id}>
                        {downloadingIds === task._id ? t("tasks.actions.downloading") : t("tasks.actions.downloadIds")}
                      </Button>
                      <Button size="sm" variant="default" onClick={() => router.push(`/${locale}/tasks/${task._id}/report`)}>
                        {t("tasks.actions.viewReport")}
                      </Button>
                    </>
                  )}

                  {task.status === "checking" && (
                    <div className="flex items-center gap-2 text-blue-600">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span className="text-sm">{t("tasks.checkingStatus")}</span>
                    </div>
                  )}

                  {(task.status === "processing" || task.status === "pending" || task.status === "pending_conversion") && (
                    <Button size="sm" variant="outline" onClick={() => router.push(`/${locale}/tasks/${task._id}`)}>
                      {t("tasks.actions.viewTask")}
                    </Button>
                  )}

                  {(task.status === "failed" || task.status === "check_failed") && (
                    <>
                      <Button size="sm" variant="default" onClick={() => retryTask(task)} disabled={retrying === task._id}>
                        {retrying === task._id ? t("tasks.actions.reviewing") : t("tasks.actions.retry")}
                      </Button>
                      {task.resultJson && task.errorMessage && isXsdValidationError(task.errorMessage) && (
                        <Button size="sm" variant="outline" onClick={() => downloadJson(task)} disabled={downloadingJson === task._id}>
                          {downloadingJson === task._id ? t("tasks.actions.downloading") : t("tasks.actions.downloadJson")}
                        </Button>
                      )}
                    </>
                  )}

                  <div className="flex-1" />
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-red-500 hover:bg-red-50 hover:text-red-700 dark:hover:bg-red-900/20"
                    onClick={() => deleteTask(task)}
                    disabled={deleting === task._id || checking === task._id}
                  >
                    {deleting === task._id ? t("tasks.actions.deleting") : t("tasks.actions.delete")}
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
