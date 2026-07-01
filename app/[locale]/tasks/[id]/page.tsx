"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowLeft, CheckCircle, Download, Loader2, Upload } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useSession } from "@/app/lib/auth-client";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useLanguage } from "@/i18n/context/language-context";

interface TaskDetail {
  _id: string;
  userId: string;
  originalname: string;
  input_type: "text" | "ifc_file";
  inputText?: string;
  status: "pending" | "processing" | "pending_conversion" | "completed" | "checking" | "checked" | "check_failed" | "failed";
  uploadTime: string;
  resultJson?: object;
  idsFilePath?: string;
  errorMessage?: string;
}

export default function TaskDetailPage() {
  const { data: session, isPending: sessionLoading } = useSession();
  const { t, locale } = useLanguage();
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
      router.push(`/${locale}/sign-in`);
    }
  }, [sessionLoading, session?.user, router, locale]);

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
    const intervalId = setInterval(() => {
      fetchTaskDetail();
    }, 5000);

    return () => clearInterval(intervalId);
  }, [taskId]);

  const getStatusBadge = (status: TaskDetail["status"]) => {
    switch (status) {
      case "completed":
      case "checked":
        return <Badge variant="success">{t(`status.${status}`)}</Badge>;
      case "processing":
      case "checking":
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

  const downloadJson = () => {
    if (!task?.resultJson) return;

    const jsonStr = JSON.stringify(task.resultJson, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${task.originalname}_result.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const downloadIdsFile = async () => {
    if (!task?._id) return;

    setDownloadingIds(true);
    try {
      const response = await fetch(`/api/tasks/${task._id}/download`);

      if (!response.ok) {
        const errorData = await response.json();
        alert(`${t("taskDetail.alert.downloadFailed")}: ${errorData.error || t("errors.unknown")}`);
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
      alert(t("taskDetail.alert.downloadFailed"));
    } finally {
      setDownloadingIds(false);
    }
  };

  const handleIfcFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith(".ifc")) {
        alert(t("taskDetail.alert.invalidIfc"));
        return;
      }
      setIfcFile(file);
    }
  };

  const handleIfcUploadAndReview = async () => {
    if (!ifcFile) {
      alert(t("taskDetail.alert.selectIfc"));
      return;
    }

    setUploadingIfc(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      alert(t("taskDetail.alert.mockReview", { name: ifcFile.name }));
    } catch (error) {
      console.error("IFC upload review failed:", error);
      alert(t("taskDetail.alert.downloadFailed"));
    } finally {
      setUploadingIfc(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!task) {
    return (
      <div className="mx-auto max-w-4xl">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="mb-4 text-lg text-gray-500">{t("taskDetail.notFound")}</p>
            <Button onClick={() => router.push(`/${locale}/tasks`)}>{t("taskDetail.backToList")}</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t("taskDetail.title")}</h1>
          <p className="mt-1 text-gray-500 dark:text-gray-400">{task.originalname}</p>
        </div>
        <Button variant="outline" onClick={() => router.push(`/${locale}/tasks`)}>
          <ArrowLeft className="mr-1 h-4 w-4" />
          {t("taskDetail.backToList")}
        </Button>
      </div>

      <Card className="border-0 bg-white shadow-sm dark:bg-gray-900">
        <CardContent className="p-6">
          <div className="mb-4 grid grid-cols-2 gap-4">
            <div>
              <p className="mb-1 text-sm text-gray-500">{t("taskDetail.status")}</p>
              <div>{getStatusBadge(task.status)}</div>
            </div>
            <div>
              <p className="mb-1 text-sm text-gray-500">{t("taskDetail.inputType")}</p>
              <p className="font-medium">
                {task.input_type === "text" ? t("taskDetail.type.text") : t("taskDetail.type.ifcFile")}
              </p>
            </div>
            <div>
              <p className="mb-1 text-sm text-gray-500">{t("taskDetail.createdAt")}</p>
              <p className="font-medium">
                {new Date(task.uploadTime).toLocaleString(locale === "zh" ? "zh-CN" : "en-US")}
              </p>
            </div>
            <div>
              <p className="mb-1 text-sm text-gray-500">{t("taskDetail.taskId")}</p>
              <p className="font-mono text-xs text-gray-600">{task._id}</p>
            </div>
          </div>

          {(task.status === "failed" || task.status === "check_failed") && task.errorMessage && (
            <div className="mt-4 rounded border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/20">
              <p className="mb-2 text-sm font-semibold text-red-700 dark:text-red-300">
                {t("taskDetail.errorMessage")}:
              </p>
              <p className="text-sm text-red-600 dark:text-red-400">{task.errorMessage}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {task.input_type === "text" && task.inputText && (
        <Card className="border-0 bg-white shadow-sm dark:bg-gray-900">
          <CardHeader>
            <CardTitle>{t("taskDetail.inputText")}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800">
              <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300">{task.inputText}</pre>
            </div>
          </CardContent>
        </Card>
      )}

      {task.resultJson && (
        <Card className="border-0 bg-white shadow-sm dark:bg-gray-900">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>{t("taskDetail.generatedJson")}</CardTitle>
              <Button onClick={downloadJson} variant="outline" size="sm">
                <Download className="mr-1 h-4 w-4" />
                {t("taskDetail.downloadJson")}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="max-h-[400px] overflow-auto rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800">
              <pre className="text-xs text-gray-700 dark:text-gray-300">
                {JSON.stringify(task.resultJson, null, 2)}
              </pre>
            </div>
          </CardContent>
        </Card>
      )}

      {task.status === "completed" && task.idsFilePath && (
        <Card className="border-0 bg-green-50 shadow-sm dark:bg-green-900/20">
          <CardContent className="p-6">
            <h2 className="mb-4 text-xl font-bold text-green-800 dark:text-green-300">
              {t("taskDetail.idsGenerated")}
            </h2>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Button onClick={downloadIdsFile} disabled={downloadingIds} className="flex items-center gap-2">
                {downloadingIds ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                {downloadingIds ? t("tasks.actions.downloading") : t("taskDetail.downloadIds")}
              </Button>

              <div className="flex items-center gap-2">
                <input
                  type="file"
                  ref={ifcInputRef}
                  accept=".ifc"
                  onChange={handleIfcFileChange}
                  className="hidden"
                />
                <Button variant="outline" onClick={() => ifcInputRef.current?.click()} className="flex items-center gap-2">
                  <Upload className="h-4 w-4" />
                  {ifcFile ? ifcFile.name : t("taskDetail.selectIfc")}
                </Button>
                {ifcFile && (
                  <Button onClick={handleIfcUploadAndReview} disabled={uploadingIfc} className="flex items-center gap-2">
                    {uploadingIfc ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle className="h-4 w-4" />}
                    {uploadingIfc ? t("taskDetail.reviewing") : t("taskDetail.startReview")}
                  </Button>
                )}
              </div>
            </div>

            {ifcFile && (
              <div className="mt-3 rounded-lg border border-blue-200 bg-blue-50 p-3 dark:border-blue-700 dark:bg-blue-900/30">
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  {t("taskDetail.selectedIfc", {
                    name: ifcFile.name,
                    size: (ifcFile.size / 1024).toFixed(2),
                  })}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {(task.status === "processing" || task.status === "checking") && (
        <Card className="border-0 bg-blue-50 shadow-sm dark:bg-blue-900/20">
          <CardContent className="p-6 text-center">
            <Loader2 className="mx-auto mb-3 h-8 w-8 animate-spin text-blue-600" />
            <p className="font-medium text-blue-700 dark:text-blue-300">
              {task.status === "checking" ? t("taskDetail.checking") : t("taskDetail.processing")}
            </p>
          </CardContent>
        </Card>
      )}

      {task.status === "pending_conversion" && (
        <Card className="border-0 bg-yellow-50 shadow-sm dark:bg-yellow-900/20">
          <CardContent className="p-6 text-center">
            <p className="font-medium text-yellow-700 dark:text-yellow-300">{t("taskDetail.pendingConversion")}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
