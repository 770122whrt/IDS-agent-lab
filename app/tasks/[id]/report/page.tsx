"use client";

import { useSession } from "@/app/lib/auth-client";
import { Badge } from "@/components/ui/badge";
import { useRouter, useParams } from "next/navigation";
import { useEffect, useState } from "react";

// 报告数据类型定义
interface Specification {
  name: string;
  description?: string;
  instructions?: string;
  status: "pass" | "fail";
  pass_count?: number;
  fail_count?: number;
  entities?: EntityResult[];
}

interface EntityResult {
  entity_id?: number;
  entity_guid?: string;
  entity_name?: string;
  entity_type?: string;
  status: "pass" | "fail";
  message?: string;
  requirements?: RequirementResult[];
}

interface RequirementResult {
  name?: string;
  status: "pass" | "fail";
  message?: string;
  value?: string;
  expected?: string;
}

interface ReportData {
  info?: {
    title?: string;
    description?: string;
    version?: string;
    copyright?: string;
  };
  specifications?: Specification[];
}

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
  status: string;
  uploadTime: string;
  idsFileId?: string;
  ifcFileName?: string;
  reportData?: ReportData;
  reportSummary?: ReportSummary;
  checkedAt?: string;
  errorMessage?: string;
}

export default function ReportPage() {
  const { data: session, isPending: sessionLoading } = useSession();
  const router = useRouter();
  const params = useParams();
  const taskId = params?.id as string;

  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSpecs, setExpandedSpecs] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!sessionLoading && !session?.user) {
      router.push("/sign-in");
    }
  }, [sessionLoading, session?.user, router]);

  useEffect(() => {
    if (!taskId) return;

    const fetchTask = async () => {
      try {
        const res = await fetch(`/api/tasks/${taskId}`);
        if (!res.ok) {
          throw new Error("获取任务失败");
        }
        const data = await res.json();
        setTask(data.task);

        if (data.task?.status !== "checked") {
          setError("任务尚未完成审查");
        }
      } catch (err) {
        console.error("Failed to fetch task:", err);
        setError(err instanceof Error ? err.message : "加载失败");
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [taskId]);

  const toggleSpec = (specName: string) => {
    setExpandedSpecs((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(specName)) {
        newSet.delete(specName);
      } else {
        newSet.add(specName);
      }
      return newSet;
    });
  };

  if (sessionLoading || loading) {
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
          <p className="text-lg text-gray-700">加载报告...</p>
        </div>
      </div>
    );
  }

  if (!session?.user) {
    return null;
  }

  if (error || !task) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <p className="text-red-600">{error || "任务不存在"}</p>
            <button
              onClick={() => router.push("/tasks")}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              返回任务列表
            </button>
          </div>
        </div>
      </div>
    );
  }

  const reportData = task.reportData;
  const summary = task.reportSummary;
  const checkedAt = task.checkedAt ? new Date(task.checkedAt).toLocaleString() : "未知";

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <button
              onClick={() => router.push("/tasks")}
              className="text-blue-600 hover:text-blue-800 mb-2 flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              返回任务列表
            </button>
            <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-100">
              IDS 审查报告
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {task.originalname}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => router.push(`/tasks/${taskId}/download`)}
              className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              下载 IDS
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {/* Overall Status */}
          <div className={`rounded-lg shadow p-6 ${summary && summary.failed_specs > 0 ? "bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800" : "bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"}`}>
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-full ${summary && summary.failed_specs > 0 ? "bg-red-100 dark:bg-red-800" : "bg-green-100 dark:bg-green-800"}`}>
                {summary && summary.failed_specs > 0 ? (
                  <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                ) : (
                  <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                )}
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">审查结果</p>
                <p className={`text-xl font-bold ${summary && summary.failed_specs > 0 ? "text-red-600 dark:text-red-400" : "text-green-600 dark:text-green-400"}`}>
                  {summary && summary.failed_specs > 0 ? "存在不合规" : "全部通过"}
                </p>
              </div>
            </div>
          </div>

          {/* Total Specs */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-full bg-blue-100 dark:bg-blue-900">
                <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">规格总数</p>
                <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                  {summary?.total_specs || 0}
                </p>
              </div>
            </div>
          </div>

          {/* Passed Specs */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-full bg-green-100 dark:bg-green-900">
                <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">通过规格</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {summary?.passed_specs || 0}
                </p>
              </div>
            </div>
          </div>

          {/* Failed Specs */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-full bg-red-100 dark:bg-red-900">
                <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">失败规格</p>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {summary?.failed_specs || 0}
                </p>
                {summary && summary.total_failed_entities > 0 && (
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {summary.total_failed_entities} 个构件错误
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Task Info */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow mb-6 p-4">
          <div className="flex flex-wrap gap-6 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>IFC 文件: <strong>{task.ifcFileName || "未知"}</strong></span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>审查时间: <strong>{checkedAt}</strong></span>
            </div>
          </div>
        </div>

        {/* Specifications List */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">
              规格审查详情
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              点击展开查看每个规格的详细结果
            </p>
          </div>

          {!reportData?.specifications || reportData.specifications.length === 0 ? (
            <div className="p-8 text-center text-gray-500 dark:text-gray-400">
              暂无规格数据
            </div>
          ) : (
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {reportData.specifications.map((spec, index) => (
                <div key={index} className="px-6 py-4">
                  {/* Specification Header */}
                  <button
                    onClick={() => toggleSpec(spec.name || `spec-${index}`)}
                    className="w-full flex items-center justify-between text-left"
                  >
                    <div className="flex items-center gap-3">
                      {spec.status === "pass" ? (
                        <Badge variant="success" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          通过
                        </Badge>
                      ) : (
                        <Badge variant="destructive" className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                          失败
                        </Badge>
                      )}
                      <div>
                        <h3 className="font-medium text-gray-800 dark:text-gray-100">
                          {spec.name || `规格 #${index + 1}`}
                        </h3>
                        {spec.description && (
                          <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-1">
                            {spec.description}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {spec.fail_count !== undefined && spec.fail_count > 0 && (
                        <span className="text-sm text-red-600 dark:text-red-400">
                          {spec.fail_count} 个构件失败
                        </span>
                      )}
                      <svg
                        className={`w-5 h-5 text-gray-400 transition-transform ${expandedSpecs.has(spec.name || `spec-${index}`) ? "rotate-180" : ""}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </button>

                  {/* Expanded Content */}
                  {expandedSpecs.has(spec.name || `spec-${index}`) && (
                    <div className="mt-4 pl-11">
                      {/* Instructions */}
                      {spec.instructions && (
                        <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded">
                          <p className="text-sm text-gray-600 dark:text-gray-300">
                            <strong>说明:</strong> {spec.instructions}
                          </p>
                        </div>
                      )}

                      {/* Entities */}
                      {spec.entities && spec.entities.length > 0 ? (
                        <div className="space-y-2">
                          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            构件审查结果 ({spec.entities.length} 个构件)
                          </h4>
                          <div className="max-h-64 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded">
                            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
                              <thead className="bg-gray-50 dark:bg-gray-700">
                                <tr>
                                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">状态</th>
                                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">类型</th>
                                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">名称</th>
                                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">ID</th>
                                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">信息</th>
                                </tr>
                              </thead>
                              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                {spec.entities.slice(0, 50).map((entity, entityIndex) => (
                                  <tr key={entityIndex} className={entity.status === "fail" ? "bg-red-50 dark:bg-red-900/10" : ""}>
                                    <td className="px-3 py-2 whitespace-nowrap">
                                      {entity.status === "pass" ? (
                                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                                          通过
                                        </span>
                                      ) : (
                                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                                          失败
                                        </span>
                                      )}
                                    </td>
                                    <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300">
                                      {entity.entity_type || "-"}
                                    </td>
                                    <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300">
                                      {entity.entity_name || "-"}
                                    </td>
                                    <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 font-mono">
                                      {entity.entity_id || entity.entity_guid || "-"}
                                    </td>
                                    <td className="px-3 py-2 text-sm text-gray-600 dark:text-gray-300">
                                      {entity.message || "-"}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                          {spec.entities.length > 50 && (
                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                              显示前 50 个构件，共 {spec.entities.length} 个
                            </p>
                          )}
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {spec.status === "pass" ? "所有构件均符合要求" : "无构件数据"}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}