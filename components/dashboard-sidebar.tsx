"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  ChevronDown,
  ClipboardCheck,
  ListTodo,
  LogOut,
  Sparkles,
  User,
} from "lucide-react";
import { signOut } from "@/app/lib/auth-client";
import { LanguageToggle } from "@/components/ui/language-toggle";
import { useLanguage } from "@/i18n/context/language-context";
import { cn } from "@/lib/utils";

interface Task {
  _id: string;
  originalname: string;
  inputText?: string;
  input_type: string;
  status: string;
  reportSummary?: {
    total_specs: number;
    passed_specs: number;
    failed_specs: number;
  };
}

interface DashboardSidebarProps {
  user: {
    name?: string | null;
    email?: string | null;
  };
}

export default function DashboardSidebar({ user }: DashboardSidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { t, locale } = useLanguage();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [tasksExpanded, setTasksExpanded] = useState(false);
  const [reportsExpanded, setReportsExpanded] = useState(false);

  const dashboardPath = `/${locale}/dashboard`;
  const tasksPath = `/${locale}/tasks`;
  const isTasksActive = pathname.startsWith(tasksPath);
  const checkedTasks = tasks.filter((task) => task.status === "checked");

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const res = await fetch("/api/resources", { credentials: "include" });
        const data = await res.json();
        setTasks(data.resources || []);
      } catch (error) {
        console.error("Failed to fetch tasks for sidebar:", error);
      }
    };
    fetchTasks();
  }, []);

  const handleSignOut = async () => {
    await signOut();
    router.push(`/${locale}/sign-in`);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
      case "checked":
        return "bg-green-500";
      case "processing":
      case "checking":
        return "animate-pulse bg-blue-500";
      case "failed":
      case "check_failed":
        return "bg-red-500";
      default:
        return "bg-slate-500";
    }
  };

  const getReportLabel = (task: Task) => {
    const label = task.input_type === "text" && task.inputText ? task.inputText : task.originalname;
    return label.slice(0, 25) + (label.length > 25 ? "..." : "");
  };

  return (
    <aside className="fixed bottom-0 left-0 top-0 z-40 flex w-64 flex-col bg-slate-900 text-white">
      <div className="flex h-16 items-center gap-3 border-b border-slate-700/50 px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600">
          <Sparkles className="h-4 w-4 text-white" />
        </div>
        <span className="text-lg font-semibold tracking-tight">{t("common.appName")}</span>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        <Link
          href={dashboardPath}
          className={cn(
            "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
            pathname === dashboardPath
              ? "bg-blue-600/20 text-blue-400"
              : "text-slate-300 hover:bg-slate-800 hover:text-white",
          )}
        >
          <Sparkles className="h-5 w-5" />
          {t("nav.generateIds")}
        </Link>

        <div>
          <button
            type="button"
            onClick={() => setTasksExpanded(!tasksExpanded)}
            className={cn(
              "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
              isTasksActive
                ? "bg-blue-600/20 text-blue-400"
                : "text-slate-300 hover:bg-slate-800 hover:text-white",
            )}
          >
            <ListTodo className="h-5 w-5" />
            <span className="flex-1 text-left">{t("nav.tasks")}</span>
            {tasks.length > 0 && (
              <span className="rounded-full bg-slate-700 px-1.5 py-0.5 text-xs text-slate-300">
                {tasks.length}
              </span>
            )}
            <ChevronDown className={cn("h-4 w-4 transition-transform", tasksExpanded && "rotate-180")} />
          </button>

          {tasksExpanded && tasks.length > 0 && (
            <div className="ml-4 mt-1 space-y-0.5 border-l border-slate-700/50 pl-3">
              {tasks.map((task) => (
                <Link
                  key={task._id}
                  href={`/${locale}/tasks/${task._id}`}
                  className={cn(
                    "flex items-center gap-2 rounded px-2 py-1.5 text-xs transition-colors",
                    pathname === `/${locale}/tasks/${task._id}`
                      ? "bg-slate-800/50 text-blue-400"
                      : "text-slate-400 hover:bg-slate-800/30 hover:text-slate-200",
                  )}
                  title={task.input_type === "text" && task.inputText ? task.inputText : task.originalname}
                >
                  <span className={cn("h-1.5 w-1.5 shrink-0 rounded-full", getStatusColor(task.status))} />
                  <span className="truncate">
                    {task.input_type === "text" && task.inputText
                      ? task.inputText.slice(0, 30) + (task.inputText.length > 30 ? "..." : "")
                      : task.originalname}
                  </span>
                </Link>
              ))}
              <Link
                href={tasksPath}
                className="flex items-center gap-2 rounded px-2 py-1.5 text-xs text-slate-500 transition-colors hover:text-slate-300"
              >
                {t("nav.viewAll")} -&gt;
              </Link>
            </div>
          )}
        </div>

        <div>
          <button
            type="button"
            onClick={() => setReportsExpanded(!reportsExpanded)}
            className={cn(
              "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
              pathname.includes("/report")
                ? "bg-blue-600/20 text-blue-400"
                : "text-slate-300 hover:bg-slate-800 hover:text-white",
            )}
          >
            <ClipboardCheck className="h-5 w-5" />
            <span className="flex-1 text-left">{t("nav.reports")}</span>
            {checkedTasks.length > 0 && (
              <span className="rounded-full bg-slate-700 px-1.5 py-0.5 text-xs text-slate-300">
                {checkedTasks.length}
              </span>
            )}
            <ChevronDown className={cn("h-4 w-4 transition-transform", reportsExpanded && "rotate-180")} />
          </button>

          {reportsExpanded && checkedTasks.length > 0 && (
            <div className="ml-4 mt-1 space-y-0.5 border-l border-slate-700/50 pl-3">
              {checkedTasks.map((task) => {
                const summary = task.reportSummary;
                return (
                  <Link
                    key={task._id}
                    href={`/${locale}/tasks/${task._id}/report`}
                    className={cn(
                      "flex items-center gap-2 rounded px-2 py-1.5 text-xs transition-colors",
                      pathname === `/${locale}/tasks/${task._id}/report`
                        ? "bg-slate-800/50 text-blue-400"
                        : "text-slate-400 hover:bg-slate-800/30 hover:text-slate-200",
                    )}
                    title={task.input_type === "text" && task.inputText ? task.inputText : task.originalname}
                  >
                    <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-green-500" />
                    <span className="flex-1 truncate">{getReportLabel(task)}</span>
                    {summary && (
                      <span
                        className={cn(
                          "rounded px-1 text-[10px]",
                          summary.failed_specs > 0
                            ? "bg-red-900/30 text-red-400"
                            : "bg-green-900/30 text-green-400",
                        )}
                      >
                        {summary.passed_specs}/{summary.total_specs}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          )}

          {reportsExpanded && checkedTasks.length === 0 && (
            <div className="ml-4 mt-1 py-2 pl-3">
              <p className="text-xs text-slate-500">{t("nav.noReports")}</p>
            </div>
          )}
        </div>
      </nav>

      <div className="border-t border-slate-700/50 p-4">
        <div className="mb-3 flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-700">
            <User className="h-4 w-4 text-slate-300" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-white">
              {user.name || t("nav.userFallback")}
            </p>
            <p className="truncate text-xs text-slate-400">{user.email}</p>
          </div>
        </div>
        <div className="mb-3">
          <LanguageToggle />
        </div>
        <button
          type="button"
          onClick={handleSignOut}
          className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-400 transition-colors hover:bg-slate-800 hover:text-white"
        >
          <LogOut className="h-4 w-4" />
          {t("nav.signOut")}
        </button>
      </div>
    </aside>
  );
}
