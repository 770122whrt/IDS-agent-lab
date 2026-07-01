"use client";

import { useEffect, useRef, useState } from "react";
import { useSession } from "@/app/lib/auth-client";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useLanguage } from "@/i18n/context/language-context";

interface Resource {
  _id: string;
  originalname: string;
  uploadTime: string;
  status?: "pending" | "processing" | "completed" | "failed";
}

export default function IdsUse() {
  const { data: session } = useSession();
  const { t, locale } = useLanguage();
  const [file, setFile] = useState<File | null>(null);
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(false);
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchResources = async () => {
    if (!session?.user?.id) return;
    try {
      const res = await fetch("/api/resources", {
        credentials: "include",
      });
      const data = await res.json();
      setResources(data.resources || []);
    } catch (error) {
      console.error("Fetch resources failed", error);
    }
  };

  const handleUpload = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!session?.user?.id || !file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      await fetch("/api/resources", {
        method: "POST",
        body: formData,
        credentials: "include",
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

  useEffect(() => {
    if (!session?.user?.id) return;

    fetchResources();
    const intervalId = setInterval(() => {
      fetchResources();
    }, 5000);

    return () => clearInterval(intervalId);
  }, [session?.user?.id]);

  const handleDownload = (resourceId: string) => {
    window.open(`/api/resources/${resourceId}/download`, "_blank");
  };

  const handleDownloadResult = (resourceId: string) => {
    window.open(`/api/resources/${resourceId}/download?type=result`, "_blank");
  };

  const handleAnalyze = async (resourceId: string) => {
    setAnalyzingId(resourceId);
    try {
      const res = await fetch("/api/resources/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resourceId }),
      });

      if (res.ok) {
        await fetchResources();
      } else {
        alert(t("idsUse.alert.analyzeFailed"));
      }
    } catch (error) {
      console.error("Analyze request failed", error);
    } finally {
      setAnalyzingId(null);
    }
  };

  const getStatusBadge = (status?: string) => {
    switch (status) {
      case "completed":
        return <Badge variant="success">{t("idsUse.status.completed")}</Badge>;
      case "processing":
        return <Badge variant="processing">{t("idsUse.status.processing")}</Badge>;
      case "failed":
        return <Badge variant="destructive">{t("idsUse.status.failed")}</Badge>;
      default:
        return <Badge variant="secondary">{t("idsUse.status.pending")}</Badge>;
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <h2 className="mb-6 flex items-center gap-2 text-3xl font-extrabold text-blue-700 dark:text-blue-300 md:text-4xl">
        {t("idsUse.title")}
      </h2>

      <form className="mb-8 space-y-4 rounded-lg border bg-white p-6 shadow-sm" onSubmit={handleUpload}>
        <div className="flex items-center gap-4">
          <Input
            type="file"
            ref={fileInputRef}
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null);
            }}
            className="flex-1"
          />
          <Button type="submit" disabled={loading || !session?.user?.id || !file}>
            {loading ? t("idsUse.uploading") : t("idsUse.uploadResource")}
          </Button>
        </div>
        <div className="flex justify-end">
          <Button type="button" variant="outline" onClick={fetchResources} disabled={!session?.user?.id}>
            {t("idsUse.manualRefresh")}
          </Button>
        </div>
      </form>

      <div>
        <h3 className="mb-4 text-xl font-semibold">{t("idsUse.resourcesTitle")}</h3>
        {resources.length === 0 ? (
          <p className="py-10 text-center text-gray-500">{t("idsUse.empty")}</p>
        ) : (
          <ul className="space-y-4">
            {resources.map((resource) => (
              <li key={resource._id} className="rounded-lg border bg-white p-4 shadow-sm transition-shadow hover:shadow-md">
                <div className="mb-2 flex items-start justify-between">
                  <div>
                    <div className="text-lg font-bold text-gray-800">{resource.originalname}</div>
                    <div className="text-sm text-gray-500">
                      {t("idsUse.uploadTime")}: {new Date(resource.uploadTime).toLocaleString(locale === "zh" ? "zh-CN" : "en-US")}
                    </div>
                  </div>
                  <div>{getStatusBadge(resource.status)}</div>
                </div>

                <div className="mt-4 flex justify-end gap-2 border-t pt-3">
                  {(resource.status === "pending" || resource.status === "failed" || !resource.status) && (
                    <Button size="sm" onClick={() => handleAnalyze(resource._id)} disabled={analyzingId === resource._id}>
                      {analyzingId === resource._id ? t("idsUse.actions.requesting") : t("idsUse.actions.analyze")}
                    </Button>
                  )}

                  <Button size="sm" variant="outline" onClick={() => handleDownload(resource._id)}>
                    {t("idsUse.actions.originalFile")}
                  </Button>

                  {resource.status === "completed" && (
                    <Button size="sm" className="bg-green-600 text-white hover:bg-green-700" onClick={() => handleDownloadResult(resource._id)}>
                      {t("idsUse.actions.downloadJsonResult")}
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
