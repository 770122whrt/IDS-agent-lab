"use client";

import { useSession } from "@/app/lib/auth-client";
import { useRouter, useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useLanguage } from "@/i18n/context/language-context";
import { LanguageToggle } from "@/components/ui/language-toggle";

// =============================================================================
// 类型定义
// =============================================================================

interface FailedEntity {
  reason: string;
  element?: string;
  element_type?: string;
  class: string;
  predefined_type?: string;
  name: string;
  description?: string;
  id?: number;
  global_id: string;
  tag?: string;
}

interface Requirement {
  facet_type: string;
  metadata?: {
    propertySet?: { simpleValue?: string };
    baseName?: { simpleValue?: string };
    "@dataType"?: string;
    "@cardinality"?: string;
    [key: string]: unknown;
  };
  label: string;
  value?: string;
  description: string;
  status: boolean;
  passed_entities: unknown[];
  failed_entities: FailedEntity[];
  total_applicable: number;
  total_pass: number;
  total_fail: number;
  percent_pass: number | string;
}

interface Specification {
  name: string;
  description: string;
  instructions: string;
  status: boolean;
  is_ifc_version: boolean;
  total_applicable: number;
  total_applicable_pass: number;
  total_applicable_fail: number;
  percent_applicable_pass: number | string;
  total_checks: number;
  total_checks_pass: number;
  total_checks_fail: number;
  percent_checks_pass: number | string;
  cardinality: string;
  applicability: string[];
  requirements: Requirement[];
}

interface ReportData {
  title: string;
  date: string;
  filepath?: string | null;
  filename?: string | null;
  specifications: Specification[];
  status: boolean;
  total_specifications: number;
  total_specifications_pass: number;
  total_specifications_fail: number;
  percent_specifications_pass: number;
  total_requirements: number;
  total_requirements_pass: number;
  total_requirements_fail: number;
  percent_requirements_pass: number;
  total_checks: number;
  total_checks_pass: number;
  total_checks_fail: number;
  percent_checks_pass: number;
}

interface Task {
  _id: string;
  originalname: string;
  input_type: "text" | "ifc_file";
  status: string;
  uploadTime: string;
  idsFileId?: string;
  ifcFileName?: string;
  reportData?: ReportData;
  checkedAt?: string;
  errorMessage?: string;
}

// =============================================================================
// 主组件
// =============================================================================

export default function ReportPage() {
  const { data: session, isPending: sessionLoading } = useSession();
  const router = useRouter();
  const params = useParams();
  const taskId = params?.id as string;
  const { t, language } = useLanguage();

  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedReqs, setExpandedReqs] = useState<Set<string>>(new Set());

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
        if (!res.ok) throw new Error(t("report.fetchError"));
        const data = await res.json();
        setTask(data.task);

        if (data.task?.status !== "checked") {
          setError(t("report.notChecked"));
        }
      } catch (err) {
        console.error("Failed to fetch task:", err);
        setError(err instanceof Error ? err.message : t("report.loadFailed"));
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [taskId]);

  const toggleRequirement = (specIndex: number, reqIndex: number) => {
    const key = `${specIndex}-${reqIndex}`;
    setExpandedReqs((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(key)) newSet.delete(key);
      else newSet.add(key);
      return newSet;
    });
  };

  // 加载状态
  if (sessionLoading || loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-600 dark:text-slate-400">{t("report.loading")}</p>
        </div>
      </div>
    );
  }

  if (!session?.user) return null;

  if (error || !task) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-6">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-6 text-center">
            <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <p className="text-red-600 dark:text-red-400 font-medium mb-4">{error || t("report.notFound")}</p>
            <button
              onClick={() => router.push("/tasks")}
              className="px-4 py-2 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 rounded-lg hover:bg-slate-800 dark:hover:bg-slate-200 transition-colors"
            >
              {t("report.backToList")}
            </button>
          </div>
        </div>
      </div>
    );
  }

  const reportData = task.reportData;
  const checkedAt = task.checkedAt ? new Date(task.checkedAt).toLocaleString(language === 'zh' ? 'zh-CN' : 'en-US') : t("report.unknown");

  // 如果没有报告数据
  if (!reportData || !reportData.specifications) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-6">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-6 text-center">
            <p className="text-slate-600 dark:text-slate-400 mb-4">{t("report.noData")}</p>
            <button
              onClick={() => router.push("/tasks")}
              className="px-4 py-2 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 rounded-lg"
            >
              {t("report.backToList")}
            </button>
          </div>
        </div>
      </div>
    );
  }

  const {
    title = t("report.title"),
    date,
    specifications = [],
    status: overallStatus,
    total_specifications = 0,
    total_specifications_pass = 0,
    total_checks = 0,
    total_checks_pass = 0,
    total_checks_fail = 0,
  } = reportData;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between mb-3">
            <button
              onClick={() => router.push("/tasks")}
              className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              {t("report.backToList")}
            </button>
            <LanguageToggle />
          </div>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h1 className="text-xl font-semibold text-slate-900 dark:text-white">{title}</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                {t("report.reviewTime")}: {date || checkedAt}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium ${
                overallStatus
                  ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                  : "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400"
              }`}>
                {overallStatus ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                )}
                {overallStatus ? t("report.allPassed") : t("report.hasIssues")}
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {/* Summary Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">{t("report.totalSpecs")}</p>
            <p className="text-2xl font-semibold text-slate-900 dark:text-white">{total_specifications}</p>
          </div>
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">{t("report.passedSpecs")}</p>
            <p className="text-2xl font-semibold text-emerald-600 dark:text-emerald-400">{total_specifications_pass}</p>
          </div>
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">{t("report.checkItems")}</p>
            <p className="text-2xl font-semibold text-slate-900 dark:text-white">{total_checks}</p>
          </div>
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">{t("report.failedItems")}</p>
            <p className="text-2xl font-semibold text-red-600 dark:text-red-400">{total_checks_fail}</p>
          </div>
        </div>

        {/* Specifications List - 垂直堆叠布局 */}
        <div className="space-y-6">
          {specifications.map((spec, specIndex) => (
            <SpecificationCard
              key={specIndex}
              spec={spec}
              specIndex={specIndex}
              expandedReqs={expandedReqs}
              onToggleRequirement={toggleRequirement}
              t={t}
            />
          ))}
        </div>
      </main>
    </div>
  );
}

// =============================================================================
// Specification 卡片组件 - 上下堆叠布局
// =============================================================================

interface SpecificationCardProps {
  spec: Specification;
  specIndex: number;
  expandedReqs: Set<string>;
  onToggleRequirement: (specIndex: number, reqIndex: number) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
}

function SpecificationCard({ spec, specIndex, expandedReqs, onToggleRequirement, t }: SpecificationCardProps) {
  // 当 percent_checks_pass 是 "N/A" 时，如果 status 为 true（全部通过），显示 100%，否则显示 0%
  const passPercent = typeof spec.percent_checks_pass === "number"
    ? spec.percent_checks_pass
    : spec.status ? 100 : 0;
  const hasFailures = spec.total_checks_fail > 0;

  return (
    <div className={`bg-white dark:bg-slate-900 rounded-xl border overflow-hidden transition-shadow hover:shadow-md ${
      spec.status
        ? "border-slate-200 dark:border-slate-800"
        : "border-red-200 dark:border-red-900/50"
    }`}>
      {/* ===== 顶部：规范信息区域 ===== */}
      <div className="p-5 border-b border-slate-100 dark:border-slate-800">
        {/* 标题行 */}
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white truncate">
              {spec.name || `Specification #${specIndex + 1}`}
            </h3>
            {spec.description && (
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{spec.description}</p>
            )}
          </div>
          {/* 状态徽章 */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium ${
              spec.status
                ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                : "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400"
            }`}>
              {spec.status ? (
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
              {spec.cardinality === "required" ? t("report.required") : t("report.optional")}: {spec.status ? t("report.passed") : t("report.failed")}
            </span>
          </div>
        </div>

        {/* 进度条 */}
        <div className="mb-3">
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1">
            <span>{t("report.passRate")}</span>
            <span>{passPercent.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                spec.status ? "bg-emerald-500" : "bg-red-500"
              }`}
              style={{ width: `${passPercent}%` }}
            />
          </div>
        </div>

        {/* 统计信息 */}
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-slate-600 dark:text-slate-400">
          <span>{t("report.checks")}: <strong className="text-slate-900 dark:text-white">{spec.total_checks_pass}</strong>/{spec.total_checks} {t("report.passed")}</span>
          <span>{t("report.entities")}: <strong className="text-slate-900 dark:text-white">{spec.total_applicable_pass}</strong>/{spec.total_applicable} {t("report.passed")}</span>
          {hasFailures && (
            <span className="text-red-600 dark:text-red-400">
              <strong>{spec.total_checks_fail}</strong> {t("report.failed")}
            </span>
          )}
        </div>

        {/* 警告/说明 */}
        {spec.is_ifc_version === false && (
          <div className="mt-3 flex items-start gap-2 p-2.5 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg text-xs text-amber-700 dark:text-amber-300">
            <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{t("report.specNotApplicable")}</span>
          </div>
        )}
        {spec.instructions && (
          <div className="mt-3 flex items-start gap-2 p-2.5 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg text-xs text-blue-700 dark:text-blue-300">
            <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{spec.instructions}</span>
          </div>
        )}
      </div>

      {/* ===== 中间：Applicability 适用范围 ===== */}
      <div className="px-5 py-4 bg-slate-50/50 dark:bg-slate-800/30 border-b border-slate-100 dark:border-slate-800">
        <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
          {t("report.applicability")}
        </h4>
        {spec.applicability?.length > 0 ? (
          <ul className="space-y-1">
            {spec.applicability.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-700 dark:text-slate-300">
                <span className="text-slate-400 dark:text-slate-500 mt-0.5">•</span>
                <code className="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded text-xs font-mono">
                  {item}
                </code>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-400 dark:text-slate-500">{t("report.noApplicability")}</p>
        )}
      </div>

      {/* ===== 底部：Requirements 要求列表 ===== */}
      <div className="p-5">
        <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">
          {t("report.requirements")}
        </h4>
        {spec.requirements?.length > 0 ? (
          <div className="space-y-2">
            {spec.requirements.map((req, reqIndex) => (
              <RequirementItem
                key={reqIndex}
                requirement={req}
                reqIndex={reqIndex}
                specIndex={specIndex}
                isExpanded={expandedReqs.has(`${specIndex}-${reqIndex}`)}
                onToggle={() => onToggleRequirement(specIndex, reqIndex)}
                t={t}
              />
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-400 dark:text-slate-500">{t("report.noRequirements")}</p>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Requirement 条目组件
// =============================================================================

interface RequirementItemProps {
  requirement: Requirement;
  reqIndex: number;
  specIndex: number;
  isExpanded: boolean;
  onToggle: () => void;
  t: (key: string, params?: Record<string, string | number>) => string;
}

function RequirementItem({ requirement: req, reqIndex, isExpanded, onToggle, t }: RequirementItemProps) {
  const hasFailures = req.failed_entities?.length > 0;
  const failedCount = req.failed_entities?.length || 0;

  return (
    <div className={`rounded-lg border transition-colors ${
      req.status
        ? "border-slate-200 dark:border-slate-700 bg-slate-50/30 dark:bg-slate-800/30"
        : hasFailures
        ? "border-red-200 dark:border-red-900/50 bg-red-50/50 dark:bg-red-900/10"
        : "border-slate-200 dark:border-slate-700 bg-slate-50/30 dark:bg-slate-800/30"
    }`}>
      {/* 标题栏 - 可点击展开 */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-3 text-left hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-lg"
      >
        <div className="flex items-center gap-3 min-w-0 flex-1">
          {/* 序号和状态图标 */}
          <span className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
            req.status
              ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-400"
              : "bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-400"
          }`}>
            {req.status ? "✓" : "✗"}
          </span>
          {/* 描述 */}
          <span className="text-sm text-slate-700 dark:text-slate-300 truncate">
            {req.description || req.label || `Requirement #${reqIndex + 1}`}
          </span>
        </div>
        {/* 右侧信息 */}
        <div className="flex items-center gap-2 flex-shrink-0 ml-3">
          {hasFailures && (
            <span className="text-xs bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 px-2 py-0.5 rounded-full">
              {failedCount} {t("report.error")}
            </span>
          )}
          <svg
            className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${isExpanded ? "rotate-180" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* 展开内容 - Failed Entities 表格 */}
      {isExpanded && (
        <div className="px-3 pb-3 border-t border-slate-100 dark:border-slate-700 mt-1 pt-3">
          {/* 元数据标签 */}
          {req.metadata && (
            <div className="mb-3 inline-flex items-center px-2.5 py-1 bg-slate-100 dark:bg-slate-800 rounded text-xs font-mono text-slate-600 dark:text-slate-400">
              {req.metadata.propertySet?.simpleValue && (
                <span>{req.metadata.propertySet.simpleValue}</span>
              )}
              {req.metadata.baseName?.simpleValue && (
                <span>.{req.metadata.baseName.simpleValue}</span>
              )}
              {req.metadata["@dataType"] && (
                <span className="ml-1 text-slate-400">({req.metadata["@dataType"]})</span>
              )}
            </div>
          )}

          {/* 失败构件表格 */}
          {hasFailures ? (
            <div className="overflow-x-auto rounded-lg border border-red-100 dark:border-red-900/30">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-red-50 dark:bg-red-900/20">
                    <th className="px-3 py-2 text-left font-medium text-red-700 dark:text-red-300">{t("report.type")}</th>
                    <th className="px-3 py-2 text-left font-medium text-red-700 dark:text-red-300">{t("report.name")}</th>
                    <th className="px-3 py-2 text-left font-medium text-red-700 dark:text-red-300">GlobalId</th>
                    <th className="px-3 py-2 text-left font-medium text-red-700 dark:text-red-300">{t("report.errorReason")}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-red-100 dark:divide-red-900/20">
                  {req.failed_entities.slice(0, 5).map((entity, idx) => (
                    <tr key={idx} className="hover:bg-red-50/50 dark:hover:bg-red-900/10">
                      <td className="px-3 py-2 font-mono text-slate-700 dark:text-slate-300">{entity.class}</td>
                      <td className="px-3 py-2 text-slate-700 dark:text-slate-300">{entity.name || "-"}</td>
                      <td className="px-3 py-2 font-mono text-blue-600 dark:text-blue-400">{entity.global_id}</td>
                      <td className="px-3 py-2 text-red-600 dark:text-red-400">{entity.reason || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {failedCount > 5 && (
                <div className="px-3 py-2 bg-slate-50 dark:bg-slate-800 text-xs text-slate-500 dark:text-slate-400 border-t border-red-100 dark:border-red-900/20">
                  {t("report.moreEntitiesWithError", { count: failedCount - 5 })}
                </div>
              )}
            </div>
          ) : req.status ? (
            <div className="flex items-center gap-2 text-sm text-emerald-600 dark:text-emerald-400 py-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>{t("report.allChecksPassed")}</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 py-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{t("report.noApplicableEntities")}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
