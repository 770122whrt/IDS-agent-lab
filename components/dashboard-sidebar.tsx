"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { signOut } from "@/app/lib/auth-client";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import {
  Sparkles,
  ListTodo,
  LogOut,
  User,
  ChevronDown,
  ClipboardCheck,
} from "lucide-react";

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
  const [tasks, setTasks] = useState<Task[]>([]);
  const [tasksExpanded, setTasksExpanded] = useState(false);
  const [reportsExpanded, setReportsExpanded] = useState(false);

  const isTasksActive = pathname.startsWith("/tasks");

  const checkedTasks = tasks.filter((t) => t.status === "checked");

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
    router.push("/sign-in");
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
      case "checked":
        return "bg-green-500";
      case "processing":
      case "checking":
        return "bg-blue-500 animate-pulse";
      case "failed":
      case "check_failed":
        return "bg-red-500";
      default:
        return "bg-slate-500";
    }
  };

  const getReportLabel = (task: Task) => {
    if (task.input_type === "text" && task.inputText) {
      return task.inputText.slice(0, 25) + (task.inputText.length > 25 ? "..." : "");
    }
    return task.originalname.slice(0, 25) + (task.originalname.length > 25 ? "..." : "");
  };

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-64 bg-slate-900 text-white flex flex-col z-40">
      {/* Logo */}
      <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-700/50">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
        <span className="text-lg font-semibold tracking-tight">IDS Agent</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {/* Dashboard */}
        <Link
          href="/dashboard"
          className={cn(
            "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
            pathname === "/dashboard"
              ? "bg-blue-600/20 text-blue-400"
              : "text-slate-300 hover:bg-slate-800 hover:text-white"
          )}
        >
          <Sparkles className="w-5 h-5" />
          生成 IDS
        </Link>

        {/* Tasks - Expandable */}
        <div>
          <button
            onClick={() => setTasksExpanded(!tasksExpanded)}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
              isTasksActive
                ? "bg-blue-600/20 text-blue-400"
                : "text-slate-300 hover:bg-slate-800 hover:text-white"
            )}
          >
            <ListTodo className="w-5 h-5" />
            <span className="flex-1 text-left">任务列表</span>
            {tasks.length > 0 && (
              <span className="text-xs bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded-full">
                {tasks.length}
              </span>
            )}
            <ChevronDown
              className={cn(
                "w-4 h-4 transition-transform",
                tasksExpanded && "rotate-180"
              )}
            />
          </button>

          {tasksExpanded && tasks.length > 0 && (
            <div className="ml-4 mt-1 space-y-0.5 border-l border-slate-700/50 pl-3">
              {tasks.map((task) => (
                <Link
                  key={task._id}
                  href={`/tasks/${task._id}`}
                  className={cn(
                    "flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-colors",
                    pathname === `/tasks/${task._id}`
                      ? "text-blue-400 bg-slate-800/50"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/30"
                  )}
                  title={task.input_type === "text" && task.inputText ? task.inputText : task.originalname}
                >
                  <span
                    className={cn(
                      "w-1.5 h-1.5 rounded-full shrink-0",
                      getStatusColor(task.status)
                    )}
                  />
                  <span className="truncate">
                    {task.input_type === "text" && task.inputText
                      ? task.inputText.slice(0, 30) + (task.inputText.length > 30 ? "..." : "")
                      : task.originalname}
                  </span>
                </Link>
              ))}
              <Link
                href="/tasks"
                className="flex items-center gap-2 px-2 py-1.5 rounded text-xs text-slate-500 hover:text-slate-300 transition-colors"
              >
                查看全部 →
              </Link>
            </div>
          )}
        </div>

        {/* Reports - Expandable */}
        <div>
          <button
            onClick={() => setReportsExpanded(!reportsExpanded)}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
              pathname.includes("/report")
                ? "bg-blue-600/20 text-blue-400"
                : "text-slate-300 hover:bg-slate-800 hover:text-white"
            )}
          >
            <ClipboardCheck className="w-5 h-5" />
            <span className="flex-1 text-left">审查报告</span>
            {checkedTasks.length > 0 && (
              <span className="text-xs bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded-full">
                {checkedTasks.length}
              </span>
            )}
            <ChevronDown
              className={cn(
                "w-4 h-4 transition-transform",
                reportsExpanded && "rotate-180"
              )}
            />
          </button>

          {reportsExpanded && checkedTasks.length > 0 && (
            <div className="ml-4 mt-1 space-y-0.5 border-l border-slate-700/50 pl-3">
              {checkedTasks.map((task) => {
                const summary = task.reportSummary;
                return (
                  <Link
                    key={task._id}
                    href={`/tasks/${task._id}/report`}
                    className={cn(
                      "flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-colors",
                      pathname === `/tasks/${task._id}/report`
                        ? "text-blue-400 bg-slate-800/50"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/30"
                    )}
                    title={task.input_type === "text" && task.inputText ? task.inputText : task.originalname}
                  >
                    <span className="w-1.5 h-1.5 rounded-full shrink-0 bg-green-500" />
                    <span className="flex-1 truncate">{getReportLabel(task)}</span>
                    {summary && (
                      <span className={cn(
                        "text-[10px] px-1 rounded",
                        summary.failed_specs > 0
                          ? "text-red-400 bg-red-900/30"
                          : "text-green-400 bg-green-900/30"
                      )}>
                        {summary.passed_specs}/{summary.total_specs}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          )}

          {reportsExpanded && checkedTasks.length === 0 && (
            <div className="ml-4 mt-1 pl-3 py-2">
              <p className="text-xs text-slate-500">暂无审查报告</p>
            </div>
          )}
        </div>
      </nav>

      {/* User Section */}
      <div className="border-t border-slate-700/50 p-4">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center">
            <User className="w-4 h-4 text-slate-300" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">
              {user.name || "用户"}
            </p>
            <p className="text-xs text-slate-400 truncate">{user.email}</p>
          </div>
        </div>
        <button
          onClick={handleSignOut}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
        >
          <LogOut className="w-4 h-4" />
          退出登录
        </button>
      </div>
    </aside>
  );
}
